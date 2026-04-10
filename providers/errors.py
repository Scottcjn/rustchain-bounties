# providers/errors.py
"""
Structured error categories for BoTTube provider failures.
Enables intelligent retry/fallback decisions based on error classification.
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCategory(Enum):
    """Error categories for provider failures."""
    AUTH = "auth"
    THROTTLED = "throttled"
    TRANSIENT = "transient"
    PERMANENT = "permanent"


class ProviderError(Exception):
    """Base exception for all provider errors."""
    
    category: ErrorCategory = ErrorCategory.PERMANENT
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code
        self.response_data = response_data or {}
        self.original_error = original_error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to structured dict for logging."""
        return {
            "error_type": self.__class__.__name__,
            "category": self.category.value,
            "message": self.message,
            "provider": self.provider,
            "status_code": self.status_code,
            "response_data": self.response_data,
        }


class AuthError(ProviderError):
    """Authentication or authorization failure (401, 403)."""
    category = ErrorCategory.AUTH


class ThrottledError(ProviderError):
    """Rate limit or quota exceeded (429, 503 with retry-after)."""
    category = ErrorCategory.THROTTLED
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class TransientError(ProviderError):
    """Temporary failure that may succeed on retry (network, timeout, 5xx)."""
    category = ErrorCategory.TRANSIENT


class PermanentError(ProviderError):
    """Permanent failure that won't succeed on retry (400, 404, validation)."""
    category = ErrorCategory.PERMANENT


def classify_http_error(
    status_code: int,
    response_data: Optional[Dict[str, Any]] = None,
    provider: Optional[str] = None
) -> ProviderError:
    """
    Classify HTTP error into appropriate error category.
    
    Args:
        status_code: HTTP status code
        response_data: Response body as dict
        provider: Provider name for context
    
    Returns:
        Appropriate ProviderError subclass instance
    """
    response_data = response_data or {}
    message = response_data.get("error", {}).get("message", f"HTTP {status_code}")
    
    if status_code == 401:
        return AuthError(
            f"Authentication failed: {message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data
        )
    
    if status_code == 403:
        return AuthError(
            f"Authorization failed: {message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data
        )
    
    if status_code == 429:
        retry_after = None
        if isinstance(response_data, dict):
            retry_after = response_data.get("retry_after")
        return ThrottledError(
            f"Rate limit exceeded: {message}",
            retry_after=retry_after,
            provider=provider,
            status_code=status_code,
            response_data=response_data
        )
    
    if status_code == 503:
        return ThrottledError(
            f"Service temporarily unavailable: {message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data
        )
    
    if 500 <= status_code < 600:
        return TransientError(
            f"Server error: {message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data
        )
    
    if status_code == 408:
        return TransientError(
            f"Request timeout: {message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data
        )
    
    if status_code in (400, 404, 422):
        return PermanentError(
            f"Client error: {message}",
            provider=provider,
            status_code=status_code,
            response_data=response_data
        )
    
    return PermanentError(
        f"Unexpected error: {message}",
        provider=provider,
        status_code=status_code,
        response_data=response_data
    )


def classify_exception(
    exc: Exception,
    provider: Optional[str] = None
) -> ProviderError:
    """
    Classify generic exception into appropriate error category.
    
    Args:
        exc: Exception to classify
        provider: Provider name for context
    
    Returns:
        Appropriate ProviderError subclass instance
    """
    if isinstance(exc, ProviderError):
        return exc
    
    exc_name = exc.__class__.__name__
    exc_msg = str(exc)
    
    # Network/connection errors are transient
    if any(keyword in exc_name.lower() for keyword in ["timeout", "connection", "network"]):
        return TransientError(
            f"Network error: {exc_msg}",
            provider=provider,
            original_error=exc
        )
    
    # Default to permanent for unknown exceptions
    return PermanentError(
        f"Unexpected error: {exc_msg}",
        provider=provider,
        original_error=exc
    )