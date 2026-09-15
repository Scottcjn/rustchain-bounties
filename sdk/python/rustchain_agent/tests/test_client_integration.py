"""
End-to-end integration tests for RustChainAgentClient against a real live local test server.
Strictly zero mocking of cryptographic primitives or state transitions.
"""

import os
import tempfile
import pytest

from rustchain_agent.client import RustChainAgentClient, compute_deliverable_hash
from rustchain_agent.exceptions import (
    InsufficientEscrowError,
    JobNotFoundError,
    JobStateError,
    UnauthorizedError,
    ValidationError,
)
from rustchain_agent.models import JobStatus
from rustchain_agent.tests.rip302_server import LiveTestServer


@pytest.fixture(scope="module")
def live_server():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_agent_economy.db")
    server = LiveTestServer(db_path)
    server.start()

    # Fund test wallets
    server.credit_wallet("poster_alice", 100.0)
    server.credit_wallet("poster_broke", 0.0)
    server.credit_wallet("worker_bob", 10.0)
    server.credit_wallet("worker_charlie", 10.0)

    yield server
    server.stop()


@pytest.fixture
def client(live_server):
    return RustChainAgentClient(base_url=live_server.url, timeout=5.0)


def test_post_job_success(client):
    res = client.post_job(
        poster_wallet="poster_alice",
        title="Develop RISC-V Attestation Module",
        description="Implement hardware CPU attestation for RISC-V StarFive VisionFive 2 board.",
        category="code",
        reward_rtc=10.0,
        tags=["riscv", "hardware"],
    )
    assert res["ok"] is True
    assert "job_id" in res
    assert res["status"] == "open"
    assert res["reward_rtc"] == 10.0
    assert res["platform_fee_rtc"] == 0.5
    assert res["escrow_total_rtc"] == 10.5


def test_post_job_insufficient_balance(client):
    with pytest.raises(InsufficientEscrowError) as exc:
        client.post_job(
            poster_wallet="poster_broke",
            title="Benchmark PowerPC G5",
            description="Run 1-hour stress test on PowerPC 970FX hardware miner.",
            category="research",
            reward_rtc=5.0,
        )
    assert "Insufficient balance" in str(exc.value)


def test_post_job_validation_errors(client):
    # Bad title length
    with pytest.raises(ValidationError):
        client.post_job("poster_alice", "tiny", "description long enough to pass validation here", reward_rtc=1.0)

    # Bad description length
    with pytest.raises(ValidationError):
        client.post_job("poster_alice", "Valid Title", "too short", reward_rtc=1.0)

    # Bad category
    with pytest.raises(ValidationError):
        client.post_job("poster_alice", "Valid Title", "Valid description that is longer than 20 characters", category="invalid_cat", reward_rtc=1.0)

    # Bad reward
    with pytest.raises(ValidationError):
        client.post_job("poster_alice", "Valid Title", "Valid description that is longer than 20 characters", reward_rtc=0.0001)


def test_full_job_lifecycle(client):
    # 1. Post
    posted = client.post_job(
        poster_wallet="poster_alice",
        title="Write RustChain Economics Article",
        description="Detailed guide covering RIP-302 agent escrow mechanics and fees.",
        category="writing",
        reward_rtc=20.0,
        tags=["rip302", "article"],
    )
    job_id = posted["job_id"]
    assert job_id.startswith("job_")

    # 2. List
    jobs_list = client.list_jobs(category="writing", status="open")
    assert any(j["job_id"] == job_id for j in jobs_list["jobs"])

    # 3. Get Details
    job = client.get_job(job_id)
    assert job.job_id == job_id
    assert job.status == JobStatus.OPEN.value
    assert job.reward_rtc == 20.0
    assert job.escrow_total_rtc == 21.0
    assert len(job.activity_log) >= 1
    assert job.activity_log[0].action == "posted"

    # 4. Poster cannot claim own job
    with pytest.raises(ValidationError):
        client.claim_job(job_id, "poster_alice")

    # 5. Worker claims job
    claimed = client.claim_job(job_id, "worker_bob")
    assert claimed["ok"] is True
    assert claimed["status"] == "claimed"

    # Cannot claim already claimed job
    with pytest.raises(JobStateError):
        client.claim_job(job_id, "worker_charlie")

    # 6. Unauthorized worker cannot deliver
    deliv_hash = compute_deliverable_hash("Article content text")
    with pytest.raises(UnauthorizedError):
        client.deliver_job(
            job_id=job_id,
            worker_wallet="worker_charlie",
            deliverable_url="https://example.com/art",
            deliverable_hash=deliv_hash,
            result_summary="Completed article",
        )

    # 7. Assigned worker delivers
    deliv = client.deliver_job(
        job_id=job_id,
        worker_wallet="worker_bob",
        deliverable_url="https://dev.to/rustchain/rip-302-economics",
        deliverable_hash=deliv_hash,
        result_summary="Completed 1500-word article on RIP-302.",
    )
    assert deliv["ok"] is True
    assert deliv["status"] == "delivered"

    # 8. Unauthorized user cannot accept
    with pytest.raises(UnauthorizedError):
        client.accept_delivery(job_id, "worker_bob")

    # 9. Poster accepts delivery with 5-star rating
    accepted = client.accept_delivery(job_id, "poster_alice", rating=5)
    assert accepted["ok"] is True
    assert accepted["status"] == "completed"
    assert accepted["reward_paid_rtc"] == 20.0
    assert accepted["platform_fee_rtc"] == 1.0

    # 10. Check reputation updated
    rep_worker = client.get_reputation("worker_bob")
    assert rep_worker.wallet_id == "worker_bob"
    assert rep_worker.jobs_completed_as_worker >= 1
    assert rep_worker.avg_rating == 5.0
    assert rep_worker.trust_score >= 50

    rep_poster = client.get_reputation("poster_alice")
    assert rep_poster.jobs_completed_as_poster >= 1
    assert rep_poster.total_rtc_paid >= 20.0


def test_job_dispute_flow(client):
    posted = client.post_job(
        poster_wallet="poster_alice",
        title="Test Dispute Protocol",
        description="Work will be disputed for missing test artifacts.",
        category="testing",
        reward_rtc=5.0,
    )
    job_id = posted["job_id"]

    client.claim_job(job_id, "worker_bob")
    client.deliver_job(job_id, "worker_bob", result_summary="Done work")

    # Poster disputes
    disputed = client.dispute_job(job_id, "poster_alice", reason="Deliverable lacked coverage report")
    assert disputed["ok"] is True
    assert disputed["status"] == "disputed"

    # Cancel disputed job
    cancelled = client.cancel_job(job_id, "poster_alice")
    assert cancelled["ok"] is True
    assert cancelled["status"] == "cancelled"
    assert cancelled["refunded_rtc"] == 5.25


def test_job_cancel_open_flow(client):
    posted = client.post_job(
        poster_wallet="poster_alice",
        title="Test Cancel Open Job",
        description="This open job will be cancelled immediately.",
        category="data",
        reward_rtc=2.0,
    )
    job_id = posted["job_id"]

    cancelled = client.cancel_job(job_id, "poster_alice")
    assert cancelled["ok"] is True
    assert cancelled["status"] == "cancelled"
    assert cancelled["refunded_rtc"] == 2.10


def test_marketplace_stats(client):
    stats = client.get_stats()
    assert stats.total_jobs > 0
    assert stats.platform_fee_rate == "5.0%"
    assert stats.escrow_wallet == "agent_escrow"
    assert isinstance(stats.categories, list)
