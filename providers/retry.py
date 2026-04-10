# providers/errors.py
"""
Error taxonomy for BoTTube provider failures.
Classifies errors into actionable categories for retry and fallback logic.
"""


class ProviderError(Exception):
    """Base exception for all provider errors."""
    
    def __init__(self, message: str, provider: str = None, original_error: Exception = None):
        super().__init__(message)
        self.provider = provider
        self.original_error = original_error
        self.category = self.__class__.__name__


class AuthenticationError(ProviderError):
    """Authentication or authorization failure. Permanent error - do not retry."""
    pass


class ThrottledError(ProviderError):
    """Rate limit or quota exceeded. Transient error - retry with backoff."""
    
    def __init__(self, message: str, provider: str = None, retry_after: int = None, original_error: Exception = None):
        super().__init__(message, provider, original_error)
        self.retry_after = retry_after


class TransientError(ProviderError):
    """Temporary failure (network, timeout, 5xx). Transient error - retry."""
    pass


class PermanentError(ProviderError):
    """Permanent failure (invalid input, not found, 4xx). Do not retry."""
    pass


class ProviderUnavailableError(ProviderError):
    """Provider is unavailable or down. Transient error - retry or fallback."""
    pass


def classify_http_error(status_code: int, response_text: str, provider: str) -> ProviderError:
    """
    Classify HTTP error into appropriate error category.
    
    Args:
        status_code: HTTP status code
        response_text: Response body text
        provider: Provider name
        
    Returns:
        Appropriate ProviderError subclass
    """
    if status_code == 401 or status_code == 403:
        return AuthenticationError(
            f"Authentication failed: {status_code} - {response_text}",
            provider=provider
        )
    elif status_code == 429:
        # Try to extract retry-after header value from response
        retry_after = None
        if "retry" in response_text.lower():
            # Simple extraction, could be enhanced
            import re
            match = re.search(r'(\d+)\s*seconds?', response_text, re.IGNORECASE)
            if match:
                retry_after = int(match.group(1))
        return ThrottledError(
            f"Rate limited: {response_text}",
            provider=provider,
            retry_after=retry_after
        )
    elif 500 <= status_code < 600:
        return TransientError(
            f"Server error {status_code}: {response_text}",
            provider=provider
        )
    elif 400 <= status_code < 500:
        return PermanentError(
            f"Client error {status_code}: {response_text}",
            provider=provider
        )
    else:
        return TransientError(
            f"Unexpected error {status_code}: {response_text}",
            provider=provider
        )


def classify_exception(exc: Exception, provider: str) -> ProviderError:
    """
    Classify generic exception into appropriate error category.
    
    Args:
        exc: Exception to classify
        provider: Provider name
        
    Returns:
        Appropriate ProviderError subclass
    """
    import requests
    
    if isinstance(exc, ProviderError):
        return exc
    
    exc_str = str(exc).lower()
    
    # Network/connection errors are transient
    if isinstance(exc, (requests.exceptions.ConnectionError, 
                       requests.exceptions.Timeout,
                       TimeoutError)):
        return TransientError(
            f"Network error: {exc}",
            provider=provider,
            original_error=exc
        )
    
    # Check for common transient error patterns
    transient_patterns = ['timeout', 'connection', 'network', 'temporary']
    if any(pattern in exc_str for pattern in transient_patterns):
        return TransientError(
            f"Transient error: {exc}",
            provider=provider,
            original_error=exc
        )
    
    # Default to permanent for unknown errors
    return PermanentError(
        f"Unknown error: {exc}",
        provider=provider,
        original_error=exc
    )