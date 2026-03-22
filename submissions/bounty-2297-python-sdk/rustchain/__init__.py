"""
RustChain Python SDK
~~~~~~~~~~~~~~~~~~~~

A pip-installable Python SDK for interacting with RustChain nodes.

Provides both async and sync interfaces for all RustChain node APIs,
including health checks, epoch info, miner management, balance queries,
signed transfers, attestation status, and block explorer functionality.

Basic usage::

    >>> from rustchain import RustChainClient
    >>> client = RustChainClient("https://50.28.86.131")
    >>> health = client.health()
    >>> print(health.status)
    'ok'

Async usage::

    >>> from rustchain import AsyncRustChainClient
    >>> async with AsyncRustChainClient("https://50.28.86.131") as client:
    ...     health = await client.health()
    ...     print(health.status)
    'ok'

:copyright: (c) 2026 RustChain Contributors
:license: Apache-2.0
"""

__version__ = "1.0.0"
__author__ = "ElromEvedElElyon"
__license__ = "Apache-2.0"

from rustchain.client import AsyncRustChainClient, RustChainClient
from rustchain.errors import (
    RustChainError,
    RustChainConnectionError,
    RustChainAPIError,
    RustChainTimeoutError,
    RustChainAuthError,
    RustChainValidationError,
)
from rustchain.models import (
    HealthStatus,
    EpochInfo,
    Miner,
    Balance,
    TransferResult,
    AttestationStatus,
    Block,
    Transaction,
)
from rustchain.explorer import ExplorerAPI, AsyncExplorerAPI

__all__ = [
    # Clients
    "RustChainClient",
    "AsyncRustChainClient",
    # Explorer
    "ExplorerAPI",
    "AsyncExplorerAPI",
    # Models
    "HealthStatus",
    "EpochInfo",
    "Miner",
    "Balance",
    "TransferResult",
    "AttestationStatus",
    "Block",
    "Transaction",
    # Errors
    "RustChainError",
    "RustChainConnectionError",
    "RustChainAPIError",
    "RustChainTimeoutError",
    "RustChainAuthError",
    "RustChainValidationError",
]
