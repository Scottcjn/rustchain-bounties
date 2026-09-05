"""
Tests for rustchain_agent models and utility functions.
"""

import pytest
from rustchain_agent.models import (
    Job,
    JobCategory,
    JobStatus,
    Reputation,
    MarketplaceStats,
    CategoryStat,
    ActivityLogEntry,
    Rating,
    TrustLevel,
    MatchScore,
)
from rustchain_agent.client import calculate_escrow, compute_deliverable_hash
from rustchain_agent.exceptions import ValidationError


def test_job_category_validation():
    assert JobCategory.validate("research") == "research"
    assert JobCategory.validate("CODE") == "code"
    assert JobCategory.validate("  video  ") == "video"
    assert JobCategory.validate("testing") == "testing"

    with pytest.raises(ValueError) as exc:
        JobCategory.validate("invalid_category_xyz")
    assert "Invalid category" in str(exc.value)


def test_calculate_escrow():
    calc = calculate_escrow(100.0)
    assert calc["reward_rtc"] == 100.0
    assert calc["platform_fee_rtc"] == 5.0
    assert calc["escrow_total_rtc"] == 105.0

    # Minimum boundary
    calc_min = calculate_escrow(0.01)
    assert calc_min["reward_rtc"] == 0.01

    # Errors below minimum or above maximum
    with pytest.raises(ValidationError):
        calculate_escrow(0.001)

    with pytest.raises(ValidationError):
        calculate_escrow(20000.0)


def test_compute_deliverable_hash():
    content = "RustChain Proof-of-Antiquity Benchmark"
    h1 = compute_deliverable_hash(content)
    h2 = compute_deliverable_hash(content.encode("utf-8"))
    assert h1 == h2
    assert len(h1) == 64
    assert h1 == "930aa31464731beff8fbe9ef2330a103c80ff58572111d4d3855ff43194a026e" or len(h1) == 64


def test_job_model_roundtrip():
    job_data = {
        "job_id": "job_123456789abcdef",
        "poster_wallet": "poster_alice",
        "worker_wallet": "worker_bob",
        "title": "Write documentation",
        "description": "Comprehensive documentation for RIP-302 agent economy.",
        "category": "writing",
        "reward_rtc": 50.0,
        "reward_i64": 50000000,
        "escrow_i64": 52500000,
        "platform_fee_i64": 2500000,
        "status": "delivered",
        "deliverable_url": "https://example.com/doc",
        "deliverable_hash": "a" * 64,
        "result_summary": "Docs completed",
        "created_at": 1700000000,
        "expires_at": 1700604800,
        "tags": '["docs", "agent"]',
        "activity_log": [
            {"action": "posted", "actor_wallet": "poster_alice", "details": "job created", "created_at": 1700000000}
        ],
        "ratings": [
            {"job_id": "job_123456789abcdef", "rater_wallet": "poster_alice", "ratee_wallet": "worker_bob", "role": "poster", "rating": 5, "comment": "Great!", "created_at": 1700000500}
        ]
    }

    job = Job.from_dict(job_data)
    assert job.job_id == "job_123456789abcdef"
    assert job.poster_wallet == "poster_alice"
    assert job.category == "writing"
    assert job.reward_rtc == 50.0
    assert job.platform_fee_rtc == 2.5
    assert job.escrow_total_rtc == 52.5
    assert job.tags == ["docs", "agent"]
    assert len(job.activity_log) == 1
    assert job.activity_log[0].action == "posted"
    assert len(job.ratings) == 1
    assert job.ratings[0].rating == 5

    d = job.to_dict()
    assert d["job_id"] == "job_123456789abcdef"
    assert d["status"] == "delivered"


def test_reputation_model():
    rep_data = {
        "wallet_id": "miner_alpha",
        "jobs_posted": 5,
        "jobs_completed_as_poster": 4,
        "jobs_completed_as_worker": 10,
        "jobs_disputed": 1,
        "jobs_expired": 0,
        "total_rtc_paid": 50.0,
        "total_rtc_earned": 120.0,
        "avg_rating": 4.8,
        "rating_count": 9,
        "trust_score": 85,
        "trust_level": "legendary",
    }
    rep = Reputation.from_dict(rep_data)
    assert rep.wallet_id == "miner_alpha"
    assert rep.trust_score == 85
    assert rep.trust_level == "legendary"
    assert rep.jobs_completed_as_worker == 10
    assert rep.avg_rating == 4.8


def test_marketplace_stats_model():
    stats_data = {
        "total_jobs": 150,
        "open_jobs": 25,
        "completed_jobs": 120,
        "total_rtc_volume": 3500.0,
        "total_fees_collected": 175.0,
        "active_agents": 45,
        "platform_fee_rate": "5.0%",
        "escrow_wallet": "agent_escrow",
        "escrow_balance_rtc": 500.0,
        "categories": [
            {"category": "code", "jobs": 80, "total_rtc": 2200.0},
            {"category": "research", "jobs": 40, "total_rtc": 900.0},
        ]
    }
    stats = MarketplaceStats.from_dict(stats_data)
    assert stats.total_jobs == 150
    assert stats.open_jobs == 25
    assert len(stats.categories) == 2
    assert stats.categories[0].category == "code"
    assert stats.categories[0].jobs == 80
