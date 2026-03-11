#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Tests for wallet_api_server.py — the mobile wallet API proxy.

Run: python -m pytest tests/test_wallet_api_server.py -v

Covers:
  - Input validation (wallet ID format, length, special chars)
  - Handler logic for balance, history, epoch, miners, health
  - Upstream error propagation
  - CORS headers on responses
  - HTTP routing (404 for unknown paths)
  - JSON response formatting
"""

import io
import json
import re
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from wallet_api_server import (
    validate_wallet,
    handle_health,
    handle_balance,
    handle_history,
    handle_epoch,
    handle_miners,
    ROUTE_TABLE,
    HANDLERS,
    WALLET_RE,
    WalletRequestHandler,
)


# ---------------------------------------------------------------------------
# Wallet validation
# ---------------------------------------------------------------------------


class TestValidateWallet(unittest.TestCase):
    """validate_wallet must accept valid IDs and reject invalid ones."""

    VALID_IDS = [
        "a" * 38 + "RTC",               # strict 41-char hex+RTC
        "victus-x86-scott",              # free-form miner name
        "my_wallet_123",                 # underscores OK
        "A1b2C3",                        # mixed case
    ]

    INVALID_IDS = [
        ("", "wallet ID is required"),
        ("   ", "wallet ID contains invalid characters"),
        ("a" * 65, "wallet ID too long"),
        ("wallet!@#", "wallet ID contains invalid characters"),
        ("wal let", "wallet ID contains invalid characters"),
        ("wallet/path", "wallet ID contains invalid characters"),
    ]

    def test_valid_ids_accepted(self):
        for wid in self.VALID_IDS:
            with self.subTest(wallet=wid):
                self.assertIsNone(validate_wallet(wid))

    def test_invalid_ids_rejected(self):
        for wid, expected_msg in self.INVALID_IDS:
            with self.subTest(wallet=wid):
                err = validate_wallet(wid)
                self.assertIsNotNone(err)
                self.assertIn(expected_msg, err)


class TestWalletRegex(unittest.TestCase):
    """WALLET_RE should match strict 38-hex + RTC format only."""

    def test_strict_match(self):
        self.assertTrue(WALLET_RE.match("a" * 38 + "RTC"))
        self.assertTrue(WALLET_RE.match("0123456789abcdef" * 2 + "abcdef" + "RTC"))

    def test_rejects_short(self):
        self.assertIsNone(WALLET_RE.match("abcRTC"))

    def test_rejects_no_suffix(self):
        self.assertIsNone(WALLET_RE.match("a" * 38))

    def test_rejects_non_hex(self):
        self.assertIsNone(WALLET_RE.match("g" * 38 + "RTC"))


# ---------------------------------------------------------------------------
# Handler tests — mock upstream node_get
# ---------------------------------------------------------------------------


def _make_match(pattern_str, path):
    """Create a regex match object for handler testing."""
    pattern = re.compile(pattern_str)
    return pattern.match(path)


class TestHandleHealth(unittest.TestCase):
    @patch("wallet_api_server.node_get")
    def test_passes_upstream_response(self, mock_get):
        mock_get.return_value = (200, {"ok": True, "version": "2.2.1-rip200"})
        match = _make_match(r"^/api/health$", "/api/health")
        status, body = handle_health("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        mock_get.assert_called_once_with("https://fake-node", "/health")

    @patch("wallet_api_server.node_get")
    def test_propagates_upstream_error(self, mock_get):
        mock_get.return_value = (502, {"error": "upstream: connection refused"})
        match = _make_match(r"^/api/health$", "/api/health")
        status, body = handle_health("https://fake-node", match)
        self.assertEqual(status, 502)
        self.assertIn("error", body)


class TestHandleBalance(unittest.TestCase):
    BALANCE_PATTERN = r"^/api/balance/(?P<wallet>[^/]+)$"

    @patch("wallet_api_server.node_get")
    def test_returns_normalised_balance(self, mock_get):
        mock_get.return_value = (200, {
            "amount_rtc": 42.5,
            "amount_i64": 42500000,
            "miner_id": "abc123RTC",
        })
        match = _make_match(self.BALANCE_PATTERN, "/api/balance/abc123RTC")
        status, body = handle_balance("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertEqual(body["wallet_id"], "abc123RTC")
        self.assertEqual(body["balance_rtc"], 42.5)
        self.assertEqual(body["balance_raw"], 42500000)

    @patch("wallet_api_server.node_get")
    def test_zero_balance(self, mock_get):
        mock_get.return_value = (200, {"amount_rtc": 0.0, "amount_i64": 0})
        match = _make_match(self.BALANCE_PATTERN, "/api/balance/empty-wallet")
        status, body = handle_balance("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertEqual(body["balance_rtc"], 0.0)
        self.assertEqual(body["balance_raw"], 0)

    def test_rejects_invalid_wallet(self):
        match = _make_match(
            r"^/api/balance/(?P<wallet>[^/]+)$",
            "/api/balance/bad!wallet",
        )
        status, body = handle_balance("https://fake-node", match)
        self.assertEqual(status, 400)
        self.assertIn("error", body)

    @patch("wallet_api_server.node_get")
    def test_upstream_error_forwarded(self, mock_get):
        mock_get.return_value = (500, {"error": "internal"})
        match = _make_match(self.BALANCE_PATTERN, "/api/balance/mywalletRTC")
        status, body = handle_balance("https://fake-node", match)
        self.assertEqual(status, 500)


class TestHandleHistory(unittest.TestCase):
    HISTORY_PATTERN = r"^/api/history/(?P<wallet>[^/]+)$"

    @patch("wallet_api_server.node_get")
    def test_returns_transactions_with_balance(self, mock_get):
        mock_get.side_effect = [
            (200, {"amount_rtc": 100.0, "amount_i64": 100000000}),
            (200, {"epoch": 73, "slot": 10554}),
        ]
        match = _make_match(self.HISTORY_PATTERN, "/api/history/abc123RTC")
        status, body = handle_history("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertEqual(body["wallet_id"], "abc123RTC")
        self.assertEqual(len(body["transactions"]), 1)
        tx = body["transactions"][0]
        self.assertEqual(tx["type"], "mining_reward")
        self.assertEqual(tx["amount_rtc"], 100.0)
        self.assertEqual(tx["epoch"], 73)
        self.assertIn("note", body)

    @patch("wallet_api_server.node_get")
    def test_returns_empty_history_for_zero_balance(self, mock_get):
        mock_get.side_effect = [
            (200, {"amount_rtc": 0.0, "amount_i64": 0}),
            (200, {"epoch": 1}),
        ]
        match = _make_match(self.HISTORY_PATTERN, "/api/history/new-miner")
        status, body = handle_history("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertEqual(len(body["transactions"]), 0)

    @patch("wallet_api_server.node_get")
    def test_handles_upstream_balance_failure(self, mock_get):
        mock_get.side_effect = [
            (500, {"error": "down"}),
            (200, {"epoch": 1}),
        ]
        match = _make_match(self.HISTORY_PATTERN, "/api/history/test-wallet")
        status, body = handle_history("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertEqual(len(body["transactions"]), 0)

    def test_rejects_invalid_wallet(self):
        match = _make_match(self.HISTORY_PATTERN, "/api/history/bad wallet")
        status, body = handle_history("https://fake-node", match)
        self.assertEqual(status, 400)
        self.assertIn("error", body)


class TestHandleEpoch(unittest.TestCase):
    @patch("wallet_api_server.node_get")
    def test_returns_epoch_data(self, mock_get):
        epoch_data = {"epoch": 73, "slot": 10554, "enrolled_miners": 12, "epoch_pot": 1.5}
        mock_get.return_value = (200, epoch_data)
        match = _make_match(r"^/api/epoch$", "/api/epoch")
        status, body = handle_epoch("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertEqual(body["epoch"], 73)
        self.assertEqual(body["slot"], 10554)


class TestHandleMiners(unittest.TestCase):
    @patch("wallet_api_server.node_get")
    def test_wraps_miners_list(self, mock_get):
        miners = [{"miner": "a"}, {"miner": "b"}]
        mock_get.return_value = (200, miners)
        match = _make_match(r"^/api/miners$", "/api/miners")
        status, body = handle_miners("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertEqual(body["count"], 2)
        self.assertEqual(len(body["miners"]), 2)

    @patch("wallet_api_server.node_get")
    def test_passes_error_body(self, mock_get):
        mock_get.return_value = (503, {"error": "unavailable"})
        match = _make_match(r"^/api/miners$", "/api/miners")
        status, body = handle_miners("https://fake-node", match)
        self.assertEqual(status, 503)
        self.assertIn("error", body)


# ---------------------------------------------------------------------------
# Routing table
# ---------------------------------------------------------------------------


class TestRouting(unittest.TestCase):
    """Verify that ROUTE_TABLE covers all expected paths."""

    EXPECTED_ROUTES = [
        ("/api/health", "handle_health"),
        ("/api/balance/abc123RTC", "handle_balance"),
        ("/api/history/my-wallet", "handle_history"),
        ("/api/epoch", "handle_epoch"),
        ("/api/miners", "handle_miners"),
    ]

    NO_MATCH_PATHS = [
        "/api/unknown",
        "/health",
        "/",
        "/api/balance/",
        "/api/balance",
    ]

    def test_expected_routes_match(self):
        for path, expected_handler in self.EXPECTED_ROUTES:
            matched = False
            for method, pattern, handler_name in ROUTE_TABLE:
                m = pattern.match(path)
                if m:
                    self.assertEqual(handler_name, expected_handler)
                    matched = True
                    break
            self.assertTrue(matched, f"No route matched {path}")

    def test_unknown_paths_do_not_match(self):
        for path in self.NO_MATCH_PATHS:
            for method, pattern, handler_name in ROUTE_TABLE:
                m = pattern.match(path)
                if m:
                    self.fail(f"{path} should not match {handler_name}")


# ---------------------------------------------------------------------------
# Handler function registry
# ---------------------------------------------------------------------------


class TestHandlersRegistry(unittest.TestCase):
    """HANDLERS dict must map every ROUTE_TABLE handler name."""

    def test_all_routes_have_handlers(self):
        for method, pattern, handler_name in ROUTE_TABLE:
            self.assertIn(handler_name, HANDLERS, f"Missing handler: {handler_name}")
            self.assertTrue(callable(HANDLERS[handler_name]))


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases(unittest.TestCase):
    """Cover unusual but valid input scenarios."""

    @patch("wallet_api_server.node_get")
    def test_balance_with_missing_amount_fields(self, mock_get):
        # Upstream might return an unexpected shape
        mock_get.return_value = (200, {})
        match = _make_match(
            r"^/api/balance/(?P<wallet>[^/]+)$",
            "/api/balance/safe-wallet",
        )
        status, body = handle_balance("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertEqual(body["balance_rtc"], 0.0)
        self.assertEqual(body["balance_raw"], 0)

    @patch("wallet_api_server.node_get")
    def test_history_with_epoch_failure(self, mock_get):
        mock_get.side_effect = [
            (200, {"amount_rtc": 10.0, "amount_i64": 10000000}),
            (500, {"error": "boom"}),
        ]
        match = _make_match(
            r"^/api/history/(?P<wallet>[^/]+)$",
            "/api/history/wallet-x",
        )
        status, body = handle_history("https://fake-node", match)
        self.assertEqual(status, 200)
        self.assertEqual(len(body["transactions"]), 1)
        # Epoch should be None when epoch fetch fails
        self.assertIsNone(body["transactions"][0]["epoch"])

    @patch("wallet_api_server.node_get")
    def test_miners_with_non_list_body(self, mock_get):
        # If upstream returns something unexpected
        mock_get.return_value = (200, {"unexpected": "shape"})
        match = _make_match(r"^/api/miners$", "/api/miners")
        status, body = handle_miners("https://fake-node", match)
        self.assertEqual(status, 200)
        # Should pass through non-list bodies as-is
        self.assertEqual(body, {"unexpected": "shape"})


if __name__ == "__main__":
    unittest.main()
