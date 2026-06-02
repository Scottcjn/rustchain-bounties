"""
node/rustchain_v2_integrated_v2.2.1_rip200.py

Node-side wallet transfer handler that derives tx_hash from idempotency key
and returns existing pending row on retry without double debit.

This module implements the wallet_transfer_v2 endpoint which:
1. Derives tx_hash from the idempotency key using SHA-256
2. Checks for existing pending transactions with the same tx_hash
3. Returns existing pending row on retry without double debit
4. Returns 409 on from/to/amount/reason mismatch
5. Validates idempotency key format [A-Za-z0-9._:-]{1,128}
"""

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Dict, Optional, Tuple, Any, Final, List, Union, Callable
from uuid import UUID, uuid4
from threading import RLock
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Idempotency key validation pattern
IDEMPOTENCY_KEY_PATTERN: Final[re.Pattern] = re.compile(r'^[A-Za-z0-9._:\-]{1,128}$')

# Transaction status constants
class TransactionStatus(Enum):
    """Enumeration of possible transaction statuses."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Error codes
class ErrorCode(Enum):
    """Enumeration of error codes for wallet transfer operations."""
    IDEMPOTENCY_MISMATCH = "IDEMPOTENCY_MISMATCH"
    INVALID_KEY = "INVALID_IDEMPOTENCY_KEY"
    INVALID_ADDRESS = "INVALID_ADDRESS"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    INVALID_REASON = "INVALID_REASON"
    STORAGE_ERROR = "STORAGE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

# Validation constants
MAX_ADDRESS_LENGTH: Final[int] = 64
MAX_AMOUNT_LENGTH: Final[int] = 32
MAX_REASON_LENGTH: Final[int] = 256
MIN_AMOUNT: Final[float] = 0.0
MAX_AMOUNT: Final[float] = 1_000_000_000.0
ADDRESS_PATTERN: Final[re.Pattern] = re.compile(r'^[A-Za-z0-9]{32,64}$')
AMOUNT_PATTERN: Final[re.Pattern] = re.compile(r'^\d+(\.\d{1,8})?$')
REASON_PATTERN: Final[re.Pattern] = re.compile(r'^[A-Za-z0-9._:\- ]{1,256}$')

# Rate limiting
MAX_REQUESTS_PER_SECOND: Final[int] = 100
RATE_LIMIT_WINDOW: Final[float] = 1.0

# Transaction hash derivation
TX_HASH_ALGORITHM: Final[str] = "sha256"
TX_HASH_PREFIX: Final[str] = "tx_"


@dataclass(frozen=True)
class TransactionRecord:
    """Immutable transaction record dataclass.
    
    Attributes:
        tx_hash: Unique transaction hash derived from idempotency key
        from_address: Source wallet address
        to_address: Destination wallet address
        amount: Transaction amount as string
        reason: Transaction reason/memo
        idempotency_key: Original idempotency key used
        status: Current transaction status
        created_at: ISO format creation timestamp
        updated_at: ISO format last update timestamp
        retry_count: Number of retry attempts
        request_id: Unique request identifier for tracing
    """
    tx_hash: str
    from_address: str
    to_address: str
    amount: str
    reason: str
    idempotency_key: str
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retry_count: int = 0
    request_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction record to dictionary.
        
        Returns:
            Dictionary representation of the transaction record
        """
        try:
            result = asdict(self)
            result['status'] = self.status.value
            return result
        except Exception as e:
            logger.error(f"Failed to convert transaction record to dict: {e}", exc_info=True)
            raise

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionRecord':
        """Create transaction record from dictionary.
        
        Args:
            data: Dictionary containing transaction record data
            
        Returns:
            TransactionRecord instance
            
        Raises:
            ValueError: If data is invalid or missing required fields
            TypeError: If data types are incorrect
        """
        try:
            data = data.copy()
            status_value = data.get('status', TransactionStatus.PENDING.value)
            data['status'] = TransactionStatus(status_value)
            return cls(**data)
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to create TransactionRecord from dict: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating TransactionRecord: {e}", exc_info=True)
            raise ValueError(f"Invalid transaction data: {e}")


class WalletTransferError(Exception):
    """Base exception for wallet transfer errors with structured error information."""
    
    def __init__(self, message: str, code: ErrorCode, status_code: int = 400, 
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp: str = datetime.now(timezone.utc).isoformat()
        self.error_id: str = str(uuid4())
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response.
        
        Returns:
            Dictionary with error details for API response
        """
        return {
            'error': {
                'code': self.code.value,
                'message': self.message,
                'status_code': self.status_code,
                'error_id': self.error_id,
                'timestamp': self.timestamp,
                'details': self.details
            }
        }


class IdempotencyMismatchError(WalletTransferError):
    """Raised when idempotency key matches but parameters differ."""
    
    def __init__(self, message: str, existing_tx: Optional[TransactionRecord] = None,
                 requested_params: Optional[Dict[str, str]] = None):
        details: Dict[str, Any] = {}
        if existing_tx:
            details['existing_transaction'] = existing_tx.to_dict()
        if requested_params:
            details['requested_parameters'] = requested_params
        super().__init__(
            message=message,
            code=ErrorCode.IDEMPOTENCY_MISMATCH,
            status_code=409,
            details=details
        )


class InvalidIdempotencyKeyError(WalletTransferError):
    """Raised when idempotency key format is invalid."""
    
    def __init__(self, message: str, key: Optional[str] = None):
        details: Dict[str, Any] = {'provided_key': key} if key else {}
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_KEY,
            status_code=400,
            details=details
        )


class ValidationError(WalletTransferError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str, value: Any, 
                 constraint: str, code: ErrorCode = ErrorCode.INTERNAL_ERROR):
        super().__init__(
            message=message,
            code=code,
            status_code=400,
            details={
                'field': field,
                'value': str(value),
                'constraint': constraint
            }
        )


class StorageError(WalletTransferError):
    """Raised when storage operations fail."""
    
    def __init__(self, message: str, operation: str, 
                 original_error: Optional[Exception] = None):
        details: Dict[str, Any] = {
            'operation': operation,
            'original_error': str(original_error) if original_error else None
        }
        super().__init__(
            message=message,
            code=ErrorCode.STORAGE_ERROR,
            status_code=500,
            details=details
        )


class RateLimitExceededError(WalletTransferError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: float):
        super().__init__(
            message=message,
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details={'retry_after_seconds': retry_after}
        )


class RateLimiter:
    """Thread-safe rate limiter using sliding window algorithm.
    
    Attributes:
        max_requests: Maximum number of requests allowed in the window
        window: Time window in seconds
    """
    
    def __init__(self, max_requests: int = MAX_REQUESTS_PER_SECOND, 
                 window: float = RATE_LIMIT_WINDOW):
        self.max_requests: int = max_requests
        self.window: float = window
        self._requests: List[float] = []
        self._lock: RLock = RLock()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed under rate limit.
        
        Returns:
            True if request is allowed, False otherwise
        """
        with self._lock:
            try:
                now: float = time.monotonic()
                cutoff: float = now - self.window
                
                # Remove expired entries
                self._requests = [t for t in self._requests if t > cutoff]
                
                if len(self._requests) >= self.max_requests:
                    return False
                
                self._requests.append(now)
                return True
            except Exception as e:
                logger.error(f"Rate limiter error: {e}", exc_info=True)
                return False
    
    def get_remaining(self) -> int:
        """Get remaining requests in current window.
        
        Returns:
            Number of remaining requests allowed
        """
        with self._lock:
            try:
                now: float = time.monotonic()
                cutoff: float = now - self.window
                self._requests = [t for t in self._requests if t > cutoff]
                return max(0, self.max_requests - len(self._requests))
            except Exception as e:
                logger.error(f"Rate limiter remaining count error: {e}", exc_info=True)
                return 0
    
    def get_retry_after(self) -> float:
        """Get seconds until next request is allowed.
        
        Returns:
            Seconds to wait before next allowed request
        """
        with self._lock:
            try:
                if not self._requests:
                    return 0.0
                now: float = time.monotonic()
                oldest: float = min(self._requests)
                return max(0.0, oldest + self.window - now)
            except Exception as e:
                logger.error(f"Rate limiter retry after error: {e}", exc_info=True)
                return 0.0


class TransactionStorage:
    """Thread-safe transaction storage with persistence support.
    
    Attributes:
        _storage: Internal dictionary mapping tx_hash to TransactionRecord
        _lock: Thread lock for thread-safe operations
    """
    
    def __init__(self, initial_data: Optional[Dict[str, Dict[str, Any]]] = None):
        self._storage: Dict[str, TransactionRecord] = {}
        self._lock: RLock = RLock()
        if initial_data:
            self._load_initial_data(initial_data)
    
    def _load_initial_data(self, data: Dict[str, Dict[str, Any]]) -> None:
        """Load initial data into storage.
        
        Args:
            data: Dictionary of initial transaction data
        """
        for key, value in data.items():
            try:
                self._storage[key] = TransactionRecord.from_dict(value)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to load initial transaction {key}: {e}")
    
    def get(self, tx_hash: str) -> Optional[TransactionRecord]:
        """Retrieve transaction by hash.
        
        Args:
            tx_hash: Transaction hash to look up
            
        Returns:
            TransactionRecord if found, None otherwise
            
        Raises:
            StorageError: If storage operation fails
        """
        try:
            with self._lock:
                return self._storage.get(tx_hash)
        except Exception as e:
            logger.error(f"Storage get error for hash {tx_hash}: {e}", exc_info=True)
            raise StorageError(
                message=f"Failed to retrieve transaction: {e}",
                operation="get",
                original_error=e
            )
    
    def put(self, tx_hash: str, record: TransactionRecord) -> None:
        """Store transaction record.
        
        Args:
            tx_hash: Transaction hash
            record: TransactionRecord to store
            
        Raises:
            StorageError: If storage operation fails
        """
        try:
            with self._lock:
                self._storage[tx_hash] = record
        except Exception as e:
            logger.error(f"Storage put error for hash {tx_hash}: {e}", exc_info=True)
            raise StorageError(
                message=f"Failed to store transaction: {e}",
                operation="put",
                original_error=e
            )
    
    def delete(self, tx_hash: str) -> bool:
        """Delete transaction record.
        
        Args:
            tx_hash: Transaction hash to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            StorageError: If storage operation fails
        """
        try:
            with self._lock:
                if tx_hash in self._storage:
                    del self._storage[tx_hash]
                    return True
                return False
        except Exception as e:
            logger.error(f"Storage delete error for hash {tx_hash}: {e}", exc_info=True)
            raise StorageError(
                message=f"Failed to delete transaction: {e}",
                operation="delete",
                original_error=e
            )
    
    def exists(self, tx_hash: str) -> bool:
        """Check if transaction exists.
        
        Args:
            tx_hash: Transaction hash to check
            
        Returns:
            True if transaction exists, False otherwise
        """
        try:
            with self._lock:
                return tx_hash in self._storage
        except Exception as e:
            logger.error(f"Storage exists error for hash {tx_hash}: {e}", exc_info=True)
            return False
    
    def get_all(self) -> Dict[str, TransactionRecord]:
        """Get all transactions.
        
        Returns:
            Dictionary of all transactions
            
        Raises:
            StorageError: If storage operation fails
        """
        try:
            with self._lock:
                return dict(self._storage)
        except Exception as e:
            logger.error(f"Storage get_all error: {e}", exc_info=True)
            raise StorageError(
                message=f"Failed to retrieve all transactions: {e}",
                operation="get_all",
                original_error=e
            )
    
    def get_by_status(self, status: TransactionStatus) -> List[TransactionRecord]:
        """Get all transactions with a specific status.
        
        Args:
            status: TransactionStatus to filter by
            
        Returns:
            List of matching TransactionRecord objects
        """
        try:
            with self._lock:
                return [record for record in self._storage.values() 
                       if record.status == status]
        except Exception as e:
            logger.error(f"Storage get_by_status error: {e}", exc_info=True)
            return []


def derive_tx_hash(idempotency_key: str) -> str:
    """Derive transaction hash from idempotency key using SHA-256.
    
    Args:
        idempotency_key: The idempotency key to derive hash from
        
    Returns:
        Transaction hash string with prefix
        
    Raises:
        ValueError: If idempotency_key is empty or invalid
    """
    if not idempotency_key:
        raise ValueError("Idempotency key cannot be empty")
    
    try:
        hash_bytes: bytes = hashlib.sha256(idempotency_key.encode('utf-8')).digest()
        hash_hex: str = hash_bytes.hex()
        return f"{TX_HASH_PREFIX}{hash_hex}"
    except Exception as e:
        logger.error(f"Failed to derive tx_hash from key: {e}", exc_info=True)
        raise ValueError(f"Failed to derive transaction hash: {e}")


def validate_idempotency_key(key: str) -> None:
    """Validate idempotency key format.
    
    Args:
        key: Idempotency key to validate
        
    Raises:
        InvalidIdempotencyKeyError: If key format is invalid
    """
    if not key:
        raise InvalidIdempotencyKeyError(
            message="Idempotency key is required",
            key=key
        )
    
    if not isinstance(key, str):
        raise InvalidIdempotencyKeyError(
            message="Idempotency key must be a string",
            key=str(key) if key else None
        )
    
    if not IDEMPOTENCY_KEY_PATTERN.match(key):
        raise InvalidIdempotencyKeyError(
            message=f"Invalid idempotency key format. Must match pattern: {IDEMPOTENCY_KEY_PATTERN.pattern}",
            key=key
        )


def validate_address(address: str, field_name: str = "address") -> None:
    """Validate wallet address format.
    
    Args:
        address: Address to validate
        field_name: Name of the field for error messages
        
    Raises:
        ValidationError: If address format is invalid
    """
    if not address:
        raise ValidationError(
            message=f"{field_name} is required",
            field=field_name,
            value=address,
            constraint="required"
        )
    
    if not isinstance(address, str):
        raise ValidationError(
            message=f"{field_name} must be a string",