# SPDX-License-Identifier: MIT

import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
