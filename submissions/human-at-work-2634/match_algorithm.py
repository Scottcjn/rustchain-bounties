#!/usr/bin/env python3
"""
Bring Your Human to Work Day — Matching Algorithm Prototype
Bounty #2634 | 500 RTC Pool

Reference implementation for correlating human-verified activity
with agent submission patterns to detect sybil farming and ensure
fair bounty distribution.
"""

import hashlib
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


# ──────────────────────────────────────────────
# Data Models
# ──────────────────────────────────────────────

@dataclass
class HumanVerification:
    wallet: str
    github_id_hash: str
    webauthn_credential_hash: str
    account_age_months: int
    public_contributions: int
    verified_at: datetime

    @property
    def is_valid(self) -> bool:
        """Check if human meets minimum verification thresholds."""
        return (
            self.account_age_months >= 6
            and self.public_contributions >= 10
            and len(self.webauthn_credential_hash) > 0
        )

    @property
    def verification_score(self) -> float:
        """Score 0-1 based on verification strength."""
        age_score = min(self.account_age_months / 24, 1.0)
        contrib_score = min(self.public_contributions / 100, 1.0)
        hw_score = 1.0 if self.webauthn_credential_hash else 0.0
        return 0.3 * age_score + 0.3 * contrib_score + 0.4 * hw_score


@dataclass
class Contribution:
    pr_id: str
    submitter_agent: str
    timestamp: datetime
    lines_added: int
    lines_removed: int
    files_changed: int
    ast_depth: float  # Abstract syntax tree depth of changes
    code_embedding: List[float] = field(default_factory=list)
    merge_status: str = "open"  # open, merged, closed
    review_comments: int = 0
    positive_reviews: int = 0

    @property
    def diff_complexity(self) -> float:
        total_lines = self.lines_added + self.lines_removed
        return math.log1p(total_lines) * math.log1p(self.files_changed) * (1 + self.ast_depth)

    @property
    def review_positive_rate(self) -> float:
        if self.review_comments == 0:
            return 0.5  # Neutral if no reviews
        return self.positive_reviews / self.review_comments


@dataclass
class Agent:
    agent_id: str
    human_wallet: str
    contributions: List[Contribution] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def submission_count(self) -> int:
        return len(self.contributions)

    @property
    def merge_rate(self) -> float:
        if not self.contributions:
            return 0.0
        merged = sum(1 for c in self.contributions if c.merge_status == "merged")
        return merged / len(self.contributions)

    @property
    def avg_diff_complexity(self) -> float:
        if not self.contributions:
            return 0.0
        return sum(c.diff_complexity for c in self.contributions) / len(self.contributions)

    @property
    def avg_code_originality(self) -> float:
        """Placeholder: in production, use embedding similarity vs. known templates."""
        if not self.contributions:
            return 0.5
        return 1.0 - (max(0.1, random.gauss(0.15, 0.05)))  # Simulated

    def frequency_score(self, now: datetime) -> dict:
        """Calculate submission frequency metrics."""
        if not self.contributions:
            return {"per_day": 0, "per_week": 0, "burst_ratio": 0, "consistency": 0}

        day_counts: dict[str, int] = {}
        for c in self.contributions:
            day_key = c.timestamp.strftime("%Y-%m-%d")
            day_counts[day_key] = day_counts.get(day_key, 0) + 1

        counts = list(day_counts.values())
        per_day = sum(counts) / max(len(counts), 1)
        per_week = per_day * 7
        burst_ratio = max(counts) / max(per_day, 0.01) if counts else 0

        # Consistency: low std dev = high consistency
        if len(counts) > 1:
            mean = sum(counts) / len(counts)
            variance = sum((x - mean) ** 2 for x in counts) / len(counts)
            std = math.sqrt(variance)
            consistency = 1.0 / (1.0 + std)
        else:
            consistency = 0.5

        return {
            "per_day": round(per_day, 2),
            "per_week": round(per_week, 2),
            "burst_ratio": round(burst_ratio, 2),
            "consistency": round(consistency, 3),
        }

    def quality_score(self) -> float:
        """Composite quality metric."""
        if not self.contributions:
            return 0.0
        avg_review = sum(c.review_positive_rate for c in self.contributions) / len(self.contributions)
        avg_complexity = self.avg_diff_complexity
        normalized_complexity = min(avg_complexity / 50, 1.0)  # Normalize to 0-1

        return (
            0.30 * self.merge_rate
            + 0.20 * avg_review
            + 0.20 * self.avg_code_originality
            + 0.15 * normalized_complexity
            + 0.15 * 0.5  # test_coverage_delta placeholder
        )


# ──────────────────────────────────────────────
# Matching Engine
# ──────────────────────────────────────────────

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def code_similarity(c1: Contribution, c2: Contribution) -> float:
    """Estimate code similarity between two contributions."""
    if c1.code_embedding and c2.code_embedding:
        return cosine_similarity(c1.code_embedding, c2.code_embedding)
    # Fallback: heuristic based on diff stats
    size_sim = 1.0 - abs(c1.lines_added - c2.lines_added) / max(c1.lines_added + c2.lines_added, 1)
    file_sim = 1.0 - abs(c1.files_changed - c2.files_changed) / max(c1.files_changed + c2.files_changed, 1)
    return 0.5 * size_sim + 0.5 * file_sim


class MatchingEngine:
    """Core matching engine for human-agent correlation."""

    # Trust score weights
    W_HUMAN = 0.35
    W_QUALITY = 0.30
    W_FREQUENCY = 0.20
    W_SOCIAL = 0.15

    def __init__(self, agents: List[Agent], humans: List[HumanVerification]):
        self.agents = agents
        self.humans = {h.wallet: h for h in humans}

    def compute_trust_score(self, agent: Agent) -> float:
        """Compute trust score for an agent-human pair."""
        human = self.humans.get(agent.human_wallet)
        if not human or not human.is_valid:
            return 0.0  # Unverified human = no trust

        human_score = human.verification_score
        quality = agent.quality_score()
        freq = agent.frequency_score(datetime.now())
        freq_normalcy = 1.0 / (1.0 + max(0, freq["burst_ratio"] - 2))  # Penalize bursts

        # Social graph strength placeholder
        social_strength = min(human.public_contributions / 50, 1.0)

        trust = (
            self.W_HUMAN * human_score
            + self.W_QUALITY * quality
            + self.W_FREQUENCY * freq_normalcy
            + self.W_SOCIAL * social_strength
        )
        return round(max(0, min(1, trust)), 4)

    def detect_sybil_clusters(self, similarity_threshold: float = 0.85) -> List[List[str]]:
        """Detect clusters of agents likely operated by the same human."""
        # Group agents by human wallet
        wallet_groups: dict[str, List[str]] = {}
        for agent in self.agents:
            wallet_groups.setdefault(agent.human_wallet, []).append(agent.agent_id)

        # For wallets with multiple agents, check similarity
        sybil_clusters: List[List[str]] = []
        for wallet, agent_ids in wallet_groups.items():
            if len(agent_ids) < 2:
                continue

            # Get all contributions for this wallet's agents
            wallet_agents = [a for a in self.agents if a.human_wallet == wallet]
            all_contribs = []
            for a in wallet_agents:
                all_contribs.extend(a.contributions)

            # Check pairwise similarity
            high_sim_pairs = 0
            total_pairs = 0
            for i in range(len(all_contribs)):
                for j in range(i + 1, len(all_contribs)):
                    sim = code_similarity(all_contribs[i], all_contribs[j])
                    total_pairs += 1
                    if sim > similarity_threshold:
                        high_sim_pairs += 1

            if total_pairs > 0 and high_sim_pairs / total_pairs > 0.5:
                sybil_clusters.append(agent_ids)

        return sybil_clusters

    def compute_payout_weights(self) -> dict[str, float]:
        """Compute bounty payout weights for all agents."""
        scores = {}
        for agent in self.agents:
            scores[agent.agent_id] = self.compute_trust_score(agent)

        total = sum(scores.values())
        if total == 0:
            # Equal distribution if no trust scores
            equal = 1.0 / max(len(self.agents), 1)
            return {aid: round(equal, 4) for aid in scores}

        return {aid: round(s / total, 4) for aid, s in scores.items()}

    def generate_report(self) -> str:
        """Generate a human-readable report."""
        lines = [
            "=" * 60,
            "Bring Your Human to Work Day — Matching Report",
            "=" * 60,
            "",
            f"Total agents: {len(self.agents)}",
            f"Verified humans: {len(self.humans)}",
            "",
        ]

        # Trust scores
        lines.append("--- Trust Scores ---")
        for agent in self.agents:
            trust = self.compute_trust_score(agent)
            quality = agent.quality_score()
            freq = agent.frequency_score(datetime.now())
            lines.append(
                f"  Agent {agent.agent_id}: trust={trust:.4f}, "
                f"quality={quality:.4f}, "
                f"submissions/day={freq['per_day']}, "
                f"burst={freq['burst_ratio']}"
            )

        # Sybil detection
        clusters = self.detect_sybil_clusters()
        lines.append("")
        lines.append("--- Sybil Detection ---")
        if clusters:
            lines.append(f"  ⚠️  {len(clusters)} suspicious cluster(s) detected:")
            for i, cluster in enumerate(clusters):
                lines.append(f"    Cluster {i+1}: {cluster}")
        else:
            lines.append("  ✅ No sybil clusters detected")

        # Payout weights
        lines.append("")
        lines.append("--- Payout Weights ---")
        weights = self.compute_payout_weights()
        for aid, w in sorted(weights.items(), key=lambda x: -x[1]):
            lines.append(f"  {aid}: {w:.2%}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


# ──────────────────────────────────────────────
# Demo / Test
# ──────────────────────────────────────────────

def demo():
    """Run a demonstration of the matching algorithm."""
    print("🚀 Running Bring Your Human to Work Day matching algorithm demo\n")

    # Create verified humans
    humans = [
        HumanVerification(
            wallet="wallet_alice",
            github_id_hash=hashlib.sha256(b"alice_github").hexdigest(),
            webauthn_credential_hash=hashlib.sha256(b"alice_yubikey").hexdigest(),
            account_age_months=18,
            public_contributions=45,
            verified_at=datetime.now() - timedelta(days=30),
        ),
        HumanVerification(
            wallet="wallet_bob",
            github_id_hash=hashlib.sha256(b"bob_github").hexdigest(),
            webauthn_credential_hash=hashlib.sha256(b"bob_yubikey").hexdigest(),
            account_age_months=8,
            public_contributions=15,
            verified_at=datetime.now() - timedelta(days=7),
        ),
        HumanVerification(
            wallet="wallet_suspicious",
            github_id_hash=hashlib.sha256(b"fresh_account").hexdigest(),
            webauthn_credential_hash="",  # No hardware key
            account_age_months=1,
            public_contributions=2,
            verified_at=datetime.now(),
        ),
    ]

    # Create agents with contributions
    now = datetime.now()
    agents = [
        # Alice's legitimate agent
        Agent(
            agent_id="agent_alice_1",
            human_wallet="wallet_alice",
            contributions=[
                Contribution(
                    pr_id=f"pr_{i}",
                    submitter_agent="agent_alice_1",
                    timestamp=now - timedelta(days=random.randint(1, 30)),
                    lines_added=random.randint(20, 200),
                    lines_removed=random.randint(5, 50),
                    files_changed=random.randint(1, 8),
                    ast_depth=round(random.uniform(1.0, 4.0), 1),
                    merge_status="merged",
                    review_comments=random.randint(2, 8),
                    positive_reviews=random.randint(1, 6),
                )
                for i in range(12)
            ],
        ),
        # Bob's agent — fewer but solid contributions
        Agent(
            agent_id="agent_bob_1",
            human_wallet="wallet_bob",
            contributions=[
                Contribution(
                    pr_id=f"pr_b{i}",
                    submitter_agent="agent_bob_1",
                    timestamp=now - timedelta(days=random.randint(1, 14)),
                    lines_added=random.randint(50, 300),
                    lines_removed=random.randint(10, 80),
                    files_changed=random.randint(2, 12),
                    ast_depth=round(random.uniform(2.0, 5.0), 1),
                    merge_status="merged" if random.random() > 0.3 else "open",
                    review_comments=random.randint(3, 10),
                    positive_reviews=random.randint(2, 8),
                )
                for i in range(5)
            ],
        ),
        # Suspicious: multiple agents under one wallet, burst submissions
        Agent(
            agent_id="agent_sybil_1",
            human_wallet="wallet_suspicious",
            contributions=[
                Contribution(
                    pr_id=f"pr_s1_{i}",
                    submitter_agent="agent_sybil_1",
                    timestamp=now - timedelta(minutes=random.randint(1, 60)),
                    lines_added=random.randint(5, 20),
                    lines_removed=random.randint(1, 5),
                    files_changed=1,
                    ast_depth=1.0,
                    merge_status="open",
                    review_comments=0,
                    positive_reviews=0,
                )
                for i in range(15)
            ],
        ),
        Agent(
            agent_id="agent_sybil_2",
            human_wallet="wallet_suspicious",
            contributions=[
                Contribution(
                    pr_id=f"pr_s2_{i}",
                    submitter_agent="agent_sybil_2",
                    timestamp=now - timedelta(minutes=random.randint(1, 60)),
                    lines_added=random.randint(5, 20),
                    lines_removed=random.randint(1, 5),
                    files_changed=1,
                    ast_depth=1.0,
                    merge_status="open",
                    review_comments=0,
                    positive_reviews=0,
                )
                for i in range(12)
            ],
        ),
    ]

    # Run matching engine
    engine = MatchingEngine(agents, humans)
    report = engine.generate_report()
    print(report)


if __name__ == "__main__":
    demo()
