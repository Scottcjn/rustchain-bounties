"""
RustChain RIP-302 Agent Economy Module.
Provides high-level typed abstractions, models, and clients for the
autonomous agent-to-agent job marketplace and on-chain reputation system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import asyncio

from .client import RustChainClient
from .exceptions import ValidationError, RustChainError


AGENT_CATEGORIES = [
    "research",
    "code",
    "video",
    "audio",
    "writing",
    "translation",
    "data",
    "design",
    "testing",
    "other",
]

PLATFORM_FEE_RATE = 0.05  # 5% platform fee


@dataclass
class EscrowCalculation:
    reward_rtc: float
    fee_rtc: float
    total_escrow_rtc: float


def calculate_escrow(reward_rtc: float) -> EscrowCalculation:
    """
    Calculate required escrow including the 5% platform fee.
    """
    if reward_rtc <= 0:
        raise ValidationError("reward_rtc must be positive")
    fee_rtc = round(reward_rtc * PLATFORM_FEE_RATE, 4)
    total_escrow_rtc = round(reward_rtc + fee_rtc, 4)
    return EscrowCalculation(
        reward_rtc=reward_rtc,
        fee_rtc=fee_rtc,
        total_escrow_rtc=total_escrow_rtc,
    )


@dataclass
class Job:
    id: str
    title: str
    category: str
    reward_rtc: float
    status: str
    description: str = ""
    poster_wallet: Optional[str] = None
    worker_wallet: Optional[str] = None
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    escrow_locked_rtc: Optional[float] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        return cls(
            id=str(data.get("id") or data.get("job_id", "")),
            title=str(data.get("title", "")),
            category=str(data.get("category", "")),
            reward_rtc=float(data.get("reward_rtc") or data.get("reward", 0.0)),
            status=str(data.get("status", "")),
            description=str(data.get("description", "")),
            poster_wallet=data.get("poster_wallet") or data.get("poster"),
            worker_wallet=data.get("worker_wallet") or data.get("worker"),
            created_at=data.get("created_at"),
            expires_at=data.get("expires_at"),
            escrow_locked_rtc=float(data.get("escrow_locked_rtc")) if data.get("escrow_locked_rtc") is not None else None,
            raw_data=data,
        )


@dataclass
class Reputation:
    trust_score: float
    trust_level: str
    avg_rating: float
    completed_jobs: int
    total_rtc_earned: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Reputation":
        rep = data.get("reputation") or data
        return cls(
            trust_score=float(rep.get("trust_score", 0.0)),
            trust_level=str(rep.get("trust_level", "neutral")),
            avg_rating=float(rep.get("avg_rating", 0.0)),
            completed_jobs=int(rep.get("completed_jobs", 0)),
            total_rtc_earned=float(rep.get("total_rtc_earned", 0.0)),
        )


@dataclass
class MarketplaceStats:
    active_agents: int
    completed_jobs: int
    open_jobs: int
    total_jobs: int
    total_rtc_volume: float
    total_fees_collected: float
    escrow_balance_rtc: float
    categories: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketplaceStats":
        stats = data.get("stats") or data
        return cls(
            active_agents=int(stats.get("active_agents", 0)),
            completed_jobs=int(stats.get("completed_jobs", 0)),
            open_jobs=int(stats.get("open_jobs", 0)),
            total_jobs=int(stats.get("total_jobs", 0)),
            total_rtc_volume=float(stats.get("total_rtc_volume", 0.0)),
            total_fees_collected=float(stats.get("total_fees_collected", 0.0)),
            escrow_balance_rtc=float(stats.get("escrow_balance_rtc", 0.0)),
            categories=stats.get("categories", []),
        )


class AgentEconomyClient:
    """
    High-level async client for the RIP-302 RustChain Agent Economy.
    """

    def __init__(
        self,
        base_url: str = "https://50.28.86.131",
        wallet: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.wallet = wallet
        self._client = RustChainClient(base_url=base_url, timeout=timeout)

    @property
    def rpc(self) -> RustChainClient:
        return self._client

    async def get_stats(self) -> MarketplaceStats:
        res = await self._client.get_agent_stats()
        return MarketplaceStats.from_dict(res)

    async def list_jobs(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        min_reward: Optional[float] = None,
    ) -> List[Job]:
        res = await self._client.list_agent_jobs(
            category=category,
            status=status,
            limit=limit,
            offset=offset,
            min_reward=min_reward,
        )
        job_list = res.get("jobs", []) if isinstance(res, dict) else res
        return [Job.from_dict(j) for j in job_list]

    async def get_job(self, job_id: str) -> Dict[str, Any]:
        return await self._client.get_agent_job(job_id)

    async def post_job(
        self,
        title: str,
        category: str,
        reward_rtc: float,
        description: str = "",
        poster_wallet: Optional[str] = None,
        expires_at: Optional[str] = None,
    ) -> Job:
        poster = poster_wallet or self.wallet
        if not poster:
            raise ValidationError("poster_wallet must be provided in method call or constructor")
        res = await self._client.post_agent_job(
            poster_wallet=poster,
            title=title,
            category=category,
            reward_rtc=reward_rtc,
            description=description,
            expires_at=expires_at,
        )
        job_data = res.get("job") or res
        return Job.from_dict(job_data)

    async def claim_job(
        self,
        job_id: str,
        worker_wallet: Optional[str] = None,
        note: str = "",
    ) -> Dict[str, Any]:
        worker = worker_wallet or self.wallet
        if not worker:
            raise ValidationError("worker_wallet must be provided in method call or constructor")
        return await self._client.claim_agent_job(
            job_id=job_id,
            worker_wallet=worker,
            note=note,
        )

    async def deliver_job(
        self,
        job_id: str,
        deliverable_url: str = "",
        summary: str = "",
        artifact_hash: str = "",
        worker_wallet: Optional[str] = None,
    ) -> Dict[str, Any]:
        worker = worker_wallet or self.wallet
        if not worker:
            raise ValidationError("worker_wallet must be provided in method call or constructor")
        return await self._client.deliver_agent_job(
            job_id=job_id,
            worker_wallet=worker,
            deliverable_url=deliverable_url,
            summary=summary,
            artifact_hash=artifact_hash,
        )

    async def accept_job(
        self,
        job_id: str,
        rating: int = 5,
        review: str = "",
        poster_wallet: Optional[str] = None,
    ) -> Dict[str, Any]:
        poster = poster_wallet or self.wallet
        if not poster:
            raise ValidationError("poster_wallet must be provided in method call or constructor")
        return await self._client.accept_agent_job(
            job_id=job_id,
            poster_wallet=poster,
            rating=rating,
            review=review,
        )

    async def dispute_job(
        self,
        job_id: str,
        reason: str = "",
        poster_wallet: Optional[str] = None,
    ) -> Dict[str, Any]:
        poster = poster_wallet or self.wallet
        if not poster:
            raise ValidationError("poster_wallet must be provided in method call or constructor")
        return await self._client.dispute_agent_job(
            job_id=job_id,
            poster_wallet=poster,
            reason=reason,
        )

    async def cancel_job(
        self,
        job_id: str,
        reason: str = "",
        poster_wallet: Optional[str] = None,
    ) -> Dict[str, Any]:
        poster = poster_wallet or self.wallet
        if not poster:
            raise ValidationError("poster_wallet must be provided in method call or constructor")
        return await self._client.cancel_agent_job(
            job_id=job_id,
            poster_wallet=poster,
            reason=reason,
        )

    async def get_reputation(self, wallet: Optional[str] = None) -> Reputation:
        target = wallet or self.wallet
        if not target:
            raise ValidationError("wallet must be provided in method call or constructor")
        res = await self._client.get_agent_reputation(target)
        return Reputation.from_dict(res)
