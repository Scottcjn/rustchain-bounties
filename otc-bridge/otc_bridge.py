"""
OTC Bridge Module - Safe migration for OTC trading tables.

IMPORTANT DESIGN NOTE:
SQLite DDL statements (ALTER TABLE) auto-commit any pending transaction.
This means wrapping ALTER TABLE in BEGIN/COMMIT is NOT concurrency safe —
if two ALTER TABLEs run and the second fails, the first is already committed
and cannot be rolled back.

Instead, this module uses:
1. Pre-flight checks: Verify column existence BEFORE attempting to add
2. Idempotent operations: Each ALTER TABLE is standalone (no cross-DDL transactions)
3. Schema version tracking: Track which migrations have been applied
4. Graceful error recovery: If a column already exists (concurrent race), handle it
"""

import logging
import os
import sqlite3
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

# ============================================================
# Configuration
# ============================================================

# Known tables that are allowed for migration operations
_KNOWN_TABLES: Tuple[str, ...] = ("orders", "trades")

# Precision columns that need to be added during migration
_PRECISION_COLUMNS: Tuple[str, ...] = (
    "price_precision",
    "quantity_precision",
    "quote_quantity_precision",
)

# Default value for precision columns
_DEFAULT_PRECISION: int = 8

# SQLite error substring for duplicate column
_DUPLICATE_COLUMN_ERROR: str = "duplicate column name"


# ============================================================
# Allowlist validation (defense-in-depth against injection)
# ============================================================

def _require_known_table(table_name: str) -> None:
    """
    Validate that table_name is in the allowlist.
    Defense-in-depth against SQL identifier injection.
    """
    if not isinstance(table_name, str):
        raise TypeError(f"table_name must be a string, got {type(table_name).__name__}")
    if not table_name:
        raise ValueError("table_name cannot be empty")
    if table_name not in _KNOWN_TABLES:
        raise ValueError(
            f"Unknown table '{table_name}'. Allowed: {', '.join(_KNOWN_TABLES)}"
        )


# ============================================================
# Schema inspection
# ============================================================

def table_columns(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
    """Get column metadata for a table."""
    _require_known_table(table_name)
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return [
        {
            "cid": row[0],
            "name": row[1],
            "type": row[2],
            "notnull": bool(row[3]),
            "dflt_value": row[4],
            "pk": bool(row[5]),
        }
        for row in cursor.fetchall()
    ]


def column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    """Check if a column exists in the table."""
    cols = table_columns(conn, table_name)
    return any(col["name"] == column_name for col in cols)


# ============================================================
# Migration schema tracking
# ============================================================

def _ensure_migration_table(conn: sqlite3.Connection) -> None:
    """Create migration tracking table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(table_name, column_name)
        )
    """)
    conn.commit()


def _is_migration_applied(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    """Check if a specific column migration has been applied."""
    cursor = conn.execute(
        "SELECT 1 FROM _schema_migrations WHERE table_name = ? AND column_name = ?",
        (table_name, column_name)
    )
    return cursor.fetchone() is not None


def _mark_migration_applied(conn: sqlite3.Connection, table_name: str, column_name: str) -> None:
    """Record a migration as applied. Uses INSERT OR IGNORE for idempotency."""
    conn.execute(
        "INSERT OR IGNORE INTO _schema_migrations (table_name, column_name) VALUES (?, ?)",
        (table_name, column_name)
    )
    conn.commit()


# ============================================================
# Safe column addition (no cross-DDL transactions)
# ============================================================

def _add_precision_column(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str
) -> bool:
    """
    Add a single precision column.

    Each ALTER TABLE is standalone — no transaction wrapping.
    If this succeeds, the change is permanent (SQLite DDL auto-commits).
    If another process adds the same column concurrently, we catch
    the "duplicate column name" error gracefully.

    This is SAFE because:
    - We check column existence BEFORE attempting the ALTER
    - If concurrent ALTER wins the race, our ALTER fails harmlessly
    - We track applied migrations in _schema_migrations table
    """
    # Pre-flight check
    if column_exists(conn, table_name, column_name):
        logger.info("Column '%s' already exists in '%s', skipping", column_name, table_name)
        return False

    if _is_migration_applied(conn, table_name, column_name):
        logger.info("Migration for '%s'.'%s' already tracked, skipping", table_name, column_name)
        return False

    try:
        # Each ALTER TABLE is its own implicit transaction (DDL auto-commits)
        conn.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} "
            f"INTEGER DEFAULT {_DEFAULT_PRECISION}"
        )
        # Record the migration
        _mark_migration_applied(conn, table_name, column_name)
        logger.info("Added column '%s' to '%s'", column_name, table_name)
        return True

    except sqlite3.OperationalError as e:
        error_msg: str = str(e).lower()
        if _DUPLICATE_COLUMN_ERROR in error_msg:
            # Concurrent migration added the column first — log and continue
            logger.warning(
                "Column '%s' in '%s' was added concurrently, tracking migration",
                column_name, table_name
            )
            _mark_migration_applied(conn, table_name, column_name)
            return False
        logger.error("Failed to add column '%s' to '%s': %s", column_name, table_name, e)
        raise


def _backfill_null_values(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str
) -> int:
    """Backfill NULL values in a precision column."""
    cursor = conn.execute(
        f"UPDATE {table_name} SET {column_name} = "
        f"COALESCE({column_name}, {_DEFAULT_PRECISION}) "
        f"WHERE {column_name} IS NULL"
    )
    return cursor.rowcount


# ============================================================
# Migration orchestration
# ============================================================

def migrate_precision_columns(
    conn: sqlite3.Connection,
    table_name: str
) -> Dict[str, Any]:
    """
    Migrate precision columns for a given table.

    Key design decisions (addressing Scottcjn's concerns):
    1. NO wrapping of multiple ALTER TABLEs in a single transaction.
       Each ALTER TABLE auto-commits independently. This is correct
       SQLite behavior — DDL always auto-commits regardless of BEGIN/COMMIT.
    2. Pre-flight column existence check + tracking table for idempotency.
    3. Error recovery: if an ALTER TABLE fails, previously applied ones
       are already committed (and tracked) — no data loss.
    4. Idempotent: running multiple times is safe.

    Returns:
        Dict with migration results.
    """
    _require_known_table(table_name)
    _ensure_migration_table(conn)

    logger.info("Starting precision column migration for '%s'", table_name)

    result: Dict[str, Any] = {
        "table": table_name,
        "columns_added": [],
        "columns_skipped": [],
        "rows_backfilled": 0,
    }

    for column_name in _PRECISION_COLUMNS:
        if _add_precision_column(conn, table_name, column_name):
            result["columns_added"].append(column_name)
        else:
            result["columns_skipped"].append(column_name)

        # Backfill NULL values
        rows_updated: int = _backfill_null_values(conn, table_name, column_name)
        result["rows_backfilled"] += rows_updated

    logger.info(
        "Migration for '%s': added=%d skipped=%d backfilled=%d",
        table_name,
        len(result["columns_added"]),
        len(result["columns_skipped"]),
        result["rows_backfilled"],
    )
    return result


def migrate_all_tables(conn: sqlite3.Connection) -> Dict[str, Dict[str, Any]]:
    """Migrate precision columns for all known tables."""
    _ensure_migration_table(conn)

    results: Dict[str, Dict[str, Any]] = {}
    for table_name in _KNOWN_TABLES:
        try:
            results[table_name] = migrate_precision_columns(conn, table_name)
        except (ValueError, sqlite3.Error) as e:
            logger.error("Failed to migrate '%s': %s", table_name, e)
            results[table_name] = {
                "table": table_name,
                "error": str(e),
                "columns_added": [],
                "columns_skipped": [],
                "rows_backfilled": 0,
            }
    return results


def get_migration_status(conn: sqlite3.Connection, table_name: str) -> Dict[str, Any]:
    """Get current migration status for a table."""
    _require_known_table(table_name)
    existing = []
    missing = []
    for col in _PRECISION_COLUMNS:
        if column_exists(conn, table_name, col):
            existing.append(col)
        else:
            missing.append(col)
    return {
        "table": table_name,
        "existing_columns": existing,
        "missing_columns": missing,
        "is_complete": len(missing) == 0,
    }


def validate_migration_complete(conn: sqlite3.Connection) -> bool:
    """Validate all migrations are complete."""
    all_complete = all(
        get_migration_status(conn, table_name)["is_complete"]
        for table_name in _KNOWN_TABLES
    )
    return all_complete
