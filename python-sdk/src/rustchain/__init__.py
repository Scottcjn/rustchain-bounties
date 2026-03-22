"""RustChain Python SDK — interact with RustChain nodes.

Copyright (c) 2026 思捷娅科技 (SJYKJ)
MIT License
"""

__version__ = "0.1.0"

from .client import RustChainClient
from .exceptions import (
    RustChainError,
    NodeUnhealthyError,
    MinerNotFoundError,
    InvalidSignatureError,
    RateLimitError,
    BadRequestError,
)

__all__ = [
    "RustChainClient",
    "RustChainError",
    "NodeUnhealthyError",
    "MinerNotFoundError",
    "InvalidSignatureError",
    "RateLimitError",
    "BadRequestError",
]
