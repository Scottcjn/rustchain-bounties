"""
Tests for the async AsyncRustChainClient.

All HTTP calls are mocked with ``respx`` so no live node is required.
"""

from __future__ import annotations

import pytest
import respx
import httpx

from rustchain.client import AsyncRustChainClient
from rustchain.errors import (
    RustChainAPIError,
    RustChainAuthError,
    RustChainValidationError,
)
from rustchain.models import (
    AttestationStatus,
    Balance,
    EpochInfo,
    HealthStatus,
    Miner,
    TransferResult,
)

from .conftest import (
    ATTESTATION_RESPONSE,
    BALANCE_RESPONSE,
    EPOCH_RESPONSE,
    HEALTH_RESPONSE,
    MINERS_RESPONSE,
    NODE_URL,
    TRANSFER_RESPONSE,
)


@pytest.mark.asyncio
class TestAsyncHealth:
    async def test_health_success(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            result = await client.health()
        assert isinstance(result, HealthStatus)
        assert result.status == "ok"
        assert result.block_height == 142857

    async def test_health_server_error(self):
        with respx.mock(base_url=NODE_URL) as router:
            router.get("/health").respond(status_code=502, text="Bad Gateway")
            async with AsyncRustChainClient(NODE_URL) as client:
                with pytest.raises(RustChainAPIError) as exc_info:
                    await client.health()
                assert exc_info.value.status_code == 502


@pytest.mark.asyncio
class TestAsyncEpoch:
    async def test_epoch_success(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            result = await client.epoch()
        assert isinstance(result, EpochInfo)
        assert result.epoch == 47


@pytest.mark.asyncio
class TestAsyncMiners:
    async def test_miners_list(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            result = await client.miners()
        assert len(result) == 2
        assert result[0].miner_id == "miner-alpha-001"


@pytest.mark.asyncio
class TestAsyncBalance:
    async def test_balance_success(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            result = await client.balance("RTC_test_wallet")
        assert isinstance(result, Balance)
        assert result.balance == 1500.75

    async def test_balance_empty_raises(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError):
                await client.balance("")


@pytest.mark.asyncio
class TestAsyncTransfer:
    async def test_transfer_success(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            result = await client.transfer(
                "RTC_sender_wallet",
                "RTC_receiver_wallet",
                100.0,
                "valid_sig",
            )
        assert isinstance(result, TransferResult)
        assert result.tx_hash == "0xabc123def456789abcdef0123456789abcdef01234567890"
        assert result.confirmations == 6

    async def test_transfer_validation(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError):
                await client.transfer("a", "b", -1, "sig")


@pytest.mark.asyncio
class TestAsyncAttestation:
    async def test_attestation_success(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            result = await client.attestation_status("miner-alpha-001")
        assert isinstance(result, AttestationStatus)
        assert result.valid is True
        assert result.verification_method == "sophia_core"

    async def test_attestation_empty_miner_raises(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError):
                await client.attestation_status("")


@pytest.mark.asyncio
class TestAsyncAuth:
    async def test_401_raises(self):
        with respx.mock(base_url=NODE_URL) as router:
            router.get("/epoch").respond(status_code=401, text="Unauthorized")
            async with AsyncRustChainClient(NODE_URL) as client:
                with pytest.raises(RustChainAuthError):
                    await client.epoch()


@pytest.mark.asyncio
class TestAsyncContextManager:
    async def test_async_context_manager(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            h = await client.health()
            assert h.status == "ok"
