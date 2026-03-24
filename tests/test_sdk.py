# SPDX-License-Identifier: MIT
"""Unit tests for the RustChain Python SDK."""

import pytest
import json
from unittest.mock import patch, MagicMock
from rustchain_sdk import RustChainClient, AsyncRustChainClient
from rustchain_sdk.exceptions import APIError, ConnectionError, RustChainError
from rustchain_sdk.models import Health, Epoch, Miner, Balance, Block, Transaction


# --- Model Tests ---

class TestModels:
    def test_health_defaults(self):
        h = Health()
        assert h.ok is False
        assert h.version == ""

    def test_health_from_real_data(self):
        h = Health(ok=True, version="2.2.1-rip200", uptime_s=217986.0,
                   db_rw=True, tip_age_slots=0, backup_age_hours=1.2)
        assert h.ok is True
        assert h.version == "2.2.1-rip200"

    def test_epoch_fields(self):
        e = Epoch(epoch=111, slot=16033, blocks_per_epoch=144,
                  enrolled_miners=20, epoch_pot=1.5, total_supply_rtc=8388608)
        assert e.epoch == 111
        assert e.enrolled_miners == 20

    def test_miner_fields(self):
        m = Miner(miner="RTC14f06ee294f327f5685d3de5e1ed501cffab33e7",
                  device_arch="aarch64", device_family="ARM",
                  antiquity_multiplier=0.001)
        assert m.device_arch == "aarch64"
        assert m.antiquity_multiplier == 0.001

    def test_balance_fields(self):
        b = Balance(wallet_id="test-wallet", balance=42.5, pending=0.0)
        assert b.balance == 42.5
        assert b.wallet_id == "test-wallet"

    def test_block_fields(self):
        b = Block(height=1000, hash="abc123", timestamp=1711234567, miner="m1", transactions=3)
        assert b.height == 1000

    def test_transaction_fields(self):
        t = Transaction(txid="tx001", from_wallet="a", to_wallet="b", amount=10.0, timestamp=0)
        assert t.amount == 10.0


# --- Exception Tests ---

class TestExceptions:
    def test_api_error_message(self):
        e = APIError(404, "Not found")
        assert "404" in str(e)
        assert "Not found" in str(e)

    def test_connection_error_is_rustchain_error(self):
        e = ConnectionError("timeout")
        assert isinstance(e, RustChainError)

    def test_api_error_is_rustchain_error(self):
        e = APIError(500, "server error")
        assert isinstance(e, RustChainError)


# --- Client Tests (mocked HTTP) ---

def _mock_urlopen(response_data, status=200):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestClient:
    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_health(self, mock_open):
        mock_open.return_value = _mock_urlopen({"ok": True, "version": "2.2.1-rip200", "uptime_s": 1000, "db_rw": True, "tip_age_slots": 0, "backup_age_hours": 0.5})
        client = RustChainClient("http://localhost:5000")
        h = client.health()
        assert h.ok is True
        assert h.version == "2.2.1-rip200"

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_epoch(self, mock_open):
        mock_open.return_value = _mock_urlopen({"epoch": 111, "slot": 100, "blocks_per_epoch": 144, "enrolled_miners": 20, "epoch_pot": 1.5, "total_supply_rtc": 8388608})
        client = RustChainClient("http://localhost:5000")
        e = client.epoch()
        assert e.epoch == 111

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_miners(self, mock_open):
        mock_open.return_value = _mock_urlopen([{"miner": "m1", "device_arch": "x86", "device_family": "Intel", "hardware_type": "Unknown", "antiquity_multiplier": 1.0, "entropy_score": 0.0, "last_attest": None, "first_attest": None}])
        client = RustChainClient("http://localhost:5000")
        miners = client.miners()
        assert len(miners) == 1
        assert miners[0].miner == "m1"

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_balance(self, mock_open):
        mock_open.return_value = _mock_urlopen({"amount_rtc": 42.5, "amount_i64": 42500000, "miner_id": "test-wallet"})
        client = RustChainClient("http://localhost:5000")
        b = client.balance("test-wallet")
        assert b.balance == 42.5
        assert b.wallet_id == "test-wallet"
        assert b.amount_i64 == 42500000

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_attestation_found(self, mock_open):
        mock_open.return_value = _mock_urlopen([{"miner": "m1", "last_attest": 12345, "antiquity_multiplier": 2.0}])
        client = RustChainClient("http://localhost:5000")
        a = client.attestation_status("m1")
        assert a["last_attest"] == 12345

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_attestation_not_found(self, mock_open):
        mock_open.return_value = _mock_urlopen([{"miner": "other"}])
        client = RustChainClient("http://localhost:5000")
        a = client.attestation_status("m1")
        assert a["status"] == "not_found"

    def test_client_strips_trailing_slash(self):
        c = RustChainClient("http://example.com/")
        assert c.node_url == "http://example.com"


# --- Integration Smoke Test (hits real node if available) ---

class TestIntegrationSmoke:
    @pytest.mark.skipif(True, reason="Set RUSTCHAIN_LIVE=1 to run")
    def test_live_health(self):
        client = RustChainClient()
        h = client.health()
        assert h.ok is True


# --- Import Tests ---

class TestImports:
    def test_package_version(self):
        from rustchain_sdk import __version__
        assert __version__ == "0.1.0"

    def test_all_exports(self):
        from rustchain_sdk import RustChainClient, AsyncRustChainClient
        assert RustChainClient is not None
        assert AsyncRustChainClient is not None

    def test_exceptions_importable(self):
        from rustchain_sdk.exceptions import (
            RustChainError, APIError, WalletNotFoundError,
            InsufficientBalanceError, InvalidSignatureError,
        )
        assert issubclass(APIError, RustChainError)
