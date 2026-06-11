"""
Tests for OTC Bridge payout idempotency using real SQLite.

Uses real database, not mocks — ensures double-spend prevention actually works.
"""

import json
import os
import sqlite3
import tempfile
from typing import Dict, Any

import pytest


@pytest.fixture
def db_path() -> str:
    """Create a temporary database for each test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def store(db_path: str):
    """Create a PayoutStore with temporary DB."""
    from otc_bridge.otc_bridge import PayoutStore
    store = PayoutStore(db_path)
    yield store


class TestPayoutStore:
    """Test SQLite-backed payout store with double-spend prevention."""

    def test_create_and_find(self, store):
        """Should create and retrieve a payout record."""
        record = store.create_payout(
            "test_key_1", "order_1", "addr_a", "addr_b", "100.50"
        )
        assert record is not None
        assert record["idempotency_key"] == "test_key_1"
        assert record["status"] == "pending"

        found = store.find_by_idempotency_key("test_key_1")
        assert found is not None
        assert found["order_id"] == "order_1"

    def test_unique_constraint_prevents_double_spend(self, store):
        """UNIQUE constraint should prevent creating duplicate payouts."""
        store.create_payout("dup_key", "order_1", "addr_a", "addr_b", "100")

        # Second attempt with same key should return the existing record
        # and NOT create a duplicate
        conn = sqlite3.connect(store._db_path)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM payouts WHERE idempotency_key = ?",
            ("dup_key",)
        )
        count_before = cursor.fetchone()[0]
        assert count_before == 1

        result = store.create_payout(
            "dup_key", "order_2", "addr_c", "addr_d", "200"
        )
        assert result is not None
        assert result.get("_duplicate") is True

        cursor = conn.execute(
            "SELECT COUNT(*) FROM payouts WHERE idempotency_key = ?",
            ("dup_key",)
        )
        count_after = cursor.fetchone()[0]
        assert count_after == 1, "Duplicate was created -- double-spend possible!"

    def test_update_status(self, store):
        """Should update payout status atomically."""
        store.create_payout("key_update", "order_1", "a", "b", "50")
        store.update_status("key_update", "completed", "0xabc123")
        record = store.find_by_idempotency_key("key_update")
        assert record["status"] == "completed"
        assert record["tx_hash"] == "0xabc123"

    def test_update_status_without_tx(self, store):
        """Should update status without requiring tx_hash."""
        store.create_payout("key_no_tx", "order_1", "a", "b", "50")
        store.update_status("key_no_tx", "failed")
        record = store.find_by_idempotency_key("key_no_tx")
        assert record["status"] == "failed"

    def test_find_nonexistent(self, store):
        """Should return None for non-existent idempotency key."""
        result = store.find_by_idempotency_key("nonexistent_key")
        assert result is None

    def test_multiple_payouts_different_keys(self, store):
        """Multiple payouts with different keys should all succeed."""
        for i in range(5):
            record = store.create_payout(
                f"key_{i}", f"order_{i}", f"addr_a", f"addr_b", f"{i * 10}"
            )
            assert record is not None
            assert record["idempotency_key"] == f"key_{i}"

        conn = sqlite3.connect(store._db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM payouts")
        assert cursor.fetchone()[0] == 5


class TestIdempotencyKeyDerivation:
    """Test idempotency key derivation is deterministic."""

    def test_deterministic_key(self):
        """Same inputs should produce same key."""
        from otc_bridge.otc_bridge import derive_idempotency_key
        key1 = derive_idempotency_key("order_1", "addr_a", "addr_b", "100")
        key2 = derive_idempotency_key("order_1", "addr_a", "addr_b", "100")
        assert key1 == key2
        assert len(key1) == 64  # SHA-256 hex

    def test_different_inputs_different_keys(self):
        """Different inputs should produce different keys."""
        from otc_bridge.otc_bridge import derive_idempotency_key
        key1 = derive_idempotency_key("order_1", "a", "b", "100")
        key2 = derive_idempotency_key("order_1", "a", "b", "101")
        assert key1 != key2


class TestPayoutValidation:
    """Test payout request validation."""

    def test_valid_request(self):
        """Valid request should return no errors."""
        from otc_bridge.otc_bridge import validate_payout_request
        data = {
            "order_id": "order_1",
            "from_address": "0xabc123",
            "to_address": "0xdef456",
            "amount": "100.50"
        }
        errors = validate_payout_request(data)
        assert errors == []

    def test_missing_fields(self):
        """Missing required fields should return errors."""
        from otc_bridge.otc_bridge import validate_payout_request
        errors = validate_payout_request({})
        assert len(errors) >= 3

    def test_invalid_amount(self):
        """Invalid amount format should return error."""
        from otc_bridge.otc_bridge import validate_payout_request
        data = {
            "order_id": "1", "from_address": "a",
            "to_address": "b", "amount": "not_a_number"
        }
        errors = validate_payout_request(data)
        assert len(errors) >= 1
