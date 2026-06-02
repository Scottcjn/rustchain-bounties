"""
Tests for OTC bridge migration functionality.

Validates security hardening for identifier-injection prevention,
idempotent migration operations, and concurrent migration safety.
"""

import logging
import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from unittest.mock import MagicMock, patch

import pytest

# Configure logging
logger = logging.getLogger(__name__)

# Import the module under test
# Adjust import path based on actual project structure
try:
    from otc_bridge.otc_bridge import (
        _KNOWN_TABLES,
        _require_known_table,
        migrate_precision_columns,
        table_columns,
    )
except ImportError:
    # Fallback for different project structures
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from otc_bridge import (
        _KNOWN_TABLES,
        _require_known_table,
        migrate_precision_columns,
        table_columns,
    )


class TestRequireKnownTable:
    """Tests for the _require_known_table allowlist guard."""

    def test_accepts_known_table(self) -> None:
        """Should accept table names in the known tables list."""
        for table in _KNOWN_TABLES:
            # Should not raise any exception
            _require_known_table(table)
            logger.debug(f"Accepted known table: {table}")

    def test_rejects_unknown_table(self) -> None:
        """Should raise ValueError for unknown table names."""
        with pytest.raises(ValueError, match="Unknown table"):
            _require_known_table("unknown_table")
        logger.info("Rejected unknown table name")

    def test_rejects_sql_injection_attempt(self) -> None:
        """Should reject table names with SQL injection attempts."""
        injection_attempts: List[str] = [
            "orders; DROP TABLE trades; --",
            "trades' OR '1'='1",
            "orders UNION SELECT * FROM users",
            "trades; --",
            "orders/*",
            "trades\"",
            "orders; DELETE FROM trades; --",
            "trades' UNION SELECT * FROM sqlite_master--",
            "orders; UPDATE trades SET amount=0; --",
        ]
        for attempt in injection_attempts:
            with pytest.raises(ValueError, match="Unknown table"):
                _require_known_table(attempt)
            logger.debug(f"Rejected injection attempt: {attempt}")

    def test_rejects_empty_string(self) -> None:
        """Should reject empty table name."""
        with pytest.raises(ValueError, match="Unknown table"):
            _require_known_table("")
        logger.info("Rejected empty string")

    def test_rejects_none(self) -> None:
        """Should reject None as table name."""
        with pytest.raises((ValueError, TypeError)):
            _require_known_table(None)
        logger.info("Rejected None value")

    def test_rejects_non_string(self) -> None:
        """Should reject non-string inputs."""
        non_string_inputs: List[Any] = [
            123,
            45.67,
            True,
            [1, 2, 3],
            {"key": "value"},
            (1, 2),
            object(),
        ]
        for input_value in non_string_inputs:
            with pytest.raises((ValueError, TypeError)):
                _require_known_table(input_value)
            logger.debug(f"Rejected non-string input: {type(input_value).__name__}")


class TestTableColumns:
    """Tests for the table_columns function."""

    @pytest.fixture
    def in_memory_db(self) -> sqlite3.Connection:
        """Create an in-memory SQLite database with test tables."""
        conn: sqlite3.Connection = sqlite3.connect(":memory:")
        cursor: sqlite3.Cursor = conn.cursor()
        
        # Create test tables matching known tables
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
        logger.debug("Created in-memory database with test tables")
        yield conn
        conn.close()
        logger.debug("Closed in-memory database")

    def test_returns_columns_for_known_table(self, in_memory_db: sqlite3.Connection) -> None:
        """Should return column names for a known table."""
        columns: List[str] = table_columns(in_memory_db, "orders")
        assert isinstance(columns, list)
        assert "id" in columns
        assert "price" in columns
        assert "amount" in columns
        assert "created_at" in columns
        logger.info(f"Retrieved columns for orders table: {columns}")

    def test_returns_empty_for_nonexistent_table(self, in_memory_db: sqlite3.Connection) -> None:
        """Should return empty list for nonexistent table."""
        columns: List[str] = table_columns(in_memory_db, "nonexistent")
        assert columns == []
        logger.info("Returned empty list for nonexistent table")

    def test_rejects_unknown_table_name(self, in_memory_db: sqlite3.Connection) -> None:
        """Should reject table names not in allowlist."""
        with pytest.raises(ValueError, match="Unknown table"):
            table_columns(in_memory_db, "users")
        logger.info("Rejected unknown table name")

    def test_rejects_injection_in_table_name(self, in_memory_db: sqlite3.Connection) -> None:
        """Should reject injection attempts in table name."""
        with pytest.raises(ValueError, match="Unknown table"):
            table_columns(in_memory_db, "orders; SELECT * FROM trades")
        logger.info("Rejected injection attempt in table name")

    def test_handles_database_connection_error(self) -> None:
        """Should handle database connection errors gracefully."""
        with pytest.raises(sqlite3.ProgrammingError):
            table_columns(None, "orders")  # type: ignore
        logger.info("Handled database connection error")


class TestMigratePrecisionColumns:
    """Tests for the migrate_precision_columns function."""

    @pytest.fixture
    def in_memory_db(self) -> sqlite3.Connection:
        """Create an in-memory SQLite database with test tables."""
        conn: sqlite3.Connection = sqlite3.connect(":memory:")
        cursor: sqlite3.Cursor = conn.cursor()
        
        # Create orders table without precision columns
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                price REAL,
                amount REAL,
                created_at TEXT
            )
        """)
        
        # Create trades table without precision columns
        cursor.execute("""
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY,
                price REAL,
                amount REAL,
                executed_at TEXT
            )
        """)
        
        conn.commit()
        logger.debug("Created in-memory database with test tables for migration")
        yield conn
        conn.close()
        logger.debug("Closed in-memory database")

    def test_adds_precision_columns_to_orders(self, in_memory_db: sqlite3.Connection) -> None:
        """Should add precision columns to orders table."""
        migrate_precision_columns(in_memory_db, "orders")
        
        columns: List[str] = table_columns(in_memory_db, "orders")
        assert "price_precision" in columns
        assert "amount_precision" in columns
        logger.info("Added precision columns to orders table")

    def test_adds_precision_columns_to_trades(self, in_memory_db: sqlite3.Connection) -> None:
        """Should add precision columns to trades table."""
        migrate_precision_columns(in_memory_db, "trades")
        
        columns: List[str] = table_columns(in_memory_db, "trades")
        assert "price_precision" in columns
        assert "amount_precision" in columns
        logger.info("Added precision columns to trades table")

    def test_idempotent_migration(self, in_memory_db: sqlite3.Connection) -> None:
        """Should be idempotent - running migration twice should not fail."""
        # First migration
        migrate_precision_columns(in_memory_db, "orders")
        
        # Second migration should not raise an error
        migrate_precision_columns(in_memory_db, "orders")
        
        columns: List[str] = table_columns(in_memory_db, "orders")
        assert "price_precision" in columns
        assert "amount_precision" in columns
        logger.info("Migration is idempotent")

    def test_handles_concurrent_migration_race(self, in_memory_db: sqlite3.Connection) -> None:
        """Should handle concurrent migration race condition gracefully."""
        # Simulate concurrent migration by catching duplicate column error
        migrate_precision_columns(in_memory_db, "orders")
        
        # This should not raise an error even if column already exists
        migrate_precision_columns(in_memory_db, "orders")
        
        columns: List[str] = table_columns(in_memory_db, "orders")
        assert "price_precision" in columns
        assert "amount_precision" in columns
        logger.info("Handled concurrent migration race condition")

    def test_rejects_unknown_table(self, in_memory_db: sqlite3.Connection) -> None:
        """Should reject unknown table names."""
        with pytest.raises(ValueError, match="Unknown table"):
            migrate_precision_columns(in_memory_db, "unknown_table")
        logger.info("Rejected unknown table name")

    def test_rejects_injection_in_table_name(self, in_memory_db: sqlite3.Connection) -> None:
        """Should reject injection attempts in table name."""
        with pytest.raises(ValueError, match="Unknown table"):
            migrate_precision_columns(in_memory_db, "orders; DROP TABLE trades; --")
        logger.info("Rejected injection attempt in table name")

    def test_handles_database_connection_error(self) -> None:
        """Should handle database connection errors gracefully."""
        with pytest.raises(sqlite3.ProgrammingError):
            migrate_precision_columns(None, "orders")  # type: ignore
        logger.info("Handled database connection error")

    def test_backfill_existing_rows(self, in_memory_db: sqlite3.Connection) -> None:
        """Should backfill existing rows with default precision values."""
        # Insert some test data
        cursor: sqlite3.Cursor = in_memory_db.cursor()
        cursor.execute("INSERT INTO orders (price, amount) VALUES (100.50, 10.25)")
        cursor.execute("INSERT INTO orders (price, amount) VALUES (200.75, 20.50)")
        in_memory_db.commit()
        
        # Run migration
        migrate_precision_columns(in_memory_db, "orders")
        
        # Verify backfill
        cursor.execute("SELECT price_precision, amount_precision FROM orders")
        rows: List[Tuple[Any, ...]] = cursor.fetchall()
        for row in rows:
            assert row[0] == 0  # Default precision
            assert row[1] == 0  # Default precision
        logger.info("Backfilled existing rows with default precision values")

    def test_preserves_existing_precision_values(self, in_memory_db: sqlite3.Connection) -> None:
        """Should preserve existing precision values during re-migration."""
        # First migration
        migrate_precision_columns(in_memory_db, "orders")
        
        # Set some precision values
        cursor: sqlite3.Cursor = in_memory_db.cursor()
        cursor.execute("UPDATE orders SET price_precision = 2, amount_precision = 4")
        in_memory_db.commit()
        
        # Second migration should preserve existing values
        migrate_precision_columns(in_memory_db, "orders")
        
        cursor.execute("SELECT price_precision, amount_precision FROM orders")
        rows: List[Tuple[Any, ...]] = cursor.fetchall()
        for row in rows:
            assert row[0] == 2  # Preserved
            assert row[1] == 4  # Preserved
        logger.info("Preserved existing precision values during re-migration")


class TestIntegration:
    """Integration tests for the migration system."""

    @pytest.fixture
    def in_memory_db(self) -> sqlite3.Connection:
        """Create an in-memory SQLite database with test tables."""
        conn: sqlite3.Connection = sqlite3.connect(":memory:")
        cursor: sqlite3.Cursor = conn.cursor()
        
        # Create orders table without precision columns
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                price REAL,
                amount REAL,
                created_at TEXT
            )
        """)
        
        # Create trades table without precision columns
        cursor.execute("""
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY,
                price REAL,
                amount REAL,
                executed_at TEXT
            )
        """)
        
        conn.commit()
        logger.debug("Created in-memory database with test tables for integration tests")
        yield conn
        conn.close()
        logger.debug("Closed in-memory database")

    def test_full_migration_workflow(self, in_memory_db: sqlite3.Connection) -> None:
        """Test the complete migration workflow for both tables."""
        # Migrate both tables
        migrate_precision_columns(in_memory_db, "orders")
        migrate_precision_columns(in_memory_db, "trades")
        
        # Verify both tables have precision columns
        orders_columns: List[str] = table_columns(in_memory_db, "orders")
        trades_columns: List[str] = table_columns(in_memory_db, "trades")
        
        assert "price_precision" in orders_columns
        assert "amount_precision" in orders_columns
        assert "price_precision" in trades_columns
        assert "amount_precision" in trades_columns
        
        logger.info("Completed full migration workflow for both tables")

    def test_migration_with_data_integrity(self, in_memory_db: sqlite3.Connection) -> None:
        """Test that migration preserves existing data integrity."""
        # Insert test data
        cursor: sqlite3.Cursor = in_memory_db.cursor()
        cursor.execute("""
            INSERT INTO orders (id, price, amount, created_at) 
            VALUES (1, 100.50, 10.25, '2024-01-01')
        """)
        cursor.execute("""
            INSERT INTO trades (id, price, amount, executed_at) 
            VALUES (1, 200.75, 20.50, '2024-01-02')
        """)
        in_memory_db.commit()
        
        # Run migration
        migrate_precision_columns(in_memory_db, "orders")
        migrate_precision_columns(in_memory_db, "trades")
        
        # Verify data integrity
        cursor.execute("SELECT id, price, amount, created_at FROM orders WHERE id = 1")
        order: Tuple[Any, ...] = cursor.fetchone()
        assert order is not None
        assert order[0] == 1
        assert order[1] == 100.50
        assert order[2] == 10.25
        assert order[3] == '2024-01-01'
        
        cursor.execute("SELECT id, price, amount, executed_at FROM trades WHERE id = 1")
        trade: Tuple[Any, ...] = cursor.fetchone()
        assert trade is not None
        assert trade[0] == 1
        assert trade[1] == 200.75
        assert trade[2] == 20.50
        assert trade[3] == '2024-01-02'
        
        logger.info("Data integrity preserved after migration")

    def test_migration_with_multiple_tables(self, in_memory_db: sqlite3.Connection) -> None:
        """Test migration with multiple tables in sequence."""
        # Migrate tables in different orders
        migrate_precision_columns(in_memory_db, "trades")
        migrate_precision_columns(in_memory_db, "orders")
        
        # Verify both tables have precision columns
        orders_columns: List[str] = table_columns(in_memory_db, "orders")
        trades_columns: List[str] = table_columns(in_memory_db, "trades")
        
        assert "price_precision" in orders_columns
        assert "amount_precision" in orders_columns
        assert "price_precision" in trades_columns
        assert "amount_precision" in trades_columns
        
        logger.info("Migration successful with multiple tables in different order")


class TestEdgeCases:
    """Tests for edge cases in the migration system."""

    def test_empty_database(self) -> None:
        """Test migration on an empty database."""
        conn: sqlite3.Connection = sqlite3.connect(":memory:")
        
        # Create empty tables
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY)")
        cursor.execute("CREATE TABLE trades (id INTEGER PRIMARY KEY)")
        conn.commit()
        
        # Migration should work on empty tables
        migrate_precision_columns(conn, "orders")
        migrate_precision_columns(conn, "trades")
        
        columns: List[str] = table_columns(conn, "orders")
        assert "price_precision" in columns
        assert "amount_precision" in columns
        
        conn.close()
        logger.info("Migration successful on empty database")

    def test_database_with_existing_precision_columns(self) -> None:
        """Test migration on database that already has precision columns."""
        conn: sqlite3.Connection = sqlite3.connect(":memory:")
        
        # Create table with precision columns already present
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                price REAL,
                amount REAL,
                price_precision INTEGER DEFAULT 2,
                amount_precision INTEGER DEFAULT 4
            )
        """)
        conn.commit()
        
        # Migration should not fail
        migrate_precision_columns(conn, "orders")
        
        columns: List[str] = table_columns(conn, "orders")
        assert "price_precision" in columns
        assert "amount_precision" in columns
        
        conn.close()
        logger.info("Migration successful on database with existing precision columns")

    def test_database_with_null_values(self) -> None:
        """Test migration on database with NULL values in precision columns."""
        conn: sql