"""
Shared pytest fixtures for the RustChain SDK test suite.
"""

from __future__ import annotations

import pytest
import respx
import httpx


# -------------------------------------------------------------------
# Sample API response payloads (used across multiple test modules)
# -------------------------------------------------------------------

HEALTH_RESPONSE = {
    "status": "ok",
    "version": "0.9.4-alpha",
    "uptime": 86400.5,
    "block_height": 142857,
    "peers": 12,
    "syncing": False,
    "timestamp": "2026-03-22T12:00:00Z",
}

EPOCH_RESPONSE = {
    "epoch": 47,
    "start_block": 140000,
    "end_block": 145000,
    "current_block": 142857,
    "progress": 0.5714,
    "difficulty": 1234567.89,
}

MINERS_RESPONSE = {
    "miners": [
        {
            "miner_id": "miner-alpha-001",
            "wallet_id": "RTC_wallet_alpha",
            "hardware": "POWER8",
            "status": "active",
            "hashrate": 42.5,
            "blocks_mined": 137,
            "last_seen": "2026-03-22T11:59:00Z",
            "attestation_valid": True,
            "region": "us-east",
        },
        {
            "miner_id": "miner-beta-002",
            "wallet_id": "RTC_wallet_beta",
            "hardware": "Apple2e",
            "status": "active",
            "hashrate": 8.3,
            "blocks_mined": 22,
            "last_seen": "2026-03-22T11:58:30Z",
            "attestation_valid": True,
            "region": "eu-west",
        },
    ]
}

BALANCE_RESPONSE = {
    "wallet_id": "RTC_test_wallet",
    "balance": 1500.75,
    "available": 1200.00,
    "locked": 250.75,
    "pending": 50.00,
    "currency": "RTC",
    "last_updated": "2026-03-22T12:00:00Z",
}

TRANSFER_RESPONSE = {
    "tx_hash": "0xabc123def456789abcdef0123456789abcdef01234567890",
    "status": "confirmed",
    "from": "RTC_sender_wallet",
    "to": "RTC_receiver_wallet",
    "amount": 100.0,
    "fee": 0.001,
    "block_height": 142858,
    "timestamp": "2026-03-22T12:01:00Z",
    "confirmations": 6,
}

ATTESTATION_RESPONSE = {
    "miner_id": "miner-alpha-001",
    "valid": True,
    "hardware": "POWER8",
    "attestation_epoch": 47,
    "expires_epoch": 50,
    "score": 98.5,
    "last_verified": "2026-03-22T10:00:00Z",
    "verification_method": "sophia_core",
}

BLOCKS_RESPONSE = {
    "blocks": [
        {
            "height": 142857,
            "hash": "0xblock_hash_142857",
            "previous_hash": "0xblock_hash_142856",
            "miner": "miner-alpha-001",
            "timestamp": "2026-03-22T12:00:00Z",
            "transactions": [
                {
                    "hash": "0xtx_001",
                    "from": "RTC_a",
                    "to": "RTC_b",
                    "amount": 50.0,
                    "fee": 0.001,
                    "status": "confirmed",
                    "block_height": 142857,
                }
            ],
            "tx_count": 1,
            "size": 1024,
            "difficulty": 1234567.89,
            "nonce": 42,
            "epoch": 47,
        },
        {
            "height": 142856,
            "hash": "0xblock_hash_142856",
            "previous_hash": "0xblock_hash_142855",
            "miner": "miner-beta-002",
            "timestamp": "2026-03-22T11:59:00Z",
            "transactions": [],
            "tx_count": 0,
            "size": 512,
            "difficulty": 1234567.89,
            "nonce": 17,
            "epoch": 47,
        },
    ]
}

TRANSACTIONS_RESPONSE = {
    "transactions": [
        {
            "hash": "0xtx_001",
            "from": "RTC_a",
            "to": "RTC_b",
            "amount": 50.0,
            "fee": 0.001,
            "status": "confirmed",
            "block_height": 142857,
            "timestamp": "2026-03-22T12:00:00Z",
            "type": "transfer",
        },
        {
            "hash": "0xtx_002",
            "from": "RTC_c",
            "to": "RTC_d",
            "amount": 25.0,
            "fee": 0.001,
            "status": "confirmed",
            "block_height": 142856,
            "timestamp": "2026-03-22T11:59:00Z",
            "type": "transfer",
        },
    ]
}


NODE_URL = "https://50.28.86.131"


@pytest.fixture()
def mock_api():
    """Context-managed respx mock router for all tests."""
    with respx.mock(base_url=NODE_URL, assert_all_called=False) as router:
        # Pre-register standard routes
        router.get("/health").respond(json=HEALTH_RESPONSE)
        router.get("/epoch").respond(json=EPOCH_RESPONSE)
        router.get("/api/miners").respond(json=MINERS_RESPONSE)
        router.get("/api/wallets/RTC_test_wallet/balance").respond(json=BALANCE_RESPONSE)
        router.post("/api/transfers").respond(json=TRANSFER_RESPONSE)
        router.get("/api/miners/miner-alpha-001/attestation").respond(json=ATTESTATION_RESPONSE)
        router.get("/api/explorer/blocks").respond(json=BLOCKS_RESPONSE)
        router.get("/api/explorer/transactions").respond(json=TRANSACTIONS_RESPONSE)
        yield router
