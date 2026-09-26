#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression tests: the docstring gate must only pay for the claimant's own
PRs in Elyan Labs repositories.

Before this fix `main()` fetched the cited PR's `author` and never compared it
with the claim's author, and `PR_RE` accepted a PR URL in any repository on
GitHub. A claim citing somebody else's merged docstring PR -- in this project
or in CPython -- was labelled `bounty-eligible` + `docstring-verified` with a
trusted payout marker, and the payout runner then paid the claimant.

These drive `main()` end to end with `gh` stubbed out.
"""
import importlib.util
import os
import unittest
from pathlib import Path

os.environ.setdefault("GITHUB_TOKEN", "dummy")
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "docstring_gate.py"
spec = importlib.util.spec_from_file_location("docstring_gate_provenance", SCRIPT)
dg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dg)

DIFF = ("diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n"
        + "\n".join(f'+    """Doc {i}."""' for i in range(10)))


class _Result:
    returncode = 0
    stdout = ""
    stderr = ""


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self._saved = {k: getattr(dg, k) for k in ("gh", "gh_raw", "add_labels", "NUM")}
        self._run = dg.subprocess.run
        self.labels, self.comments, self.removed = [], [], []

        def fake_run(args, **kw):
            if "DELETE" in args:
                self.removed.append(args[-1].rsplit("/", 1)[-1])
            return _Result()
        dg.subprocess.run = fake_run
        dg.NUM = "500"
        dg.add_labels = lambda *names: self.labels.extend(names) or True
        dg.gh_raw = lambda args: DIFF

    def tearDown(self):
        for k, v in self._saved.items():
            setattr(dg, k, v)
        dg.subprocess.run = self._run

    def _run_claim(self, claimant, pr_url, pr_author, state="MERGED"):
        def fake_gh(args, default=None, strict=False):
            if args[:2] == ["issue", "view"]:
                return {"title": "Bounty claim: docstring batch (10 functions documented)",
                        "body": f"PR: {pr_url}\n10 functions documented",
                        "labels": [], "author": {"login": claimant}, "state": "OPEN"}
            if args[:2] == ["pr", "view"]:
                return {"state": state, "additions": 10, "deletions": 0, "files": [],
                        "author": {"login": pr_author} if pr_author else None,
                        "mergedAt": "2026-09-01T00:00:00Z"}
            if args[:2] == ["issue", "comment"]:
                self.comments.append(args[args.index("--body") + 1])
                return None
            if "search/issues" in " ".join(args):
                return {"items": []}
            return default
        dg.gh = fake_gh
        return dg.main()

    def assertHeld(self):
        self.assertNotIn("bounty-eligible", self.labels)
        self.assertNotIn("docstring-verified", self.labels)
        self.assertIn("needs-human", self.labels)
        self.assertFalse(any("rtc-payout-amount" in c for c in self.comments),
                         "a held claim must not carry a payout marker")

    def test_own_pr_in_project_repo_is_verified(self):
        rc = self._run_claim("alice", "https://github.com/Scottcjn/bottube/pull/1", "alice")
        self.assertEqual(rc, 0)
        self.assertIn("bounty-eligible", self.labels)
        self.assertIn("docstring-verified", self.labels)
        self.assertTrue(any("rtc-payout-amount: 0.1" in c for c in self.comments))

    def test_owner_and_login_match_is_case_insensitive(self):
        self._run_claim("Alice", "https://github.com/scottcjn/Rustchain/pull/2", "alice")
        self.assertIn("docstring-verified", self.labels)

    def test_someone_elses_pr_is_held_not_paid(self):
        rc = self._run_claim("mallory", "https://github.com/Scottcjn/bottube/pull/1", "alice")
        self.assertEqual(rc, 0)
        self.assertHeld()
        self.assertTrue(any("@alice" in c for c in self.comments))

    def test_pr_outside_project_repos_is_held_not_paid(self):
        self._run_claim("mallory", "https://github.com/psf/requests/pull/6000", "mallory")
        self.assertHeld()

    def test_unknown_pr_author_fails_closed(self):
        self._run_claim("mallory", "https://github.com/Scottcjn/bottube/pull/1", None)
        self.assertHeld()

    def test_someone_elses_open_pr_is_not_parked_awaiting_merge(self):
        self._run_claim("mallory", "https://github.com/Scottcjn/bottube/pull/1", "alice",
                        state="OPEN")
        self.assertNotIn("awaiting-merge", self.labels)
        self.assertIn("awaiting-merge", self.removed,
                      "a previously parked claim must leave the re-check sweep")
        self.assertHeld()


if __name__ == "__main__":
    unittest.main()
