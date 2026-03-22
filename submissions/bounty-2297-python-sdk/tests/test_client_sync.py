"""
Tests for the synchronous RustChainClient.

All HTTP calls are mocked with ``respx`` so no live node is required.
"""

from __future__ import annotations

import pytest
import respx
import httpx

from rustchain.client import RustChainClient
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


class TestSyncHealth:
    def test_health_success(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            result = client.health()
        assert isinstance(result, HealthStatus)
        assert result.status == "ok"
        assert result.version == "0.9.4-alpha"
        assert result.block_height == 142857

    def test_health_server_error(self):
        with respx.mock(base_url=NODE_URL) as router:
            router.get("/health").respond(status_code=500, text="Internal Server Error")
            with RustChainClient(NODE_URL) as client:
                with pytest.raises(RustChainAPIError) as exc_info:
                    client.health()
                assert exc_info.value.status_code == 500


class TestSyncEpoch:
    def test_epoch_success(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            result = client.epoch()
        assert isinstance(result, EpochInfo)
        assert result.epoch == 47
        assert result.progress == pytest.approx(0.5714)


class TestSyncMiners:
    def test_miners_list(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            result = client.miners()
        assert len(result) == 2
        assert all(isinstance(m, Miner) for m in result)
        assert result[0].miner_id == "miner-alpha-001"
        assert result[1].hardware == "Apple2e"


class TestSyncBalance:
    def test_balance_success(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            result = client.balance("RTC_test_wallet")
        assert isinstance(result, Balance)
        assert result.balance == 1500.75
        assert result.available == 1200.00
        assert result.locked == 250.75

    def test_balance_empty_wallet_raises(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError) as exc_info:
                client.balance("")
            assert exc_info.value.field == "wallet_id"

    def test_balance_whitespace_wallet_raises(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError):
                client.balance("   ")


class TestSyncTransfer:
    def test_transfer_success(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            result = client.transfer(
                "RTC_sender_wallet",
                "RTC_receiver_wallet",
                100.0,
                "valid_signature_hex",
            )
        assert isinstance(result, TransferResult)
        assert result.status == "confirmed"
        assert result.amount == 100.0

    def test_transfer_negative_amount_raises(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError) as exc_info:
                client.transfer("a", "b", -10.0, "sig")
            assert exc_info.value.field == "amount"

    def test_transfer_zero_amount_raises(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError):
                client.transfer("a", "b", 0, "sig")

    def test_transfer_empty_from_raises(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError) as exc_info:
                client.transfer("", "b", 10.0, "sig")
            assert exc_info.value.field == "from_wallet"

    def test_transfer_empty_signature_raises(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError) as exc_info:
                client.transfer("a", "b", 10.0, "")
            assert exc_info.value.field == "signature"


class TestSyncAttestation:
    def test_attestation_success(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            result = client.attestation_status("miner-alpha-001")
        assert isinstance(result, AttestationStatus)
        assert result.valid is True
        assert result.score == 98.5
        assert result.hardware == "POWER8"

    def test_attestation_empty_miner_raises(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            with pytest.raises(RustChainValidationError):
                client.attestation_status("")


class TestSyncAuth:
    def test_401_raises_auth_error(self):
        with respx.mock(base_url=NODE_URL) as router:
            router.get("/health").respond(status_code=401, text="Unauthorized")
            with RustChainClient(NODE_URL) as client:
                with pytest.raises(RustChainAuthError) as exc_info:
                    client.health()
                assert exc_info.value.status_code == 401

    def test_403_raises_auth_error(self):
        with respx.mock(base_url=NODE_URL) as router:
            router.get("/health").respond(status_code=403, text="Forbidden")
            with RustChainClient(NODE_URL) as client:
                with pytest.raises(RustChainAuthError) as exc_info:
                    client.health()
                assert exc_info.value.status_code == 403


class TestSyncClientConfig:
    def test_url_normalisation(self):
        client = RustChainClient("50.28.86.131/")
        assert client._base_url == "https://50.28.86.131"
        client.close()

    def test_api_key_header(self):
        client = RustChainClient(NODE_URL, api_key="test-key")
        assert client._http.headers.get("Authorization") == "Bearer test-key"
        client.close()

    def test_context_manager(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            h = client.health()
            assert h.status == "ok"
