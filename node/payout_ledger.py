"""Payout ledger operations for RustChain."""

import json
import sqlite3
from typing import Any, TypedDict


class LedgerEntry(TypedDict):
    """Typed definition for a ledger entry row."""

    block_height: int
    miner_id: str
    amount: int
    tx_hash: str
    timestamp: int


def _get_columns(entries: list[dict[str, Any]]) -> list[str]:
    """Extract column names from the first ledger entry dictionary.

    Args:
        entries: A list of dictionaries representing ledger entries.

    Returns:
        A list of unique column names from the entries.
    """
    if not entries:
        return []
    return list(entries[0].keys())


def _select_columns_sql(columns: list[str]) -> str:
    """Generate a SQL SELECT clause string from a list of column names.

    Args:
        columns: List of column names to include in the SELECT clause.

    Returns:
        A formatted SQL string selecting the specified columns.
    """
    return ", ".join(f'"{col}"' for col in columns)


def _json_object_body(entries: list[dict[str, Any]]) -> str:
    """Convert a list of ledger entries to a JSON object body string.

    Serializes each entry dictionary to JSON format for use in API responses.

    Args:
        entries: List of dictionaries representing ledger entries.

    Returns:
        A JSON-formatted string of the entries array.
    """
    return json.dumps(entries, default=str)


def _handle_ledger_state_error(error: Exception) -> dict:
    """Handle a ledger state error and return a standardized error response.

    Args:
        error: The exception that occurred during ledger operations.

    Returns:
        A dictionary containing the error code and message.
    """
    return {
        "ok": False,
        "error": f"Ledger state error: {str(error)}",
    }


def ledger_page(
    conn: sqlite3.Connection,
    offset: int,
    limit: int,
    columns: list[str],
) -> list[dict[str, Any]]:
    """Fetch a single page of ledger entries from the database.

    Args:
        conn: SQLite database connection.
        offset: Number of rows to skip for pagination.
        limit: Maximum number of rows to return.
        columns: List of column names to select.

    Returns:
        A list of dictionaries representing ledger entries.
    """
    sql = f'SELECT {_select_columns_sql(columns)} FROM payout_ledger ORDER BY block_height DESC LIMIT ? OFFSET ?'
    rows = conn.execute(sql, (limit, offset)).fetchall()
    return [dict(row) for row in rows]


def api_ledger_list(conn: sqlite3.Connection, limit: int, offset: int) -> dict:
    """API endpoint handler for listing ledger entries.

    Fetches a paginated list of payout ledger entries from the database.

    Args:
        conn: SQLite database connection.
        limit: Maximum number of entries to return per page.
        offset: Number of entries to skip for pagination.

    Returns:
        A dictionary with 'entries' list and 'total' count.
    """
    columns = ["block_height", "miner_id", "amount", "tx_hash", "timestamp"]
    entries = ledger_page(conn, offset, limit, columns)
    total = conn.execute("SELECT COUNT(*) FROM payout_ledger").fetchone()[0]
    return {"entries": entries, "total": total}


def api_ledger_summary(conn: sqlite3.Connection) -> dict:
    """API endpoint handler for summarizing payout ledger statistics.

    Computes aggregate statistics across all ledger entries including
    total payout amount, number of unique miners, and transaction count.

    Args:
        conn: SQLite database connection.

    Returns:
        A dictionary containing summary statistics of the payout ledger.
    """
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total_txs,
            COUNT(DISTINCT miner_id) AS total_miners,
            COALESCE(SUM(amount), 0) AS total_amount
        FROM payout_ledger
        """
    ).fetchone()
    return {
        "total_transactions": row[0],
        "total_miners": row[1],
        "total_amount": int(row[2]),
    }
