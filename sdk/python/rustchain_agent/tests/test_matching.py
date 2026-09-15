"""
Tests for AutoMatcher reputation scoring and worker ranking (RIP-302 Tier 3 Bounty).
"""

from rustchain_agent.matching import AutoMatcher
from rustchain_agent.models import Job, Reputation


def test_auto_matcher_scoring():
    matcher = AutoMatcher()
    job = Job(
        job_id="job_test_001",
        poster_wallet="poster_alpha",
        title="Implement SIMD Hash",
        description="Write high performance C code.",
        reward_rtc=25.0,
        category="code",
    )

    # Candidate 1: Legendary agent with high rating and zero disputes
    rep_stellar = Reputation(
        wallet_id="worker_star",
        jobs_completed_as_worker=15,
        jobs_disputed=0,
        jobs_expired=0,
        avg_rating=4.9,
        rating_count=14,
        trust_score=95,
        trust_level="legendary",
    )

    # Candidate 2: Risky agent with low ratings and disputes
    rep_risky = Reputation(
        wallet_id="worker_risky",
        jobs_completed_as_worker=2,
        jobs_disputed=4,
        jobs_expired=1,
        avg_rating=2.1,
        rating_count=3,
        trust_score=30,
        trust_level="risky",
    )

    score_stellar = matcher.calculate_score(job, rep_stellar)
    score_risky = matcher.calculate_score(job, rep_risky)

    assert score_stellar.match_score > score_risky.match_score
    assert score_stellar.trust_score == 95
    assert score_stellar.trust_level == "legendary"
    assert "Disputes: 0" in score_stellar.rationale
    assert score_stellar.match_score >= 80.0
    assert score_risky.match_score <= 45.0
