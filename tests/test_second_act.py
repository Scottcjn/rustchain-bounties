#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for scripts/second_act.py (payout second-act hook).

Covers the substring bug that shipped in the first draft: naive
`"review" in title` also matches "Rich Link PREVIEWs", which suggested a
BoTTube embed bounty to a code reviewer. Family keys are word-anchored now.

Also asserts the hook is fail-open: it must never raise into the payout path,
because a broken retention hook must not block a payment.
"""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "second_act.py"
spec = importlib.util.spec_from_file_location("second_act_under_test", SCRIPT)
sa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sa)


class ClassifyTests(unittest.TestCase):
    def test_review_titles(self):
        for t in ["PR Review - RustChain PR #5395 (Bounty #73)",
                  "[Bounty Claim] Code Review - PR #5746",
                  "Bounty claim: review Scottcjn/Rustchain#5358"]:
            self.assertEqual(sa.classify(t), "review", t)

    def test_preview_is_not_review(self):
        """The shipped bug: 'previews' must not classify as review work."""
        t = "BoTTube OEmbed Protocol - Rich Link Previews Everywhere"
        self.assertNotEqual(sa.classify(t), "review")

    def test_reviewer_is_not_a_substring_match(self):
        self.assertNotEqual(sa.classify("Add reviewerless CI stage"), "review")

    def test_writing_titles(self):
        self.assertEqual(sa.classify("Write a Blog Post About RustChain"), "writing")
        self.assertEqual(sa.classify("Make a written tutorial on Proof of Antiquity"), "writing")

    def test_security_and_mining(self):
        self.assertEqual(sa.classify("[SECURITY] Airdrop claim theft"), "security")
        self.assertEqual(sa.classify("Run a RustChain miner on real hardware"), "mining")

    def test_unmatched_is_general(self):
        self.assertEqual(sa.classify("Update the changelog"), "general")
        self.assertEqual(sa.classify(""), "general")
        self.assertEqual(sa.classify(None), "general")


class BountyParseTests(unittest.TestCase):
    def test_amount_extraction(self):
        m = sa.BOUNTY_TITLE_RE.search("[BOUNTY: 35 RTC] Harden x86 validation")
        self.assertEqual(m.group(1), "35")

    def test_range_amount(self):
        m = sa.BOUNTY_TITLE_RE.search("[BOUNTY: 3-5 RTC] Write an explainer")
        self.assertEqual(m.group(1), "3")

    def test_non_bounty_title_ignored(self):
        self.assertIsNone(sa.BOUNTY_TITLE_RE.search("Claim: PR Review #4944"))


class FailOpenTests(unittest.TestCase):
    def test_build_never_raises(self):
        """A broken hook must degrade to empty, never block a payout."""
        def boom(*a, **k):
            raise RuntimeError("gh exploded")

        orig = sa._gh_json
        sa._gh_json = boom
        try:
            self.assertEqual(sa.build("alice", "o/r", "PR Review"), "")
        finally:
            sa._gh_json = orig

    def test_empty_inputs_are_safe(self):
        orig = sa._gh_json
        sa._gh_json = lambda a, d: d
        try:
            self.assertEqual(sa.build("", "o/r", ""), "")
        finally:
            sa._gh_json = orig


if __name__ == "__main__":
    unittest.main()
