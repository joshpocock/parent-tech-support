#!/usr/bin/env python3
"""Scam Call Detector: checks a text, email, pop-up or call description for scam red flags.

Standard library only. It looks for the patterns that real scams share (gift cards, codes,
remote access, urgency, fake authorities). It can say "red flags found" with confidence. It can
never promise a message is safe, and it says so.

Usage:
  python scamcheck.py --text "Your Amazon account is locked. Call 1-800-..."
  echo "message" | python scamcheck.py
  python scamcheck.py --file message.txt [--json]
"""
import argparse
import json
import re
import sys

# Phrases are matched as whole words, with an optional plural "s". A phrase that starts with
# "re:" is a regular expression instead.
RULES = [
    ("gift_cards", 4, ["gift card", "itunes card", "apple card", "google play card", "steam card",
                       "ebay card", "target card", "vanilla card"],
     "Asks for gift cards. No real company, bank or government office takes payment in gift cards."),
    ("gift_card_codes", 3, ["scratch off", "picture of the back", "photo of the back",
                            "pictures of the back", "photos of the back", "re:numbers? on the back",
                            "re:(send|text|read) me the (card )?(codes|numbers)"],
     "Wants the numbers from the back of a card. Once someone has those, the money is gone."),
    ("odd_payment", 4, ["bitcoin", "crypto", "wire transfer", "western union", "moneygram",
                        "bitcoin atm", "zelle yourself", "send it to yourself", "safe account",
                        "cash in an envelope", "withdraw",
                        "re:courier (will|would|is going to) (come|collect|pick)",
                        "re:(come|coming) to (the|your) (house|door) to (collect|pick)"],
     "Asks for crypto, a wire, a 'safe account' or cash handed to a courier. That money cannot be got back."),
    ("remote_access", 4, ["anydesk", "teamviewer", "ultraviewer", "logmein", "quick assist",
                          "remote access", "connect to your computer", "let me into your computer",
                          "download this app so i can", "screen share", "share your screen"],
     "Wants to get into the computer or phone. Only let in someone you called yourself."),
    ("codes", 4, ["read me the code", "the code we sent",
                  "re:(send|tell|give|read|text|forward|share) (me|us) (the|that|your) ([0-9]-digit |six digit |verification |security )?code",
                  "re:what (is|was) the code", "re:reply with (the|your) code", "re:(confirm|verify) the code"],
     "Asks you to share a code. Codes are for you to type, never to read to anyone who contacted you."),
    ("overpayment", 4, ["refunded too much", "overpaid", "send back the difference",
                        "refund the difference", "accidentally sent you"],
     "The 'we refunded you too much' trick. The first refund is fake; the money you send back is real."),
    ("new_number", 3, ["new number", "lost my phone", "phone broke", "phone is broken", "broke my phone",
                       "save this number", "delete my old number", "my old number", "my phone died",
                       "re:(call|text) me (back )?on this number", "text me back here"],
     "Says it is family or a friend on a new number. Call them on the number you already have before replying."),
    ("family_trouble", 3, ["in jail", "bail", "had an accident", "car crash", "car accident",
                           "hit someone", "been arrested", "got arrested", "need a lawyer", "for a lawyer",
                           "don't tell mom", "dont tell mom", "don't tell dad", "dont tell dad",
                           "don't tell mum", "dont tell mum", "please don't be mad"],
     "A family emergency that needs money fast. Hang up and call the family member on their usual number."),
    ("money_ask", 2, ["help paying", "pay a bill", "need money", "send money", "send me money",
                      "lend me", "re:need [$] ?[0-9]", "re:need [0-9][0-9,]* (dollars|pounds)"],
     "Asks you for money. Check by calling the person on a number you already have before sending anything."),
    ("prize", 3, ["you've won", "you have won", "you won", "claim your prize", "claim your reward",
                  "sweepstakes", "lottery winner", "selected as a winner", "inheritance", "unclaimed funds"],
     "A prize you did not enter. Real prizes never ask for a fee or your bank details."),
    ("sensitive_info", 3, ["card number", "bank login", "your password", "confirm your password",
                           "enter your password", "social security number", "ssn", "sin number",
                           "national insurance number", "pin number", "your pin", "date of birth and",
                           "mother's maiden", "cvv", "security code on the back"],
     "Asks for private details. Your bank already has them and will never ask for your password or PIN."),
    ("secrecy", 3, ["don't tell", "dont tell", "keep this between us", "do not hang up",
                    "don't hang up", "stay on the line", "confidential case"],
     "Asks you to keep it secret or stay on the line. Real officials let you hang up and call back."),
    ("tech_popup", 3, ["virus detected", "your computer is infected", "your computer has been",
                       "call this number", "call microsoft", "call apple", "windows defender alert",
                       "do not close this window", "your device has been locked", "pc is blocked",
                       "computer is blocked", "computer has been blocked", "do not restart",
                       "do not shut down", "do not turn off your computer", "contact windows support",
                       "contact microsoft", "contact apple support"],
     "A pop-up with a phone number. Microsoft and Apple never put phone numbers in warning pop-ups."),
    ("account_lock", 2, ["account has been disabled", "account has been suspended", "account has been locked",
                         "account is locked", "account will be restricted", "unusual sign-in",
                         "unusual activity", "suspicious activity", "verify your account",
                         "confirm your identity", "verify your identity", "update your details",
                         "update your payment", "log in to unlock", "unlock your account"],
     "Says your account is locked or needs checking. Open the real app or call the number on your card instead."),
    ("urgency", 2, ["immediately", "within 24 hours", "urgent", "final notice", "act now",
                    "suspended", "has been locked", "will be closed", "will be arrested", "warrant",
                    "last warning", "expires today", "late fee"],
     "Rushes you. Scammers rush so you do not stop and ask someone."),
    ("authority", 2, ["irs", "social security", "medicare", "cra", "hmrc", "police", "sheriff",
                      "fbi", "microsoft support", "apple support", "amazon security", "fraud department",
                      "geek squad", "norton", "mcafee", "paypal", "windows support", "windows security",
                      "microsoft windows", "re:this is (amazon|apple|microsoft|paypal|your bank)"],
     "Claims to be a big company or government office. Look up their real number yourself and call that."),
    ("delivery_toll", 2, ["could not be delivered", "redelivery", "delivery fee", "unpaid toll",
                          "toll balance", "customs fee", "package is on hold", "incomplete address"],
     "A delivery or toll fee by text. A favourite scam right now; check the real app or website instead."),
]

SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "is.gd", "rb.gy", "cutt.ly", "shorturl.at", "ow.ly",
              "tiny.cc", "goo.gl"]
BRANDS = ["amazon", "paypal", "apple", "microsoft", "netflix", "usps", "fedex", "ups", "dhl",
          "wellsfargo", "chase", "bankofamerica", "irs", "google", "facebook", "instagram"]
REAL_DOMAINS = {"amazon.com", "paypal.com", "apple.com", "microsoft.com", "netflix.com", "usps.com",
                "fedex.com", "ups.com", "dhl.com", "wellsfargo.com", "chase.com",
                "bankofamerica.com", "irs.gov", "google.com", "facebook.com", "instagram.com"}
LINK_ASKS = re.compile(r"(?<![a-z])(pay|payment|verify|confirm|log ?in|sign ?in|update|unlock|claim|reschedule)(?![a-z])")
CODE_TEXT = re.compile(r"(?<![a-z])(code|passcode|otp)(?![a-z])")


def find_links(text):
    return re.findall(r"(?:https?://)?(?:www\.)?([a-z0-9-]+(?:\.[a-z0-9-]+)+)(/\S*)?", text.lower())


def link_flags(text):
    flags = []
    hosts = []
    for host, _path in find_links(text):
        if not re.search(r"[a-z]", host.split(".")[-1]):
            continue  # numbers like 1.800 or $4.35
        hosts.append(host)
        base = ".".join(host.split(".")[-2:])
        if any(host == s or host.endswith("." + s) for s in SHORTENERS):
            flags.append(("short_link", 2, f"Shortened link ({host}) hides where it really goes."))
            continue
        squashed = host.replace("-", "").replace("0", "o").replace("1", "l")
        for b in BRANDS:
            if b in squashed and base not in REAL_DOMAINS:
                flags.append(("lookalike", 3, f"'{host}' looks like {b} but is not {b}'s real website."))
                break
    return flags, hosts


def _pattern(p):
    body = p[3:] if p.startswith("re:") else re.escape(p) + "s?"
    return r"(?<![a-z])(?:" + body + r")(?![a-z])"


def check(text):
    low = " " + re.sub(r"\s+", " ", text.lower().replace("\u2019", "'")) + " "
    hits = []
    for key, weight, phrases, why in RULES:
        found = []
        for p in phrases:
            m = re.search(_pattern(p), low)
            if m:
                found.append(m.group(0).strip())
        if found:
            hits.append({"flag": key, "points": weight, "matched": found, "why": why})
    flags, hosts = link_flags(text)
    for key, weight, why in flags:
        hits.append({"flag": key, "points": weight, "matched": [], "why": why})
    if hosts:
        asks = sorted(set(m.group(1) for m in LINK_ASKS.finditer(low)))
        if asks:
            hits.append({"flag": "link_asks", "points": 2, "matched": asks,
                         "why": "Has a link that asks you to pay, log in or confirm something. Go to the "
                                "real app or type the website yourself instead."})
    pts = sum(h["points"] for h in hits)
    if pts >= 6:
        verdict = "ALMOST CERTAINLY A SCAM"
    elif pts >= 3:
        verdict = "LOOKS LIKE A SCAM"
    elif pts >= 1:
        verdict = "BE CAREFUL"
    else:
        verdict = "NO RED FLAGS FOUND"
    has_code = bool(CODE_TEXT.search(low))
    return {"verdict": verdict, "points": pts, "flags": hits, "next_steps": next_steps(hits, has_code)}


def next_steps(hits, has_code=False):
    keys = {h["flag"] for h in hits}
    steps = []
    if not hits:
        steps.append("No known scam patterns found, but that does not make it safe. If it asks for money, "
                     "a code or access, check with your family helper first.")
        steps.append("If it says it is from a bank or company, check by calling the number on the back of "
                     "your card or on their official website, never a number or link in the message.")
    if hits:
        steps.append("Do not click, reply, or call any number in the message.")
        steps.append("If it claims to be a company or office you use, call the number on your card, "
                     "bill or their official website, not the one in the message.")
    if keys & {"gift_cards", "gift_card_codes", "odd_payment", "overpayment", "sensitive_info", "lookalike", "link_asks"}:
        steps.append("Already paid or shared card details? Call your bank now on the number on the "
                     "back of your card.")
    if "remote_access" in keys or "tech_popup" in keys:
        steps.append("If someone already got into the computer: turn off the Wi-Fi, shut it down, and "
                     "call your family helper before turning it back on.")
    if "codes" in keys:
        steps.append("Already read out a code? Change that account's password from another device and "
                     "tell the bank or company.")
    if keys & {"new_number", "family_trouble", "money_ask"}:
        steps.append("Call the family member on the number you already have for them.")
    if has_code and "codes" not in keys:
        steps.append("If it is a login code: type it only into the app or website you are using right now. "
                     "Never read it to anyone who calls or texts. If you did not ask for it, ignore it.")
    if hits:
        steps.append("Report it: US reportfraud.ftc.gov; Canada, the Canadian Anti-Fraud Centre; UK, "
                     "Action Fraud. Then delete it.")
    return steps


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scam Call Detector")
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.text:
        text = a.text
    elif a.file:
        with open(a.file, encoding="utf-8") as fh:
            text = fh.read()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        sys.exit("Give the message with --text, --file or on stdin.")
    res = check(text)
    if a.json:
        print(json.dumps(res, indent=2))
        return 0
    print(f"SCAM CALL DETECTOR: {res['verdict']}  ({res['points']} points)")
    for h in res["flags"]:
        m = f"  [{', '.join(h['matched'])}]" if h["matched"] else ""
        print(f"  RED FLAG: {h['why']}{m}")
    print("WHAT TO DO NOW:")
    for i, s in enumerate(res["next_steps"], 1):
        print(f"  {i}. {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
