"""
rustchain.models
~~~~~~~~~~~~~~~~

Typed dataclasses representing RustChain API response objects.

All models use :func:`dataclasses.dataclass` with ``frozen=True`` for
immutability and include a :meth:`from_dict` class method that safely
parses raw JSON dictionaries returned by the node.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


def _parse_timestamp(value: Any) -> Optional[datetime]:
    """Best-effort ISO-8601 / epoch timestamp parser."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    if isinstance(value, str):
        # Try ISO format first, then epoch-string fallback
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        try:
            return datetime.utcfromtimestamp(float(value))
        except (ValueError, OSError):
            pass
    return None


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HealthStatus:
    """Node health check response."""

    status: str
    version: str = ""
    uptime: float = 0.0
    block_height: int = 0
    peers: int = 0
    syncing: bool = False
    timestamp: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HealthStatus:
        return cls(
            status=data.get("status", "unknown"),
            version=str(data.get("version", "")),
            uptime=float(data.get("uptime", 0)),
            block_height=int(data.get("block_height", data.get("blockHeight", 0))),
            peers=int(data.get("peers", data.get("peer_count", 0))),
            syncing=bool(data.get("syncing", False)),
            timestamp=_parse_timestamp(data.get("timestamp")),
        )


# ---------------------------------------------------------------------------
# Epoch
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EpochInfo:
    """Current epoch information."""

    epoch: int
    start_block: int = 0
    end_block: int = 0
    current_block: int = 0
    progress: float = 0.0
    estimated_end: Optional[datetime] = None
    difficulty: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EpochInfo:
        return cls(
            epoch=int(data.get("epoch", data.get("current_epoch", 0))),
            start_block=int(data.get("start_block", data.get("startBlock", 0))),
            end_block=int(data.get("end_block", data.get("endBlock", 0))),
            current_block=int(data.get("current_block", data.get("currentBlock", 0))),
            progress=float(data.get("progress", 0)),
            estimated_end=_parse_timestamp(data.get("estimated_end")),
            difficulty=float(data.get("difficulty", 0)),
        )


# ---------------------------------------------------------------------------
# Miners
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Miner:
    """Active miner information."""

    miner_id: str
    wallet_id: str = ""
    hardware: str = ""
    status: str = "active"
    hashrate: float = 0.0
    blocks_mined: int = 0
    last_seen: Optional[datetime] = None
    attestation_valid: bool = False
    region: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Miner:
        return cls(
            miner_id=str(data.get("miner_id", data.get("minerId", data.get("id", "")))),
            wallet_id=str(data.get("wallet_id", data.get("walletId", ""))),
            hardware=str(data.get("hardware", data.get("hw_type", ""))),
            status=str(data.get("status", "active")),
            hashrate=float(data.get("hashrate", 0)),
            blocks_mined=int(data.get("blocks_mined", data.get("blocksMined", 0))),
            last_seen=_parse_timestamp(data.get("last_seen", data.get("lastSeen"))),
            attestation_valid=bool(data.get("attestation_valid", data.get("attestationValid", False))),
            region=str(data.get("region", "")),
        )


# ---------------------------------------------------------------------------
# Balance
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Balance:
    """Wallet balance information."""

    wallet_id: str
    balance: float
    available: float = 0.0
    locked: float = 0.0
    pending: float = 0.0
    currency: str = "RTC"
    last_updated: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], wallet_id: str = "") -> Balance:
        wid = str(data.get("wallet_id", data.get("walletId", data.get("address", wallet_id))))
        bal = float(data.get("balance", 0))
        avail = float(data.get("available", bal))
        return cls(
            wallet_id=wid,
            balance=bal,
            available=avail,
            locked=float(data.get("locked", data.get("staked", 0))),
            pending=float(data.get("pending", 0)),
            currency=str(data.get("currency", "RTC")),
            last_updated=_parse_timestamp(data.get("last_updated", data.get("lastUpdated"))),
        )


# ---------------------------------------------------------------------------
# Transfer
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TransferResult:
    """Result of a signed RTC transfer."""

    tx_hash: str
    status: str
    from_wallet: str = ""
    to_wallet: str = ""
    amount: float = 0.0
    fee: float = 0.0
    block_height: Optional[int] = None
    timestamp: Optional[datetime] = None
    confirmations: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TransferResult:
        return cls(
            tx_hash=str(data.get("tx_hash", data.get("txHash", data.get("hash", "")))),
            status=str(data.get("status", "pending")),
            from_wallet=str(data.get("from", data.get("from_wallet", data.get("sender", "")))),
            to_wallet=str(data.get("to", data.get("to_wallet", data.get("recipient", "")))),
            amount=float(data.get("amount", 0)),
            fee=float(data.get("fee", 0)),
            block_height=data.get("block_height", data.get("blockHeight")),
            timestamp=_parse_timestamp(data.get("timestamp")),
            confirmations=int(data.get("confirmations", 0)),
        )


# ---------------------------------------------------------------------------
# Attestation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AttestationStatus:
    """Miner Proof-of-Antiquity attestation status."""

    miner_id: str
    valid: bool
    hardware: str = ""
    attestation_epoch: int = 0
    expires_epoch: int = 0
    score: float = 0.0
    last_verified: Optional[datetime] = None
    verification_method: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any], miner_id: str = "") -> AttestationStatus:
        mid = str(data.get("miner_id", data.get("minerId", miner_id)))
        return cls(
            miner_id=mid,
            valid=bool(data.get("valid", data.get("is_valid", data.get("attestation_valid", False)))),
            hardware=str(data.get("hardware", data.get("hw_type", ""))),
            attestation_epoch=int(data.get("attestation_epoch", data.get("attestationEpoch", 0))),
            expires_epoch=int(data.get("expires_epoch", data.get("expiresEpoch", 0))),
            score=float(data.get("score", data.get("attestation_score", 0))),
            last_verified=_parse_timestamp(data.get("last_verified", data.get("lastVerified"))),
            verification_method=str(data.get("verification_method", data.get("method", ""))),
        )


# ---------------------------------------------------------------------------
# Block Explorer Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Transaction:
    """A single transaction on the RustChain."""

    tx_hash: str
    from_wallet: str = ""
    to_wallet: str = ""
    amount: float = 0.0
    fee: float = 0.0
    status: str = "confirmed"
    block_height: int = 0
    timestamp: Optional[datetime] = None
    tx_type: str = "transfer"
    data: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Transaction:
        return cls(
            tx_hash=str(data.get("tx_hash", data.get("txHash", data.get("hash", "")))),
            from_wallet=str(data.get("from", data.get("from_wallet", data.get("sender", "")))),
            to_wallet=str(data.get("to", data.get("to_wallet", data.get("recipient", "")))),
            amount=float(data.get("amount", data.get("value", 0))),
            fee=float(data.get("fee", data.get("gas_fee", 0))),
            status=str(data.get("status", "confirmed")),
            block_height=int(data.get("block_height", data.get("blockHeight", data.get("block", 0)))),
            timestamp=_parse_timestamp(data.get("timestamp")),
            tx_type=str(data.get("type", data.get("tx_type", "transfer"))),
            data=data.get("data"),
        )


@dataclass(frozen=True)
class Block:
    """A single block on the RustChain."""

    height: int
    block_hash: str = ""
    previous_hash: str = ""
    miner_id: str = ""
    timestamp: Optional[datetime] = None
    transactions: List[Transaction] = field(default_factory=list)
    tx_count: int = 0
    size: int = 0
    difficulty: float = 0.0
    nonce: int = 0
    epoch: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Block:
        txs_raw = data.get("transactions", [])
        txs: List[Transaction] = []
        if isinstance(txs_raw, list):
            for tx in txs_raw:
                if isinstance(tx, dict):
                    txs.append(Transaction.from_dict(tx))
        return cls(
            height=int(data.get("height", data.get("block_height", data.get("number", 0)))),
            block_hash=str(data.get("hash", data.get("block_hash", data.get("blockHash", "")))),
            previous_hash=str(data.get("previous_hash", data.get("previousHash", data.get("parent_hash", "")))),
            miner_id=str(data.get("miner", data.get("miner_id", data.get("minerId", "")))),
            timestamp=_parse_timestamp(data.get("timestamp")),
            transactions=txs,
            tx_count=int(data.get("tx_count", data.get("txCount", len(txs)))),
            size=int(data.get("size", 0)),
            difficulty=float(data.get("difficulty", 0)),
            nonce=int(data.get("nonce", 0)),
            epoch=int(data.get("epoch", 0)),
        )
