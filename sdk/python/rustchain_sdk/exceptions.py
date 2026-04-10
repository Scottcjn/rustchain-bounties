"""
RustChain SDK — Custom Exceptions
"""


class RustChainError(Exception):
    """Base exception for all RustChain SDK errors."""
    pass


class NodeOfflineError(RustChainError):
    """Raised when the RustChain node is unreachable."""
    pass


class APIError(RustChainError):
    """Raised when the API returns an error response."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class WalletNotFoundError(RustChainError):
    """Raised when a wallet cannot be found on the network."""
    pass


class InsufficientBalanceError(RustChainError):
    """Raised when a wallet has insufficient balance for a transfer."""
    pass
