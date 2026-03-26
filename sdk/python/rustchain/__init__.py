"""
RustChain Python SDK
A pip-installable async API client for the RustChain Proof-of-Antiquity blockchain network.

Install: pip install rustchain
"""

__version__ = "0.1.0"

from .client import RustChainClient
from .exceptions import (
    RustChainError,
    APIError,
    AuthenticationError,
    ValidationError,
    TransferError,
)
from .explorer import ExplorerClient
from .cli import main as cli_main

__all__ = [
    "RustChainError",
    "APIError",
    "AuthenticationError",
    "ValidationError",
    "TransferError",
    "RustChainClient",
    "ExplorerClient",
    "cli_main",
]
