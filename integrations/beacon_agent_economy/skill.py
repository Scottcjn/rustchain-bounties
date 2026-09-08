"""
RustChain Beacon Autonomous Skill for RIP-302 Agent Economy.
Enables Beacon workers and Grazer nodes to poll the decentralized marketplace,
claim jobs matching their capabilities, execute tasks, and submit deliverables.
"""

import hashlib
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable

from sdk.python.rustchain_sdk.agent_economy import (
    AgentEconomyClient,
    Job,
)


class BeaconAgentEconomyWorker:
    """
    Autonomous Beacon Agent that continuously monitors for bounties and completes them.
    """

    def __init__(
        self,
        node_url: str = "https://50.28.86.131",
        worker_wallet: str = "beacon_worker_01",
        supported_categories: Optional[List[str]] = None,
    ):
        self.node_url = node_url
        self.worker_wallet = worker_wallet
        self.supported_categories = supported_categories or ["research", "code", "testing", "data"]
        self.client = AgentEconomyClient(base_url=node_url, wallet=worker_wallet)

    async def scan_and_claim(self, min_reward_rtc: float = 10.0) -> Optional[Job]:
        """
        Scan open jobs matching worker capabilities and claim the highest value job.
        """
        open_jobs = await self.client.list_jobs(status="posted", limit=50)
        matching_jobs = [
            j for j in open_jobs
            if j.category in self.supported_categories and j.reward_rtc >= min_reward_rtc
        ]

        if not matching_jobs:
            return None

        # Pick highest reward job
        best_job = sorted(matching_jobs, key=lambda j: j.reward_rtc, reverse=True)[0]
        print(f"[Beacon Worker] Claiming job {best_job.id}: '{best_job.title}' ({best_job.reward_rtc} RTC)...")

        await self.client.claim_job(
            job_id=best_job.id,
            worker_wallet=self.worker_wallet,
            note="Beacon autonomous node claiming task",
        )
        return best_job

    async def execute_and_deliver(
        self,
        job: Job,
        executor_fn: Callable[[Job], str],
    ) -> Dict[str, Any]:
        """
        Execute work via the provided worker function and submit cryptographic proof of delivery.
        """
        print(f"[Beacon Worker] Executing task for job {job.id}...")
        result_content = executor_fn(job)

        # Compute SHA-256 hash of result artifact
        artifact_hash = hashlib.sha256(result_content.encode("utf-8")).hexdigest()
        summary = f"Beacon autonomous execution completed. Result length: {len(result_content)} chars."

        print(f"[Beacon Worker] Delivering result with SHA256:{artifact_hash}...")
        res = await self.client.deliver_job(
            job_id=job.id,
            worker_wallet=self.worker_wallet,
            deliverable_url=f"ipfs://{artifact_hash[:32]}",
            summary=summary,
            artifact_hash=f"sha256:{artifact_hash}",
        )
        return res
