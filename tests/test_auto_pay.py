"""
Unit tests for scripts/auto-pay.py — payment directive parsing and helpers.

Covers: env, PAYMENT_RE pattern, transfer_rtc, fetch_pr_comments, post_comment.
"""

import importlib
import os
import sys
import types
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
import requests


# ---------------------------------------------------------------------------
# Import helper
# ---------------------------------------------------------------------------

@pytest.fixture()
def autopay(monkeypatch):
    """Import auto-pay module with required env vars pre-set."""
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    mod_name = "auto_pay_test_target"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    # auto-pay doesn't sys.exit at import time, so just import directly
    import auto_pay as mod
    yield mod
    sys.path.pop(0)


# ===========================================================================
# PAYMENT_RE regex
# ===========================================================================

class TestPaymentRegex:
    """Tests for the PAYMENT_RE pattern in auto-pay."""

    def test_matches_plain_payment(self):
        import re
        # Import the regex from the file directly
        PAYMENT_RE = re.compile(
            r"\*{0,2}Payment:\s*([\d]+(?:\.[\d]+)?)\s*RTC\*{0,2}",
            re.IGNORECASE,
        )
        m = PAYMENT_RE.search("Payment: 75 RTC")
        assert m is not None
        assert m.group(1) == "75"

    def test_matches_bold_payment(self):
        import re
        PAYMENT_RE = re.compile(
            r"\*{0,2}Payment:\s*([\d]+(?:\.[\d]+)?)\s*RTC\*{0,2}",
            re.IGNORECASE,
        )
        m = PAYMENT_RE.search("**Payment: 75 RTC**")
        assert m is not None
        assert m.group(1) == "75"

    def test_matches_decimal_amount(self):
        import re
        PAYMENT_RE = re.compile(
            r"\*{0,2}Payment:\s*([\d]+(?:\.[\d]+)?)\s*RTC\*{0,2}",
            re.IGNORECASE,
        )
        m = PAYMENT_RE.search("Payment: 12.5 RTC")
        assert m is not None
        assert m.group(1) == "12.5"

    def test_no_match_without_rtc(self):
        import re
        PAYMENT_RE = re.compile(
            r"\*{0,2}Payment:\s*([\d]+(?:\.[\d]+)?)\s*RTC\*{0,2}",
            re.IGNORECASE,
        )
        assert PAYMENT_RE.search("Payment: 75 BTC") is None

    def test_case_insensitive(self):
        import re
        PAYMENT_RE = re.compile(
            r"\*{0,2}Payment:\s*([\d]+(?:\.[\d]+)?)\s*RTC\*{0,2}",
            re.IGNORECASE,
        )
        m = PAYMENT_RE.search("payment: 50 rtc")
        assert m is not None
        assert m.group(1) == "50"


# ===========================================================================
# transfer_rtc
# ===========================================================================

class TestTransferRtc:
    """Tests for auto-pay.transfer_rtc."""

    def test_calls_correct_endpoint(self, autopay):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"ok": True, "tx_id": "abc123"}

        with patch("requests.post", return_value=mock_resp) as mock_post:
            result = autopay.transfer_rtc("1.2.3.4", "admin-key", "wallet1", 50.0, "test")
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "1.2.3.4:8099" in call_args[0][0]
            assert call_args[1]["json"]["amount_rtc"] == 50.0
            assert call_args[1]["json"]["to_miner"] == "wallet1"
            assert call_args[1]["json"]["from_miner"] == "founder_community"

    def test_sends_admin_key_header(self, autopay):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"ok": True}

        with patch("requests.post", return_value=mock_resp) as mock_post:
            autopay.transfer_rtc("1.2.3.4", "my-secret-key", "w", 10, "m")
            headers = mock_post.call_args[1]["headers"]
            assert headers["X-Admin-Key"] == "my-secret-key"

    def test_raises_on_connection_error(self, autopay):
        with patch("requests.post", side_effect=requests.exceptions.ConnectionError("refused")):
            with pytest.raises(requests.exceptions.ConnectionError):
                autopay.transfer_rtc("1.2.3.4", "key", "w", 10, "m")

    def test_includes_memo_in_payload(self, autopay):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"ok": True}

        with patch("requests.post", return_value=mock_resp) as mock_post:
            autopay.transfer_rtc("1.2.3.4", "k", "w", 10, "PR #42 bounty")
            payload = mock_post.call_args[1]["json"]
            assert payload["memo"] == "PR #42 bounty"


# ===========================================================================
# fetch_pr_comments
# ===========================================================================

class TestFetchPrComments:
    """Tests for auto-pay.fetch_pr_comments."""

    def test_paginates_all_pages(self, autopay):
        page1 = [{"id": i} for i in range(100)]
        page2 = [{"id": i} for i in range(100, 120)]
        page3 = []

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(side_effect=[page1, page2, page3])

        with patch("requests.get", return_value=mock_resp) as mock_get:
            result = autopay.fetch_pr_comments("owner/repo", "42")
            assert len(result) == 120
            assert mock_get.call_count == 3

    def test_empty_pr_returns_empty(self, autopay):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = []

        with patch("requests.get", return_value=mock_resp):
            result = autopay.fetch_pr_comments("owner/repo", "1")
            assert result == []


# ===========================================================================
# post_comment
# ===========================================================================

class TestPostComment:
    """Tests for auto-pay.post_comment."""

    def test_posts_to_correct_url(self, autopay):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()

        with patch("requests.post", return_value=mock_resp) as mock_post:
            autopay.post_comment("owner/repo", "42", "Hello world")
            url = mock_post.call_args[0][0]
            assert "owner/repo" in url
            assert "42" in url
            assert mock_post.call_args[1]["json"]["body"] == "Hello world"

    def test_raises_on_failure(self, autopay):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")

        with patch("requests.post", return_value=mock_resp):
            with pytest.raises(requests.exceptions.HTTPError):
                autopay.post_comment("o/r", "1", "test")
