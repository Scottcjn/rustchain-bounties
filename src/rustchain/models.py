"""
RustChain SDK — Data models / typed response objects.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@dataclass
class HealthResponse:
    ok: bool
    version: str
    uptime_s: int
    db_rw: bool
    backup_age_hours: float
    tip_age_slots: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthResponse":
        return cls(
            ok=data["ok"],
            version=data["version"],
            uptime_s=data["uptime_s"],
            db_rw=data["db_rw"],
            backup_age_hours=data["backup_age_hours"],
            tip_age_slots=data["tip_age_slots"],
        )


# ---------------------------------------------------------------------------
# Epoch
# ---------------------------------------------------------------------------


@dataclass
class EpochResponse:
    epoch: int
    slot: int
    blocks_per_epoch: int
    epoch_pot: float
    enrolled_miners: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EpochResponse":
        return cls(
            epoch=data["epoch"],
            slot=data["slot"],
            blocks_per_epoch=data["blocks_per_epoch"],
            epoch_pot=data["epoch_pot"],
            enrolled_miners=data["enrolled_miners"],
        )


# ---------------------------------------------------------------------------
# Miner
# ---------------------------------------------------------------------------


@dataclass
class Miner:
    miner: str
    device_family: str
    device_arch: str
    hardware_type: str
    antiquity_multiplier: float
    entropy_score: float
    last_attest: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Miner":
        return cls(
            miner=data["miner"],
            device_family=data["device_family"],
            device_arch=data["device_arch"],
            hardware_type=data["hardware_type"],
            antiquity_multiplier=data["antiquity_multiplier"],
            entropy_score=data["entropy_score"],
            last_attest=data["last_attest"],
        )


# ---------------------------------------------------------------------------
# Wallet Balance
# ---------------------------------------------------------------------------


@dataclass
class BalanceResponse:
    miner_id: str
    amount_rtc: float
    amount_i64: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BalanceResponse":
        return cls(
            miner_id=data["miner_id"],
            amount_rtc=data["amount_rtc"],
            amount_i64=data["amount_i64"],
        )


# ---------------------------------------------------------------------------
# Transfer History
# ---------------------------------------------------------------------------


@dataclass
class TransferRecord:
    tx_id: str
    tx_hash: str
    from_addr: str
    to_addr: str
    amount: float
    amount_i64: int
    amount_rtc: float
    timestamp: int
    created_at: int
    confirmed_at: Optional[int]
    confirms_at: Optional[int]
    status: str
    raw_status: str
    status_reason: Optional[str]
    confirmations: int
    direction: str
    counterparty: str
    reason: Optional[str]
    memo: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransferRecord":
        return cls(
            tx_id=data["tx_id"],
            tx_hash=data["tx_hash"],
            from_addr=data["from_addr"],
            to_addr=data["to_addr"],
            amount=data["amount"],
            amount_i64=data["amount_i64"],
            amount_rtc=data["amount_rtc"],
            timestamp=data["timestamp"],
            created_at=data["created_at"],
            confirmed_at=data.get("confirmed_at"),
            confirms_at=data.get("confirms_at"),
            status=data["status"],
            raw_status=data["raw_status"],
            status_reason=data.get("status_reason"),
            confirmations=data["confirmations"],
            direction=data["direction"],
            counterparty=data["counterparty"],
            reason=data.get("reason"),
            memo=data.get("memo"),
        )


# ---------------------------------------------------------------------------
# Signed Transfer
# ---------------------------------------------------------------------------


@dataclass
class TransferResponse:
    ok: bool
    verified: bool
    phase: str
    tx_hash: str
    amount_rtc: float
    chain_id: str
    confirms_in_hours: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransferResponse":
        return cls(
            ok=data["ok"],
            verified=data["verified"],
            phase=data["phase"],
            tx_hash=data["tx_hash"],
            amount_rtc=data["amount_rtc"],
            chain_id=data["chain_id"],
            confirms_in_hours=data["confirms_in_hours"],
        )


# ---------------------------------------------------------------------------
# Attestation
# ---------------------------------------------------------------------------


@dataclass
class AttestationResponse:
    success: bool
    enrolled: bool
    epoch: Optional[int] = None
    multiplier: Optional[float] = None
    next_settlement_slot: Optional[int] = None
    error: Optional[str] = None
    check_failed: Optional[str] = None
    detail: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttestationResponse":
        return cls(
            success=data["success"],
            enrolled=data.get("enrolled", False),
            epoch=data.get("epoch"),
            multiplier=data.get("multiplier"),
            next_settlement_slot=data.get("next_settlement_slot"),
            error=data.get("error"),
            check_failed=data.get("check_failed"),
            detail=data.get("detail"),
        )


# ---------------------------------------------------------------------------
# Lottery Eligibility
# ---------------------------------------------------------------------------


@dataclass
class LotteryEligibility:
    miner_id: str
    epoch: int
    eligible: bool
    chance: float  # 0.0 – 1.0
    antiquity_multiplier: float
    entropy_score: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LotteryEligibility":
        return cls(
            miner_id=data["miner_id"],
            epoch=data["epoch"],
            eligible=data["eligible"],
            chance=data["chance"],
            antiquity_multiplier=data["antiquity_multiplier"],
            entropy_score=data["entropy_score"],
        )


# ---------------------------------------------------------------------------
# Fingerprint (for attestation)
# ---------------------------------------------------------------------------


@dataclass
class Fingerprint:
    """
    Hardware fingerprint bundle submitted during attestation.
    All fields are required by the RustChain node.
    """

    clock_skew: Dict[str, Any]
    cache_timing: Dict[str, Any]
    simd_identity: Dict[str, Any]
    thermal_entropy: Dict[str, Any]
    instruction_jitter: Dict[str, Any]
    behavioral_heuristics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clock_skew": self.clock_skew,
            "cache_timing": self.cache_timing,
            "simd_identity": self.simd_identity,
            "thermal_entropy": self.thermal_entropy,
            "instruction_jitter": self.instruction_jitter,
            "behavioral_heuristics": self.behavioral_heuristics,
        }
