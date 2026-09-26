#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""End-to-end guards in scripts/bounty_payout.py's payout loop.

The loop runs at import time, so each case executes the script against a fake
`gh` and a fake HTTPS node and records which claims actually got a transfer.

1. "Already paid" skip: any comment by ANY author containing
   `RTC-AutoPay-Confirmed` used to cancel an eligible claim's payout. Now only
   a trusted, structured confirmation does (scripts/payment_markers.py).
2. Docstring provenance at payout time: the docstring gate only began
   checking that the cited PR is the claimant's own, in an allowed repo, on
   2026-09-26, and it never re-adjudicates labelled claims. Claims verified
   before that are re-checked here, when money would move.
"""
import importlib.util
import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "bounty_payout.py"
WALLET = "RTC" + "a" * 40
_orig_run = subprocess.run


def run_payout(issue, pr=None):
    """Execute bounty_payout.py for one open claim. Returns (transfers, gh_calls)."""
    transfers, calls = [], []

    def fake_run(args, *a, **kw):
        calls.append(args)
        out = ""
        if args[:3] == ["gh", "issue", "list"]:
            out = json.dumps([{"number": issue["number"], "title": issue["title"],
                               "labels": [{"name": n} for n in issue["labels"]]}]
                             if "--label" in args else [])
        elif args[:3] == ["gh", "issue", "view"]:
            out = json.dumps({"body": issue["body"], "comments": issue["comments"],
                              "author": {"login": issue["author"]}})
        elif args[:3] == ["gh", "pr", "view"]:
            if pr is None:
                return mock.Mock(stdout="", stderr="not found", returncode=1)
            out = json.dumps(pr)
        return mock.Mock(stdout=out, stderr="", returncode=0)

    class FakeConn:
        def __init__(self, host, port, timeout=None, context=None):
            self.sock = mock.Mock()

        def connect(self):
            pass

        def request(self, method, path, body=None, headers=None):
            transfers.append(json.loads(body))

        def getresponse(self):
            return mock.Mock(status=200, read=lambda: b'{"ok": true, "phase": "pending"}')

        def close(self):
            pass

    env = {"GITHUB_TOKEN": "t", "RTC_ADMIN_KEY": "k", "RTC_VPS_HOST": "node.test",
           "GH_REPO": "Scottcjn/rustchain-bounties"}
    with mock.patch.dict(os.environ, env), \
         mock.patch("subprocess.run", fake_run), \
         mock.patch("http.client.HTTPSConnection", FakeConn), \
         mock.patch("time.sleep"):
        os.environ.pop("RUSTCHAIN_TLS_PIN_SHA256", None)
        os.environ.pop("RUSTCHAIN_PAYOUT_INSECURE", None)
        spec = importlib.util.spec_from_file_location("bounty_payout_loop_test", SCRIPT)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    return transfers, calls


def review_claim(comments):
    return {"number": 501, "title": "PR review claim for #73", "labels": ["bounty-eligible"],
            "body": f"Wallet: {WALLET}", "author": "alice", "comments": comments}


def docstring_claim(pr_url="https://github.com/Scottcjn/bottube/pull/77"):
    return {"number": 502, "title": "Docstring batch 50", "author": "alice",
            "labels": ["bounty-eligible", "docstring-verified"],
            "body": f"PR: {pr_url}\nWallet: {WALLET}",
            "comments": [{"author": {"login": "github-actions"},
                          "body": "✅ verified\n<!-- rtc-payout-amount: 0.5 -->"}]}


class AlreadyPaidSkip(unittest.TestCase):
    def test_stranger_marker_does_not_cancel_payout(self):
        t, _ = run_payout(review_claim([{"author": {"login": "mallory"},
                                         "body": "RTC-AutoPay-Confirmed"}]))
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]["to_miner"], WALLET)

    def test_stranger_copying_the_full_confirmation_does_not_cancel(self):
        t, _ = run_payout(review_claim([{"author": {"login": "mallory"},
                                         "body": "💸 **RTC-AutoPay-Confirmed** — payout **settled**"}]))
        self.assertEqual(len(t), 1)

    def test_trusted_prose_mention_does_not_cancel(self):
        t, _ = run_payout(review_claim([{"author": {"login": "Scottcjn"},
                                         "body": "note: `RTC-AutoPay-Confirmed` is the dedup marker"}]))
        self.assertEqual(len(t), 1)

    def test_own_confirmation_still_dedups(self):
        t, _ = run_payout(review_claim([{"author": {"login": "github-actions"},
                                         "body": "💸 **RTC-AutoPay-Confirmed** — payout **queued** — 3 RTC"}]))
        self.assertEqual(t, [])

    def test_new_confirmation_carries_structured_marker(self):
        _, calls = run_payout(review_claim([]))
        bodies = [c[c.index("--body") + 1] for c in calls if c[:3] == ["gh", "issue", "comment"]]
        self.assertEqual(len(bodies), 1)
        self.assertIn("\n<!-- RTC-AutoPay-Confirmed kind=claim claim=501 -->", bodies[0])
        from payment_markers import comment_records_payment
        self.assertTrue(comment_records_payment({"author": {"login": "github-actions"},
                                                 "body": bodies[0]}))


class DocstringProvenanceAtPayout(unittest.TestCase):
    def test_claimants_own_merged_pr_is_paid(self):
        t, _ = run_payout(docstring_claim(), {"author": {"login": "Alice"}, "state": "MERGED"})
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]["amount_rtc"], 0.5)

    def test_someone_elses_pr_is_not_paid(self):
        t, _ = run_payout(docstring_claim(), {"author": {"login": "bob"}, "state": "MERGED"})
        self.assertEqual(t, [])

    def test_foreign_repo_is_not_paid(self):
        t, _ = run_payout(docstring_claim("https://github.com/python/cpython/pull/1"),
                          {"author": {"login": "alice"}, "state": "MERGED"})
        self.assertEqual(t, [])

    def test_unreadable_pr_is_not_paid(self):
        t, _ = run_payout(docstring_claim(), None)
        self.assertEqual(t, [])

    def test_unmerged_pr_is_not_paid(self):
        t, _ = run_payout(docstring_claim(), {"author": {"login": "alice"}, "state": "OPEN"})
        self.assertEqual(t, [])


if __name__ == "__main__":
    unittest.main()
