"""
Exception redaction for health check responses.

Maps known exception types to safe, generic messages that can be
returned to clients.  Full exception context is preserved in server-side
logs to aid debugging without leaking internals.
"""

import logging
from typing import Type, Dict, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exception for RPC request timeouts (distinct from database timeouts)
# ---------------------------------------------------------------------------
class RPCRequestTimeout(TimeoutError):
    """Exception raised when an RPC request times out."""
    pass


# ---------------------------------------------------------------------------
# Mapping of exception types to client-safe messages
# ---------------------------------------------------------------------------
_REDACTION_MAP: Dict[Type[BaseException], str] = {
    # Database errors
    ConnectionError: "Database connection error",
    TimeoutError: "Database connection timeout",
    # RPC / network errors
    ConnectionRefusedError: "RPC service unavailable",
    ConnectionResetError: "RPC connection reset",
    RPCRequestTimeout: "RPC request timed out",
    # Generic fallback registered below for safety
}

# Ensure every exception class appears exactly once (the dict overwrites
# duplicates above; we keep the last definition).  Add any additional
# exception types here.
_REDACTION_MAP[BrokenPipeError] = "Connection lost"
_REDACTION_MAP[PermissionError] = "Access denied"
_REDACTION_MAP[FileNotFoundError] = "Resource not found"
_REDACTION_MAP[ValueError] = "Invalid response data"
_REDACTION_MAP[TypeError] = "Unexpected data type"


def redact_error(
    exception_type: Type[BaseException],
    exception_message: str,
) -> str:
    """
    Map a known exception type to a safe, generic error message.

    The original exception type and message are logged at DEBUG level so
    that all context is retained server-side.  For any unrecognised
    exception type a generic ``"Internal server error"`` message is
    returned.

    Parameters
    ----------
    exception_type : Type[BaseException]
        The class of the exception that occurred (e.g. ``ConnectionError``).
    exception_message : str
        The original message from the exception.  This is *never*
        included in the returned string but is written to the log.

    Returns
    -------
    str
        A client-safe, generic description of the error.

    Examples
    --------
    >>> redact_error(ConnectionError, "could not connect to db:5432")
    'Database connection error'

    >>> redact_error(ValueError, "invalid status: -1")
    'Invalid response data'
    """
    # Log the original exception details for forensic analysis
    logger.debug(
        "Redacting exception type=%s message=%r",
        exception_type.__name__,
        exception_message,
    )

    # Look up the generic message; fall back to a safe default
    generic_message: Optional[str] = _REDACTION_MAP.get(exception_type)
    if generic_message is not None:
        return generic_message

    # Unmapped exception – log a warning so we know to add it later
    logger.warning(
        "Unmapped exception type %s – falling back to generic message",
        exception_type.__name__,
    )
    return "Internal server error"