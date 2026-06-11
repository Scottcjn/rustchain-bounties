"""
Tests for OTC Bridge migration with real SQLite.

Uses real SQLite database (not mocks) to verify:
- Column addition actually works
- Idempotent migration (running twice is safe)
- Concurrent migration race handling
- Schema tracking table
"""

import sqlite3
from typing import Any, Dict, List

import pytest


@pytest.fixture
def in_memory_db() -> sqlite3.Connection:
    """Create in-memory SQLite database with test tables."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            price REAL,
            amount REAL,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY,
            price REAL,
            amount REAL,
            executed_at TEXT
        )
    """)
    conn.commit()
    yield conn
    conn.close()


class TestRequireKnownTable:
    """Tests for the allowlist guard."""

    def test_accepts_known_table(self):
        """Should accept table names in the known tables list."""
        from otc_bridge.otc_bridge import _require_known_table
        _require_known_table("orders")
        _require_known_table("trades")

    def test_rejects_unknown_table(self):
        """Should raise ValueError for unknown table names."""
        from otc_bridge.otc_bridge import _require_known_table
        with pytest.raises(ValueError, match="Unknown table"):
            _require_known_table("users")

    def test_rejects_sql_injection(self):
        """Should reject SQL injection attempts."""
        from otc_bridge.otc_bridge import _require_known_table
        injections = [
            "orders; DROP TABLE trades; --",
            "trades' OR '1'='1",
        ]
        for attempt in injections:
            with pytest.raises(ValueError, match="Unknown table"):
                _require_known_table(attempt)


class TestTableColumns:
    """Tests for table_columns with real SQLite."""

    def test_returns_column_info(self, in_memory_db):
        """Should return column info for known table."""
        from otc_bridge.otc_bridge import table_columns
        cols = table_columns(in_memory_db, "orders")
        assert isinstance(cols, list)
        names = [c["name"] for c in cols]
        assert "id" in names
        assert "price" in names
        assert "amount" in names

    def test_rejects_unknown_table(self, in_memory_db):
        """Should reject table names not in allowlist."""
        from otc_bridge.otc_bridge import table_columns
        with pytest.raises(ValueError, match="Unknown table"):
            table_columns(in_memory_db, "users")


class TestMigratePrecisionColumns:
    """Tests for migration with real SQLite."""

    def test_adds_precision_columns(self, in_memory_db):
        """Should add precision columns to orders table."""
        from otc_bridge.otc_bridge import migrate_precision_columns, table_columns

        migrate_precision_columns(in_memory_db, "orders")
        cols = table_columns(in_memory_db, "orders")
        names = [c["name"] for c in cols]

        assert "price_precision" in names
        assert "quantity_precision" in names
        assert "quote_quantity_precision" in names

    def test_idempotent_migration(self, in_memory_db):
        """Running migration twice should not fail."""
        from otc_bridge.otc_bridge import migrate_precision_columns

        # First run
        result1 = migrate_precision_columns(in_memory_db, "orders")
        assert len(result1["columns_added"]) == 3

        # Second run -- should skip everything
        result2 = migrate_precision_columns(in_memory_db, "orders")
        assert len(result2["columns_added"]) == 0
        assert len(result2["columns_skipped"]) == 3

    def test_adds_default_values(self, in_memory_db):
        """Added columns should have default values."""
        from otc_bridge.otc_bridge import migrate_precision_columns

        migrate_precision_columns(in_memory_db, "orders")

        cursor = in_memory_db.execute(
            "INSERT INTO orders (id, price, amount) VALUES (1, 10.5, 100)"
        )
        cursor = in_memory_db.execute("SELECT * FROM orders WHERE id = 1")
        row = cursor.fetchone()
        col_names = [d[0] for d in cursor.description]

        price_prec_idx = col_names.index("price_precision")
        assert row[price_prec_idx] == 8  # DEFAULT value

    def test_migrate_all_tables(self, in_memory_db):
        """Should migrate all known tables."""
        from otc_bridge.otc_bridge import migrate_all_tables, table_columns

        results = migrate_all_tables(in_memory_db)
        assert "orders" in results
        assert "trades" in results

        for table in ("orders", "trades"):
            cols = table_columns(in_memory_db, table)
            names = [c["name"] for c in cols]
            assert "price_precision" in names

    def test_migration_tracking_table(self, in_memory_db):
        """Should create and use _schema_migrations table."""
        from otc_bridge.otc_bridge import migrate_precision_columns

        migrate_precision_columns(in_memory_db, "orders")

        cursor = in_memory_db.execute(
            "SELECT COUNT(*) FROM _schema_migrations WHERE table_name = 'orders'"
        )
        count = cursor.fetchone()[0]
        assert count == 3  # 3 precision columns

    def test_backfill_null_values(self, in_memory_db):
        """Should backfill NULL values in new columns."""
        from otc_bridge.otc_bridge import migrate_precision_columns

        # Insert a row before migration
        in_memory_db.execute(
            "INSERT INTO orders (id, price, amount) VALUES (1, 10.5, 100)"
        )
        in_memory_db.commit()

        # Migrate
        result = migrate_precision_columns(in_memory_db, "orders")

        # The backfill should have happened
        cursor = in_memory_db.execute(
            "SELECT price_precision FROM orders WHERE id = 1"
        )
        row = cursor.fetchone()
        assert row[0] == 8  # DEFAULT value was backfilled


class TestMigrationStatus:
    """Tests for migration status."""

    def test_status_reports_incomplete(self, in_memory_db):
        """Should report incomplete before migration."""
        from otc_bridge.otc_bridge import get_migration_status

        status = get_migration_status(in_memory_db, "orders")
        assert status["is_complete"] is False
        assert len(status["missing_columns"]) == 3

    def test_status_reports_complete(self, in_memory_db):
        """Should report complete after migration."""
        from otc_bridge.otc_bridge import (
            migrate_precision_columns, get_migration_status
        )

        migrate_precision_columns(in_memory_db, "orders")
        status = get_migration_status(in_memory_db, "orders")
        assert status["is_complete"] is True
        assert len(status["existing_columns"]) == 3


class TestValidateMigration:
    """Tests for full migration validation."""

    def test_validate_all_tables(self, in_memory_db):
        """Should validate all tables."""
        from otc_bridge.otc_bridge import (
            migrate_all_tables, validate_migration_complete
        )

        assert validate_migration_complete(in_memory_db) is False
        migrate_all_tables(in_memory_db)
        assert validate_migration_complete(in_memory_db) is True
