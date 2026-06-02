"""
OTC Bridge - Main implementation for payout idempotency and secure admin transport.

This module provides:
1. Stable idempotency key generation for OTC payouts
2. Secure admin transport blocking for non-local/TLS-disabled connections
3. Integration with RustChain node for wallet transfers
"""

import hashlib
import logging
import os
import re
import time
from typing import Optional, Tuple, Dict, Any, Union, List
from urllib.parse import urlparse, ParseResult
from dataclasses import dataclass, asdict
from enum import Enum, auto
from functools import lru_cache
from contextlib import contextmanager
from datetime import datetime, timezone

import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError
from requests.exceptions import (
    RequestException,
    ConnectionError,
    Timeout,
    HTTPError as RequestsHTTPError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('otc_bridge.log')
    ]
)
logger = logging.getLogger(__name__)

# Constants
IDEMPOTENCY_KEY_PATTERN: re.Pattern = re.compile(r'^[A-Za-z0-9._:-]{1,128}$')
RC_ADMIN_KEY: str = os.environ.get('RC_ADMIN_KEY', '')
ADMIN_TRANSPORT_BLOCK_REASON: str = "admin_transport_blocked"
DEFAULT_NODE_URL: str = 'https://localhost:8545'
MAX_RETRIES: int = 3
RETRY_DELAY: float = 1.0
REQUEST_TIMEOUT: float = 30.0
MAX_RETRY_BACKOFF: float = 10.0

# Validation constants
VALID_HOSTS_LOCAL: Tuple[str, ...] = ('localhost', '127.0.0.1', '::1', '0.0.0.0')
MAX_ORDER_ID_LENGTH: int = 64
MAX_ADDRESS_LENGTH: int = 42
MAX_AMOUNT_LENGTH: int = 32
MAX_REASON_LENGTH: int = 128

# Security constants
ADDRESS_PATTERN: re.Pattern = re.compile(r'^[a-zA-Z0-9_]{1,42}$')
AMOUNT_PATTERN: re.Pattern = re.compile(r'^\d+(\.\d+)?$')
ORDER_ID_SANITIZE_PATTERN: re.Pattern = re.compile(r'[^a-zA-Z0-9._:-]')


class TransportSecurityError(Exception):
    """Raised when admin transport security check fails."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class TransferError(Exception):
    """Raised when transfer operation fails."""
    pass


class IdempotencyError(Exception):
    """Raised when idempotency key generation fails."""
    pass


class NodeConnectionError(Exception):
    """Raised when connection to RustChain node fails."""
    pass


class RateLimitError(Exception):
    """Raised when rate limiting is triggered."""
    pass


class TransferStatus(Enum):
    """Transfer status enumeration."""
    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()
    DUPLICATE = auto()


@dataclass(frozen=True)
class TransferResult:
    """Immutable transfer result data class."""
    status: TransferStatus
    order_id: str
    idempotency_key: str
    tx_hash: str
    error_message: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', 
                datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: Dict[str, Any] = {
            "status": self.status.name.lower(),
            "order_id": self.order_id,
            "idempotency_key": self.idempotency_key,
            "tx_hash": self.tx_hash,
            "timestamp": self.timestamp
        }
        if self.error_message:
            result["error_message"] = self.error_message
        return result


@dataclass(frozen=True)
class TransferRequest:
    """Immutable transfer request data class."""
    order_id: str
    from_address: str
    to_address: str
    amount: str
    reason: str = "otc_payout"

    def validate(self) -> None:
        """Validate all fields in the transfer request.
        
        Raises:
            ValidationError: If any validation check fails
        """
        errors: List[str] = []
        
        # Validate order_id
        if not self.order_id or len(self.order_id) > MAX_ORDER_ID_LENGTH:
            errors.append(
                f"order_id must be 1-{MAX_ORDER_ID_LENGTH} characters"
            )
        
        # Validate addresses
        if not self.from_address or len(self.from_address) > MAX_ADDRESS_LENGTH:
            errors.append(
                f"from_address must be 1-{MAX_ADDRESS_LENGTH} characters"
            )
        elif not ADDRESS_PATTERN.match(self.from_address):
            errors.append("Invalid from_address format")
        
        if not self.to_address or len(self.to_address) > MAX_ADDRESS_LENGTH:
            errors.append(
                f"to_address must be 1-{MAX_ADDRESS_LENGTH} characters"
            )
        elif not ADDRESS_PATTERN.match(self.to_address):
            errors.append("Invalid to_address format")
        
        # Validate amount
        if not self.amount or len(self.amount) > MAX_AMOUNT_LENGTH:
            errors.append(
                f"amount must be 1-{MAX_AMOUNT_LENGTH} characters"
            )
        elif not AMOUNT_PATTERN.match(self.amount):
            errors.append("Invalid amount format")
        
        # Validate reason
        if self.reason and len(self.reason) > MAX_REASON_LENGTH:
            errors.append(
                f"reason must be 0-{MAX_REASON_LENGTH} characters"
            )
        
        if errors:
            raise ValidationError(
                f"Validation failed: {'; '.join(errors)}"
            )


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int = 10, window: float = 1.0):
        self.max_calls: int = max_calls
        self.window: float = window
        self.calls: List[float] = []
    
    def acquire(self) -> bool:
        """Try to acquire a rate limit slot.
        
        Returns:
            True if allowed, False if rate limited
        """
        now: float = time.time()
        # Remove old calls
        self.calls = [t for t in self.calls if now - t < self.window]
        
        if len(self.calls) >= self.max_calls:
            return False
        
        self.calls.append(now)
        return True
    
    def wait_time(self) -> float:
        """Get the time to wait before next allowed call."""
        if not self.calls:
            return 0.0
        now: float = time.time()
        oldest: float = min(self.calls)
        return max(0.0, self.window - (now - oldest))


class MetricsCollector:
    """Collect and expose metrics for monitoring."""
    
    def __init__(self):
        self.transfer_count: int = 0
        self.transfer_success: int = 0
        self.transfer_failure: int = 0
        self.transfer_duplicate: int = 0
        self.transport_blocks: int = 0
        self.total_latency: float = 0.0
    
    def record_transfer(self, status: TransferStatus, latency: float) -> None:
        """Record a transfer attempt."""
        self.transfer_count += 1
        self.total_latency += latency
        
        if status == TransferStatus.COMPLETED:
            self.transfer_success += 1
        elif status == TransferStatus.FAILED:
            self.transfer_failure += 1
        elif status == TransferStatus.DUPLICATE:
            self.transfer_duplicate += 1
    
    def record_transport_block(self) -> None:
        """Record a transport block event."""
        self.transport_blocks += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        return {
            "transfer_count": self.transfer_count,
            "transfer_success": self.transfer_success,
            "transfer_failure": self.transfer_failure,
            "transfer_duplicate": self.transfer_duplicate,
            "transport_blocks": self.transport_blocks,
            "average_latency": (
                self.total_latency / self.transfer_count 
                if self.transfer_count > 0 else 0.0
            )
        }


# Global instances
rate_limiter: RateLimiter = RateLimiter()
metrics_collector: MetricsCollector = MetricsCollector()


def generate_idempotency_key(order_id: str) -> str:
    """Generate a stable idempotency key for OTC payouts.
    
    The key format is: otc_payout:{order_id}
    This ensures that retries with the same order_id produce the same key,
    allowing the node to detect and handle duplicate payouts.
    
    Args:
        order_id: The OTC order identifier (must be non-empty and <= 64 chars)
        
    Returns:
        A stable idempotency key string
        
    Raises:
        IdempotencyError: If the generated key doesn't match validation pattern
        ValidationError: If order_id is invalid
    """
    if not order_id or len(order_id) > MAX_ORDER_ID_LENGTH:
        raise ValidationError(
            f"order_id must be 1-{MAX_ORDER_ID_LENGTH} characters, "
            f"got: '{order_id}'"
        )
    
    # Sanitize order_id to prevent injection
    sanitized_order_id: str = ORDER_ID_SANITIZE_PATTERN.sub('_', order_id)
    
    key: str = f"otc_payout:{sanitized_order_id}"
    
    if not IDEMPOTENCY_KEY_PATTERN.match(key):
        raise IdempotencyError(
            f"Generated idempotency key '{key}' does not match required pattern "
            f"'{IDEMPOTENCY_KEY_PATTERN.pattern}'"
        )
    
    logger.debug(f"Generated idempotency key: {key}")
    return key


def _admin_transport_block_reason(
    target_url: str,
    tls_verify: bool = True,
    admin_key: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """Validate admin transport security before sending RC_ADMIN_KEY.
    
    This function implements fail-closed admin transport security:
    - Refuses to send admin key over HTTP (non-TLS)
    - Refuses to send admin key to non-localhost when TLS verification is disabled
    - Returns structured error and logs alert if blocked
    
    Args:
        target_url: The URL to send the admin key to
        tls_verify: Whether TLS verification is enabled
        admin_key: The admin key to send (defaults to RC_ADMIN_KEY env var)
        
    Returns:
        Tuple of (is_allowed: bool, reason: Optional[str])
        - If allowed: (True, None)
        - If blocked: (False, reason_string)
        
    Raises:
        TransportSecurityError: If URL parsing fails
    """
    admin_key = admin_key or RC_ADMIN_KEY
    
    if not admin_key:
        logger.debug("No admin key configured, transport check skipped")
        return True, None
    
    try:
        parsed: ParseResult = urlparse(target_url)
        host: str = parsed.hostname or ''
    except Exception as e:
        raise TransportSecurityError(
            f"Failed to parse URL '{target_url}': {e}"
        )
    
    # Check for HTTP (non-TLS) transport
    if target_url.startswith('http://'):
        reason: str = (
            f"Admin transport blocked: Refusing to send RC_ADMIN_KEY over HTTP "
            f"(target: {target_url}). TLS is required for admin credentials."
        )
        logger.error(reason)
        metrics_collector.record_transport_block()
        return False, reason
    
    # Check for non-localhost with TLS verification disabled
    if not tls_verify:
        # Allow localhost even without TLS verification (for development)
        if host not in VALID_HOSTS_LOCAL:
            reason = (
                f"Admin transport blocked: Refusing to send RC_ADMIN_KEY to "
                f"non-localhost ({host}) with TLS verification disabled. "
                f"Target: {target_url}"
            )
            logger.error(reason)
            metrics_collector.record_transport_block()
            return False, reason
    
    logger.debug(
        f"Admin transport check passed for {target_url} "
        f"(tls_verify={tls_verify})"
    )
    return True, None


def _make_request_with_retry(
    url: str,
    payload: Dict[str, Any],
    headers: Dict[str, str],
    tls_verify: bool = True,
    max_retries: int = MAX_RETRIES,
    timeout: float = REQUEST_TIMEOUT
) -> requests.Response:
    """Make HTTP request with retry logic and exponential backoff.
    
    Args:
        url: Target URL
        payload: Request payload
        headers: Request headers
        tls_verify: Whether to verify TLS certificates
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        
    Returns:
        Response object
        
    Raises:
        NodeConnectionError: If all retries fail
        RateLimitError: If rate limited
    """
    last_exception: Optional[Exception] = None
    
    for attempt in range(max_retries):
        try:
            # Check rate limit
            if not rate_limiter.acquire():
                wait: float = rate_limiter.wait_time()
                logger.warning(
                    f"Rate limited, waiting {wait:.2f}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(min(wait, MAX_RETRY_BACKOFF))
                continue
            
            response: requests.Response = requests.post(
                url,
                json=payload,
                headers=headers,
                verify=tls_verify,
                timeout=timeout
            )
            response.raise_for_status()
            return response
            
        except Timeout as e:
            last_exception = e
            logger.warning(
                f"Request timeout (attempt {attempt + 1}/{max_retries}): {e}"
            )
        except ConnectionError as e:
            last_exception = e
            logger.warning(
                f"Connection error (attempt {attempt + 1}/{max_retries}): {e}"
            )
        except RequestsHTTPError as e:
            if e.response.status_code == 429:
                raise RateLimitError(f"Rate limited by node: {e}")
            last_exception = e
            logger.warning(
                f"HTTP error (attempt {attempt + 1}/{max_retries}): {e}"
            )
        except RequestException as e:
            last_exception = e
            logger.warning(
                f"Request failed (attempt {attempt + 1}/{max_retries}): {e}"
            )
        
        # Exponential backoff with jitter
        if attempt < max_retries - 1:
            delay: float = min(
                RETRY_DELAY * (2 ** attempt) + (time.time() % 0.1),
                MAX_RETRY_BACKOFF
            )
            logger.debug(f"Retrying in {delay:.2f}s...")
            time.sleep(delay)
    
    raise NodeConnectionError(
        f"Failed to connect to node after {max_retries} attempts: {last_exception}"
    )


def rtc_transfer_from_worker(
    order_id: str,
    from_address: str,
    to_address: str,
    amount: str,
    reason: str = "otc_payout",
    node_url: str = DEFAULT_NODE_URL,
    tls_verify: bool = True
) -> TransferResult:
    """Execute a transfer from worker wallet with idempotency.
    
    This function:
    1. Validates all input parameters
    2. Generates stable idempotency key
    3. Checks admin transport security
    4. Executes transfer with retry logic
    5. Returns structured result
    
    Args:
        order_id: OTC order identifier
        from_address: Source wallet address
        to_address: Destination wallet address
        amount: Transfer amount
        reason: Transfer reason (default: "otc_payout")
        node_url: RustChain node URL
        tls_verify: Whether to verify TLS certificates
        
    Returns:
        TransferResult with status and details
        
    Raises:
        ValidationError: If input validation fails
        TransportSecurityError: If admin transport check fails
        NodeConnectionError: If node communication fails
    """
    start_time: float = time.time()
    
    try:
        # Validate input
        request_data: TransferRequest = TransferRequest(
            order_id=order_id,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            reason=reason
        )
        request_data.validate()
        
        # Generate idempotency key
        idempotency_key: str = generate_idempotency_key(order_id)
        
        # Check admin transport security
        is_allowed, block_reason = _admin_transport_block_reason(
            node_url, tls_verify
        )
        if not is_allowed:
            raise TransportSecurityError(
                block_reason or "Admin transport blocked"
            )
        
        # Prepare request
        payload: Dict[str, Any] = {
            "from": from_address,
            "to": to_address,
            "amount": amount,
            "reason": reason,
            "idempotency_key": idempotency_key
        }
        
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "X-Admin-Key": RC_ADMIN_KEY
        }
        
        # Execute transfer with retry
        response