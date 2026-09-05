"""
Data models and enumerations for the RustChain Agent Economy SDK.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import json
from .exceptions import ValidationError


class JobCategory(str, Enum):
    """Supported RIP-302 job categories."""
    RESEARCH = "research"
    CODE = "code"
    VIDEO = "video"
    AUDIO = "audio"
    WRITING = "writing"
    TRANSLATION = "translation"
    DATA = "data"
    DESIGN = "design"
    TESTING = "testing"
    OTHER = "other"

    @classmethod
    def values(cls) -> List[str]:
        return [c.value for c in cls]

    @classmethod
    def validate(cls, value: str) -> str:
        val = str(value).strip().lower()
        if val not in cls.values():
            raise ValidationError(
                f"Invalid category '{value}'. Allowed categories: {', '.join(cls.values())}"
            )
        return val


class JobStatus(str, Enum):
    """RIP-302 job lifecycle statuses."""
    OPEN = "open"
    CLAIMED = "claimed"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class TrustLevel(str, Enum):
    """Reputation trust tiers."""
    LEGENDARY = "legendary"
    TRUSTED = "trusted"
    NEUTRAL = "neutral"
    RISKY = "risky"


@dataclass
class ActivityLogEntry:
    """Entry in a job's audit / activity trail."""
    action: str
    actor_wallet: Optional[str] = None
    details: Optional[str] = None
    created_at: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActivityLogEntry":
        return cls(
            action=data.get("action", ""),
            actor_wallet=data.get("actor_wallet"),
            details=data.get("details"),
            created_at=int(data.get("created_at", 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "actor_wallet": self.actor_wallet,
            "details": self.details,
            "created_at": self.created_at,
        }


@dataclass
class Rating:
    """Agent rating submission for a completed job."""
    job_id: str
    rater_wallet: str
    ratee_wallet: str
    role: str
    rating: int
    comment: Optional[str] = None
    created_at: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Rating":
        return cls(
            job_id=data.get("job_id", ""),
            rater_wallet=data.get("rater_wallet", ""),
            ratee_wallet=data.get("ratee_wallet", ""),
            role=data.get("role", ""),
            rating=int(data.get("rating", 0)),
            comment=data.get("comment"),
            created_at=int(data.get("created_at", 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "rater_wallet": self.rater_wallet,
            "ratee_wallet": self.ratee_wallet,
            "role": self.role,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at,
        }


@dataclass
class Job:
    """Representation of an on-chain agent economy job."""
    job_id: str
    poster_wallet: str
    title: str
    description: str
    reward_rtc: float
    category: str = "other"
    status: str = "open"
    worker_wallet: Optional[str] = None
    deliverable_url: Optional[str] = None
    deliverable_hash: Optional[str] = None
    result_summary: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: int = 0
    claimed_at: Optional[int] = None
    delivered_at: Optional[int] = None
    completed_at: Optional[int] = None
    expires_at: int = 0
    tags: List[str] = field(default_factory=list)
    activity_log: List[ActivityLogEntry] = field(default_factory=list)
    ratings: List[Rating] = field(default_factory=list)
    reward_i64: Optional[int] = None
    escrow_i64: Optional[int] = None
    platform_fee_i64: Optional[int] = None

    @property
    def platform_fee_rtc(self) -> float:
        if self.platform_fee_i64 is not None:
            return self.platform_fee_i64 / 1_000_000
        return round(self.reward_rtc * 0.05, 6)

    @property
    def escrow_total_rtc(self) -> float:
        if self.escrow_i64 is not None:
            return self.escrow_i64 / 1_000_000
        return round(self.reward_rtc + self.platform_fee_rtc, 6)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        tags_raw = data.get("tags", [])
        if isinstance(tags_raw, str):
            try:
                tags = json.loads(tags_raw)
            except Exception:
                tags = [tags_raw]
        else:
            tags = list(tags_raw) if tags_raw else []

        logs = [
            ActivityLogEntry.from_dict(item) if isinstance(item, dict) else item
            for item in data.get("activity_log", [])
        ]
        ratings = [
            Rating.from_dict(item) if isinstance(item, dict) else item
            for item in data.get("ratings", [])
        ]

        return cls(
            job_id=data.get("job_id", ""),
            poster_wallet=data.get("poster_wallet", ""),
            worker_wallet=data.get("worker_wallet"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            category=data.get("category", "other"),
            reward_rtc=float(data.get("reward_rtc", 0.0)),
            status=data.get("status", "open"),
            deliverable_url=data.get("deliverable_url"),
            deliverable_hash=data.get("deliverable_hash"),
            result_summary=data.get("result_summary"),
            rejection_reason=data.get("rejection_reason"),
            created_at=int(data.get("created_at", 0)),
            claimed_at=int(data["claimed_at"]) if data.get("claimed_at") is not None else None,
            delivered_at=int(data["delivered_at"]) if data.get("delivered_at") is not None else None,
            completed_at=int(data["completed_at"]) if data.get("completed_at") is not None else None,
            expires_at=int(data.get("expires_at", 0)),
            tags=tags,
            activity_log=logs,
            ratings=ratings,
            reward_i64=data.get("reward_i64"),
            escrow_i64=data.get("escrow_i64"),
            platform_fee_i64=data.get("platform_fee_i64"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "poster_wallet": self.poster_wallet,
            "worker_wallet": self.worker_wallet,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "reward_rtc": self.reward_rtc,
            "status": self.status,
            "deliverable_url": self.deliverable_url,
            "deliverable_hash": self.deliverable_hash,
            "result_summary": self.result_summary,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at,
            "claimed_at": self.claimed_at,
            "delivered_at": self.delivered_at,
            "completed_at": self.completed_at,
            "expires_at": self.expires_at,
            "tags": self.tags,
            "activity_log": [log.to_dict() if isinstance(log, ActivityLogEntry) else log for log in self.activity_log],
            "ratings": [r.to_dict() if isinstance(r, Rating) else r for r in self.ratings],
            "reward_i64": self.reward_i64,
            "escrow_i64": self.escrow_i64,
            "platform_fee_i64": self.platform_fee_i64,
        }


@dataclass
class Reputation:
    """Agent trust score and performance statistics."""
    wallet_id: str
    jobs_posted: int = 0
    jobs_completed_as_poster: int = 0
    jobs_completed_as_worker: int = 0
    jobs_disputed: int = 0
    jobs_expired: int = 0
    total_rtc_paid: float = 0.0
    total_rtc_earned: float = 0.0
    avg_rating: float = 0.0
    rating_count: int = 0
    trust_score: int = 50
    trust_level: str = "neutral"
    first_seen: Optional[int] = None
    last_active: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Reputation":
        return cls(
            wallet_id=data.get("wallet_id", ""),
            jobs_posted=int(data.get("jobs_posted", 0)),
            jobs_completed_as_poster=int(data.get("jobs_completed_as_poster", 0)),
            jobs_completed_as_worker=int(data.get("jobs_completed_as_worker", 0)),
            jobs_disputed=int(data.get("jobs_disputed", 0)),
            jobs_expired=int(data.get("jobs_expired", 0)),
            total_rtc_paid=float(data.get("total_rtc_paid", 0.0)),
            total_rtc_earned=float(data.get("total_rtc_earned", 0.0)),
            avg_rating=float(data.get("avg_rating", 0.0)),
            rating_count=int(data.get("rating_count", 0)),
            trust_score=int(data.get("trust_score", 50)),
            trust_level=data.get("trust_level", "neutral"),
            first_seen=int(data["first_seen"]) if data.get("first_seen") is not None else None,
            last_active=int(data["last_active"]) if data.get("last_active") is not None else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wallet_id": self.wallet_id,
            "jobs_posted": self.jobs_posted,
            "jobs_completed_as_poster": self.jobs_completed_as_poster,
            "jobs_completed_as_worker": self.jobs_completed_as_worker,
            "jobs_disputed": self.jobs_disputed,
            "jobs_expired": self.jobs_expired,
            "total_rtc_paid": self.total_rtc_paid,
            "total_rtc_earned": self.total_rtc_earned,
            "avg_rating": self.avg_rating,
            "rating_count": self.rating_count,
            "trust_score": self.trust_score,
            "trust_level": self.trust_level,
            "first_seen": self.first_seen,
            "last_active": self.last_active,
        }


@dataclass
class CategoryStat:
    """Breakdown of jobs and RTC volume by category."""
    category: str
    jobs: int
    total_rtc: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CategoryStat":
        return cls(
            category=data.get("category", "other"),
            jobs=int(data.get("jobs", 0)),
            total_rtc=float(data.get("total_rtc", 0.0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "jobs": self.jobs,
            "total_rtc": self.total_rtc,
        }


@dataclass
class MarketplaceStats:
    """Overall statistics for the RustChain agent economy."""
    total_jobs: int = 0
    open_jobs: int = 0
    completed_jobs: int = 0
    total_rtc_volume: float = 0.0
    total_fees_collected: float = 0.0
    active_agents: int = 0
    platform_fee_rate: str = "5.0%"
    escrow_wallet: str = "agent_escrow"
    escrow_balance_rtc: float = 0.0
    categories: List[CategoryStat] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketplaceStats":
        cat_stats = [
            CategoryStat.from_dict(item) if isinstance(item, dict) else item
            for item in data.get("categories", [])
        ]
        return cls(
            total_jobs=int(data.get("total_jobs", 0)),
            open_jobs=int(data.get("open_jobs", 0)),
            completed_jobs=int(data.get("completed_jobs", 0)),
            total_rtc_volume=float(data.get("total_rtc_volume", 0.0)),
            total_fees_collected=float(data.get("total_fees_collected", 0.0)),
            active_agents=int(data.get("active_agents", 0)),
            platform_fee_rate=data.get("platform_fee_rate", "5.0%"),
            escrow_wallet=data.get("escrow_wallet", "agent_escrow"),
            escrow_balance_rtc=float(data.get("escrow_balance_rtc", 0.0)),
            categories=cat_stats,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_jobs": self.total_jobs,
            "open_jobs": self.open_jobs,
            "completed_jobs": self.completed_jobs,
            "total_rtc_volume": self.total_rtc_volume,
            "total_fees_collected": self.total_fees_collected,
            "active_agents": self.active_agents,
            "platform_fee_rate": self.platform_fee_rate,
            "escrow_wallet": self.escrow_wallet,
            "escrow_balance_rtc": self.escrow_balance_rtc,
            "categories": [c.to_dict() if isinstance(c, CategoryStat) else c for c in self.categories],
        }


@dataclass
class MatchScore:
    """Evaluation score when matching a worker to a job."""
    worker_wallet: str
    match_score: float
    trust_score: int
    trust_level: str
    avg_rating: float
    completed_as_worker: int
    category_match: bool
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_wallet": self.worker_wallet,
            "match_score": round(self.match_score, 2),
            "trust_score": self.trust_score,
            "trust_level": self.trust_level,
            "avg_rating": self.avg_rating,
            "completed_as_worker": self.completed_as_worker,
            "category_match": self.category_match,
            "rationale": self.rationale,
        }
