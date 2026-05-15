import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "github-tip-bot" / "tip_bot.py"


def load_tip_bot():
    fake_github = types.ModuleType("github")
    fake_github.Github = object
    fake_requests = types.ModuleType("requests")
    fake_requests.get = lambda *args, **kwargs: None

    spec = importlib.util.spec_from_file_location("github_tip_bot_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"github": fake_github, "requests": fake_requests}):
        assert spec.loader is not None
        spec.loader.exec_module(module)
    return module


class GitHubTipBotTests(unittest.TestCase):
    def setUp(self):
        self.tip_bot = load_tip_bot()
        self.tip_bot.registered_wallets.clear()
        self.tip_bot.tip_ledger.clear()

    def test_parse_tip_command_accepts_decimal_amount_and_memo(self):
        command, args = self.tip_bot.parse_command("/tip @alice 2.5 RTC Great PR")

        self.assertEqual(command, "tip")
        self.assertEqual(args["recipient"], "alice")
        self.assertEqual(args["amount"], 2.5)
        self.assertEqual(args["memo"], "Great PR")

    def test_parse_command_rejects_incomplete_or_unknown_commands(self):
        self.assertEqual(self.tip_bot.parse_command("/register"), (None, {}))
        self.assertEqual(self.tip_bot.parse_command("thanks for the review"), (None, {}))

    def test_process_tip_requires_registered_recipient_wallet(self):
        result = self.tip_bot.process_tip("carol", "missing_wallet", 1.0, "thanks")

        self.assertEqual(result["status"], "error")
        self.assertIn("not registered", result["message"])
        self.assertEqual(self.tip_bot.tip_ledger, [])

    def test_register_process_tip_and_leaderboard_ordering(self):
        self.assertTrue(self.tip_bot.register_wallet("alice", "alice_wallet"))
        self.assertTrue(self.tip_bot.register_wallet("bob", "bob_wallet"))

        self.assertEqual(
            self.tip_bot.process_tip("carol", "bob_wallet", 1.0)["status"],
            "queued",
        )
        self.assertEqual(
            self.tip_bot.process_tip("dana", "alice_wallet", 5.0, "review")["status"],
            "queued",
        )
        self.assertEqual(
            self.tip_bot.process_tip("erin", "alice_wallet", 2.5, "docs")["status"],
            "queued",
        )

        self.assertEqual(
            self.tip_bot.get_leaderboard(),
            [("alice_wallet", 7.5), ("bob_wallet", 1.0)],
        )


if __name__ == "__main__":
    unittest.main()
