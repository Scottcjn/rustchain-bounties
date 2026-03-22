"""
Tests for rustchain.models — dataclass construction and from_dict parsing.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from rustchain.models import (
    AttestationStatus,
    Balance,
    Block,
    EpochInfo,
    HealthStatus,
    Miner,
    Transaction,
    TransferResult,
    _parse_timestamp,
)


# -------------------------------------------------------------------
# Timestamp parser
# -------------------------------------------------------------------


class TestParseTimestamp:
    def test_iso_with_z(self):
        ts = _parse_timestamp("2026-03-22T12:00:00Z")
        assert ts is not None
        assert ts.year == 2026
        assert ts.month == 3
        assert ts.hour == 12

    def test_iso_with_millis(self):
        ts = _parse_timestamp("2026-03-22T12:00:00.123456Z")
        assert ts is not None
        assert ts.year == 2026

    def test_epoch_int(self):
        ts = _parse_timestamp(1711108800)
        assert ts is not None
        assert isinstance(ts, datetime)

    def test_epoch_float(self):
        ts = _parse_timestamp(1711108800.5)
        assert ts is not None

    def test_none_returns_none(self):
        assert _parse_timestamp(None) is None

    def test_invalid_string_returns_none(self):
        assert _parse_timestamp("not-a-date") is None

    def test_datetime_passthrough(self):
        dt = datetime(2026, 3, 22, 12, 0, 0)
        assert _parse_timestamp(dt) is dt


# -------------------------------------------------------------------
# HealthStatus
# -------------------------------------------------------------------


class TestHealthStatus:
    def test_from_dict_full(self):
        h = HealthStatus.from_dict({
            "status": "ok",
            "version": "0.9.4",
            "uptime": 3600.0,
            "block_height": 100,
            "peers": 5,
            "syncing": False,
            "timestamp": "2026-03-22T12:00:00Z",
        })
        assert h.status == "ok"
        assert h.version == "0.9.4"
        assert h.uptime == 3600.0
        assert h.block_height == 100
        assert h.peers == 5
        assert h.syncing is False

    def test_from_dict_minimal(self):
        h = HealthStatus.from_dict({"status": "ok"})
        assert h.status == "ok"
        assert h.version == ""
        assert h.block_height == 0

    def test_from_dict_camelcase_keys(self):
        h = HealthStatus.from_dict({"status": "ok", "blockHeight": 999})
        assert h.block_height == 999

    def test_frozen(self):
        h = HealthStatus.from_dict({"status": "ok"})
        with pytest.raises(AttributeError):
            h.status = "bad"  # type: ignore[misc]


# -------------------------------------------------------------------
# EpochInfo
# -------------------------------------------------------------------


class TestEpochInfo:
    def test_from_dict(self):
        e = EpochInfo.from_dict({
            "epoch": 47,
            "start_block": 140000,
            "end_block": 145000,
            "current_block": 142857,
            "progress": 0.57,
            "difficulty": 123.45,
        })
        assert e.epoch == 47
        assert e.start_block == 140000
        assert e.progress == 0.57

    def test_camelcase_fallback(self):
        e = EpochInfo.from_dict({"current_epoch": 10, "startBlock": 100, "endBlock": 200})
        assert e.epoch == 10
        assert e.start_block == 100


# -------------------------------------------------------------------
# Miner
# -------------------------------------------------------------------


class TestMiner:
    def test_from_dict(self):
        m = Miner.from_dict({
            "miner_id": "m1",
            "wallet_id": "w1",
            "hardware": "POWER8",
            "status": "active",
            "hashrate": 42.0,
            "blocks_mined": 10,
        })
        assert m.miner_id == "m1"
        assert m.hardware == "POWER8"
        assert m.hashrate == 42.0

    def test_fallback_keys(self):
        m = Miner.from_dict({"minerId": "m2", "walletId": "w2", "hw_type": "C64"})
        assert m.miner_id == "m2"
        assert m.hardware == "C64"


# -------------------------------------------------------------------
# Balance
# -------------------------------------------------------------------


class TestBalance:
    def test_from_dict(self):
        b = Balance.from_dict({
            "wallet_id": "w1",
            "balance": 1000.0,
            "available": 800.0,
            "locked": 150.0,
            "pending": 50.0,
        })
        assert b.wallet_id == "w1"
        assert b.balance == 1000.0
        assert b.available == 800.0

    def test_wallet_id_fallback(self):
        b = Balance.from_dict({"balance": 500.0}, wallet_id="override")
        assert b.wallet_id == "override"
        assert b.available == 500.0  # defaults to balance


# -------------------------------------------------------------------
# TransferResult
# -------------------------------------------------------------------


class TestTransferResult:
    def test_from_dict(self):
        t = TransferResult.from_dict({
            "tx_hash": "0xabc",
            "status": "confirmed",
            "from": "w1",
            "to": "w2",
            "amount": 100.0,
            "fee": 0.001,
            "confirmations": 6,
        })
        assert t.tx_hash == "0xabc"
        assert t.status == "confirmed"
        assert t.from_wallet == "w1"
        assert t.amount == 100.0


# -------------------------------------------------------------------
# AttestationStatus
# -------------------------------------------------------------------


class TestAttestationStatus:
    def test_from_dict(self):
        a = AttestationStatus.from_dict({
            "miner_id": "m1",
            "valid": True,
            "hardware": "POWER8",
            "attestation_epoch": 47,
            "expires_epoch": 50,
            "score": 98.5,
        })
        assert a.valid is True
        assert a.score == 98.5

    def test_miner_id_override(self):
        a = AttestationStatus.from_dict({"valid": False}, miner_id="forced")
        assert a.miner_id == "forced"


# -------------------------------------------------------------------
# Block & Transaction
# -------------------------------------------------------------------


class TestTransaction:
    def test_from_dict(self):
        t = Transaction.from_dict({
            "hash": "0xtx",
            "from": "a",
            "to": "b",
            "amount": 25.0,
            "fee": 0.001,
            "block_height": 100,
        })
        assert t.tx_hash == "0xtx"
        assert t.from_wallet == "a"
        assert t.amount == 25.0


class TestBlock:
    def test_from_dict_with_transactions(self):
        b = Block.from_dict({
            "height": 100,
            "hash": "0xblock",
            "previous_hash": "0xprev",
            "miner": "m1",
            "transactions": [
                {"hash": "0xtx1", "from": "a", "to": "b", "amount": 10.0},
                {"hash": "0xtx2", "from": "c", "to": "d", "amount": 20.0},
            ],
            "size": 2048,
            "difficulty": 1000.0,
            "nonce": 42,
            "epoch": 5,
        })
        assert b.height == 100
        assert b.block_hash == "0xblock"
        assert len(b.transactions) == 2
        assert b.transactions[0].tx_hash == "0xtx1"
        assert b.tx_count == 2

    def test_from_dict_empty_transactions(self):
        b = Block.from_dict({"height": 50, "hash": "0xempty"})
        assert len(b.transactions) == 0
        assert b.tx_count == 0
