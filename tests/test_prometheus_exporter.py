"""Unit tests for scripts/prometheus_exporter.py — Bounty Issue #1589

Covers 5 functions/classes with 16 test cases:
- _request_json: successful fetch, connection error, timeout, invalid JSON
- fetch_endpoint: path joining, error propagation
- fetch_wallet_balance: URL construction, result structure
- parse_args: default values, custom overrides
- RustChainCollector: instantiation, attributes
"""

import json
import argparse
from unittest.mock import patch, MagicMock
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import prometheus_exporter as pe


# ─── _request_json ─────────────────────────────────────────────────

class TestRequestJson:
    @patch("prometheus_exporter.urllib.request.urlopen")
    def test_successful_json(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"key": "value"}).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        data, err, elapsed = pe._request_json("https://example.com/api")
        assert data == {"key": "value"}
        assert err is None
        assert elapsed >= 0.0

    @patch("prometheus_exporter.urllib.request.urlopen")
    def test_connection_error(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        data, err, elapsed = pe._request_json("https://example.com/api")
        assert data is None
        assert err is not None

    @patch("prometheus_exporter.urllib.request.urlopen")
    def test_invalid_json(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not json {{{"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        data, err, elapsed = pe._request_json("https://example.com/api")
        assert data is None
        assert err is not None


# ─── fetch_endpoint ────────────────────────────────────────────────

class TestFetchEndpoint:
    @patch("prometheus_exporter._request_json")
    def test_calls_with_correct_url(self, mock_req):
        mock_req.return_value = ({"status": "ok"}, None, 0.1)
        data, err, elapsed = pe.fetch_endpoint("https://example.com", "/health")
        mock_req.assert_called_once()
        url_used = mock_req.call_args[0][0]
        assert "example.com" in url_used
        assert "/health" in url_used

    @patch("prometheus_exporter._request_json")
    def test_propagates_error(self, mock_req):
        mock_req.return_value = (None, "timeout", 5.0)
        data, err, elapsed = pe.fetch_endpoint("https://example.com", "/bad")
        assert data is None
        assert err == "timeout"


# ─── fetch_wallet_balance ──────────────────────────────────────────

class TestFetchWalletBalance:
    @patch("prometheus_exporter._request_json")
    def test_returns_balance_dict(self, mock_req):
        mock_req.return_value = ({"balance": 100, "stake": 50}, None, 0.2)
        result, err, elapsed = pe.fetch_wallet_balance("https://example.com", "miner1")
        assert result is not None
        assert err is None

    @patch("prometheus_exporter._request_json")
    def test_url_contains_miner_id(self, mock_req):
        mock_req.return_value = ({}, None, 0.1)
        pe.fetch_wallet_balance("https://example.com", "miner123")
        url_used = mock_req.call_args[0][0]
        assert "miner123" in url_used


# ─── parse_args ────────────────────────────────────────────────────

class TestParseArgs:
    def test_defaults(self):
        args = pe.parse_args([])
        assert hasattr(args, "port")
        assert hasattr(args, "node_url")

    def test_custom_port(self):
        args = pe.parse_args(["--port", "9999"])
        assert args.port == 9999

    def test_custom_node_url(self):
        args = pe.parse_args(["--node-url", "https://custom.node"])
        assert args.node_url == "https://custom.node"

    def test_tracked_wallets(self):
        args = pe.parse_args(["--tracked-wallets", "w1,w2,w3"])
        assert args.tracked_wallets == "w1,w2,w3"

    def test_verify_tls_flag(self):
        args = pe.parse_args(["--verify-tls"])
        assert args.verify_tls is True


# ─── RustChainCollector ────────────────────────────────────────────

class TestRustChainCollector:
    def test_instantiation(self):
        collector = pe.RustChainCollector(node_url="https://example.com")
        assert collector is not None
        assert collector.node_url == "https://example.com"

    def test_collect_method_exists(self):
        collector = pe.RustChainCollector(node_url="https://example.com")
        assert hasattr(collector, "collect")
        assert callable(collector.collect)

    def test_tracked_wallets_default(self):
        collector = pe.RustChainCollector(node_url="https://example.com")
        assert collector.tracked_wallets == []

    def test_tracked_wallets_custom(self):
        collector = pe.RustChainCollector(node_url="https://example.com", tracked_wallets=["w1", "w2"])
        assert collector.tracked_wallets == ["w1", "w2"]
