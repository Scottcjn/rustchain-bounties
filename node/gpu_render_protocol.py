"""
node/gpu_render_protocol.py

Contains the `release_escrow` and `refund_escrow` methods with TOCTOU fix.
The unconditional UPDATE was changed to use `WHERE job_id=? AND status='locked'`
with a `cur.rowcount != 1` check to prevent race conditions.

This module implements atomic escrow state transitions with proper error handling,
logging, input validation, and comprehensive type annotations.
"""

import logging
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Dict, Iterator, Optional, Tuple, Any, List, Union, Callable
from uuid import UUID, uuid4
import re
from functools import wraps

# Configure module logger
logger = logging.getLogger(__name__)


class EscrowStatus(Enum):
    """Enumeration of possible escrow states."""
    LOCKED = "locked"
    RELEASED = "released"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class EscrowError(Exception):
    """Base exception for escrow operations."""
    pass


class EscrowAuthorizationError(EscrowError):
    """Raised when escrow action is not authorized."""
    pass


class EscrowStateError(EscrowError):
    """Raised when escrow is in an invalid state for the requested operation."""
    pass


class EscrowRaceConditionError(EscrowError):
    """Raised when a race condition is detected during escrow transition."""
    pass


class EscrowDatabaseError(EscrowError):
    """Raised when a database error occurs during escrow operations."""
    pass


class EscrowValidationError(EscrowError):
    """Raised when input validation fails."""
    pass


class EscrowNotFoundError(EscrowError):
    """Raised when escrow record is not found."""
    pass


@dataclass(frozen=True)
class EscrowConfig:
    """Configuration for escrow operations."""
    db_path: str = ":memory:"
    max_retries: int = 3
    retry_delay_seconds: float = 0.1
    connection_timeout: float = 5.0
    enable_audit_logging: bool = True
    max_job_id_length: int = 128
    max_wallet_length: int = 64
    min_amount_rtc: float = 0.000001
    max_amount_rtc: float = 1000000.0


@dataclass
class EscrowResult:
    """Result of an escrow operation."""
    success: bool
    job_id: str
    wallet: str
    amount_rtc: float
    status: EscrowStatus
    error: Optional[str] = None
    transaction_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for API responses."""
        result: Dict[str, Any] = {
            "success": self.success,
            "job_id": self.job_id,
            "wallet": self.wallet,
            "amount_rtc": self.amount_rtc,
            "status": self.status.value,
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.error:
            result["error"] = self.error
        return result


class EscrowDatabase:
    """Manages database connections and operations for escrow system."""

    def __init__(self, config: EscrowConfig) -> None:
        """
        Initialize the database manager.

        Args:
            config: Configuration for database operations

        Raises:
            EscrowDatabaseError: If initialization fails
        """
        self._config = config
        self._local = threading.local()
        self._lock = threading.Lock()
        self._initialized: bool = False

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection for the current thread.

        Returns:
            SQLite connection with row factory configured

        Raises:
            EscrowDatabaseError: If connection cannot be established
        """
        if not hasattr(self._local, "connection") or self._local.connection is None:
            try:
                conn = sqlite3.connect(
                    self._config.db_path,
                    timeout=self._config.connection_timeout,
                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                )
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA busy_timeout=5000")
                self._local.connection = conn
                logger.debug("Database connection established for thread %s", 
                           threading.current_thread().name)
            except sqlite3.Error as e:
                logger.error("Failed to establish database connection: %s", e)
                raise EscrowDatabaseError(f"Database connection failed: {e}") from e
        return self._local.connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Cursor]:
        """
        Context manager for database transactions with automatic rollback on error.

        Yields:
            Database cursor for executing queries

        Raises:
            EscrowDatabaseError: If transaction operations fail
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
            logger.debug("Transaction committed successfully")
        except sqlite3.Error as e:
            conn.rollback()
            logger.error("Transaction rolled back due to error: %s", e)
            raise EscrowDatabaseError(f"Transaction failed: {e}") from e
        except Exception:
            conn.rollback()
            logger.error("Transaction rolled back due to unexpected error")
            raise

    def initialize_schema(self) -> None:
        """Create the escrow table if it doesn't exist."""
        try:
            with self.transaction() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS escrow (
                        job_id TEXT PRIMARY KEY,
                        status TEXT NOT NULL DEFAULT 'locked'
                            CHECK(status IN ('locked', 'released', 'refunded', 'expired')),
                        wallet TEXT NOT NULL,
                        amount_rtc REAL NOT NULL CHECK(amount_rtc > 0),
                        released_at TIMESTAMP,
                        refunded_at TIMESTAMP,
                        expired_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        version INTEGER DEFAULT 1
                    )
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_escrow_status 
                    ON escrow(status)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_escrow_wallet 
                    ON escrow(wallet)
                """)
                self._initialized = True
                logger.info("Database schema initialized successfully")
        except sqlite3.Error as e:
            logger.error("Failed to initialize database schema: %s", e)
            raise EscrowDatabaseError(f"Schema initialization failed: {e}") from e

    def close(self) -> None:
        """Close the database connection for the current thread."""
        if hasattr(self._local, "connection") and self._local.connection:
            try:
                self._local.connection.close()
                logger.debug("Database connection closed for thread %s",
                           threading.current_thread().name)
            except sqlite3.Error as e:
                logger.warning("Error closing database connection: %s", e)
            finally:
                self._local.connection = None


class EscrowAuthorizer:
    """Handles authorization for escrow operations."""

    def __init__(self, config: EscrowConfig) -> None:
        """
        Initialize the authorizer.

        Args:
            config: Configuration for authorization
        """
        self._config = config

    def authorize(self, job_id: str, action: str, wallet: str, amount_rtc: float) -> Tuple[bool, Optional[str]]:
        """
        Authorize an escrow action.

        In production, this would verify signatures, permissions, etc.

        Args:
            job_id: The unique identifier for the render job
            action: The action to authorize ('release' or 'refund')
            wallet: The wallet address involved
            amount_rtc: The amount in RTC

        Returns:
            Tuple of (authorized, error_message)

        Raises:
            EscrowValidationError: If input validation fails
        """
        try:
            # Validate inputs
            if not self._validate_job_id(job_id):
                return False, "Invalid job ID format"
            
            if not self._validate_wallet(wallet):
                return False, "Invalid wallet address format"
            
            if not self._validate_amount(amount_rtc):
                return False, "Invalid amount format"
            
            if action not in ("release", "refund"):
                return False, f"Invalid action: {action}"
            
            # In production, implement actual authorization logic here
            # For example: verify digital signatures, check permissions, etc.
            
            logger.info("Authorization successful for job %s, action %s", job_id, action)
            return True, None
            
        except Exception as e:
            logger.error("Authorization failed for job %s: %s", job_id, str(e))
            return False, f"Authorization error: {str(e)}"

    def _validate_job_id(self, job_id: str) -> bool:
        """
        Validate job ID format.

        Args:
            job_id: The job ID to validate

        Returns:
            True if valid, False otherwise
        """
        if not job_id or not isinstance(job_id, str):
            return False
        if len(job_id) > self._config.max_job_id_length:
            return False
        # Allow alphanumeric, hyphens, underscores
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', job_id))

    def _validate_wallet(self, wallet: str) -> bool:
        """
        Validate wallet address format.

        Args:
            wallet: The wallet address to validate

        Returns:
            True if valid, False otherwise
        """
        if not wallet or not isinstance(wallet, str):
            return False
        if len(wallet) > self._config.max_wallet_length:
            return False
        # Allow alphanumeric wallet addresses
        return bool(re.match(r'^[a-zA-Z0-9]+$', wallet))

    def _validate_amount(self, amount: float) -> bool:
        """
        Validate amount format.

        Args:
            amount: The amount to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(amount, (int, float)):
            return False
        if amount < self._config.min_amount_rtc or amount > self._config.max_amount_rtc:
            return False
        return True


class EscrowAuditor:
    """Handles audit logging for escrow operations."""

    def __init__(self, config: EscrowConfig) -> None:
        """
        Initialize the auditor.

        Args:
            config: Configuration for audit logging
        """
        self._config = config
        self._audit_log: List[Dict[str, Any]] = []

    def log_event(self, event_type: str, job_id: str, details: Dict[str, Any]) -> None:
        """
        Log an audit event.

        Args:
            event_type: Type of event (e.g., 'release', 'refund', 'error')
            job_id: The job ID associated with the event
            details: Additional details about the event
        """
        if not self._config.enable_audit_logging:
            return

        audit_entry: Dict[str, Any] = {
            "event_type": event_type,
            "job_id": job_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details,
            "thread": threading.current_thread().name,
        }
        self._audit_log.append(audit_entry)
        logger.info("Audit event: %s for job %s", event_type, job_id)

    def get_audit_log(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get audit log entries, optionally filtered by job ID.

        Args:
            job_id: Optional job ID to filter by

        Returns:
            List of audit log entries
        """
        if job_id:
            return [entry for entry in self._audit_log if entry["job_id"] == job_id]
        return self._audit_log.copy()

    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        self._audit_log.clear()
        logger.debug("Audit log cleared")


class EscrowManager:
    """
    Manages escrow operations with atomic state transitions and race condition prevention.
    
    This class implements the core business logic for escrow operations including
    release and refund actions with proper TOCTOU protection.
    """

    def __init__(self, config: Optional[EscrowConfig] = None) -> None:
        """
        Initialize the escrow manager.

        Args:
            config: Optional configuration for escrow operations
        """
        self._config = config or EscrowConfig()
        self._database = EscrowDatabase(self._config)
        self._authorizer = EscrowAuthorizer(self._config)
        self._auditor = EscrowAuditor(self._config)
        self._lock = threading.Lock()
        
        # Initialize database schema
        self._database.initialize_schema()
        
        logger.info("EscrowManager initialized with config: %s", self._config)

    def _validate_escrow_inputs(self, job_id: str, wallet: str, amount_rtc: float) -> None:
        """
        Validate escrow operation inputs.

        Args:
            job_id: The job ID to validate
            wallet: The wallet address to validate
            amount_rtc: The amount to validate

        Raises:
            EscrowValidationError: If any input is invalid
        """
        if not job_id or not isinstance(job_id, str):
            raise EscrowValidationError("Job ID must be a non-empty string")
        
        if not wallet or not isinstance(wallet, str):
            raise EscrowValidationError("Wallet must be a non-empty string")
        
        if not isinstance(amount_rtc, (int, float)):
            raise EscrowValidationError("Amount must be a number")
        
        if amount_rtc <= 0:
            raise EscrowValidationError("Amount must be positive")
        
        if len(job_id) > self._config.max_job_id_length:
            raise EscrowValidationError(f"Job ID exceeds maximum length of {self._config.max_job_id_length}")
        
        if len(wallet) > self._config.max_wallet_length:
            raise EscrowValidationError(f"Wallet exceeds maximum length of {self._config.max_wallet_length}")

    def _get_escrow_record(self, cursor: sqlite3.Cursor, job_id: str) -> Optional[sqlite3.Row]:
        """
        Get an escrow record from the database.

        Args:
            cursor: Database cursor
            job_id: The job ID to look up

        Returns:
            Escrow record if found, None otherwise
        """
        cursor.execute(
            "SELECT job_id, status, wallet, amount_rtc, version FROM escrow WHERE job_id = ?",
            (job_id,)
        )
        return cursor.fetchone()

    def _update_escrow_status(self, cursor: sqlite3.Cursor, job_id: str, 
                              new_status: str, old_status: str) -> int:
        """
        Update escrow status atomically with version check.

        Args:
            cursor: Database cursor
            job_id: The job ID to update
            new_status: The new status to set
            old_status: The expected current status

        Returns:
            Number of rows affected (should be 1 for success)
        """
        timestamp_field = f"{new_status}_at"
        cursor.execute(
            f"""
            UPDATE escrow 
            SET status = ?, 
                {timestamp_field} = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP,
                version = version + 1
            WHERE job_id = ? 
                AND status = ?
                AND version = (SELECT version FROM escrow WHERE job_id = ?)
            """,
            (new_status, job_id, old_status, job_id)
        )
        return cursor.rowcount

    def release_escrow(self, job_id: str, wallet: str, amount_rtc: float) -> Dict[str, Any]:
        """
        Release escrow funds for a completed render job.

        This method implements atomic state transition with TOCTOU protection.
        Only one concurrent release/refund can succeed due to the guarded UPDATE.

        Args:
            job_id: The unique identifier for the render job
            wallet: The wallet address to receive the funds
            amount_rtc: The amount in RTC to release

        Returns:
            Dictionary containing the result of the operation

        Raises:
            EscrowValidationError: If input validation fails
            EscrowAuthorizationError: If authorization fails
            EscrowStateError: If escrow is in invalid state
            EscrowRaceConditionError: If race condition is detected
            EscrowDatabaseError: If database operation fails
        """
        try:
            # Validate inputs
            self._validate_escrow_inputs(job_id, wallet, amount_rtc)
            
            # Authorize the action
            authorized, error_msg = self._authorizer.authorize(job_id, "release", wallet, amount_rtc)
            if not authorized:
                raise EscrowAuthorizationError(error_msg or "Authorization failed")
            
            # Perform atomic state transition
            with self._database.transaction() as cursor:
                # Get current escrow record
                record = self._get_escrow_record(cursor, job_id)
                
                if record is None:
                    raise EscrowNotFoundError(f"Escrow record not found for job {job_id}")
                
                # Verify wallet matches
                if record["wallet"] != wallet:
                    raise EscrowAuthorizationError(f"Wallet mismatch for job {job_id}")
                
                # Verify amount matches
                if abs(record["amount_rtc"] - amount_rtc) > 0.000001:
                    raise EscrowValidationError(f"Amount mismatch for job {job_id}")
                
                # Check current status
                current_status = record["status"]
                if current_status != EscrowStatus.LOCKED.value:
                    raise EscrowStateError(
                        f"Cannot release escrow for job {job_id}: "
                        f"