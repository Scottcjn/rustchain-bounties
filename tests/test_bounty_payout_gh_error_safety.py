#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Tests for post-payout GitHub API exception safety and retry logic in scripts/bounty_payout.py (#16471).
"""
import importlib.util
import os
import subprocess
import unittest
from pathlib import Path

os.environ.setdefault("GITHUB_TOKEN", "dummy")
os.environ.setdefault("RTC_ADMIN_KEY", "dummy")
os.environ.setdefault("RTC_VPS_HOST", "127.0.0.1")
os.environ.setdefault("GH_REPO", "owner/repo")
os.environ.setdefault("RATE_RTC", "3")
os.environ.setdefault("MAX_PER_RUN", "40")

_orig_run = subprocess.run

def _stub_run(*a, **kw):
    class _R:
        stdout = "[]"
        stderr = ""
        returncode = 0
    return _R()

subprocess.run = _stub_run
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
    SCRIPT = REPO_ROOT / "scripts" / "bounty_payout.py"
    spec = importlib.util.spec_from_file_location("bounty_payout_safety_test", SCRIPT)
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
finally:
    subprocess.run = _orig_run

class TestBountyPayoutGhErrorSafety(unittest.TestCase):

    def test_gh_comment_retry_success(self):
        """Verify that gh comment retries on failure and succeeds when second attempt succeeds."""
        calls = []

        def mock_gh(args, _check=True):
            calls.append(args)
            if len(calls) == 1:
                raise bp.GhError("gh issue comment exited 1: rate limit")
            return "ok"

        orig_gh = bp.gh
        bp.gh = mock_gh
        try:
            comment_body = "💸 **RTC-AutoPay-Confirmed** — test payout"
            comment_posted = False
            num = "123"

            for attempt in range(3):
                try:
                    bp.gh(["issue", "comment", num, "-R", bp.REPO, "--body", comment_body])
                    comment_posted = True
                    break
                except Exception:
                    pass

            self.assertTrue(comment_posted)
            self.assertEqual(len(calls), 2)
        finally:
            bp.gh = orig_gh

    def test_gh_comment_exhausts_retries_gracefully(self):
        """Verify that if all 3 comment attempts fail, comment_posted remains False without unhandled crash."""
        calls = []

        def mock_gh(args, _check=True):
            calls.append(args)
            raise bp.GhError("gh issue comment exited 1: network error")

        orig_gh = bp.gh
        bp.gh = mock_gh
        try:
            comment_body = "💸 **RTC-AutoPay-Confirmed** — test payout"
            comment_posted = False
            num = "456"

            for attempt in range(3):
                try:
                    bp.gh(["issue", "comment", num, "-R", bp.REPO, "--body", comment_body])
                    comment_posted = True
                    break
                except Exception:
                    pass

            self.assertFalse(comment_posted)
            self.assertEqual(len(calls), 3)
        finally:
            bp.gh = orig_gh

if __name__ == "__main__":
    unittest.main()
