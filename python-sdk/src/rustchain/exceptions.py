"""Typed exceptions for RustChain SDK.

Copyright (c) 2026 思捷娅科技 (SJYKJ)
MIT License
"""


class RustChainError(Exception):
    """Base exception for all RustChain SDK errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class NodeUnhealthyError(RustChainError):
    """Raised when the node health check fails."""


class MinerNotFoundError(RustChainError):
    """Raised when a miner or wallet is not found (404)."""


class InvalidSignatureError(RustChainError):
    """Raised when a signature verification fails (401/403)."""


class RateLimitError(RustChainError):
    """Raised when rate limited by the node (429)."""


class BadRequestError(RustChainError):
    """Raised when the request is invalid (400)."""
