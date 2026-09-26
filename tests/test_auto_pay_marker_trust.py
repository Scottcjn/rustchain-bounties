#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression: auto-pay's "already paid" dedup must only trust markers from
identities that can have made the payment.

Before the fix, any comment containing `RTC-AutoPay-Confirmed` -- from any
GitHub account -- made scripts/auto-pay.py print "Payment already processed.
Skipping." and exit 0, so one planted (or merely quoted) comment silently
cancelled a contributor's payout on a green run.
"""
import importlib.util
import os
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "auto-pay.py"
spec = importlib.util.spec_from_file_location("auto_pay_marker_trust", SCRIPT)
ap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap)

ENV = {"GITHUB_TOKEN": "t", "PR_NUMBER": "42", "REPO": "Scottcjn/rustchain-bounties",
       "PR_AUTHOR": "alice", "RTC_VPS_HOST": "vps.example", "RTC_ADMIN_KEY": "k",
       "REPO_OWNER": "Scottcjn"}
DIRECTIVE = {"id": 1, "user": {"login": "Scottcjn"}, "body": "**Payment: 5 RTC**"}


def marker(login, body="<!-- RTC-AutoPay-Confirmed kind=directive pending_id=9 -->"):
    return {"id": 2, "user": {"login": login}, "body": body}


class MarkerTrustTests(unittest.TestCase):
    def _run(self, comments):
        with mock.patch.dict(os.environ, ENV), \
             mock.patch.object(ap, "fetch_pr_comments", return_value=comments), \
             mock.patch.object(ap, "post_comment") as post, \
             mock.patch.object(ap, "transfer_rtc",
                               return_value={"ok": True, "pending_id": 7}) as xfer:
            ap.main()
        return xfer, post

    def test_untrusted_marker_does_not_cancel_payment(self):
        xfer, _ = self._run([DIRECTIVE, marker("mallory")])
        xfer.assert_called_once()
        self.assertEqual(xfer.call_args.args[2], "alice")
        self.assertEqual(xfer.call_args.args[3], 5.0)

    def test_any_other_commenter_marker_is_ignored(self):
        xfer, _ = self._run([DIRECTIVE, marker("alice")])
        xfer.assert_called_once()

    def test_bot_marker_still_dedups(self):
        xfer, post = self._run([DIRECTIVE, marker("github-actions[bot]")])
        xfer.assert_not_called()
        post.assert_not_called()

    def test_repo_owner_marker_still_dedups_case_insensitively(self):
        xfer, _ = self._run([DIRECTIVE, marker("scottcjn")])
        xfer.assert_not_called()

    def test_trusted_legacy_failure_marker_is_still_not_a_payment(self):
        legacy = marker("github-actions[bot]", "<!-- RTC-AutoPay-Confirmed:FAILED -->")
        xfer, _ = self._run([DIRECTIVE, legacy])
        xfer.assert_called_once()

    def test_non_dict_and_missing_user_are_untrusted(self):
        self.assertFalse(ap.records_completed_payment(None, "Scottcjn"))
        self.assertFalse(ap.records_completed_payment(
            {"body": "RTC-AutoPay-Confirmed"}, "Scottcjn"))


if __name__ == "__main__":
    unittest.main()
