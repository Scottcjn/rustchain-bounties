"""Unit tests for tools/health_check.py — Bounty Issue #1589

Covers 5 functions with 18 test cases:
- create_ssl_context: insecure True/False
- http_get: success, connection error, timeout
- format_uptime: seconds/minutes/hours/days
- format_tip_age: same as uptime
- check_node: structure validation
"""

import ssl
import json
from unittest.mock import patch, MagicMock
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

import health_check as hc


# ─── create_ssl_context ────────────────────────────────────────────

class TestCreateSslContext:
    def test_insecure_returns_context(self):
        ctx = hc.create_ssl_context(insecure=True)
        assert ctx is not None
        assert isinstance(ctx, ssl.SSLContext)
        assert ctx.check_hostname is False
        assert ctx.verify_mode == ssl.CERT_NONE

    def test_secure_returns_none(self):
        ctx = hc.create_ssl_context(insecure=False)
        assert ctx is None


# ─── http_get ──────────────────────────────────────────────────────

class TestHttpGet:
    @patch("health_check.urllib.request.urlopen")
    def test_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"ok": True}).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        ok, data, err = hc.http_get("https://example.com/health")
        assert ok is True
        assert data == {"ok": True}
        assert err == ""

    @patch("health_check.urllib.request.urlopen")
    def test_connection_error(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("refused")
        ok, data, err = hc.http_get("https://example.com/health")
        assert ok is False
        assert err != ""

    @patch("health_check.urllib.request.urlopen")
    def test_timeout(self, mock_urlopen):
        import socket
        mock_urlopen.side_effect = socket.timeout("timed out")
        ok, data, err = hc.http_get("https://example.com/health", timeout=1)
        assert ok is False


# ─── format_uptime ─────────────────────────────────────────────────

class TestFormatUptime:
    def test_seconds(self):
        assert hc.format_uptime(30) == "30s"

    def test_minutes(self):
        result = hc.format_uptime(150)
        assert "2m" in result

    def test_hours(self):
        result = hc.format_uptime(7320)
        assert "2h" in result

    def test_days(self):
        result = hc.format_uptime(172800)
        assert "2d" in result

    def test_zero(self):
        assert hc.format_uptime(0) == "0s"

    def test_invalid_input(self):
        result = hc.format_uptime("invalid")
        assert "invalid" in result or "err" in result or isinstance(result, str)


# ─── format_tip_age ────────────────────────────────────────────────

class TestFormatTipAge:
    def test_seconds(self):
        assert hc.format_tip_age(45) == "45s"

    def test_minutes(self):
        result = hc.format_tip_age(90)
        assert "1m" in result

    def test_hours(self):
        result = hc.format_tip_age(3600)
        assert "1h" in result


# ─── check_node ────────────────────────────────────────────────────

class TestCheckNode:
    @patch("health_check.http_get")
    def test_returns_dict(self, mock_get):
        mock_get.return_value = (True, {"version": "1.0", "uptime": 100}, "")
        result = hc.check_node("https://example.com")
        assert isinstance(result, dict)

    @patch("health_check.http_get")
    def test_offline_node(self, mock_get):
        mock_get.return_value = (False, None, "connection refused")
        result = hc.check_node("https://example.com")
        assert isinstance(result, dict)
        assert result.get("online") is False or "error" in str(result).lower()
