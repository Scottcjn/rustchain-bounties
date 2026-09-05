"""
CrewAI Multi-Agent Delegation Example using RustChain RIP-302 Agent Economy.
Demonstrates how autonomous CrewAI agents can create tasks and hire external agents
on the decentralized marketplace using real RTC escrow.
"""

from typing import Dict, Any
from .tools import RustChainAgentTools


class RustChainCrewDelegator:
    """
    CrewAI delegation harness that hooks task delegation into RustChain Agent Economy.
    """

    def __init__(self, node_url: str = "https://50.28.86.131", poster_wallet: str = "crew_manager_wallet"):
        self.tools = RustChainAgentTools(node_url=node_url, wallet=poster_wallet)
        self.poster_wallet = poster_wallet

    async def delegate_task_to_marketplace(
        self,
        task_name: str,
        category: str,
        reward_rtc: float,
        specification: str,
    ) -> Dict[str, Any]:
        """
        Escrow funds on RustChain to outsource a task to the open agent economy.
        """
        print(f"[CrewAI Manager] Outsourcing task '{task_name}' to RustChain ({reward_rtc} RTC)...")
        job = await self.tools.post_job(
            title=task_name,
            category=category,
            reward_rtc=reward_rtc,
            description=specification,
            poster_wallet=self.poster_wallet,
        )
        print(f"[CrewAI Manager] Job {job['id']} posted with escrow locked!")
        return job

    async def verify_and_settle(self, job_id: str, rating: int = 5, feedback: str = "Verified by CrewAI QA") -> Dict[str, Any]:
        """
        Verify deliverable and release escrow payment to the completing agent.
        """
        print(f"[CrewAI Manager] Settling payment for job {job_id}...")
        res = await self.tools.accept_job(
            job_id=job_id,
            rating=rating,
            review=feedback,
            poster_wallet=self.poster_wallet,
        )
        print(f"[CrewAI Manager] Escrow released! Settlement: {res.get('payout')}")
        return res
