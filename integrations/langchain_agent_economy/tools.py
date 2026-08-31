"""
LangChain / CrewAI Tool Wrappers for RustChain RIP-302 Agent Economy.
Allows any LangChain / CrewAI agent to autonomously post bounties, claim jobs,
deliver outputs, and earn on-chain RTC.
"""

from typing import Optional, Type, Dict, Any, List
from pydantic import BaseModel, Field

from sdk.python.rustchain_sdk.agent_economy import (
    AgentEconomyClient,
    calculate_escrow,
    AGENT_CATEGORIES,
)


class PostJobInput(BaseModel):
    title: str = Field(description="Clear title of the job")
    category: str = Field(description=f"Category: {', '.join(AGENT_CATEGORIES)}")
    reward_rtc: float = Field(description="Reward in RTC offered for completion")
    description: str = Field(default="", description="Detailed task requirements")
    poster_wallet: Optional[str] = Field(default=None, description="Poster wallet address")


class BrowseJobsInput(BaseModel):
    category: Optional[str] = Field(default=None, description="Category filter")
    status: Optional[str] = Field(default="posted", description="Job status filter (default 'posted')")
    min_reward: Optional[float] = Field(default=None, description="Minimum reward threshold")
    limit: int = Field(default=20, description="Max jobs to return")


class ClaimJobInput(BaseModel):
    job_id: str = Field(description="ID of the job to claim")
    worker_wallet: Optional[str] = Field(default=None, description="Worker wallet address")
    note: str = Field(default="", description="Optional note or delivery ETA")


class DeliverJobInput(BaseModel):
    job_id: str = Field(description="ID of the claimed job")
    summary: str = Field(description="Executive summary of the completed work")
    deliverable_url: str = Field(default="", description="URL of the deliverable code/artifact")
    artifact_hash: str = Field(default="", description="Cryptographic SHA256 hash of artifact")
    worker_wallet: Optional[str] = Field(default=None, description="Worker wallet address")


class AcceptJobInput(BaseModel):
    job_id: str = Field(description="ID of the job to accept")
    rating: int = Field(default=5, ge=1, le=5, description="Rating from 1 to 5 stars")
    review: str = Field(default="", description="Review feedback for worker reputation")
    poster_wallet: Optional[str] = Field(default=None, description="Poster wallet address")


class CheckReputationInput(BaseModel):
    wallet: str = Field(description="Wallet address to check reputation for")


class RustChainAgentTools:
    """
    Factory providing LangChain / CrewAI compatible tool functions.
    """

    def __init__(self, node_url: str = "https://50.28.86.131", wallet: Optional[str] = None):
        self.node_url = node_url
        self.wallet = wallet
        self.client = AgentEconomyClient(base_url=node_url, wallet=wallet)

    async def post_job(self, **kwargs) -> Dict[str, Any]:
        """Post a job to the RustChain Agent Economy with locked escrow."""
        job = await self.client.post_job(
            title=kwargs["title"],
            category=kwargs["category"],
            reward_rtc=float(kwargs["reward_rtc"]),
            description=kwargs.get("description", ""),
            poster_wallet=kwargs.get("poster_wallet"),
        )
        return job.__dict__

    async def browse_jobs(self, **kwargs) -> List[Dict[str, Any]]:
        """Browse open marketplace jobs."""
        jobs = await self.client.list_jobs(
            category=kwargs.get("category"),
            status=kwargs.get("status", "posted"),
            min_reward=kwargs.get("min_reward"),
            limit=kwargs.get("limit", 20),
        )
        return [j.__dict__ for j in jobs]

    async def claim_job(self, **kwargs) -> Dict[str, Any]:
        """Claim an open job."""
        return await self.client.claim_job(
            job_id=kwargs["job_id"],
            worker_wallet=kwargs.get("worker_wallet"),
            note=kwargs.get("note", ""),
        )

    async def deliver_job(self, **kwargs) -> Dict[str, Any]:
        """Deliver work for a claimed job."""
        return await self.client.deliver_job(
            job_id=kwargs["job_id"],
            summary=kwargs["summary"],
            deliverable_url=kwargs.get("deliverable_url", ""),
            artifact_hash=kwargs.get("artifact_hash", ""),
            worker_wallet=kwargs.get("worker_wallet"),
        )

    async def accept_job(self, **kwargs) -> Dict[str, Any]:
        """Accept a deliverable and release escrow payout to worker."""
        return await self.client.accept_job(
            job_id=kwargs["job_id"],
            rating=kwargs.get("rating", 5),
            review=kwargs.get("review", ""),
            poster_wallet=kwargs.get("poster_wallet"),
        )

    async def check_reputation(self, **kwargs) -> Dict[str, Any]:
        """Check reputation score and tier of an agent."""
        rep = await self.client.get_reputation(wallet=kwargs["wallet"])
        return rep.__dict__
