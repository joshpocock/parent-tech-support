# Scam Call Detector: the patterns

`scripts/scamcheck.py` scores these. Use this list by hand when code execution is off.

| Red flag | Points | The plain-words reason to give |
|---|---|---|
| Gift cards as payment | 4 | No real company, bank or government office takes gift cards. |
| Wants photos or numbers from the back of a card | 3 | Once someone has those, the money is gone. |
| Crypto, wire, "safe account", cash handed to a courier, "withdraw" | 4 | That money cannot be got back. |
| Wants remote access (AnyDesk, TeamViewer, Quick Assist, "share your screen") | 4 | Only let in someone you called yourself. |
| Asks you to read out or send a code that was texted to you | 4 | Codes are for you to type, never to read out. |
| "We refunded you too much, send the difference" | 4 | The refund is fake, the money you send is real. |
| Family or a friend on a "new number", "lost my phone" | 3 | Call them on the number you already have. |
| Family emergency (accident, jail, bail, lawyer, "don't tell Mom") | 3 | Hang up and call them on their usual number. |
| Asks for money ("help paying a bill", "need $500") | 2 | Check with the person on a number you already have. |
| A prize you never entered | 3 | Real prizes never charge a fee. |
| Asks for your password, PIN, card, CVV or ID numbers | 3 | Your bank will never ask for your password or PIN. |
| "Don't tell anyone", "don't hang up" | 3 | Real officials let you hang up and call back. |
| Virus or "PC blocked" pop-up with a phone number | 3 | Microsoft and Apple never put phone numbers in warnings. |
| A link that pretends to be a brand (amaz0n-help.com, usps.com-trackhelp.top) | 3 | It is not that company's website. |
| "Account locked", "unusual sign-in", "verify your identity" | 2 | Open the real app or call the number on your card instead. |
| Rush ("within 24 hours", "late fee", "suspended", "arrest warrant") | 2 | Rushing stops you asking someone. |
| Claims to be the IRS, Social Security, Medicare, CRA, HMRC, police, Microsoft, Apple, Amazon, PayPal, the bank's fraud team | 2 | Look up the real number yourself and call that. |
| Delivery or toll fee by text | 2 | Check the real app or website instead. |
| A link that asks you to pay, log in, verify or confirm | 2 | Go to the real app or type the website yourself. |
| Shortened link (bit.ly, tinyurl) | 2 | It hides where it goes. |

A real login code text ("Your code is 482913, don't share it") is not a red flag on its own. The
red flag is anyone asking you to read it out. A normal "Hi Mum" text is not a red flag either; a
"Hi Mum, new number, can you help with a bill" text is.

Verdicts: 6 or more points "almost certainly a scam", 3 to 5 "looks like a scam", 1 to 2 "be
careful", 0 "no red flags found". Zero never means safe.

## The one rule worth taping to the fridge

Hang up, then call back on a number you already have: the back of your card, a bill, or the
official website you typed yourself.

## Reporting

US: reportfraud.ftc.gov. Canada: the Canadian Anti-Fraud Centre. UK: Action Fraud. Elsewhere:
the national police or consumer protection site. Then delete the message.

## Sources for the patterns

These are the common patterns named in public consumer warnings from the US Federal Trade
Commission (gift card, impersonation, tech support, grandparent and "refund overpayment" scams)
and similar agencies. Check the current warning pages when a new pattern shows up; scams change
faster than any list.
