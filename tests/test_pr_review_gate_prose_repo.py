#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for prose_repo() in scripts/pr_review_gate.py.

Claims that name their repo in prose rather than as a full PR URL resolved to
(None, N), so the gate assumed TARGET_REPO, looked up a number belonging to a
different repo, found nothing, and filed the claim as needs-human. That was 7
of the 13 claims paid out by hand on 2026-08-07.

The risk in fixing it is over-matching: a resolver that grabs "this PR #12"
would redirect valid claims to a nonexistent repo. These tests pin both
directions.
"""
import importlib.util
import os
import unittest
from pathlib import Path

os.environ.setdefault("GITHUB_TOKEN", "dummy")
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "pr_review_gate.py"
spec = importlib.util.spec_from_file_location("gate_under_test", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class ProseRepoMatches(unittest.TestCase):
    def test_bare_repo_then_pr(self):
        self.assertEqual(
            gate.prose_repo("[CLAIM] Code review bounty #73 for rustchain-bounties PR #13434", ""),
            "rustchain-bounties")

    def test_owner_qualified_with_pr(self):
        self.assertEqual(
            gate.prose_repo("[Bounty Claim] Code Review - Scottcjn/rustchain-dialup PR #4", ""),
            "rustchain-dialup")

    def test_owner_qualified_hash_form(self):
        self.assertEqual(
            gate.prose_repo("Bounty claim: review Scottcjn/Rustchain#5358", ""),
            "Rustchain")

    def test_found_in_body_when_absent_from_title(self):
        self.assertEqual(
            gate.prose_repo("[Bounty Claim] Code Review", "Reviewed bottube PR #1622 today."),
            "bottube")

    def test_product_prefix_without_hyphen(self):
        self.assertEqual(gate.prose_repo("review of bottube PR #900", ""), "bottube")


class ProseRepoRejects(unittest.TestCase):
    """Over-matching would redirect valid claims at a repo that does not exist."""

    def test_plain_pr_reference_is_not_a_repo(self):
        self.assertIsNone(gate.prose_repo("[Bounty Claim] PR Review - PR #5536 (Bounty #73)", ""))

    def test_common_words_are_not_repos(self):
        for t in ["I reviewed this PR #12", "the PR #4944 was fine",
                  "Claim: PR Review #4944 - missing SPDX gate failure"]:
            self.assertIsNone(gate.prose_repo(t, ""), t)

    def test_empty_inputs(self):
        self.assertIsNone(gate.prose_repo("", ""))
        self.assertIsNone(gate.prose_repo("", None))


class PrRefUnchanged(unittest.TestCase):
    """The existing resolver must keep its current behaviour exactly."""

    def test_full_url_still_wins(self):
        r, n = gate.pr_ref("", "https://github.com/Scottcjn/Rustchain/pull/5395 reviewed")
        self.assertEqual((r, n), ("Scottcjn/Rustchain", "5395"))

    def test_bounty_number_not_mistaken_for_pr(self):
        r, n = gate.pr_ref("Bounty #1009 claim: review of PR #1396", "")
        self.assertEqual(n, "1396")

    def test_prose_repo_does_not_change_pr_number(self):
        title = "[CLAIM] Code review bounty #73 for rustchain-bounties PR #13434"
        _, n = gate.pr_ref(title, "")
        self.assertEqual(n, "13434")


if __name__ == "__main__":
    unittest.main()
