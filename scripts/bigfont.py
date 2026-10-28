#!/usr/bin/env python3
"""Big Font Mode: turns a short step list into a printable, large-print HTML guide.

Standard library only. Open the HTML in any browser and print it, or save it as a PDF.

Input format (plain text):
  # Title of the guide
  For: Mum's iPhone 13                 (optional line starting with "For:")
  ## A section heading
  1. One action per step.
  2. Next action.
  > A tip shown in a soft box.
  ! A warning shown in a red box.
  ? Call me only if this happens.     (collected into the "Call me only if" box)

Usage:
  python bigfont.py steps.txt -o guide.html [--helper "Josh" --helper-phone "555 0100"]
"""
import argparse
import html
import os
import re
import sys

CSS = """
*{box-sizing:border-box}
body{font-family:Verdana,Arial,sans-serif;font-size:26px;line-height:1.5;color:#111;background:#fff;
     margin:0 auto;max-width:900px;padding:32px}
h1{font-size:44px;margin:0 0 8px}
.for{font-size:24px;color:#333;margin:0 0 28px}
h2{font-size:32px;margin:36px 0 12px;border-bottom:4px solid #111;padding-bottom:4px}
ol{list-style:none;padding:0;margin:0;counter-reset:step}
ol>li{counter-increment:step;display:flex;gap:18px;align-items:flex-start;border:3px solid #111;
   border-radius:14px;padding:18px 20px;margin:0 0 16px;page-break-inside:avoid;break-inside:avoid}
ol>li::before{content:counter(step);flex:0 0 64px;height:64px;border-radius:50%;background:#111;color:#fff;
   font-size:34px;font-weight:bold;display:flex;align-items:center;justify-content:center}
.box{flex:0 0 40px;height:40px;border:3px solid #111;border-radius:6px;margin-left:auto;margin-top:12px}
.tip{background:#eef5ff;border-left:10px solid #2457c5;padding:14px 18px;margin:0 0 16px;border-radius:8px}
.warn{background:#fff0f0;border-left:10px solid #c00;padding:14px 18px;margin:0 0 16px;border-radius:8px;font-weight:bold}
.callme{border:4px dashed #111;border-radius:14px;padding:18px 22px;margin-top:36px;page-break-inside:avoid}
.callme h2{border:0;margin-top:0}
.callme ul{margin:0;padding-left:1.2em}
.callme li{margin:0 0 10px}
.footer{margin-top:28px;font-size:24px;color:#333}
@media print{body{padding:0}}
"""


def parse(lines):
    doc = {"title": "Step by step", "for": "", "blocks": [], "callme": []}
    current = None
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            doc["title"] = line[2:].strip()
        elif line.lower().startswith("for:"):
            doc["for"] = line[4:].strip()
        elif line.startswith("## "):
            current = None
            doc["blocks"].append(("h2", line[3:].strip()))
        elif re.match(r"^\d+[.)]\s+", line):
            text = re.sub(r"^\d+[.)]\s+", "", line)
            if current is None:
                current = []
                doc["blocks"].append(("ol", current))
            current.append(text)
        elif line.startswith("> "):
            current = None
            doc["blocks"].append(("tip", line[2:].strip()))
        elif line.startswith("! "):
            current = None
            doc["blocks"].append(("warn", line[2:].strip()))
        elif line.startswith("? "):
            doc["callme"].append(line[2:].strip())
        else:
            current = None
            doc["blocks"].append(("p", line.strip()))
    return doc


def render(doc, helper=None, phone=None):
    e = html.escape
    out = ["<!doctype html><html lang='en'><head><meta charset='utf-8'>",
           "<meta name='viewport' content='width=device-width,initial-scale=1'>",
           f"<title>{e(doc['title'])}</title><style>{CSS}</style></head><body>",
           f"<h1>{e(doc['title'])}</h1>"]
    if doc["for"]:
        out.append(f"<p class='for'>For: {e(doc['for'])}</p>")
    for kind, val in doc["blocks"]:
        if kind == "h2":
            out.append(f"<h2>{e(val)}</h2>")
        elif kind == "ol":
            out.append("<ol>" + "".join(f"<li><span>{e(s)}</span><span class='box'></span></li>" for s in val) + "</ol>")
        elif kind == "tip":
            out.append(f"<div class='tip'>Tip: {e(val)}</div>")
        elif kind == "warn":
            out.append(f"<div class='warn'>Careful: {e(val)}</div>")
        else:
            out.append(f"<p>{e(val)}</p>")
    if doc["callme"] or helper:
        who = e(helper) if helper else "me"
        out.append(f"<div class='callme'><h2>Call {who} only if</h2><ul>")
        out += [f"<li>{e(c)}</li>" for c in doc["callme"]]
        out.append("</ul>")
        if phone:
            out.append(f"<p><strong>{who}: {e(phone)}</strong></p>")
        out.append("</div>")
    out.append("<p class='footer'>Tick each box as you go. If a screen looks different, stop and call. "
               "Nobody real will ever ask you for a code, a password or a gift card.</p></body></html>")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Big Font Mode guide maker")
    ap.add_argument("steps", help="plain-text step file ('-' for stdin)")
    ap.add_argument("-o", "--out", default="guide.html")
    ap.add_argument("--helper", help="name of the family helper for the 'Call me only if' box")
    ap.add_argument("--helper-phone")
    a = ap.parse_args(argv)
    if a.steps == "-":
        lines = sys.stdin.read().splitlines()
    else:
        with open(a.steps, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    doc = parse(lines)
    steps = sum(len(v) for k, v in doc["blocks"] if k == "ol")
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(render(doc, a.helper, a.helper_phone))
    print(f"BIG FONT MODE: wrote {os.path.abspath(a.out)}  ({steps} steps, {len(doc['callme'])} call-me rules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
