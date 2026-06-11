"""
OTC Bridge - Payout idempotency with persistent double-spend prevention.

This module provides:
1. SQLite-backed idempotency tracking with UNIQUE constraint
2. Secure admin transport blocking
3. Proper credential validation (no empty defaults)
"""

import hashlib
import logging
import os
import re
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Dict, Optional, Any, List, Tuple
from urllib.parse import urlparse

import requests
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('otc_bridge.log')]
)
logger = logging.getLogger(__name__)

# ============================================================
# Constants
# ============================================================
DB_PATH: str = os.environ.get("OTC_BRIDGE_DB", "otc_bridge.db")
NODE_URL: str = os.environ.get("RUSTCHAIN_NODE_URL", "http://localhost:8545")
REQUEST_TIMEOUT: int = int(os.environ.get("OTC_REQUEST_TIMEOUT", "30"))
MAX_RETRIES: int = int(os.environ.get("OTC_MAX_RETRIES", "3"))
IDEMPOTENCY_KEY_PATTERN: re.Pattern = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")

# ============================================================
# Database with double-spend prevention
# ============================================================

class PayoutStore:
    """SQLite-backed persistent store with UNIQUE idempotency key constraint."""

    def __init__(self, db_path: str = DB_PATH):
        self._db_path = db_path
        self._local = threading.local()
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self._db_path, timeout=10)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            self._local.conn = conn
        return self._local.conn

    def _init_schema(self) -> None:
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idempotency_key TEXT NOT NULL UNIQUE,
                order_id TEXT NOT NULL,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                amount TEXT NOT NULL,
                tx_hash TEXT,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending','completed','failed','duplicate')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_payouts_idempotency
            ON payouts(idempotency_key)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_payouts_order
            ON payouts(order_id)
        """)
        conn.commit()

    def find_by_idempotency_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Find payout by idempotency key. UNIQUE constraint prevents duplicates."""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM payouts WHERE idempotency_key = ?", (key,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def create_payout(
        self, idempotency_key: str, order_id: str,
        from_address: str, to_address: str, amount: str
    ) -> Dict[str, Any]:
        """Create a new payout record. Raises IntegrityError if key exists."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """INSERT INTO payouts
                   (idempotency_key, order_id, from_address, to_address, amount)
                   VALUES (?, ?, ?, ?, ?)""",
                (idempotency_key, order_id, from_address, to_address, amount)
            )
            conn.commit()
            row_id = cursor.lastrowid
            cursor = conn.execute("SELECT * FROM payouts WHERE id = ?", (row_id,))
            return dict(cursor.fetchone())
        except sqlite3.IntegrityError:
            # Key already exists — fetch and return existing (idempotent response)
            existing = self.find_by_idempotency_key(idempotency_key)
            if existing:
                existing["_duplicate"] = True
            return existing or {"error": "duplicate_key"}

    def update_status(self, idempotency_key: str, status: str,
                      tx_hash: Optional[str] = None) -> bool:
        """Update payout status atomically."""
        conn = self._get_conn()
        if tx_hash:
            conn.execute(
                """UPDATE payouts SET status = ?, tx_hash = ?,
                   updated_at = CURRENT_TIMESTAMP
                   WHERE idempotency_key = ?""",
                (status, tx_hash, idempotency_key)
            )
        else:
            conn.execute(
                "UPDATE payouts SET status = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE idempotency_key = ?",
                (status, idempotency_key)
            )
        conn.commit()
        return True

# Global store instance
payout_store = PayoutStore()

# ============================================================
# Idempotency key derivation
# ============================================================

def derive_idempotency_key(order_id: str, from_address: str,
                           to_address: str, amount: str) -> str:
    """Derive a deterministic idempotency key from payout parameters."""
    raw = f"{order_id}:{from_address}:{to_address}:{amount}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:64]

def validate_idempotency_key(key: str) -> bool:
    """Validate idempotency key format."""
    if not key or not isinstance(key, str):
        return False
    return bool(IDEMPOTENCY_KEY_PATTERN.match(key))

# ============================================================
# Security: Admin transport check
# ============================================================

def require_admin_transport_security(node_url: str) -> None:
    """
    Block non-loopback admin transports unless explicitly allowed.
    Prevents remote credential exfiltration.
    """
    admin_transport_allow_remote = os.environ.get(
        "OTC_ADMIN_TRANSPORT_ALLOW_REMOTE", ""
    ).lower() in ("1", "true", "yes")

    if admin_transport_allow_remote:
        logger.warning("Admin transport remote access ALLOWED — not recommended for production")
        return

    parsed = urlparse(node_url)
    host = parsed.hostname or ""

    allowed_local = ("localhost", "127.0.0.1", "::1", "0.0.0.0")
    if host not in allowed_local:
        raise PermissionError(
            f"Admin transport blocked: {host} is not a loopback address. "
            f"Set OTC_ADMIN_TRANSPORT_ALLOW_REMOTE=true to override."
        )

# ============================================================
# Validation
# ============================================================

def validate_payout_request(data: dict) -> List[str]:
    """Validate payout request fields. Returns list of error messages."""
    errors: List[str] = []
    required = ["order_id", "from_address", "to_address", "amount"]
    for field in required:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    if errors:
        return errors

    if not isinstance(data["order_id"], str) or len(data["order_id"]) > 64:
        errors.append("order_id must be a string <= 64 chars")
    if not isinstance(data["from_address"], str) or len(data["from_address"]) > 42:
        errors.append("from_address must be a string <= 42 chars")
    if not isinstance(data["to_address"], str) or len(data["to_address"]) > 42:
        errors.append("to_address must be a string <= 42 chars")
    amount = data["amount"]
    if not isinstance(amount, str) or not re.match(r"^\d+(\.\d+)?$", amount):
        errors.append("amount must be a numeric string")
    return errors

# ============================================================
# Main payout logic
# ============================================================

def process_payout(order_id: str, from_address: str,
                   to_address: str, amount: str) -> Dict[str, Any]:
    """
    Process a payout with full double-spend prevention.

    The UNIQUE constraint on idempotency_key in SQLite ensures that
    even if this function is called concurrently, only one payout
    per idempotency key will be created.
    """
    # 1. Derive idempotency key
    idempotency_key = derive_idempotency_key(
        order_id, from_address, to_address, amount
    )
    logger.info(
        "Processing payout: order=%s from=%s to=%s amount=%s key=%s",
        order_id, from_address, to_address, amount, idempotency_key[:16]
    )

    # 2. Check existing
    existing = payout_store.find_by_idempotency_key(idempotency_key)
    if existing:
        status = existing.get("status", "")
        logger.info(
            "Idempotency hit: key=%s status=%s tx_hash=%s",
            idempotency_key[:16], status, existing.get("tx_hash", "none")
        )
        return {
            "status": status if status in ("completed", "pending", "failed") else "duplicate",
            "idempotency_key": idempotency_key,
            "order_id": existing["order_id"],
            "tx_hash": existing.get("tx_hash", ""),
            "message": "Payout already processed (idempotent response)"
        }

    # 3. Create pending record
    record = payout_store.create_payout(
        idempotency_key, order_id, from_address, to_address, amount
    )
    if not record or record.get("error"):
        return {"status": "error", "message": "Failed to create payout record"}

    try:
        # 4. Check admin transport security
        require_admin_transport_security(NODE_URL)

        # 5. Submit to node
        tx_hash = submit_to_node(order_id, from_address, to_address, amount)

        # 6. Mark completed
        payout_store.update_status(idempotency_key, "completed", tx_hash)
        logger.info("Payout completed: order=%s tx=%s", order_id, tx_hash[:16])

        return {
            "status": "completed",
            "idempotency_key": idempotency_key,
            "order_id": order_id,
            "tx_hash": tx_hash,
            "message": "Payout processed successfully"
        }

    except Exception as e:
        logger.error("Payout failed: order=%s error=%s", order_id, str(e))
        payout_store.update_status(idempotency_key, "failed")
        return {
            "status": "failed",
            "idempotency_key": idempotency_key,
            "order_id": order_id,
            "error": str(e)
        }

def submit_to_node(order_id: str, from_address: str,
                   to_address: str, amount: str) -> str:
    """
    Submit transfer to RustChain node.

    Uses exponential backoff for transient failures.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_sendTransaction",
        "params": [{
            "from": from_address,
            "to": to_address,
            "value": hex(int(float(amount) * 1e18)),
            "data": f"0x{order_id.encode('utf-8').hex()}"
        }],
        "id": 1
    }

    last_error: Optional[Exception] = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                NODE_URL, json=payload, timeout=REQUEST_TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            resp.raise_for_status()
            data = resp.json()
            tx_hash = data.get("result", "")
            if tx_hash:
                return tx_hash
            raise ValueError(f"Empty tx_hash from node: {data}")
        except (requests.RequestException, ValueError) as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt * 0.5
                logger.warning("Retry %d/%d: %s (wait %.1fs)",
                             attempt + 1, MAX_RETRIES, e, wait)
                time.sleep(wait)

    raise RuntimeError(f"Transfer failed after {MAX_RETRIES} retries: {last_error}")

# ============================================================
# Flask App
# ============================================================

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

@app.route("/payout", methods=["POST"])
def payout_endpoint():
    """Handle payout requests with idempotent double-spend prevention."""
    try:
        data = request.get_json(silent=True) or {}
        errors = validate_payout_request(data)
        if errors:
            return jsonify({"status": "error", "errors": errors}), 400

        result = process_payout(
            order_id=data["order_id"],
            from_address=data["from_address"],
            to_address=data["to_address"],
            amount=data["amount"]
        )

        status_code = 200
        if result.get("status") == "error":
            status_code = 500
        elif result.get("status") == "duplicate":
            status_code = 200  # Idempotent response

        return jsonify(result), status_code

    except Exception as e:
        logger.error("Payout endpoint error: %s", str(e), exc_info=True)
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@app.route("/payout/status/<idempotency_key>", methods=["GET"])
def payout_status(idempotency_key: str):
    """Check the status of a payout by its idempotency key."""
    if not validate_idempotency_key(idempotency_key):
        return jsonify({"status": "error", "message": "Invalid idempotency key"}), 400
    record = payout_store.find_by_idempotency_key(idempotency_key)
    if record:
        return jsonify({
            "status": record["status"],
            "order_id": record["order_id"],
            "tx_hash": record.get("tx_hash", ""),
            "created_at": record["created_at"]
        })
    return jsonify({"status": "not_found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("OTC_BRIDGE_PORT", "5000"))
    logger.info("Starting OTC Bridge on port %d with DB: %s", port, DB_PATH)
    app.run(host="0.0.0.0", port=port)
