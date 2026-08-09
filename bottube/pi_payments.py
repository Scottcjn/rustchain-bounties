#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Payment processing module for Bottube's Pi integration.
Handles database operations, payment verification and approval workflows.
"""

import os
import sqlite3
from typing import Optional, Dict, Any, Tuple

def _db_path() -> str:
    """
    Returns the path to the Bottube payments database.

    Returns:
        str: Absolute path to the SQLite database file.

    Example:
        >>> _db_path()
        '/home/user/.bottube/payments.db'
    """
    return os.path.expanduser('~/.bottube/payments.db')

def _conn() -> sqlite3.Connection:
    """
    Creates and returns a connection to the payments database.

    Returns:
        sqlite3.Connection: Active database connection.

    Raises:
        sqlite3.Error: If database creation or connection fails.
    """
    db_path = _db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def init_pi_payment_tables() -> None:
    """
    Initializes the required tables in the payments database.

    Creates tables for:
    - pi_headers (payment metadata)
    - pi_payments (transaction records)
    - pi_products (product catalog)

    Raises:
        sqlite3.Error: If table creation fails.
    """
    conn = _conn()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pi_headers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_hash TEXT UNIQUE,
                    amount REAL,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pi_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    header_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    price REAL,
                    FOREIGN KEY(header_id) REFERENCES pi_headers(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pi_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    price REAL,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
    finally:
        conn.close()

def _pi_headers() -> sqlite3.Cursor:
    """
    Returns a cursor for the pi_headers table.

    Returns:
        sqlite3.Cursor: Active cursor for reading/writing headers.

    Note:
        Caller is responsible for closing the cursor.
    """
    conn = _conn()
    return conn.cursor()

def _pi_get_payment(header_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves a payment record by its header ID.

    Args:
        header_id: ID of the payment header to retrieve.

    Returns:
        Optional[Dict]: Payment record as dictionary if found, None otherwise.

    Example:
        >>> payment = _pi_get_payment(123)
        >>> payment['amount']
        10.50
    """
    cursor = _pi_headers()
    try:
        cursor.execute("""
            SELECT h.*, p.product_id, p.quantity, p.price
            FROM pi_headers h
            LEFT JOIN pi_payments p ON h.id = p.header_id
            WHERE h.id = ?
        """, (header_id,))
        return cursor.fetchone()
    finally:
        cursor.close()

def _verify_against_products(payment: Dict[str, Any]) -> bool:
    """
    Verifies that all products in a payment exist and are active.

    Args:
        payment: Payment record dictionary from _pi_get_payment.

    Returns:
        bool: True if all products are valid, False otherwise.

    Raises:
        ValueError: If payment record is invalid.
    """
    if not payment:
        raise ValueError("Invalid payment record")

    cursor = _conn().cursor()
    try:
        product_ids = [row[0] for row in cursor.execute(
            "SELECT id FROM pi_products WHERE id IN (?) AND is_active = 1",
            (tuple(payment['product_id']),)
        )]
        return len(product_ids) == len(payment['product_id'])
    finally:
        cursor.close()

def pi_health() -> Dict[str, Any]:
    """
    Returns the health status of the payment system.

    Returns:
        Dict: Dictionary containing:
            - 'database': Connection status
            - 'tables': List of existing tables
            - 'products': Count of active products

    Example:
        >>> health = pi_health()
        >>> health['database']
        'connected'
    """
    conn = _conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*) FROM pi_products WHERE is_active = 1")
        product_count = cursor.fetchone()[0]

        return {
            'database': 'connected',
            'tables': tables,
            'products': product_count
        }
    finally:
        conn.close()

def pi_approve(header_id: int) -> bool:
    """
    Approves a payment header and all associated payments.

    Args:
        header_id: ID of the payment header to approve.

    Returns:
        bool: True if approval succeeded, False otherwise.

    Raises:
        sqlite3.Error: If database operations fail.
    """
    conn = _conn()
    try:
        with conn:
            # Mark header as approved
            conn.execute(
                "UPDATE pi_headers SET status = 'approved' WHERE id = ?",
                (header_id,)
            )

            # Verify all payments are valid
            payment = _pi_get_payment(header_id)
            if not _verify_against_products(payment):
                return False

            return True
    except sqlite3.Error as e:
        print(f"Approval failed: {e}")
        return False

def pi_complete(header_id: int) -> bool:
    """
    Completes a payment header by marking it as completed.

    Args:
        header_id: ID of the payment header to complete.

    Returns:
        bool: True if completion succeeded, False otherwise.

    Note:
        This is the final step in the payment workflow.
    """
    conn = _conn()
    try:
        with conn:
            conn.execute(
                "UPDATE pi_headers SET status = 'completed' WHERE id = ?",
                (header_id,)
            )
            return True
    except sqlite3.Error as e:
        print(f"Completion failed: {e}")
        return False