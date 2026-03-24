# SPDX-License-Identifier: MIT
"""Unit tests for the RustChain Python SDK."""

import json
import os
from unittest.mock import patch, MagicMock

import pytest

from rustchain_sdk import RustChainClient, AsyncRustChainClient
from rustchain_sdk.exceptions import APIError, ConnectionError, RustChainError
from rustchain_sdk.models import Health, Epoch, Miner, Balance, Block, Transaction


# --- Model Tests ---

class TestModels:
    def test_health_defaults(self):
        assert Health().ok is False

    def test_health_from_real_data(self):
        h = Health(ok=True, version="2.2.1-rip200", uptime_s=217986.0,
                   db_rw=True, tip_age_slots=0, backup_age_hours=1.2)
        assert h.version == "2.2.1-rip200"

    def test_epoch_fields(self):
        assert Epoch(epoch=111, enrolled_miners=20).enrolled_miners == 20

    def test_miner_fields(self):
        assert Miner(device_arch="aarch64").device_arch == "aarch64"

    def test_balance_fields(self):
        b = Balance(wallet_id="w", balance=42.5)
        assert b.balance == 42.5

    def test_block_fields(self):
        assert Block(height=1000).height == 1000

    def test_transaction_fields(self):
        assert Transaction(amount=10.0).amount == 10.0


# --- Exception Tests ---

class TestExceptions:
    def test_api_error_message(self):
        e = APIError(404, "Not found")
        assert "404" in str(e)

    def test_hierarchy(self):
        assert isinstance(ConnectionError("x"), RustChainError)
        assert isinstance(APIError(500, "x"), RustChainError)


# --- Client Tests (mocked) ---

def _mock_urlopen(data):
    m = MagicMock()
    m.read.return_value = json.dumps(data).encode()
    m.__enter__ = lambda s: s
    m.__exit__ = MagicMock(return_value=False)
    return m


class TestClient:
    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_health(self, mock):
        mock.return_value = _mock_urlopen({"ok": True, "version": "2.2.1", "uptime_s": 1000, "db_rw": True, "tip_age_slots": 0, "backup_age_hours": 0.5})
        assert RustChainClient("http://test").health().ok is True

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_epoch(self, mock):
        mock.return_value = _mock_urlopen({"epoch": 111, "slot": 100, "blocks_per_epoch": 144, "enrolled_miners": 20, "epoch_pot": 1.5, "total_supply_rtc": 8388608})
        assert RustChainClient("http://test").epoch().epoch == 111

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_miners(self, mock):
        mock.return_value = _mock_urlopen([{"miner": "m1", "device_arch": "x86", "device_family": "Intel", "hardware_type": "Unknown", "antiquity_multiplier": 1.0, "entropy_score": 0.0}])
        assert len(RustChainClient("http://test").miners()) == 1

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_balance(self, mock):
        mock.return_value = _mock_urlopen({"amount_rtc": 42.5, "amount_i64": 42500000, "miner_id": "w"})
        b = RustChainClient("http://test").balance("w")
        assert b.balance == 42.5
        assert b.amount_i64 == 42500000

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_attestation_found(self, mock):
        mock.return_value = _mock_urlopen([{"miner": "m1", "last_attest": 12345, "antiquity_multiplier": 2.0}])
        assert RustChainClient("http://test").attestation_status("m1")["last_attest"] == 12345

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_attestation_not_found(self, mock):
        mock.return_value = _mock_urlopen([{"miner": "other"}])
        assert RustChainClient("http://test").attestation_status("m1")["status"] == "not_found"

    def test_trailing_slash(self):
        assert RustChainClient("http://x/").node_url == "http://x"

    @patch("rustchain_sdk.client.urllib.request.urlopen")
    def test_explorer_blocks(self, mock):
        mock.return_value = _mock_urlopen([{"height": 1, "hash": "a", "timestamp": 0, "miner": "m", "transactions": 0}])
        c = RustChainClient("http://test")
        assert len(c.explorer.blocks()) == 1

    def test_verify_ssl_default_true(self):
        c = RustChainClient("http://test")
        assert c._ctx is None  # no override = default SSL


# --- Async Tests ---

class TestAsyncClient:
    def test_requires_context_manager(self):
        """Async client should raise if used without 'async with'."""
        import asyncio
        async def _run():
            c = AsyncRustChainClient("http://test")
            with pytest.raises(Exception):
                await c.health()
        asyncio.get_event_loop().run_until_complete(_run())


# --- Integration Smoke ---

class TestIntegration:
    @pytest.mark.skipif(os.getenv("RUSTCHAIN_LIVE") != "1", reason="Set RUSTCHAIN_LIVE=1")
    def test_live_health(self):
        assert RustChainClient(verify_ssl=False).health().ok is True


# --- Import Tests ---

class TestImports:
    def test_version(self):
        from rustchain_sdk import __version__
        assert __version__ == "0.1.0"

    def test_exports(self):
        from rustchain_sdk import RustChainClient, AsyncRustChainClient
        assert RustChainClient is not None
