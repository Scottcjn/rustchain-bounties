"""
rustchain.errors
~~~~~~~~~~~~~~~~

Exception hierarchy for the RustChain Python SDK.

All exceptions inherit from :class:`RustChainError` so callers can catch
a single base class or handle specific failure modes.
"""

from __future__ import annotations

from typing import Any, Optional


class RustChainError(Exception):
    """Base exception for all RustChain SDK errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


class RustChainConnectionError(RustChainError):
    """Raised when the SDK cannot reach the RustChain node."""

    pass


class RustChainTimeoutError(RustChainError):
    """Raised when a request to the RustChain node times out."""

    pass


class RustChainAPIError(RustChainError):
    """Raised when the RustChain node returns a non-2xx HTTP response.

    Attributes:
        status_code: HTTP status code from the node.
        response_body: Raw response body, if available.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message, details={"status_code": status_code})

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(status_code={self.status_code}, message={self.message!r})"
        )


class RustChainAuthError(RustChainAPIError):
    """Raised on 401/403 responses — invalid or missing credentials."""

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: int = 401,
        response_body: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code, response_body)


class RustChainValidationError(RustChainError):
    """Raised when client-side validation fails before sending a request.

    For example, an empty wallet ID or negative transfer amount.
    """

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(f"Validation error on '{field}': {message}")
