"""Tests for attestation schema initialization in fresh database setup.

This module verifies that the attestation-related tables are created during
database initialization, preventing runtime errors when first submitting
attestations.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# SPDX-License-Identifier: MIT
# Copyright (c) RustChain contributors

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from node.db import init_db
from node.db.models import BlockedWallets, IpRateLimit, MinerAttestRecent, MinerMacs

@pytest.fixture
def fresh_db_path():
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield f.name
    os.unlink(f.name)

def test_attestation_tables_created_on_init(fresh_db_path):
    """Verify all attestation tables exist after DB initialization."""
    init_db(fresh_db_path)

    # Check tables exist
    tables = [
        BlockedWallets.__tablename__,
        IpRateLimit.__tablename__,
        MinerAttestRecent.__tablename__,
        MinerMacs.__tablename__
    ]

    from sqlalchemy import inspect
    inspector = inspect(engine_from_db(fresh_db_path))
    existing = {table.name for table in inspector.get_table_names()}

    assert all(table in existing for table in tables), \
        f"Missing tables: {set(tables) - existing}"

def engine_from_db(db_path):
    """Helper to create SQLAlchemy engine from path."""
    from sqlalchemy import create_engine
    return create_engine(f"sqlite:///{db_path}")

def test_attestation_tables_have_correct_columns():
    """Verify schema of attestation tables."""
    inspector = inspect(engine_from_db(":memory:"))
    init_db(":memory:")

    # Test BlockedWallets
    blocked_cols = set(inspector.get_columns(BlockedWallets.__tablename__))
    assert "wallet_address" in blocked_cols
    assert "blocked_until" in blocked_cols

    # Test MinerAttestRecent
    attest_cols = set(inspector.get_columns(MinerAttestRecent.__tablename__))
    assert "nonce" in attest_cols
    assert "miner_id" in attest_cols
    assert "node_peer_id" in attest_cols
    assert "created_at" in attest_cols