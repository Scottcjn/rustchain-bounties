"""Tests for RustChain Telegram Bot"""

import json
import unittest
from unittest.mock import patch, MagicMock

import bot


class TestRateLimit(unittest.TestCase):
    def test_first_request_allowed(self):
        bot._last_request.clear()
        self.assertFalse(bot.check_rate_limit(12345))

    def test_rapid_request_blocked(self):
        bot._last_request.clear()
        bot.check_rate_limit(12345)
        self.assertTrue(bot.check_rate_limit(12345))

    def test_different_users_independent(self):
        bot._last_request.clear()
        bot.check_rate_limit(1)
        self.assertFalse(bot.check_rate_limit(2))


class TestApiGet(unittest.TestCase):
    @patch("bot.urlopen")
    def test_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"balance": 100}).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        result = bot.api_get("/balance/test")
        self.assertEqual(result, {"balance": 100})

    @patch("bot.urlopen", side_effect=bot.URLError("offline"))
    def test_node_offline(self, mock_urlopen):
        result = bot.api_get("/balance/test")
        self.assertIsNone(result)


class TestGetBalance(unittest.TestCase):
    @patch("bot.api_get", return_value={"balance": 42.5})
    def test_balance_found(self, mock_api):
        result = bot.get_balance("test_wallet")
        self.assertEqual(result["wallet"], "test_wallet")
        self.assertEqual(result["balance"], 42.5)

    @patch("bot.api_get", return_value=None)
    def test_balance_not_found(self, mock_api):
        result = bot.get_balance("nonexistent")
        self.assertIsNone(result)


class TestGetMiners(unittest.TestCase):
    @patch("bot.api_get", return_value=[{"name": "miner1", "hashrate": 100}])
    def test_miners_found(self, mock_api):
        result = bot.get_miners()
        self.assertEqual(len(result), 1)

    @patch("bot.api_get", return_value=None)
    def test_miners_offline(self, mock_api):
        result = bot.get_miners()
        self.assertIsNone(result)


class TestGetEpoch(unittest.TestCase):
    @patch("bot.api_get", return_value={"epoch": 42, "height": 1000})
    def test_epoch_found(self, mock_api):
        result = bot.get_epoch()
        self.assertEqual(result["epoch"], 42)

    @patch("bot.api_get", return_value=None)
    def test_epoch_offline(self, mock_api):
        result = bot.get_epoch()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
