"""Exceptions for RustChain SDK."""

from typing import Optional


class RustChainError(Exception):
    """Base exception for all RustChain errors."""
    
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ConnectionError(RustChainError):
    """Raised when connection to RustChain node fails."""
    pass


class TimeoutError(RustChainError):
    """Raised when request times out."""
    pass


class ValidationError(RustChainError):
    """Raised when input validation fails."""
    pass


class AuthenticationError(RustChainError):
    """Raised when authentication fails."""
    pass


class NotFoundError(RustChainError):
    """Raised when a requested resource is not found."""
    pass


class ServerError(RustChainError):
    """Raised when server returns a 5xx error."""
    pass


class RateLimitError(RustChainError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(message, code="RATE_LIMIT")


class TransferError(RustChainError):
    """Raised when a transfer operation fails."""
    pass


class InsufficientFundsError(TransferError):
    """Raised when account has insufficient funds."""
    pass


class InvalidSignatureError(TransferError):
    """Raised when signature validation fails."""
    pass


class AttestationError(RustChainError):
    """Raised when attestation operation fails."""
    pass