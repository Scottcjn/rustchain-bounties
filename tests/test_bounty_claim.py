#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for scripts/bounty_claim.py."""

import datetime
import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("GITHUB_TOKEN", "dummy")
SCRIPT = Path(__file__).resolve().parent / "scripts" / "bounty_claim.py"
spec = importlib.util.spec_from_file_location("bounty_claim_under_test", SCRIPT)
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

TODAY = datetime.date.today()

class TestBountyValidation(unittest.TestCase):
    def setUp(self):
        self._gh = bc.gh

    def tearDown(self):
        bc.gh = self._gh

    def test_starred_repo_validation(self):
        bc.gh = lambda a, d=None: [{"id": 1}] if a == "users/HCIE2054/starred/rustchain-bounties" else []
        self.assertTrue(bc.validate_starred_repo("HCIE2054"))
        bc.gh = lambda a, d=None: []
        self.assertFalse(bc.validate_starred_repo("HCIE2054"))

    def test_review_quality_validation(self):
        mock_reviews = [
            {"type": "ReviewCommentEvent", "payload": {"state": "APPROVED", "body": "LGTM"}},
            {"type": "ReviewCommentEvent", "payload": {"state": "APPROVED", "body": "Approved"}},
            {"type": "ReviewCommentEvent", "payload": {"state": "CHANGES_REQUESTED", "body": "Needs work"}}
        ]
        bc.gh = lambda a, d=None: mock_reviews if a == "users/HCIE2054/events" else []
        self.assertTrue(bc.validate_review_quality("HCIE2054", 2))
        self.assertFalse(bc.validate_review_quality("HCIE2054", 4))

    def test_star_plus_review_validation(self):
        bc.gh = lambda a, d=None: (
            [{"id": 1}] if a == "users/HCIE2054/starred/rustchain-bounties" else
            [
                {"type": "ReviewCommentEvent", "payload": {"state": "APPROVED", "body": "LGTM"}},
                {"type": "ReviewCommentEvent", "payload": {"state": "APPROVED", "body": "Approved"}},
                {"type": "ReviewCommentEvent", "payload": {"state": "APPROVED", "body": "LGTM"}}
            ]
        )
        self.assertTrue(bc.validate_bounty_claim(2782, "HCIE2054", "star+review"))

    def test_star_plus_review_failure(self):
        bc.gh = lambda a, d=None: (
            [] if a == "users/HCIE2054/starred/rustchain-bounties" else
            [
                {"type": "ReviewCommentEvent", "payload": {"state": "CHANGES_REQUESTED", "body": "Needs work"}}
            ]
        )
        self.assertFalse(bc.validate_bounty_claim(2782, "HCIE2054", "star+review"))

if __name__ == "__main__":
    unittest.main()