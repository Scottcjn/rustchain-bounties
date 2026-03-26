"""
RustChain SDK Exceptions
Typed exceptions for all error conditions.
"""

from typing import Optional


class RustChainError(Exception):
    """Base exception for all RustChain SDK errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class APIError(RustChainError):
    """Raised when the API returns a non-2xx status or a structured error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[dict] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __repr__(self) -> str:
        return f"APIError({self.message!r}, status_code={self.status_code})"


class AuthenticationError(RustChainError):
    """Raised when authentication or authorization fails."""

    pass


class ValidationError(RustChainError):
    """Raised when input validation fails (e.g. invalid wallet address, negative amount)."""

    pass


class TransferError(RustChainError):
    """Raised when a transfer transaction fails."""

    def __init__(
        self,
        message: str,
        tx_hash: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.tx_hash = tx_hash
        self.reason = reason


class NetworkError(RustChainError):
    """Raised when a network connection fails."""

    pass
