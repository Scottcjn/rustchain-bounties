"""
RustChain Python SDK
~~~~~~~~~~~~~~~~~~~~~
Python SDK for the RustChain Proof-of-Antiquity blockchain node API.

Basic usage::

    from rustchain import RustChainClient

    client = RustChainClient(base_url="https://rustchain.org")
    health = client.health()
    print(health.ok, health.version)

    balance = client.get_balance("my-miner-id")
    print(balance.amount_rtc)

    # Lottery eligibility
    eligibility = client.get_lottery_eligibility("my-miner-id")
    print(eligibility.eligible, eligibility.reason)

    # Signed transfer
    tx = client.signed_transfer(
        from_address="RTCaaa...",
        to_address="RTCbbb...",
        amount_rtc=1.5,
        nonce=12345,
        public_key="ed25519_pubkey_hex",
        signature="ed25519_signature_hex",
    )
    print(tx.tx_hash)
"""

from rustchain.client import RustChainClient
from rustchain.exceptions import (
    RustChainError,
    NodeUnreachableError,
    RateLimitError,
    AttestationError,
    TransferError,
    MinerNotFoundError,
)

__version__ = "0.1.0"
__all__ = [
    "RustChainClient",
    "RustChainError",
    "NodeUnreachableError",
    "RateLimitError",
    "AttestationError",
    "TransferError",
    "MinerNotFoundError",
]
