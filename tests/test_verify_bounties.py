# SPDX-License-Identifier: MIT

import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


def load_verify_bounties():
    os.environ.setdefault("GITHUB_TOKEN", "dummy-token-for-tests")
    requests_stub = types.SimpleNamespace(
        Session=lambda: types.SimpleNamespace(headers={}, get=None, post=None, patch=None)
    )
    sys.modules.setdefault("requests", requests_stub)
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "verify_bounties.py"
    spec = importlib.util.spec_from_file_location("verify_bounties", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestVerifyBounties(unittest.TestCase):
    def test_extract_claimants_skips_bot_owner_empty_and_dedupes_users(self):
        mod = load_verify_bounties()
        comments = [
            {
                "id": 1,
                "user": {"login": "alice"},
                "body": "Claiming this one for wallet RTCabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            },
            {
                "id": 2,
                "user": {"login": "Alice"},
                "body": "Duplicate claim should not create another claimant",
            },
            {
                "id": 3,
                "user": {"login": mod.OWNER},
                "body": "Maintainer note",
            },
            {
                "id": 4,
                "user": {"login": "verify-bot"},
                "body": f"{mod.BOT_SIGNATURE}\nExisting report",
            },
            {
                "id": 5,
                "user": {"login": "empty"},
                "body": "   ",
            },
            {
                "id": 6,
                "user": {"login": "bob"},
                "body": "I can verify this manually.",
            },
        ]

        claimants = mod.extract_claimants(comments, issue_number=1589)

        self.assertEqual([c["username"] for c in claimants], ["alice", "bob"])
        self.assertEqual(claimants[0]["comment_id"], 1)
        self.assertTrue(claimants[0]["wallet"].startswith("RTCabcdef"))
        self.assertEqual(claimants[1]["comment_id"], 6)
        self.assertEqual(claimants[1]["wallet"], "")

    def test_find_existing_bot_comment_returns_first_signature_match(self):
        mod = load_verify_bounties()
        comments = [
            {"id": 10, "body": "Regular comment"},
            {"id": 11, "body": f"Report\n{mod.BOT_SIGNATURE}"},
            {"id": 12, "body": f"Newer report\n{mod.BOT_SIGNATURE}"},
        ]

        self.assertEqual(mod.find_existing_bot_comment(comments), 11)
        self.assertIsNone(mod.find_existing_bot_comment([{"id": 13, "body": "none"}]))

    def test_extract_claimants_handles_wallet_address_phrase(self):
        mod = load_verify_bounties()
        comments = [
            {
                "id": 20,
                "user": {"login": "alice"},
                "body": "Wallet address: bai-su",
            },
            {
                "id": 21,
                "user": {"login": "bob"},
                "body": "Wallet address: 6Da5nELroja5ngTwYZuofFur5V7gZCLvKVRX7iUahwz2",
            },
        ]

        claimants = mod.extract_claimants(comments, issue_number=1589)

        self.assertEqual(claimants[0]["wallet"], "bai-su")
        self.assertEqual(
            claimants[1]["wallet"],
            "6Da5nELroja5ngTwYZuofFur5V7gZCLvKVRX7iUahwz2",
        )

    def test_targeted_distribution_event_does_not_fetch_stargazers(self):
        mod = load_verify_bounties()
        with patch.object(mod, "is_issue_open", return_value=True), \
             patch.object(mod, "verify_distribution_claims") as verify, \
             patch.object(mod, "get_all_stargazers") as get_stars:
            failures = mod.run_targeted_issue(mod.DISTRIBUTION_BOUNTY_ISSUES[0])

        self.assertEqual(failures, [])
        verify.assert_called_once_with(mod.DISTRIBUTION_BOUNTY_ISSUES[0])
        get_stars.assert_not_called()

    def test_targeted_unknown_issue_is_a_clean_noop(self):
        mod = load_verify_bounties()
        with patch.object(mod, "is_issue_open", return_value=True), \
             patch.object(mod, "get_all_stargazers") as get_stars:
            failures = mod.run_targeted_issue(999999)

        self.assertEqual(failures, [])
        get_stars.assert_not_called()

    def test_zero_star_claim_is_reported_as_unverified(self):
        mod = load_verify_bounties()
        comments = [{
            "id": 1,
            "user": {"login": "alice"},
            "body": "/claim\nWallet: RTCC8CDAA67B90F9B06987135B8B65AB037BFB603A9",
        }]
        posted = []
        with patch.object(mod, "get_issue_comments", return_value=comments), \
             patch.object(mod, "post_comment", side_effect=lambda n, b: posted.append((n, b))):
            mod.verify_star_claims(1, {repo: set() for repo in mod.STAR_REPOS})

        self.assertEqual(len(posted), 1)
        self.assertIn(f"| @alice | 0/{len(mod.STAR_REPOS)} | None | No stars found |", posted[0][1])


if __name__ == "__main__":
    unittest.main()
