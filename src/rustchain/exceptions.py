"""
RustChain SDK — Custom exceptions.
"""

from typing import Optional


class RustChainError(Exception):
    """Base exception for all RustChain SDK errors."""

    def __init__(self, message: str, *, code: Optional[str] = None):
        super().__init__(message)
        self.code = code

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {super().__str__()}"
        return super().__str__()


class NodeUnreachableError(RustChainError):
    """Raised when the RustChain node cannot be reached."""

    def __init__(self, message: str = "RustChain node is unreachable"):
        super().__init__(message, code="NODE_UNREACHABLE")


class RateLimitError(RustChainError):
    """Raised when the API rate limit is exceeded."""

    def __init__(self, message: str = "API rate limit exceeded"):
        super().__init__(message, code="RATE_LIMITED")


class AttestationError(RustChainError):
    """Raised when attestation submission fails."""

    def __init__(
        self,
        message: str,
        *,
        check_failed: Optional[str] = None,
        detail: Optional[str] = None,
    ):
        super().__init__(message, code="ATTESTATION_FAILED")
        self.check_failed = check_failed
        self.detail = detail


class TransferError(RustChainError):
    """Raised when a transfer fails."""

    def __init__(
        self,
        message: str,
        *,
        tx_hash: Optional[str] = None,
        verified: bool = False,
    ):
        super().__init__(message, code="TRANSFER_FAILED")
        self.tx_hash = tx_hash
        self.verified = verified


class MinerNotFoundError(RustChainError):
    """Raised when a miner ID is not found."""

    def __init__(self, miner_id: str):
        super().__init__(f"Miner not found: {miner_id}", code="MINER_NOT_FOUND")
        self.miner_id = miner_id


class InvalidSignatureError(RustChainError):
    """Raised when an Ed25519 signature is invalid."""

    def __init__(self, message: str = "Ed25519 signature verification failed"):
        super().__init__(message, code="INVALID_SIGNATURE")


class InsufficientBalanceError(RustChainError):
    """Raised when the wallet has insufficient balance for a transfer."""

    def __init__(self, available: float, required: float):
        super().__init__(
            f"Insufficient balance: have {available} RTC, need {required} RTC",
            code="INSUFFICIENT_BALANCE",
        )
        self.available = available
        self.required = required
