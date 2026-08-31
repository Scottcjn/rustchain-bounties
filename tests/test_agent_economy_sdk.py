"""
Unit and Integration tests for RustChain RIP-302 Agent Economy Python SDK.
"""

import pytest
import httpx
from typing import Dict, Any

from sdk.python.rustchain_sdk import (
    AgentEconomyClient,
    RustChainClient,
    Job,
    Reputation,
    MarketplaceStats,
    calculate_escrow,
    ValidationError,
    AGENT_CATEGORIES,
    PLATFORM_FEE_RATE,
)


def test_escrow_calculation():
    calc = calculate_escrow(100.0)
    assert calc.reward_rtc == 100.0
    assert calc.fee_rtc == 5.0
    assert calc.total_escrow_rtc == 105.0
    assert PLATFORM_FEE_RATE == 0.05
    assert "code" in AGENT_CATEGORIES
    assert "research" in AGENT_CATEGORIES


def test_escrow_calculation_invalid():
    with pytest.raises(ValidationError):
        calculate_escrow(-10.0)


@pytest.mark.asyncio
async def test_agent_economy_client_lifecycle():
    # Mock handler using httpx.MockTransport
    def handler(request: httpx.Request) -> httpx.Response:
        url_path = request.url.path
        if url_path == "/agent/stats":
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "stats": {
                        "active_agents": 12,
                        "completed_jobs": 45,
                        "open_jobs": 8,
                        "total_jobs": 53,
                        "total_rtc_volume": 1250.0,
                        "total_fees_collected": 62.5,
                        "escrow_balance_rtc": 180.0,
                    },
                },
            )
        elif url_path == "/agent/jobs" and request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "jobs": [
                        {
                            "id": "job_001",
                            "title": "Analyze telemetry",
                            "category": "data",
                            "reward_rtc": 50.0,
                            "status": "posted",
                            "poster_wallet": "poster_1",
                        }
                    ],
                },
            )
        elif url_path == "/agent/jobs" and request.method == "POST":
            import json
            body = json.loads(request.content.decode("utf-8"))
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "job": {
                        "id": "job_002",
                        "title": body["title"],
                        "category": body["category"],
                        "reward_rtc": body["reward_rtc"],
                        "status": "posted",
                        "poster_wallet": body["poster_wallet"],
                    },
                },
            )
        elif "/claim" in url_path:
            return httpx.Response(200, json={"ok": True, "message": "Job claimed"})
        elif "/deliver" in url_path:
            return httpx.Response(200, json={"ok": True, "message": "Delivered"})
        elif "/accept" in url_path:
            return httpx.Response(
                200,
                json={"ok": True, "payout": {"worker_rtc": 50.0, "fee_rtc": 2.5}},
            )
        elif "/reputation/" in url_path:
            wallet = url_path.split("/")[-1]
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "wallet_id": wallet,
                    "reputation": {
                        "trust_score": 95.0,
                        "trust_level": "legendary",
                        "avg_rating": 4.9,
                        "completed_jobs": 15,
                        "total_rtc_earned": 650.0,
                    },
                },
            )
        return httpx.Response(404, json={"message": "Not Found"})

    transport = httpx.MockTransport(handler)

    client = AgentEconomyClient(base_url="https://50.28.86.131", wallet="agent_test_wallet")
    # Inject mock client
    client._client._client = httpx.AsyncClient(
        base_url="https://50.28.86.131",
        transport=transport,
    )

    # 1. Stats
    stats = await client.get_stats()
    assert stats.active_agents == 12
    assert stats.total_rtc_volume == 1250.0

    # 2. List jobs
    jobs = await client.list_jobs(category="data")
    assert len(jobs) == 1
    assert jobs[0].id == "job_001"
    assert jobs[0].reward_rtc == 50.0

    # 3. Post job
    new_job = await client.post_job(
        title="Write unit tests",
        category="code",
        reward_rtc=75.0,
    )
    assert new_job.id == "job_002"
    assert new_job.title == "Write unit tests"
    assert new_job.poster_wallet == "agent_test_wallet"

    # 4. Claim, Deliver, Accept
    claim_res = await client.claim_job("job_002", note="Taking this on")
    assert claim_res["ok"] is True

    deliver_res = await client.deliver_job(
        "job_002",
        deliverable_url="https://github.com/PR/42",
        summary="Tests written and passing",
        artifact_hash="sha256:fedcba987654321",
    )
    assert deliver_res["ok"] is True

    accept_res = await client.accept_job("job_002", rating=5, review="Perfect execution")
    assert accept_res["ok"] is True
    assert accept_res["payout"]["worker_rtc"] == 50.0

    # 5. Reputation
    rep = await client.get_reputation()
    assert rep.trust_score == 95.0
    assert rep.trust_level == "legendary"
    assert rep.completed_jobs == 15
