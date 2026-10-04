#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression: which text in an owner comment counts as a payment directive.

scripts/auto-pay.py used `PAYMENT_RE.search(body)` on the raw comment body, so:

  1. a directive inside a `> ` quote, a fenced code block or inline code -- an
     owner quoting someone else, or showing the syntax as an example -- paid;
  2. within one comment the FIRST directive won, so "Payment: 50 RTC ...
     correction: Payment: 30 RTC" paid 50.

Reported by @asbelcas (CropCircuit).
"""
import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import payment_markers as pm  # noqa: E402

spec = importlib.util.spec_from_file_location("auto_pay_directive_parsing",
                                              ROOT / "scripts" / "auto-pay.py")
ap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap)

ENV = {"GITHUB_TOKEN": "t", "PR_NUMBER": "42", "REPO": "Scottcjn/rustchain-bounties",
       "PR_AUTHOR": "alice", "RTC_VPS_HOST": "vps.example", "RTC_ADMIN_KEY": "k",
       "REPO_OWNER": "Scottcjn"}


def owner(body, cid=1):
    return {"id": cid, "user": {"login": "Scottcjn"}, "body": body}


class FindPaymentDirectiveTests(unittest.TestCase):
    def test_plain_directive(self):
        self.assertEqual(ap.find_payment_directive("Payment: 75 RTC"), 75.0)

    def test_bold_directive(self):
        self.assertEqual(ap.find_payment_directive("Thanks!\n\n**Payment: 75.5 RTC**"), 75.5)

    def test_no_directive(self):
        self.assertIsNone(ap.find_payment_directive("LGTM, merging."))
        self.assertIsNone(ap.find_payment_directive(""))
        self.assertIsNone(ap.find_payment_directive(None))

    def test_quoted_directive_ignored(self):
        body = "> I think this deserves Payment: 500 RTC\n\nNot that much, sorry."
        self.assertIsNone(ap.find_payment_directive(body))

    def test_nested_and_indented_quote_ignored(self):
        self.assertIsNone(ap.find_payment_directive(">> Payment: 500 RTC"))
        self.assertIsNone(ap.find_payment_directive("   > **Payment: 500 RTC**"))

    def test_backtick_fenced_directive_ignored(self):
        body = "Use this format:\n\n```\n**Payment: 75 RTC**\n```\n"
        self.assertIsNone(ap.find_payment_directive(body))

    def test_tilde_fenced_directive_ignored(self):
        body = "Example:\n~~~markdown\nPayment: 75 RTC\n~~~"
        self.assertIsNone(ap.find_payment_directive(body))

    def test_unterminated_fence_ignored(self):
        self.assertIsNone(ap.find_payment_directive("Example:\n```\nPayment: 75 RTC"))

    def test_inline_code_directive_ignored(self):
        self.assertIsNone(ap.find_payment_directive("Write `Payment: 75 RTC` to pay."))
        self.assertIsNone(ap.find_payment_directive("Write ``Payment: 75 RTC`` to pay."))

    def test_in_comment_correction_pays_last(self):
        body = "Payment: 50 RTC\n\nOops, correction: Payment: 30 RTC"
        self.assertEqual(ap.find_payment_directive(body), 30.0)

    def test_quoted_correction_does_not_override_own_directive(self):
        body = "**Payment: 20 RTC**\n\n> Payment: 900 RTC"
        self.assertEqual(ap.find_payment_directive(body), 20.0)

    def test_own_directive_survives_alongside_example(self):
        body = "Format is `Payment: N RTC`. For this PR:\n\n**Payment: 12 RTC**"
        self.assertEqual(ap.find_payment_directive(body), 12.0)

    def test_crlf_body(self):
        body = "```\r\nPayment: 99 RTC\r\n```\r\nPayment: 7 RTC\r\n"
        self.assertEqual(ap.find_payment_directive(body), 7.0)


class StripQuotedAndCodeTests(unittest.TestCase):
    def test_keeps_own_prose(self):
        out = pm.strip_quoted_and_code("Hello\n> quoted\n```\ncode\n```\nbye `x` end")
        self.assertIn("Hello", out)
        self.assertIn("bye", out)
        self.assertIn("end", out)
        for gone in ("quoted", "code", "`x`"):
            self.assertNotIn(gone, out)

    def test_non_string(self):
        self.assertEqual(pm.strip_quoted_and_code(None), "")


class MainDirectiveTests(unittest.TestCase):
    def _run(self, comments, files=None):
        with mock.patch.dict(os.environ, ENV), \
             mock.patch.object(ap, "fetch_pr_comments", return_value=comments), \
             mock.patch.object(ap, "fetch_pr_files", return_value=files or []), \
             mock.patch.object(ap, "post_comment") as post, \
             mock.patch.object(ap, "transfer_rtc",
                               return_value={"ok": True, "pending_id": 7}) as xfer:
            ap.main()
        return xfer, post

    def _sensitive(self):
        # Touching scripts/ makes the auto-tier fall through to "skipped", so a
        # transfer can only come from a (wrongly) recognised directive.
        return [{"filename": "scripts/x.py", "additions": 1, "deletions": 0}]

    def test_quoted_directive_does_not_pay(self):
        xfer, _ = self._run([owner("> Payment: 500 RTC\n\nNo.")], self._sensitive())
        xfer.assert_not_called()

    def test_fenced_directive_does_not_pay(self):
        xfer, _ = self._run([owner("```\nPayment: 500 RTC\n```")], self._sensitive())
        xfer.assert_not_called()

    def test_inline_code_directive_does_not_pay(self):
        xfer, _ = self._run([owner("Use `Payment: 500 RTC`.")], self._sensitive())
        xfer.assert_not_called()

    def test_in_comment_correction_pays_last_amount(self):
        xfer, _ = self._run([owner("Payment: 50 RTC\ncorrection: Payment: 30 RTC")])
        xfer.assert_called_once()
        self.assertEqual(xfer.call_args.args[2], "alice")
        self.assertEqual(xfer.call_args.args[3], 30.0)

    def test_plain_directive_pays(self):
        xfer, _ = self._run([owner("Payment: 75 RTC")])
        self.assertEqual(xfer.call_args.args[3], 75.0)

    def test_bold_directive_pays(self):
        xfer, _ = self._run([owner("**Payment: 75 RTC**")])
        self.assertEqual(xfer.call_args.args[3], 75.0)

    def test_last_owner_comment_still_wins(self):
        xfer, _ = self._run([owner("Payment: 10 RTC", 1), owner("Payment: 15 RTC", 2)])
        self.assertEqual(xfer.call_args.args[3], 15.0)

    def test_quoted_later_comment_does_not_override_earlier_directive(self):
        xfer, _ = self._run([owner("Payment: 10 RTC", 1),
                             owner("> Payment: 900 RTC\n\nquoting the ask", 2)])
        self.assertEqual(xfer.call_args.args[3], 10.0)

    def test_non_owner_directive_ignored(self):
        comments = [{"id": 1, "user": {"login": "alice"}, "body": "**Payment: 500 RTC**"}]
        xfer, _ = self._run(comments, self._sensitive())
        xfer.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
