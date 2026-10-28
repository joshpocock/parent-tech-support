import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import bigfont  # noqa: E402
import scamcheck  # noqa: E402


class ScamTests(unittest.TestCase):
    def test_gift_card_tech_support_scam(self):
        r = scamcheck.check("VIRUS DETECTED. Call Microsoft support now at 1-888-555-0199. "
                            "Do not close this window. Payment by Google Play card.")
        self.assertEqual(r["verdict"], "ALMOST CERTAINLY A SCAM")
        flags = {h["flag"] for h in r["flags"]}
        self.assertTrue({"gift_cards", "tech_popup"} <= flags)

    def test_grandparent_scam(self):
        r = scamcheck.check("Grandma it's me, I had an accident and I'm in jail. Please don't tell mom, "
                            "I need bail money")
        self.assertIn("family_trouble", {h["flag"] for h in r["flags"]})
        self.assertNotEqual(r["verdict"], "NO RED FLAGS FOUND")

    def test_lookalike_and_short_link(self):
        r = scamcheck.check("USPS: package on hold, pay redelivery fee at usps-redelivery-help.com or bit.ly/x1")
        flags = {h["flag"] for h in r["flags"]}
        self.assertIn("lookalike", flags)
        self.assertIn("short_link", flags)

    def test_real_domain_not_flagged(self):
        r = scamcheck.check("Your order shipped, details at amazon.com/orders")
        self.assertNotIn("lookalike", {h["flag"] for h in r["flags"]})

    def test_normal_message_has_no_flags_but_never_says_safe(self):
        r = scamcheck.check("Dinner at 6 on Sunday? Bring the photos from the trip.")
        self.assertEqual(r["verdict"], "NO RED FLAGS FOUND")
        self.assertIn("does not make it safe", r["next_steps"][0])

    def test_word_boundaries(self):
        # "pin" inside "spinach" and "otp" inside "hotpot" must not fire
        r = scamcheck.check("Making spinach and a hotpot tonight")
        self.assertEqual(r["points"], 0)

    # Realistic-input fixes (2026-10-28 launch check)
    def test_plural_gift_cards_with_photos_of_backs(self):
        r = scamcheck.check("Hi it's Pastor Mike. I'm in a meeting and can't talk. I need you to pick up 4 Apple "
                            "gift cards at $200 each. Send me pictures of the backs.")
        self.assertEqual(r["verdict"], "ALMOST CERTAINLY A SCAM")
        self.assertIn("gift_cards", {h["flag"] for h in r["flags"]})

    def test_real_login_code_text_not_flagged_but_warned(self):
        r = scamcheck.check("Your Google verification code is 482913. Don't share it with anyone.")
        self.assertEqual(r["verdict"], "NO RED FLAGS FOUND")
        self.assertTrue(any("login code" in s for s in r["next_steps"]))

    def test_someone_asking_for_the_code_is_flagged(self):
        r = scamcheck.check("This is Amazon. Read me the 6-digit code we just texted you to cancel the order.")
        self.assertIn("codes", {h["flag"] for h in r["flags"]})

    def test_normal_family_greeting_not_flagged(self):
        for t in ("Hi Mum, landed safe! Phone's nearly dead, will call you tonight. Love you x",
                  "Mom, the wifi password is on the sticker on the back of the router"):
            self.assertEqual(scamcheck.check(t)["verdict"], "NO RED FLAGS FOUND", t)

    def test_new_number_asking_for_money(self):
        r = scamcheck.check("Hi Mum, this is my new number, I lost my phone. I need help paying a bill today")
        self.assertEqual(r["verdict"], "LOOKS LIKE A SCAM")

    def test_shortener_match_is_exact_host(self):
        # "support.com" contains "t.co"; it must read as a lookalike, not a short link
        r = scamcheck.check("Apple ID disabled. Log in to unlock: appleid-unlock-support.com")
        flags = {h["flag"] for h in r["flags"]}
        self.assertNotIn("short_link", flags)
        self.assertIn("lookalike", flags)
        self.assertEqual(r["verdict"], "ALMOST CERTAINLY A SCAM")

    def test_popup_without_virus_wording(self):
        r = scamcheck.check("Microsoft Windows Security Center. Your PC is blocked due to suspicious activity. "
                            "Please contact Windows Support toll free +1 (844) 555-0182. Do not restart your computer.")
        self.assertEqual(r["verdict"], "ALMOST CERTAINLY A SCAM")

    def test_grandson_call_with_courier_cash(self):
        r = scamcheck.check("Caller said he was my grandson, said he hit someone with his car. The lawyer said to "
                            "withdraw $8,000 in cash and a courier would come to the house to collect it.")
        self.assertEqual(r["verdict"], "ALMOST CERTAINLY A SCAM")

    def test_toll_text_with_pay_link(self):
        r = scamcheck.check("NC Quick Pass: You have an unpaid toll balance of $4.35. To avoid a late fee of "
                            "$50.00 pay within 24 hours: https://ncquickpass-tolls.com/pay")
        self.assertEqual(r["verdict"], "ALMOST CERTAINLY A SCAM")
        self.assertIn("link_asks", {h["flag"] for h in r["flags"]})

    def test_pharmacy_and_appointment_reminders_not_flagged(self):
        for t in ("CVS Pharmacy: Your prescription for MARGARET is ready for pickup at 123 Main St. Reply STOP to opt out.",
                  "Reminder: you have an appointment with Dr. Patel on Tue Oct 29 at 10:30 AM. Reply C to confirm."):
            self.assertEqual(scamcheck.check(t)["verdict"], "NO RED FLAGS FOUND", t)


class BigFontTests(unittest.TestCase):
    def test_render(self):
        src = ["# Make the text bigger", "For: Mum's iPhone", "1. Open Settings.", "2. Tap Display.",
               "! Do not tap Reset.", "? The screen goes black and stays black."]
        doc = bigfont.parse(src)
        page = bigfont.render(doc, helper="Sam", phone="555 0100")
        self.assertIn("<title>Make the text bigger</title>", page)
        self.assertEqual(page.count("<li><span>"), 2)
        self.assertIn("Call Sam only if", page)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.txt")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("\n".join(src))
            bigfont.main([p, "-o", os.path.join(d, "g.html")])
            self.assertTrue(os.path.exists(os.path.join(d, "g.html")))

    def test_escapes_html(self):
        page = bigfont.render(bigfont.parse(["1. Type <script> exactly"]))
        self.assertIn("&lt;script&gt;", page)


    def test_call_me_items_are_not_step_cards(self):
        # 2026-10-28: the bare li::before rule drew black numbered ovals on the Call me only if list
        self.assertNotRegex(bigfont.CSS, r"(?m)^li(\{|::before)")
        page = bigfont.render(bigfont.parse(["1. Open Settings.", "? The screen stays black."]), helper="Sam")
        self.assertIn("<li>The screen stays black.</li>", page)


if __name__ == "__main__":
    unittest.main()
