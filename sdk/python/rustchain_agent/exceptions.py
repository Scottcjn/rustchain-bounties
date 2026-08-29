"""
Exceptions for the RustChain Agent Economy SDK.
"""

class AgentEconomyError(Exception):
    """Base exception for all RustChain Agent Economy errors."""
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class ValidationError(AgentEconomyError, ValueError):
    """Raised when client-side or server-side parameter validation fails."""
    pass


class InsufficientEscrowError(AgentEconomyError):
    """Raised when the poster has insufficient balance for escrow (reward + 5% platform fee)."""
    pass


class JobNotFoundError(AgentEconomyError):
    """Raised when a requested job ID is not found (HTTP 404)."""
    pass


class JobStateError(AgentEconomyError):
    """Raised when an operation cannot be performed due to invalid job state (HTTP 409)."""
    pass


class JobExpiredError(AgentEconomyError):
    """Raised when an operation fails because the job has expired (HTTP 410)."""
    pass


class UnauthorizedError(AgentEconomyError):
    """Raised when an actor is not authorized to perform the action (HTTP 403)."""
    pass


class RateLimitExceededError(AgentEconomyError):
    """Raised when the agent exceeds maximum active jobs limit (HTTP 429)."""
    pass


class APIError(AgentEconomyError):
    """Raised when an unexpected server error occurs (HTTP 5xx)."""
    pass


class ConnectionError(AgentEconomyError):
    """Raised when communication with the RustChain node fails."""
    pass
