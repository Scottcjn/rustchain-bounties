"""RustChain Python SDK - Interact with RustChain nodes.

Example:
    >>> import asyncio
    >>> from rustchain import RustChainClient
    >>> 
    >>> async def main():
    ...     async with RustChainClient() as client:
    ...         health = await client.health()
    ...         print(f"Node status: {health.status}")
    ...         
    ...         epoch = await client.epoch()
    ...         print(f"Current epoch: {epoch.current_epoch}")
    ...         
    ...         balance = await client.balance("my-wallet-id")
    ...         print(f"Balance: {balance.balance} RTC")
    >>> 
    >>> asyncio.run(main())
"""

__version__ = "0.1.0"
__author__ = "HuiNeng"
__email__ = "3650306360@qq.com"

from .client import RustChainClient
from .models import (
    HealthStatus,
    EpochInfo,
    Miner,
    Balance,
    TransferResult,
    Block,
    Transaction,
    AttestationStatus,
    ExplorerBlocks,
    ExplorerTransactions,
)
from .exceptions import (
    RustChainError,
    ConnectionError,
    TimeoutError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    ServerError,
    RateLimitError,
    TransferError,
    InsufficientFundsError,
    InvalidSignatureError,
    AttestationError,
)

__all__ = [
    "RustChainClient",
    "HealthStatus",
    "EpochInfo",
    "Miner",
    "Balance",
    "TransferResult",
    "Block",
    "Transaction",
    "AttestationStatus",
    "ExplorerBlocks",
    "ExplorerTransactions",
    "RustChainError",
    "ConnectionError",
    "TimeoutError",
    "ValidationError",
    "AuthenticationError",
    "NotFoundError",
    "ServerError",
    "RateLimitError",
    "TransferError",
    "InsufficientFundsError",
    "InvalidSignatureError",
    "AttestationError",
]