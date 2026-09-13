"""Deterministic contract tests for the RIP-302 Python SDK."""

import json
from urllib.parse import parse_qs, urlsplit

import pytest
import responses
from rustchain_agent import RustChainAgent, RustChainAPIError

BASE_URL = "https://example.test"
WALLET = "RTC0123456789abcdef0123456789abcdef01234567"


@pytest.fixture
def agent():
    return RustChainAgent(
        agent_id="rafaio1",
        wallet_address=WALLET,
        base_url=BASE_URL,
        timeout=5,
    )


def request_json(call):
    return json.loads(call.request.body.decode("utf-8"))


def test_wallet_and_agent_validation():
    RustChainAgent(agent_id="valid-agent", wallet_address=WALLET)

    with pytest.raises(ValueError, match="RTC"):
        RustChainAgent(agent_id="valid-agent", wallet_address="0x1234")
    with pytest.raises(ValueError, match="40 hex"):
        RustChainAgent(agent_id="valid-agent", wallet_address="RTC1234")
    with pytest.raises(ValueError, match="agent_id"):
        RustChainAgent(agent_id="Invalid--Agent", wallet_address=WALLET)


@responses.activate
def test_wallet_endpoints_have_exact_urls_and_payload(agent):
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/agent/wallet/create",
        json={"wallet_address": WALLET},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/agent/wallet/worker-agent",
        json={"agent_id": "worker-agent", "wallet_address": WALLET},
        status=200,
    )

    agent.create_wallet(name="Rafaio Agent")
    agent.get_wallet("worker-agent")

    assert responses.calls[0].request.url == f"{BASE_URL}/api/agent/wallet/create"
    assert request_json(responses.calls[0]) == {
        "agent_id": "rafaio1",
        "wallet_address": WALLET,
        "name": "Rafaio Agent",
    }
    assert responses.calls[1].request.url == (
        f"{BASE_URL}/api/agent/wallet/worker-agent"
    )


@responses.activate
def test_send_payment_uses_rip302_path_and_payload(agent):
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/agent/payment/send",
        json={"status": "pending", "payment_id": "pay_test"},
        status=200,
    )

    agent.send_payment(
        to_agent="service-agent",
        amount=1.25,
        memo="test payment",
        resource="/api/premium/data",
        payment_id="pay_test",
    )

    assert responses.calls[0].request.url == f"{BASE_URL}/api/agent/payment/send"
    assert request_json(responses.calls[0]) == {
        "payment_id": "pay_test",
        "from_agent": "rafaio1",
        "to_agent": "service-agent",
        "amount": 1.25,
        "memo": "test payment",
        "resource": "/api/premium/data",
    }


@responses.activate
def test_request_payment_uses_deterministic_payload(agent):
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/agent/payment/request",
        json={"status": "pending", "intent_id": "intent_test"},
        status=200,
    )

    agent.request_payment(
        from_agent="payer-agent",
        amount=0.5,
        description="analysis",
        intent_id="intent_test",
        expires_at="2026-08-28T20:30:00+00:00",
    )

    assert request_json(responses.calls[0]) == {
        "intent_id": "intent_test",
        "from_agent": "payer-agent",
        "to_agent": "rafaio1",
        "amount": 0.5,
        "description": "analysis",
        "resource": "/api/agent/payment/intent_test",
        "expires_at": "2026-08-28T20:30:00+00:00",
    }


@responses.activate
def test_payment_get_and_history_use_spec_paths(agent):
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/agent/payment/pay_123",
        json={"payment_id": "pay_123"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/agent/payment/history",
        json={"payments": []},
        status=200,
    )

    agent.get_payment("pay_123")
    agent.get_payment_history(limit=7, status="completed")

    assert responses.calls[0].request.url == (f"{BASE_URL}/api/agent/payment/pay_123")
    history_url = urlsplit(responses.calls[1].request.url)
    assert history_url.path == "/api/agent/payment/history"
    assert parse_qs(history_url.query) == {
        "limit": ["7"],
        "status": ["completed"],
    }


@responses.activate
def test_x402_challenge_uses_spec_payload(agent):
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/agent/payment/x402/challenge",
        json={"nonce": "abc"},
        status=200,
    )

    agent.create_x402_challenge(
        resource="/api/premium/data",
        required_amount=2,
    )

    assert request_json(responses.calls[0]) == {
        "resource": "/api/premium/data",
        "amount": 2.0,
        "recipient": "rafaio1",
    }


@responses.activate
def test_reputation_read_endpoints_are_exact(agent):
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/agent/reputation/service-agent",
        json={"score": 80},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/agent/reputation/leaderboard",
        json={"leaders": []},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/agent/reputation/service-agent/proof",
        json={"proof": "test"},
        status=200,
    )

    agent.get_reputation("service-agent")
    agent.get_reputation_leaderboard(limit=10, tier="trusted")
    agent.get_trust_proof("service-agent")

    assert urlsplit(responses.calls[0].request.url).path == (
        "/api/agent/reputation/service-agent"
    )
    leaderboard = urlsplit(responses.calls[1].request.url)
    assert leaderboard.path == "/api/agent/reputation/leaderboard"
    assert parse_qs(leaderboard.query) == {
        "limit": ["10"],
        "tier": ["trusted"],
    }
    assert urlsplit(responses.calls[2].request.url).path == (
        "/api/agent/reputation/service-agent/proof"
    )


@responses.activate
def test_attestation_payload_is_deterministic(agent):
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/agent/reputation/attest",
        json={"attestation_id": "att_1"},
        status=200,
    )

    agent.submit_attestation(
        to_agent="service-agent",
        rating=5,
        comment="reliable",
        transaction_id="tx_1",
    )

    assert request_json(responses.calls[0]) == {
        "from_agent": "rafaio1",
        "to_agent": "service-agent",
        "rating": 5,
        "comment": "reliable",
        "transaction_id": "tx_1",
    }


@responses.activate
def test_http_errors_include_status_without_response_body(agent):
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/agent/reputation/rafaio1",
        json={"error": "not found", "internal": "must not leak"},
        status=404,
    )

    with pytest.raises(RustChainAPIError) as exc_info:
        agent.get_reputation()

    assert exc_info.value.status_code == 404
    assert str(exc_info.value) == ("GET /api/agent/reputation/rafaio1 failed")
