#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for scripts/bounty_claim.py.

Two things carry the weight:

  - `is_claim_request` must not fire on someone QUOTING the instructions. A
    false positive silently marks a bounty as taken and turns this feature into
    the very problem it exists to prevent.
  - `active_claim` must treat an expired claim as absent, or a bounty stays
    reserved forever by whoever touched it first.
"""
import datetime
import importlib.util
import os
import unittest
from pathlib import Path

os.environ.setdefault("GITHUB_TOKEN", "dummy")
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "bounty_claim.py"
spec = importlib.util.spec_from_file_location("bounty_claim_under_test", SCRIPT)
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

TODAY = datetime.date.today()


class ClaimDetectionTests(unittest.TestCase):
    def test_slash_claim(self):
        self.assertTrue(bc.is_claim_request("/claim"))
        self.assertTrue(bc.is_claim_request("Sounds good, /claim"))

    def test_natural_phrasings(self):
        for s in ["claiming this", "I'm taking this", "taking this one",
                  "I will take this", "Im taking this"]:
            self.assertTrue(bc.is_claim_request(s), s)

    def test_quoted_instructions_do_not_claim(self):
        """Someone quoting the how-to must not accidentally claim the bounty."""
        body = "> Anyone can take it now by commenting `/claim`.\n\nHow long do claims last?"
        self.assertFalse(bc.is_claim_request(body))

    def test_ordinary_comment_does_not_claim(self):
        for s in ["This looks interesting", "What is the reward here?",
                  "I disclaimed any warranty", "", None]:
            self.assertFalse(bc.is_claim_request(s), repr(s))

    def test_disclaim_is_not_a_claim(self):
        """Word-boundary check: 'disclaim' must not match '/claim'."""
        self.assertFalse(bc.is_claim_request("I disclaim all responsibility"))


class ActiveClaimTests(unittest.TestCase):
    def setUp(self):
        self._gh = bc.gh

    def tearDown(self):
        bc.gh = self._gh

    def _comments(self, *bodies):
        bc.gh = lambda a, d=None: [{"body": b} for b in bodies]

    def _claim(self, who, days):
        d = (TODAY + datetime.timedelta(days=days)).isoformat()
        return f"{bc.MARKER}\n🔒 **Claimed.** holder: @{who} · expires: {d}"

    def test_unexpired_claim_is_active(self):
        self._comments(self._claim("alice", 3))
        got = bc.active_claim(1)
        self.assertIsNotNone(got)
        self.assertEqual(got[0], "alice")

    def test_expired_claim_is_not_active(self):
        """Otherwise a bounty stays reserved forever."""
        self._comments(self._claim("alice", -1))
        self.assertIsNone(bc.active_claim(1))

    def test_expiring_today_still_counts(self):
        self._comments(self._claim("alice", 0))
        self.assertIsNotNone(bc.active_claim(1))

    def test_newest_claim_wins(self):
        self._comments(self._claim("alice", 1), self._claim("bob", 5))
        self.assertEqual(bc.active_claim(1)[0], "bob")

    def test_renewal_supersedes_expired(self):
        self._comments(self._claim("alice", -3), self._claim("alice", 4))
        got = bc.active_claim(1)
        self.assertIsNotNone(got)
        self.assertEqual(got[0], "alice")

    def test_no_marker_means_no_claim(self):
        self._comments("just a normal comment", "another one")
        self.assertIsNone(bc.active_claim(1))

    def test_no_comments_at_all(self):
        bc.gh = lambda a, d=None: []
        self.assertIsNone(bc.active_claim(1))


class LiveUrlGateTests(unittest.TestCase):
    """On `distribution` issues a claim without an allowlisted Live-URL must
    NOT lock the bounty — it gets an explanation instead. Everywhere else the
    gate is inert."""

    def setUp(self):
        self._gh, self._add = bc.gh, bc.add_label
        self.comments, self.labels = [], []

        def fake_gh(args, default=None):
            if args[:2] == ["issue", "view"]:
                return self.issue
            if args[:2] == ["issue", "comment"]:
                self.comments.append(args[args.index("--body") + 1])
                return None
            return []  # active_claim: no prior comments
        bc.gh = fake_gh
        bc.add_label = lambda n, name: self.labels.append(name) or True

    def tearDown(self):
        bc.gh, bc.add_label = self._gh, self._add

    def _issue(self, *labels):
        self.issue = {"title": "[BOUNTY] Share on X", "state": "OPEN",
                      "labels": [{"name": name} for name in labels]}

    def test_distribution_without_live_url_is_explained_not_locked(self):
        self._issue("distribution")
        bc.do_claim(2798, "alice", "/claim")
        self.assertEqual(self.labels, [])
        self.assertEqual(len(self.comments), 1)
        self.assertIn("Live-URL", self.comments[0])
        self.assertNotIn(bc.MARKER, self.comments[0])

    def test_distribution_with_off_list_url_is_explained_not_locked(self):
        self._issue("distribution")
        bc.do_claim(2798, "alice", "/claim\nLive-URL: https://gist.github.com/alice/x")
        self.assertEqual(self.labels, [])
        self.assertIn("gist.github.com", self.comments[0])
        self.assertNotIn(bc.MARKER, self.comments[0])

    def test_distribution_with_live_url_locks(self):
        self._issue("distribution", "standard")
        bc.do_claim(2798, "alice", "/claim\nLive-URL: https://x.com/alice/status/123")
        self.assertEqual(self.labels, [bc.LABEL])
        self.assertIn(bc.MARKER, self.comments[0])

    def test_non_distribution_issue_unchanged(self):
        self._issue("standard")
        bc.do_claim(16250, "alice", "/claim")
        self.assertEqual(self.labels, [bc.LABEL])
        self.assertIn(bc.MARKER, self.comments[0])

    def test_gate_helper_direct(self):
        self.assertTrue(bc.live_url_gate(1, "a", "/claim", {"standard"}))
        self.assertFalse(bc.live_url_gate(1, "a", "/claim", {"distribution"}))
        self.assertTrue(bc.live_url_gate(1, "a", "Live-URL: https://youtu.be/dQw4w9WgXcQ",
                                         {"distribution"}))


if __name__ == "__main__":
    unittest.main()
