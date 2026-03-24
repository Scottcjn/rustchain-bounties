# SPDX-License-Identifier: MIT
"""Typed exceptions for the RustChain SDK."""


class RustChainError(Exception):
    """Base exception for all RustChain SDK errors."""
    pass


class ConnectionError(RustChainError):
    """Failed to connect to RustChain node."""
    pass


class APIError(RustChainError):
    """Node returned an error response."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class WalletNotFoundError(RustChainError):
    """Wallet ID not found on chain."""
    pass


class InsufficientBalanceError(RustChainError):
    """Wallet has insufficient RTC balance."""
    pass


class InvalidSignatureError(RustChainError):
    """Transfer signature is invalid."""
    pass
