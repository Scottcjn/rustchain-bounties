"""Tests for rustchain_agent SDK."""
import pytest
import responses
from rustchain_agent import RustChainAgent, Job

BASE_URL = "https://rustchain.org"

@pytest.fixture
def agent():
    return RustChainAgent(wallet_address="0xTestWallet123")

@responses.activate
def test_list_jobs(agent):
    responses.add(
        responses.GET,
        f"{BASE_URL}/agent/jobs",
        json={"jobs": [{"id": "j1", "poster": "0xABC", "title": "Test Job", 
                        "description": "Desc", "reward_rtc": 50, 
                        "status": "open", "created_at": "2026-03-06T00:00:00Z"}]},
        status=200
    )
    jobs = agent.list_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == "j1"
    assert jobs[0].reward_rtc == 50

@responses.activate  
def test_claim_job(agent):
    responses.add(responses.POST, f"{BASE_URL}/agent/jobs/j1/claim", json={"status": "claimed"}, status=200)
    result = agent.claim_job("j1")
    assert result["status"] == "claimed"

@responses.activate
def test_deliver_job(agent):
    responses.add(responses.POST, f"{BASE_URL}/agent/jobs/j1/deliver", json={"status": "delivered"}, status=200)
    result = agent.deliver_job("j1", "https://example.com/deliverable", "Done")
    assert result["status"] == "delivered"
