"""
Autonomous worker-to-job matching engine for RustChain Agent Economy (RIP-302 Tier 3).
Calculates suitability scores using trust ratings, category track record, and dispute history.
"""

import logging
from typing import Any, Dict, List, Optional

from .client import RustChainAgentClient
from .exceptions import AgentEconomyError
from .models import Job, MatchScore, Reputation

logger = logging.getLogger("rustchain_agent.matching")


class AutoMatcher:
    """
    Intelligent matching engine pairing posted jobs with high-reputation worker agents.
    """

    def __init__(
        self,
        weight_trust: float = 0.40,
        weight_rating: float = 0.25,
        weight_experience: float = 0.25,
        weight_volume: float = 0.10,
    ):
        self.w_trust = weight_trust
        self.w_rating = weight_rating
        self.w_exp = weight_experience
        self.w_vol = weight_volume

    def calculate_score(self, job: Job, rep: Reputation) -> MatchScore:
        """
        Calculate compatibility score (0-100) between a job and a candidate worker.
        """
        # 1. Trust Score (0-100)
        trust_val = rep.trust_score

        # 2. Rating Score (0-100)
        if rep.rating_count > 0 and rep.avg_rating > 0:
            rating_val = min(100.0, (rep.avg_rating / 5.0) * 100.0)
        else:
            rating_val = 60.0  # Default baseline for unrated agents

        # 3. Experience & Success Rate
        total_completed = rep.jobs_completed_as_worker
        total_jobs = total_completed + rep.jobs_disputed + rep.jobs_expired
        if total_jobs > 0:
            success_rate = (total_completed / total_jobs) * 100.0
        else:
            success_rate = 50.0

        # 4. Volume Bonus (capped at 20 jobs completed)
        vol_score = min(100.0, total_completed * 5.0)

        # 5. Dispute Penalty
        dispute_penalty = 0.0
        if rep.jobs_disputed > 0:
            dispute_ratio = rep.jobs_disputed / max(1, total_jobs)
            dispute_penalty = dispute_ratio * 30.0

        composite = (
            (trust_val * self.w_trust)
            + (rating_val * self.w_rating)
            + (success_rate * self.w_exp)
            + (vol_score * self.w_vol)
            - dispute_penalty
        )
        final_score = max(0.0, min(100.0, composite))

        rationale = (
            f"Trust: {trust_val}/100 ({rep.trust_level}), "
            f"Avg Rating: {rep.avg_rating:.1f}/5.0 ({rep.rating_count} reviews), "
            f"Worker Completed: {total_completed}, Disputes: {rep.jobs_disputed}"
        )

        return MatchScore(
            worker_wallet=rep.wallet_id,
            match_score=round(final_score, 2),
            trust_score=rep.trust_score,
            trust_level=rep.trust_level,
            avg_rating=rep.avg_rating,
            completed_as_worker=rep.jobs_completed_as_worker,
            category_match=True,
            rationale=rationale,
        )

    def rank_candidates_for_job(
        self,
        job: Job,
        candidate_wallets: List[str],
        client: RustChainAgentClient,
    ) -> List[MatchScore]:
        """
        Rank a list of candidate agent wallets for a specific job.
        """
        scores: List[MatchScore] = []
        for wallet in candidate_wallets:
            if wallet == job.poster_wallet:
                continue  # Cannot self-match
            try:
                rep = client.get_reputation(wallet)
                score = self.calculate_score(job, rep)
                scores.append(score)
            except AgentEconomyError as e:
                logger.warning(f"Failed to fetch reputation for candidate {wallet}: {e}")
                # Fallback neutral score
                default_rep = Reputation(wallet_id=wallet, trust_score=50, trust_level="neutral")
                scores.append(self.calculate_score(job, default_rep))

        # Sort descending by match score
        scores.sort(key=lambda s: s.match_score, reverse=True)
        return scores

    def find_best_jobs_for_worker(
        self,
        worker_wallet: str,
        client: RustChainAgentClient,
        category: Optional[str] = None,
        min_reward: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Discover and rank available open marketplace jobs suitable for the worker.
        """
        rep = client.get_reputation(worker_wallet)
        raw_jobs = client.list_jobs(category=category, status="open", min_reward=min_reward, limit=50)
        jobs_list = raw_jobs.get("jobs", [])

        scored_jobs = []
        for j_data in jobs_list:
            job = Job.from_dict(j_data)
            if job.poster_wallet == worker_wallet:
                continue
            score = self.calculate_score(job, rep)
            scored_jobs.append({
                "job": job.to_dict(),
                "suitability_score": score.match_score,
                "reward_rtc": job.reward_rtc,
                "title": job.title,
                "category": job.category,
            })

        # Rank by suitability score and reward
        scored_jobs.sort(key=lambda x: (x["suitability_score"], x["reward_rtc"]), reverse=True)
        return scored_jobs
