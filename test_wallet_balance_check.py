import json
import pytest
import sys
from unittest.mock import patch, MagicMock
import urllib.request
import urllib.error

import wallet_balance_check as wbc


# ── Fixtures ─────────────────────────────────────────────────────────────────

def _mock_response(status: int, body: dict) -> MagicMock:
    """Return a context-manager-like mock of urllib.request.urlopen()."""
    resp = MagicMock()
    resp.status = status
    resp.read.return_value = json.dumps(body).encode("utf-8")
    resp.__enter__ = lambda s: resp
    resp.__exit__ = lambda s, *a: None
    return resp


def _mock_urlopen_side_effect(*args, **kwargs):
    """Helper to build a side-effect callable for patching urlopen."""
    def _inner(req, timeout=None):
        # Simulate the real request shape loosely enough for our tests
        return _mock_response(200, {"result": "0x10"})
    return _inner


# ── Happy path ───────────────────────────────────────────────────────────────

class TestHappyPath:
    def test_returns_balance_on_200_ok(self):
        req, _ = None, None
        with patch("wallet_balance_check.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = _mock_response(
                200, {"jsonrpc": "2.0", "result": "0x10", "id": 1}
            )
            balance = wbc.get_wallet_balance(
                "0xDEADbEEF", "http://localhost:8545"
            )
        assert balance == "0x10"
        assert mock_urlopen.call_count == 1


# ── NetworkError (exit code 2) ───────────────────────────────────────────────

class TestNetworkError:
    def test_url_error_raises_network_error(self):
        with patch(
            "wallet_balance_check.urllib.request.urlopen",
            side_effect=urllib.error.URLError("Connection refused"),
        ):
            with pytest.raises(wbc.NetworkError, match="Network error"):
                wbc.get_wallet_balance("0xABC", "http://localhost:9999")

    def test_exit_code_2_on_network_error(self, capsys):
        with patch(
            "wallet_balance_check.urllib.request.urlopen",
            side_effect=urllib.error.URLError("timed out"),
        ):
            code = wbc.main()
        assert code == 2
        captured = capsys.readouterr()
        assert "error: network failure" in captured.err


# ── ResponseError (exit code 3) ──────────────────────────────────────────────

class TestResponseError:
    def test_non_200_status_raises_response_error(self):
        with patch(
            "wallet_balance_check.urllib.request.urlopen"
        ) as mock_open:
            mock_open.return_value = _mock_response(500, {})
            with pytest.raises(wbc.ResponseError, match="HTTP 500"):
                wbc.get_wallet_balance("0xABC", "http://localhost:8545")

    def test_malformed_json_raises_response_error(self):
        resp = MagicMock()
        resp.status = 200
        resp.read.return_value = b"not-json"
        resp.__enter__ = lambda s: resp
        resp.__exit__ = lambda s, *a: None

        with patch(
            "wallet_balance_check.urllib.request.urlopen",
            return_value=resp,
        ):
            with pytest.raises(wbc.ResponseError, match="Malformed JSON"):
                wbc.get_wallet_balance("0xABC", "http://localhost:8545")

    def test_rpc_error_in_response_raises_response_error(self):
        with patch(
            "wallet_balance_check.urllib.request.urlopen"
        ) as mock_open:
            mock_open.return_value = _mock_response(
                200, {"jsonrpc": "2.0", "error": {"code": -32000, "message": "account not found"}, "id": 1}
            )
            with pytest.raises(wbc.ResponseError, match="RPC error"):
                wbc.get_wallet_balance("0xABC", "http://localhost:8545")

    def test_exit_code_3_on_response_error(self, capsys):
        with patch(
            "wallet_balance_check.urllib.request.urlopen"
        ) as mock_open:
            mock_open.return_value = _mock_response(502, {})
            code = wbc.main()
        assert code == 3
        captured = capsys.readouterr()
        assert "error: bad response" in captured.err


# ── WalletError (exit code 1) ────────────────────────────────────────────────

class TestWalletError:
    def test_null_result_raises_wallet_error(self):
        with patch(
            "wallet_balance_check.urllib.request.urlopen"
        ) as mock_open:
            mock_open.return_value = _mock_response(
                200, {"jsonrpc": "2.0", "result": None, "id": 1}
            )
            with pytest.raises(wbc.WalletError, match="Unknown wallet"):
                wbc.get_wallet_balance("0xUNKNOWN", "http://localhost:8545")

    def test_exit_code_1_on_wallet_error(self, capsys):
        with patch(
            "wallet_balance_check.urllib.request.urlopen"
        ) as mock_open:
            mock_open.return_value = _mock_response(
                200, {"jsonrpc": "2.0", "result": None, "id": 1}
            )
            code = wbc.main()
        assert code == 1
        captured = capsys.readouterr()
        assert "error:" in captured.err


# ── Usage / argparse ─────────────────────────────────────────────────────────

class TestUsage:
    def test_missing_args_exits_nonzero(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["wallet_balance_check.py"])
        code = wbc.main()
        assert code == 2  # argparse exits with code 2 on bad input
        captured = capsys.readouterr()
        assert "usage:" in captured.err.lower()

    def test_help_flag_exits_zero(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["wallet_balance_check.py", "--help"])
        with pytest.raises(SystemExit) as exc:
            wbc.main()
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "Exit codes" in captured.out
