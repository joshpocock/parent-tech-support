# Parent Tech Support

One Claude skill that does tech support for your parents so you don't have to. Free, MIT, no
signup, no API key, nothing to connect.

**It never asks for passwords, PINs or codes, never connects to anyone's device, and never calls a
message "safe". It finds scam red flags and tells you what to do next.**

Your mum asks how to make the text bigger for the tenth time. Claude explains it one step at a
time with infinite patience, then prints a large-print guide she can keep by the phone. Your dad
gets a "virus detected, call Microsoft" pop-up. Claude checks it for scam red flags before anyone
calls anything.

## Install

**Claude Code, one paste.** Paste this into Claude Code:

```
Install the Parent Tech Support skill: clone https://github.com/joshpocock/parent-tech-support into ~/.claude/skills/parent-tech-support, then confirm /parent-tech-support works.
```

Or in a terminal:

```
git clone https://github.com/joshpocock/parent-tech-support ~/.claude/skills/parent-tech-support
```

Start a new Claude Code session and type `/parent-tech-support`, then paste the text, describe the
pop-up, or say what your parent is stuck on.

**Claude.ai (website or app), best for parents themselves.** Turn on Settings, Capabilities,
**Code execution and file creation**. On this GitHub page click Code, Download ZIP. In Claude go to
Customize, Skills, +, Upload a skill, and pick the zip. New chat: "use the parent-tech-support skill".

**Any chat, no install.** Paste `SKILL.md` and `references/scam-patterns.md` into a chat.

## What it does

| Stage | What happens |
|---|---|
| Patience Engine | Talking to your parent directly: one step per message, plain words, it waits for "done" |
| Scam Call Detector | Checks a text, email, pop-up or call for 20 red flags (gift cards, code requests, remote access, fake authorities, lookalike links, pay-here links) and gives the next steps |
| Have You Tried Turning It Off Module | The restart routine for each device, done properly, before anything deeper |
| Big Font Mode | Writes a printable large-print guide: numbered cards, one action each, a tick box per step |
| Call Me Only If | Every guide ends with the two or three situations that really need you |
| New device setup | A checklist for a new phone, tablet or computer: readable, safe, findable |

## One text, start to finish

A made-up example, real tool output. The text: "NC Quick Pass: You have an unpaid toll balance of
$4.35. To avoid a late fee of $50.00 pay within 24 hours: https://ncquickpass-tolls.com/pay"

```
SCAM CALL DETECTOR: ALMOST CERTAINLY A SCAM  (6 points)
  RED FLAG: Rushes you. Scammers rush so you do not stop and ask someone.  [within 24 hours, late fee]
  RED FLAG: A delivery or toll fee by text. A favourite scam right now; check the real app or website instead.  [unpaid toll, toll balance]
  RED FLAG: Has a link that asks you to pay, log in or confirm something. Go to the real app or type the website yourself instead.  [pay]
WHAT TO DO NOW:
  1. Do not click, reply, or call any number in the message.
  2. If it claims to be a company or office you use, call the number on your card, bill or their official website, not the one in the message.
  3. Already paid or shared card details? Call your bank now on the number on the back of your card.
  4. Report it: US reportfraud.ftc.gov; Canada, the Canadian Anti-Fraud Centre; UK, Action Fraud. Then delete it.
```

A normal message ("are we still on for Thursday at 2?") gets "no red flags found, but that does
not make it safe", never a green tick. A real login code text ("your code is 482913, don't share
it") is not flagged; someone asking you to read the code out is.

## The tools

Plain Python 3, no installs.

```
python scripts/scamcheck.py --text "the message"          # or --file, or pipe it in
python scripts/bigfont.py steps.txt -o guide.html --helper "Sam" --helper-phone "555 0100"
python -m unittest discover -s tests                       # 19 tests
```

`bigfont.py` reads a simple text format: `# Title`, `For:`, `## Section`, `1. step`, `> tip`,
`! warning`, `? call me only if`. Open the HTML in any browser and print it.

## Fine print

- Scams change faster than any list. The detector catches common patterns; it cannot clear a
  message. When money, a code or access is involved, check with someone you trust first.
- Phone and computer menus change between versions. If a screen looks different, stop and check
  the maker's help page.
- Money already sent? Call the bank on the number on the back of the card, right away.

## More free skills

- [Don't Text Them](https://github.com/joshpocock/dont-text-them) (stops the 2am text)
- [Dinner Arena](https://github.com/joshpocock/dinner-arena) (ten Claudes pick where you eat)

Made by Josh Pocock. More at [strideaiacademy.com](https://strideaiacademy.com).

MIT licence.
