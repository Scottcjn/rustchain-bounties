"""Typed exceptions for RustChain SDK."""

class RustChainError(Exception):
    """Base exception for RustChain SDK."""
    pass

class ConnectionError(RustChainError):
    """Failed to connect to RustChain node."""
    pass

class APIError(RustChainError):
    """API returned an error response."""
    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API error {status_code}: {message}")

class ValidationError(RustChainError):
    """Invalid input parameters."""
    pass

class TimeoutError(RustChainError):
    """Request timed out."""
    pass
