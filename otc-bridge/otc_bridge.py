"""
OTC Bridge Module - Main migration logic for OTC trading tables.

This module provides functionality to migrate precision columns in OTC trading
tables (orders and trades) with security hardening against identifier injection.
"""

import logging
import sqlite3
from typing import Dict, List, Optional, Tuple, Any, Set, Union

# Configure module logger
logger = logging.getLogger(__name__)

# Known tables that are allowed for migration operations
_KNOWN_TABLES: Tuple[str, ...] = ("orders", "trades")

# Precision columns that need to be added during migration
_PRECISION_COLUMNS: Tuple[str, ...] = (
    "price_precision",
    "quantity_precision",
    "quote_quantity_precision",
)

# Default value for precision columns
_DEFAULT_PRECISION: int = 0

# SQLite error message for duplicate column
_DUPLICATE_COLUMN_ERROR: str = "duplicate column name"


def _require_known_table(table_name: str) -> None:
    """
    Validate that the table_name is in the allowlist of known tables.
    
    This function provides defense-in-depth against identifier injection attacks
    by ensuring only whitelisted table names can be used in SQL operations.
    
    Args:
        table_name: The name of the table to validate.
        
    Raises:
        ValueError: If table_name is not in _KNOWN_TABLES.
        TypeError: If table_name is not a string.
    """
    if not isinstance(table_name, str):
        raise TypeError(f"table_name must be a string, got {type(table_name).__name__}")
    
    if not table_name:
        raise ValueError("table_name cannot be empty")
    
    if table_name not in _KNOWN_TABLES:
        raise ValueError(
            f"Unknown table '{table_name}'. Allowed tables: {', '.join(_KNOWN_TABLES)}"
        )
    
    logger.debug(f"Table '{table_name}' validated against known tables allowlist")


def _validate_connection(conn: sqlite3.Connection) -> None:
    """
    Validate that the database connection is valid and open.
    
    Args:
        conn: Database connection to validate.
        
    Raises:
        TypeError: If conn is not a sqlite3.Connection.
        sqlite3.Error: If the connection is closed or invalid.
    """
    if not isinstance(conn, sqlite3.Connection):
        raise TypeError(f"Expected sqlite3.Connection, got {type(conn).__name__}")
    
    try:
        # Test if connection is alive
        conn.execute("SELECT 1")
    except sqlite3.Error as e:
        logger.error(f"Database connection validation failed: {e}")
        raise


def table_columns(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
    """
    Get column information for a given table.
    
    Retrieves detailed column metadata including column ID, name, type,
    not-null constraint, default value, and primary key status.
    
    Args:
        conn: Database connection.
        table_name: Name of the table to inspect.
        
    Returns:
        List of dictionaries containing column information with keys:
        - cid: Column ID
        - name: Column name
        - type: Column data type
        - notnull: Not-null constraint flag
        - dflt_value: Default value
        - pk: Primary key flag
        
    Raises:
        TypeError: If conn is not a sqlite3.Connection or table_name is not a string.
        ValueError: If table_name is not in the known tables allowlist.
        sqlite3.Error: If there's a database error.
    """
    _validate_connection(conn)
    _require_known_table(table_name)
    
    logger.info(f"Retrieving column information for table '{table_name}'")
    
    try:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns: List[Dict[str, Any]] = []
        for row in cursor.fetchall():
            column_info: Dict[str, Any] = {
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": bool(row[3]),
                "dflt_value": row[4],
                "pk": bool(row[5]),
            }
            columns.append(column_info)
        
        logger.debug(f"Found {len(columns)} columns in table '{table_name}'")
        return columns
        
    except sqlite3.Error as e:
        logger.error(f"Failed to get column info for table '{table_name}': {e}")
        raise


def _column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    """
    Check if a column exists in the specified table.
    
    Performs a case-sensitive comparison of column names to ensure accurate
    detection of existing columns.
    
    Args:
        conn: Database connection.
        table_name: Name of the table.
        column_name: Name of the column to check.
        
    Returns:
        True if the column exists, False otherwise.
        
    Raises:
        TypeError: If any argument has invalid type.
        ValueError: If table_name is not in the known tables allowlist.
        sqlite3.Error: If there's a database error.
    """
    if not isinstance(column_name, str):
        raise TypeError(f"column_name must be a string, got {type(column_name).__name__}")
    
    if not column_name:
        raise ValueError("column_name cannot be empty")
    
    columns = table_columns(conn, table_name)
    exists = any(col["name"] == column_name for col in columns)
    
    logger.debug(f"Column '{column_name}' in table '{table_name}': {'exists' if exists else 'does not exist'}")
    return exists


def _add_precision_column(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str
) -> bool:
    """
    Add a single precision column to the specified table.
    
    Handles concurrent migration races by catching duplicate column errors.
    
    Args:
        conn: Database connection.
        table_name: Name of the table.
        column_name: Name of the column to add.
        
    Returns:
        True if column was added, False if it already existed.
        
    Raises:
        sqlite3.Error: If there's a database error other than duplicate column.
    """
    if _column_exists(conn, table_name, column_name):
        logger.info(f"Column '{column_name}' already exists in table '{table_name}', skipping")
        return False
    
    try:
        conn.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} "
            f"INTEGER DEFAULT {_DEFAULT_PRECISION}"
        )
        logger.info(f"Added column '{column_name}' to table '{table_name}'")
        return True
        
    except sqlite3.OperationalError as e:
        error_msg: str = str(e).lower()
        if _DUPLICATE_COLUMN_ERROR in error_msg:
            # Column was added by another process in concurrent migration
            logger.warning(
                f"Column '{column_name}' in table '{table_name}' was added "
                f"by concurrent migration, skipping"
            )
            return False
        logger.error(f"Failed to add column '{column_name}' to table '{table_name}': {e}")
        raise


def _backfill_null_values(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str
) -> int:
    """
    Backfill NULL values in a precision column with the default value.
    
    Uses COALESCE for idempotent convergence on re-runs.
    
    Args:
        conn: Database connection.
        table_name: Name of the table.
        column_name: Name of the column to backfill.
        
    Returns:
        Number of rows updated.
        
    Raises:
        sqlite3.Error: If there's a database error.
    """
    try:
        cursor = conn.execute(
            f"UPDATE {table_name} SET {column_name} = "
            f"COALESCE({column_name}, {_DEFAULT_PRECISION}) "
            f"WHERE {column_name} IS NULL"
        )
        updated_rows: int = cursor.rowcount
        if updated_rows > 0:
            logger.info(
                f"Backfilled {updated_rows} NULL values in column "
                f"'{column_name}' of table '{table_name}'"
            )
        return updated_rows
        
    except sqlite3.Error as e:
        logger.error(
            f"Failed to backfill NULL values in column "
            f"'{column_name}' of table '{table_name}': {e}"
        )
        raise


def migrate_precision_columns(
    conn: sqlite3.Connection,
    table_name: str
) -> Dict[str, Any]:
    """
    Migrate precision columns for a given table.
    
    Adds missing precision columns and backfills NULL values.
    This function is idempotent and safe for concurrent execution.
    
    Args:
        conn: Database connection.
        table_name: Name of the table to migrate.
        
    Returns:
        Dictionary containing migration results:
        - table: Table name
        - columns_added: List of columns that were added
        - columns_skipped: List of columns that already existed
        - rows_backfilled: Total number of rows backfilled
        
    Raises:
        TypeError: If conn is not a sqlite3.Connection or table_name is not a string.
        ValueError: If table_name is not in the known tables allowlist.
        sqlite3.Error: If there's a database error.
    """
    _validate_connection(conn)
    _require_known_table(table_name)
    
    logger.info(f"Starting precision column migration for table '{table_name}'")
    
    result: Dict[str, Any] = {
        "table": table_name,
        "columns_added": [],
        "columns_skipped": [],
        "rows_backfilled": 0,
    }
    
    try:
        # Begin transaction for atomicity
        conn.execute("BEGIN TRANSACTION")
        
        for column_name in _PRECISION_COLUMNS:
            if _add_precision_column(conn, table_name, column_name):
                result["columns_added"].append(column_name)
            else:
                result["columns_skipped"].append(column_name)
            
            # Backfill NULL values for each column
            rows_updated: int = _backfill_null_values(conn, table_name, column_name)
            result["rows_backfilled"] += rows_updated
        
        # Commit the transaction
        conn.execute("COMMIT")
        
        logger.info(
            f"Migration completed for table '{table_name}': "
            f"added {len(result['columns_added'])} columns, "
            f"skipped {len(result['columns_skipped'])} columns, "
            f"backfilled {result['rows_backfilled']} rows"
        )
        
        return result
        
    except sqlite3.Error as e:
        # Rollback on error
        conn.execute("ROLLBACK")
        logger.error(
            f"Migration failed for table '{table_name}': {e}"
        )
        raise


def migrate_all_tables(
    conn: sqlite3.Connection
) -> Dict[str, Dict[str, Any]]:
    """
    Migrate precision columns for all known tables.
    
    Performs migration on all tables in the _KNOWN_TABLES allowlist.
    
    Args:
        conn: Database connection.
        
    Returns:
        Dictionary mapping table names to their migration results.
        
    Raises:
        TypeError: If conn is not a sqlite3.Connection.
        sqlite3.Error: If there's a database error.
    """
    _validate_connection(conn)
    
    logger.info("Starting migration for all known tables")
    
    results: Dict[str, Dict[str, Any]] = {}
    
    for table_name in _KNOWN_TABLES:
        try:
            result: Dict[str, Any] = migrate_precision_columns(conn, table_name)
            results[table_name] = result
        except (ValueError, sqlite3.Error) as e:
            logger.error(f"Failed to migrate table '{table_name}': {e}")
            results[table_name] = {
                "table": table_name,
                "error": str(e),
                "columns_added": [],
                "columns_skipped": [],
                "rows_backfilled": 0,
            }
    
    logger.info(f"Migration completed for {len(results)} tables")
    return results


def get_migration_status(
    conn: sqlite3.Connection,
    table_name: str
) -> Dict[str, Any]:
    """
    Get the current migration status for a given table.
    
    Checks which precision columns exist and which are missing.
    
    Args:
        conn: Database connection.
        table_name: Name of the table to check.
        
    Returns:
        Dictionary containing migration status:
        - table: Table name
        - existing_columns: List of precision columns that exist
        - missing_columns: List of precision columns that are missing
        - is_complete: True if all precision columns exist
        
    Raises:
        TypeError: If conn is not a sqlite3.Connection or table_name is not a string.
        ValueError: If table_name is not in the known tables allowlist.
        sqlite3.Error: If there's a database error.
    """
    _validate_connection(conn)
    _require_known_table(table_name)
    
    logger.info(f"Checking migration status for table '{table_name}'")
    
    try:
        existing_columns: List[str] = []
        missing_columns: List[str] = []
        
        for column_name in _PRECISION_COLUMNS:
            if _column_exists(conn, table_name, column_name):
                existing_columns.append(column_name)
            else:
                missing_columns.append(column_name)
        
        status: Dict[str, Any] = {
            "table": table_name,
            "existing_columns": existing_columns,
            "missing_columns": missing_columns,
            "is_complete": len(missing_columns) == 0,
        }
        
        logger.info(
            f"Migration status for table '{table_name}': "
            f"{len(existing_columns)} columns exist, "
            f"{len(missing_columns)} columns missing"
        )
        
        return status
        
    except sqlite3.Error as e:
        logger.error(f"Failed to get migration status for table '{table_name}': {e}")
        raise


def validate_migration_complete(
    conn: sqlite3.Connection
) -> bool:
    """
    Validate that all migrations are complete for all known tables.
    
    Checks if all precision columns exist in all known tables.
    
    Args:
        conn: Database connection.
        
    Returns:
        True if all migrations are complete, False otherwise.
        
    Raises:
        TypeError: If conn is not a sqlite3.Connection.
        sqlite3.Error: If there's a database error.
    """
    _validate_connection(conn)
    
    logger.info("Validating migration completion for all tables")
    
    try:
        all_complete: bool = True
        
        for table_name in _KNOWN_TABLES:
            status: Dict[str, Any] = get_migration_status(conn, table_name)
            if not status["is_complete"]:
                logger.warning(
                    f"Migration incomplete for table '{table_name}': "
                    f"missing columns: {status['missing_columns']}"
                )
                all_complete = False
        
        if all_complete:
            logger.info("All migrations are complete")
        else:
            logger.warning("Some migrations are incomplete")
        
        return all_complete
        
    except sqlite3.Error as e:
        logger.error(f"Failed to validate migration completion: {e}")
        raise