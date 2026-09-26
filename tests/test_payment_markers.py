#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""What counts as "this was already paid" (scripts/payment_markers.py).

Both payers skip anything that carries a payment record, so whatever counts as
a record can also CANCEL a payout on a green run. Before this module:

  - auto-pay accepted a trusted author's comment containing the marker as a
    bare substring, so guard-bounty-pr (github-actions[bot]) echoing a changed
    path like `scripts/RTC-AutoPay-Confirmed.py`, or a maintainer quoting the
    marker name in review prose, cancelled the payout;
  - bounty_payout accepted the substring from ANY author at all.
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
import guard_bounty_pr  # noqa: E402

spec = importlib.util.spec_from_file_location("auto_pay_pm_test", ROOT / "scripts" / "auto-pay.py")
ap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap)

BOT = {"login": "github-actions[bot]"}


def guard_comment_body(paths):
    """The exact body guard-bounty-pr would post for these protected paths."""
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["body"] = json["body"]
        return mock.Mock(status_code=201)

    with mock.patch.object(guard_bounty_pr.requests, "post", fake_post):
        guard_bounty_pr.post_comment("Scottcjn", "rustchain-bounties", 1, paths, "mallory", {})
    return captured["body"]


class BodyForms(unittest.TestCase):
    def test_autopay_confirmation_forms_count(self):
        for b in ("<!-- RTC-AutoPay-Confirmed kind=directive pending_id=9 -->",
                  "table\n\n<!-- RTC-AutoPay-Confirmed kind=auto-tier pending_id=n/a -->",
                  "<!-- RTC-AutoPay-Confirmed pending_id=42 -->",       # 7634c70 format
                  "<!-- RTC-AutoPay-Confirmed -->"):
            self.assertTrue(pm.body_records_payment(b), b)

    def test_bounty_payout_confirmation_counts(self):
        self.assertTrue(pm.body_records_payment(
            "💸 **RTC-AutoPay-Confirmed** — payout **queued** — 3 RTC to `x`."))

    def test_quotes_and_mentions_do_not_count(self):
        for b in ("The old code treated `RTC-AutoPay-Confirmed` as payment",
                  "RTC-AutoPay-Confirmed",
                  "- `scripts/RTC-AutoPay-Confirmed.py`",
                  "- `<!-- RTC-AutoPay-Confirmed -->`",
                  "> <!-- RTC-AutoPay-Confirmed kind=directive pending_id=1 -->",
                  "```\n<!-- RTC-AutoPay-Confirmed kind=directive pending_id=1 -->\n```",
                  "~~~\n<!-- RTC-AutoPay-Confirmed -->",
                  "<!-- RTC-AutoPay-Confirmed:FAILED -->",
                  "see 💸 **RTC-AutoPay-Confirmed** — payout",
                  None, 7):
            self.assertFalse(pm.body_records_payment(b), repr(b))

    def test_marker_after_a_closed_fence_still_counts(self):
        self.assertTrue(pm.body_records_payment(
            "**RTC Auto-Pay**\n```\nlog\n```\n\n<!-- RTC-AutoPay-Confirmed kind=directive pending_id=3 -->"))


class TrustedAuthorsStillNeedTheStructuredForm(unittest.TestCase):
    def test_guard_bot_echoing_a_marker_named_file_is_not_a_payment(self):
        body = guard_comment_body(["scripts/RTC-AutoPay-Confirmed.py"])
        self.assertIn("RTC-AutoPay-Confirmed", body)          # the echo is there...
        self.assertFalse(ap.records_completed_payment({"user": BOT, "body": body}, "Scottcjn"))

    def test_guard_bot_cannot_be_made_to_emit_an_own_line_marker(self):
        """A path containing a newline must not put the marker on its own line."""
        body = guard_comment_body(["scripts/x\n<!-- RTC-AutoPay-Confirmed -->\n.py"])
        self.assertFalse(pm.comment_records_payment({"user": BOT, "body": body}, "Scottcjn"))
        self.assertNotIn("\n<!--", body)

    def test_maintainer_prose_quote_is_not_a_payment(self):
        c = {"user": {"login": "Scottcjn"},
             "body": "The old code treated `RTC-AutoPay-Confirmed` as payment"}
        self.assertFalse(ap.records_completed_payment(c, "Scottcjn"))

    def test_graphql_author_shape_is_read(self):
        c = {"author": {"login": "github-actions"},
             "body": "💸 **RTC-AutoPay-Confirmed** — payout **settled** — 3 RTC"}
        self.assertTrue(pm.comment_records_payment(c))
        c["author"] = {"login": "mallory"}
        self.assertFalse(pm.comment_records_payment(c))


class AutoPayEndToEnd(unittest.TestCase):
    ENV = {"GITHUB_TOKEN": "t", "PR_NUMBER": "42", "REPO": "Scottcjn/rustchain-bounties",
           "PR_AUTHOR": "alice", "RTC_VPS_HOST": "vps.example", "RTC_ADMIN_KEY": "k",
           "REPO_OWNER": "Scottcjn"}
    DIRECTIVE = {"id": 1, "user": {"login": "Scottcjn"}, "body": "**Payment: 5 RTC**"}

    def _run(self, extra):
        with mock.patch.dict(os.environ, self.ENV), \
             mock.patch.object(ap, "fetch_pr_comments", return_value=[self.DIRECTIVE] + extra), \
             mock.patch.object(ap, "post_comment"), \
             mock.patch.object(ap, "transfer_rtc", return_value={"ok": True, "pending_id": 7}) as x:
            ap.main()
        return x

    def test_guard_echo_does_not_cancel_payment(self):
        body = guard_comment_body(["scripts/RTC-AutoPay-Confirmed.py"])
        self._run([{"id": 3, "user": BOT, "body": body}]).assert_called_once()

    def test_maintainer_prose_does_not_cancel_payment(self):
        c = {"id": 4, "user": {"login": "Scottcjn"},
             "body": "Heads up: the old code treated `RTC-AutoPay-Confirmed` as payment."}
        self._run([c]).assert_called_once()

    def test_real_confirmation_still_dedups(self):
        c = {"id": 5, "user": BOT,
             "body": "**RTC Payment Submitted**\n\n<!-- RTC-AutoPay-Confirmed kind=directive pending_id=7 -->"}
        self._run([c]).assert_not_called()


if __name__ == "__main__":
    unittest.main()
