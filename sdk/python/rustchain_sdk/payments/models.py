"""
RustChain Agent-to-Agent Payments Data Models & Types
Defines schemas for Upvote+Donate, Cross-Wallet Bridge, x402 Protocol, and Cross-Bounty Escrow.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional


class DonationTier:
    """Standard RTC donation tiers."""
    MICRO = 0.001   # Microtip / quick reaction
    SMALL = 0.01    # Upvote + standard tip
    MEDIUM = 0.1    # High value post / tutorial tip
    LARGE = 1.0     # Creator grant / major tip

    ALL_TIERS = [MICRO, SMALL, MEDIUM, LARGE]


class BridgeDirection(str, Enum):
    """Direction of cross-wallet bridge transfer."""
    RTC_TO_BOTTUBE = "rtc_to_botttube"
    BOTTUBE_TO_RTC = "botttube_to_rtc"


class BridgeStatus(str, Enum):
    """Lifecycle state of a bridge transaction."""
    PENDING = "pending"
    LOCKED = "locked"
    SETTLED = "settled"
    REFUNDED = "refunded"
    FAILED = "failed"


class BountyStatus(str, Enum):
    """Status of a cross-bounty."""
    OPEN = "open"
    CLAIMED = "claimed"
    UNDER_REVIEW = "under_review"
    SETTLED = "settled"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class UpvoteRecord:
    """Represents an upvote (free signal or with RTC donation)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    voter: str = ""
    creator: str = ""
    is_donation: bool = False
    amount: float = 0.0
    platform: str = "bottube"
    hardware_multiplier: float = 1.0
    signature: Optional[str] = None
    public_key: Optional[str] = None
    tx_hash: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentStats:
    """Aggregated statistics for a piece of content."""
    content_id: str = ""
    upvote_count: int = 0
    donation_count: int = 0
    total_donated_rtc: float = 0.0
    unique_voters: List[str] = field(default_factory=list)
    donations_by_tier: Dict[str, int] = field(default_factory=lambda: {
        "0.001": 0,
        "0.01": 0,
        "0.1": 0,
        "1.0": 0,
        "custom": 0,
    })
    top_donors: Dict[str, float] = field(default_factory=dict)
    average_multiplier: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BridgeTransaction:
    """Represents an atomic RTC ↔ BoTTube cross-wallet bridge transaction."""
    tx_id: str = field(default_factory=lambda: f"br_{uuid.uuid4().hex[:12]}")
    direction: BridgeDirection = BridgeDirection.RTC_TO_BOTTUBE
    sender: str = ""
    recipient: str = ""
    amount: float = 0.0
    fee: float = 0.0
    net_amount: float = 0.0
    exchange_rate: float = 1.0
    status: BridgeStatus = BridgeStatus.PENDING
    escrow_lock_id: str = ""
    signature: Optional[str] = None
    receipt_hash: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    settled_at: Optional[float] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["direction"] = self.direction.value if isinstance(self.direction, BridgeDirection) else self.direction
        d["status"] = self.status.value if isinstance(self.status, BridgeStatus) else self.status
        return d


@dataclass
class X402Challenge:
    """Challenge returned by a server requiring 402 payment."""
    quote_id: str = field(default_factory=lambda: f"q402_{uuid.uuid4().hex[:12]}")
    price_rtc: float = 0.0
    recipient: str = ""
    realm: str = "rustchain"
    currency: str = "RTC"
    service_name: str = "Agent Service"
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex)
    expires_at: float = field(default_factory=lambda: time.time() + 300)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class X402PaymentProof:
    """Proof of payment supplied by client in X-Payment header."""
    payer: str = ""
    recipient: str = ""
    amount: float = 0.0
    quote_id: str = ""
    nonce: str = ""
    timestamp: float = field(default_factory=time.time)
    signature: str = ""
    public_key: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BountyClaim:
    """Claim on a dual-currency bounty."""
    claim_id: str = field(default_factory=lambda: f"clm_{uuid.uuid4().hex[:8]}")
    claimant_rtc: str = ""
    claimant_bottube: str = ""
    proof_url: str = ""
    notes: str = ""
    submitted_at: float = field(default_factory=time.time)
    approved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DualCurrencyBounty:
    """Bounty escrow managing both RTC and BoTTube payouts."""
    bounty_id: str = ""
    title: str = ""
    description: str = ""
    poster_rtc: str = ""
    poster_bottube: str = ""
    escrow_rtc: float = 0.0
    escrow_bottube: float = 0.0
    status: BountyStatus = BountyStatus.OPEN
    claims: List[BountyClaim] = field(default_factory=list)
    payout_records: List[Dict[str, Any]] = field(default_factory=list)
    stipulations: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    settled_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value if isinstance(self.status, BountyStatus) else self.status
        d["claims"] = [c.to_dict() if isinstance(c, BountyClaim) else c for c in self.claims]
        return d
