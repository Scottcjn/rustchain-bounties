#!/usr/bin/env python3
"""Unit tests for rtc_balance.py"""

import pytest
import json
from unittest.mock import patch, MagicMock
from rtc_balance import (
    extract_balance,
    extract_epoch,
    extract_miners,
    format_balance,
    query,
    _validate_wallet,
    RTCBalanceError,
    UsageError,
    NetworkError,
    BadResponseError,
    WalletNotFoundError,
    RTC_USD,
    main,
)


class TestExtractBalance:
    """Test extract_balance function with various JSON shapes."""

    def test_balance_direct(self):
        """Test when balance is at top level with 'amount_rtc' key."""
        data = {"amount_rtc": 100.5}
        assert extract_balance(data) == 100.5

    def test_balance_key(self):
        """Test when balance is at top level with 'balance' key."""
        data = {"balance": 50.25}
        assert extract_balance(data) == 50.25

    def test_balance_nested_result(self):
        """Test when balance is nested under 'result' key."""
        data = {"result": {"amount_rtc": 75.0}}
        assert extract_balance(data) == 75.0

    def test_balance_nested_data(self):
        """Test when balance is nested under 'data' key."""
        data = {"data": {"amount_rtc": 200.0}}
        assert extract_balance(data) == 200.0

    def test_balance_wallet_nested(self):
        """Test when balance is nested under 'wallet' key."""
        data = {"wallet": {"balance": 30.0}}
        assert extract_balance(data) == 30.0

    def test_balance_empty(self):
        """Test when data is empty."""
        assert extract_balance({}) is None

    def test_balance_none(self):
        """Test when data is None (edge case)."""
        data = {"result": None}
        assert extract_balance(data) is None

    def test_balance_prefers_amount_rtc(self):
        """Test that amount_rtc is preferred over balance."""
        data = {"amount_rtc": 100.0, "balance": 200.0}
        assert extract_balance(data) == 100.0

    def test_balance_string_values(self):
        """Test that string balance values work."""
        data = {"amount_rtc": "123.45"}
        assert extract_balance(data) == "123.45"


class TestExtractEpoch:
    """Test extract_epoch function."""

    def test_epoch_top_level(self):
        data = {"epoch": 42}
        assert extract_epoch(data) == 42

    def test_epoch_nested(self):
        data = {"result": {"epoch": 100}}
        assert extract_epoch(data) == 100

    def test_epoch_missing(self):
        assert extract_epoch({}) is None

    def test_epoch_invalid(self):
        data = {"epoch": "not-a-number"}
        assert extract_epoch(data) is None


class TestExtractMiners:
    """Test extract_miners function."""

    def test_miners_top_level(self):
        data = {"miners_online": 10}
        assert extract_miners(data) == 10

    def test_miners_nested_result(self):
        data = {"result": {"miners_online": 25}}
        assert extract_miners(data) == 25

    def test_miners_data_key(self):
        data = {"data": {"miners": 50}}
        assert extract_miners(data) == 50

    def test_miners_missing(self):
        assert extract_miners({}) is None


class TestFormatBalance:
    """Test format_balance function."""

    def test_format_positive(self):
        result = format_balance(100.5)
        assert "100.50" in result
        assert "RTC" in result
        assert "$10.05" in result

    def test_format_zero(self):
        result = format_balance(0)
        assert "0" in result

    def test_format_large(self):
        result = format_balance(10000)
        assert "10,000" in result or "10000" in result
        assert "$1,000" in result or "$1000" in result

    def test_format_string(self):
        result = format_balance("50.25")
        assert "50.25" in result
        assert "$5.03" in result or "$5.02" in result


class TestValidateWallet:
    """Test _validate_wallet function."""

    def test_valid_wallet(self):
        assert _validate_wallet("my-wallet") == "my-wallet"
        assert _validate_wallet("wallet_123") == "wallet_123"
        assert _validate_wallet("Wallet123") == "Wallet123"

    def test_invalid_wallet_special_chars(self):
        with pytest.raises(UsageError):
            _validate_wallet("wallet@name")
        with pytest.raises(UsageError):
            _validate_wallet("wallet&extra=1")

    def test_invalid_wallet_too_long(self):
        with pytest.raises(UsageError):
            _validate_wallet("a" * 65)

    def test_invalid_wallet_empty(self):
        with pytest.raises(UsageError):
            _validate_wallet("")


class TestQuery:
    """Test query function with mocked HTTP."""

    @patch("rtc_balance.urllib.request.urlopen")
    def test_query_success(self, mock_urlopen):
        """Test successful query returns parsed JSON."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"amount_rtc": 100.0}'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = query("https://example.com/health")
        assert result == {"amount_rtc": 100.0}

    @patch("rtc_balance.urllib.request.urlopen")
    def test_query_non_200_raises_bad_response(self, mock_urlopen):
        """Test non-200 status raises BadResponseError."""
        mock_resp = MagicMock()
        mock_resp.status = 404
        mock_resp.reason = "Not Found"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        with pytest.raises(BadResponseError) as exc:
            query("https://example.com/health")
        assert "HTTP 404" in str(exc.value)
        assert exc.value.exit_code == 3

    @patch("rtc_balance.urllib.request.urlopen")
    def test_query_malformed_json_raises_bad_response(self, mock_urlopen):
        """Test malformed JSON raises BadResponseError."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'not valid json'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        with pytest.raises(BadResponseError) as exc:
            query("https://example.com/health")
        assert "Malformed JSON" in str(exc.value)
        assert exc.value.exit_code == 3

    @patch("rtc_balance.urllib.request.urlopen")
    def test_query_network_error_raises_network_error(self, mock_urlopen):
        """Test network error raises NetworkError."""
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")

        with pytest.raises(NetworkError) as exc:
            query("https://example.com/health")
        assert "Network error" in str(exc.value)
        assert exc.value.exit_code == 2

    @patch("rtc_balance.urllib.request.urlopen")
    def test_query_timeout_raises_network_error(self, mock_urlopen):
        """Test timeout raises NetworkError."""
        mock_urlopen.side_effect = TimeoutError("Request timed out")

        with pytest.raises(NetworkError) as exc:
            query("https://example.com/health")
        assert "timed out" in str(exc.value).lower()
        assert exc.value.exit_code == 2

    @patch("rtc_balance.urllib.request.urlopen")
    def test_query_http_error_raises_bad_response(self, mock_urlopen):
        """Test HTTPError raises BadResponseError."""
        from urllib.error import HTTPError
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'error'
        mock_urlopen.side_effect = HTTPError("url", 500, "Internal Server Error", {}, mock_resp)

        with pytest.raises(BadResponseError) as exc:
            query("https://example.com/health")
        assert "HTTP 500" in str(exc.value)
        assert exc.value.exit_code == 3

    @patch("rtc_balance.urllib.request.urlopen")
    def test_query_ssl_error_raises_network_error(self, mock_urlopen):
        """Test SSL error raises NetworkError."""
        import ssl
        mock_urlopen.side_effect = ssl.SSLError("Certificate verify failed")

        with pytest.raises(NetworkError) as exc:
            query("https://example.com/health", insecure=False)
        assert "TLS error" in str(exc.value)
        assert exc.value.exit_code == 2


class TestMain:
    """Integration tests for main() function."""

    @patch("rtc_balance.query")
    @patch("builtins.input", return_value="test-wallet")
    @patch("sys.argv", ["rtc_balance.py"])
    def test_main_success(self, mock_input, mock_query, capsys):
        """Test successful balance query."""
        mock_query.side_effect = [
            {"status": "ok"},  # health check
            {"amount_rtc": 123.45},  # balance
            {"epoch": 10, "miners_online": 5},  # epoch
        ]
        main()
        captured = capsys.readouterr()
        assert "Wallet: test-wallet" in captured.out
        assert "123.45" in captured.out
        assert "RTC" in captured.out
        assert "Epoch: 10" in captured.out
        assert "Miners online: 5" in captured.out

    @patch("sys.argv", ["rtc_balance.py"])
    @patch("builtins.input", return_value="")
    def test_main_no_wallet_exits_usage(self, mock_input):
        """Test missing wallet exits with usage error."""
        with pytest.raises(UsageError) as exc:
            main()
        assert exc.value.exit_code == 1
        assert "Wallet name required" in str(exc.value)

    @patch("rtc_balance.query")
    @patch("sys.argv", ["rtc_balance.py", "test-wallet"])
    def test_main_health_network_error(self, mock_query):
        """Test health check network error exits with network error code."""
        from rtc_balance import NetworkError
        mock_query.side_effect = NetworkError("Connection refused")
        with pytest.raises(NetworkError) as exc:
            main()
        assert exc.value.exit_code == 2
        assert "Node unreachable" in str(exc.value)

    @patch("rtc_balance.query")
    @patch("sys.argv", ["rtc_balance.py", "test-wallet"])
    def test_main_health_bad_response(self, mock_query):
        """Test health check bad response exits with bad response code."""
        from rtc_balance import BadResponseError
        mock_query.side_effect = BadResponseError("HTTP 500")
        with pytest.raises(BadResponseError) as exc:
            main()
        assert exc.value.exit_code == 3
        assert "Health check failed" in str(exc.value)

    @patch("rtc_balance.query")
    @patch("sys.argv", ["rtc_balance.py", "test-wallet"])
    def test_main_balance_network_error(self, mock_query):
        """Test balance query network error exits with network error code."""
        from rtc_balance import NetworkError
        mock_query.side_effect = [
            {"status": "ok"},  # health check
            NetworkError("Timeout"),  # balance query
        ]
        with pytest.raises(NetworkError) as exc:
            main()
        assert exc.value.exit_code == 2
        assert "Failed to fetch wallet" in str(exc.value)

    @patch("rtc_balance.query")
    @patch("sys.argv", ["rtc_balance.py", "test-wallet"])
    def test_main_balance_bad_response(self, mock_query):
        """Test balance query bad response exits with bad response code."""
        from rtc_balance import BadResponseError
        mock_query.side_effect = [
            {"status": "ok"},  # health check
            BadResponseError("HTTP 404"),  # balance query
        ]
        with pytest.raises(BadResponseError) as exc:
            main()
        assert exc.value.exit_code == 3
        assert "Balance query failed" in str(exc.value)

    @patch("rtc_balance.query")
    @patch("sys.argv", ["rtc_balance.py", "test-wallet"])
    def test_main_wallet_not_found(self, mock_query):
        """Test wallet not found exits with wallet not found code."""
        from rtc_balance import WalletNotFoundError
        mock_query.side_effect = [
            {"status": "ok"},  # health check
            {"result": {}},  # balance query - no balance
        ]
        with pytest.raises(WalletNotFoundError) as exc:
            main()
        assert exc.value.exit_code == 4
        assert "not found" in str(exc.value).lower()

    @patch("sys.argv", ["rtc_balance.py", "invalid@wallet"])
    def test_main_invalid_wallet_name(self):
        """Test invalid wallet name exits with usage error."""
        with pytest.raises(UsageError) as exc:
            main()
        assert exc.value.exit_code == 1
        assert "Invalid wallet name" in str(exc.value)


class TestExitCodes:
    """Test that exit codes are properly defined."""

    def test_exit_codes_defined(self):
        assert UsageError.exit_code == 1
        assert NetworkError.exit_code == 2
        assert BadResponseError.exit_code == 3
        assert WalletNotFoundError.exit_code == 4

    def test_exception_messages(self):
        assert str(UsageError("test")) == "test"
        assert str(NetworkError("test")) == "test"
        assert str(BadResponseError("test")) == "test"
        assert str(WalletNotFoundError("test")) == "test"


