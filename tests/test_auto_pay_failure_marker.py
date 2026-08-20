#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""A failed payout must not poison the PR, and a POST is not a confirmation.

Two defects, one file:

1. The failure comment embedded `<!-- RTC-AutoPay-Confirmed:FAILED -->`, which
   CONTAINS `ALREADY_PAID_MARKER` as a substring. After any failed payout the
   dedup check matched on every later run, printed "Payment already processed.
   Skipping." and exited 0 green. The PR could never be auto-paid again, and
   the log asserted that it already had been.

2. The human-directive path posted "Transfer confirmed on RustChain" off a POST
   that only returns a `pending_id`. RustChain transfers are two-phase with a
   ~24h void window; the balance moves only when the confirmer runs. The
   auto-tier path already worded this correctly.

The `AUTO_TIER_MARKER` substring overlap is DELIBERATE (an auto-tier award is a
real payment and should dedup as one) and is pinned here so it is not "fixed"
by mistake.
"""
import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch


def load_auto_pay():
    script = Path(__file__).resolve().parents[1] / "scripts" / "auto-pay.py"
    spec = importlib.util.spec_from_file_location("auto_pay_markers", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


auto_pay = load_auto_pay()

OWNER = "Scottcjn"
ENV = {
    "GITHUB_TOKEN": "t",
    "REPO": f"{OWNER}/rustchain-bounties",
    "PR_NUMBER": "1234",
    "PR_AUTHOR": "alice",
    "RTC_VPS_HOST": "203.0.113.1",
    "RTC_ADMIN_KEY": "k",
    "REPO_OWNER": OWNER,
}

DIRECTIVE_COMMENT = [{
    "id": 1,
    "user": {"login": OWNER},
    "body": "Nice work. **Payment: 75 RTC**",
}]


class FailureMarkerDoesNotCollide(unittest.TestCase):
    def test_failure_marker_is_not_a_substring_of_the_paid_marker(self):
        self.assertNotIn(auto_pay.ALREADY_PAID_MARKER, auto_pay.FAILED_PAYMENT_MARKER)

    def test_auto_tier_overlap_is_preserved_on_purpose(self):
        # Deliberate and documented: an auto-tier award IS a payment.
        self.assertIn(auto_pay.ALREADY_PAID_MARKER, auto_pay.AUTO_TIER_MARKER)

    def test_success_comment_dedupes(self):
        body = f"<!-- {auto_pay.ALREADY_PAID_MARKER} kind=directive pending_id=p1 -->"
        self.assertTrue(auto_pay.is_already_paid_comment(body))

    def test_new_failure_comment_does_not_dedupe(self):
        body = f"**RTC Auto-Pay Failed**\n<!-- {auto_pay.FAILED_PAYMENT_MARKER} -->"
        self.assertFalse(auto_pay.is_already_paid_comment(body))

    def test_legacy_failure_comment_no_longer_poisons_the_pr(self):
        """PRs already carrying the old marker must become payable again."""
        body = f"**RTC Auto-Pay Failed**\n<!-- {auto_pay.LEGACY_FAILED_MARKER} -->"
        self.assertFalse(auto_pay.is_already_paid_comment(body))

    def test_legacy_failure_plus_real_payment_still_dedupes(self):
        body = (f"<!-- {auto_pay.LEGACY_FAILED_MARKER} -->\n"
                f"<!-- {auto_pay.ALREADY_PAID_MARKER} kind=directive pending_id=p9 -->")
        self.assertTrue(auto_pay.is_already_paid_comment(body))


class EndToEndPaths(unittest.TestCase):
    def _run(self, transfer_result):
        posted = []
        with patch.dict(os.environ, ENV, clear=False), \
             patch.object(auto_pay, "fetch_pr_comments", return_value=list(DIRECTIVE_COMMENT)), \
             patch.object(auto_pay, "transfer_rtc", return_value=transfer_result), \
             patch.object(auto_pay, "post_comment",
                          side_effect=lambda repo, pr, body: posted.append(body)):
            try:
                auto_pay.main()
                exit_code = 0
            except SystemExit as e:
                exit_code = e.code
        return posted, exit_code

    def test_failed_transfer_leaves_the_pr_payable(self):
        posted, exit_code = self._run({"ok": False, "error": "insufficient_balance"})

        self.assertEqual(exit_code, 1)
        self.assertEqual(len(posted), 1)
        self.assertIn("Failed", posted[0])
        # THE regression: re-running must not see this as an already-paid PR.
        self.assertFalse(auto_pay.is_already_paid_comment(posted[0]))

    def test_directive_path_does_not_claim_confirmation(self):
        posted, exit_code = self._run({"ok": True, "pending_id": "p42"})

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(posted), 1)
        body = posted[0]
        self.assertNotIn("Transfer confirmed on RustChain", body)
        self.assertIn("pending", body.lower())
        self.assertIn("void", body.lower())
        # A real payment still dedupes.
        self.assertTrue(auto_pay.is_already_paid_comment(body))


if __name__ == "__main__":
    unittest.main(verbosity=2)
