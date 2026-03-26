"""
Unit tests for RustChainClient.
"""

import json
import pytest
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch, Mock

from rustchain import RustChainClient
from rustchain.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    ValidationError,
    TransferError,
)


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a client pointing at a test URL with SSL verification disabled."""
    return RustChainClient(
        base_url="https://test.rustchain.org",
        verify_ssl=False,
        timeout=10,
        retry_count=1,
    )


# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------

class TestHealth:
    def test_health_returns_dict(self, client):
        mock_resp = {"ok": True, "version": "2.2.1", "uptime_s": 1234}

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = client.health()
            assert result == mock_resp
            assert result["ok"] is True

    def test_health_endpoint_is_get(self, client):
        mock_resp = {"ok": True}

        opened = []

        def fake_open(req, **kwargs):
            opened.append(req)
            return _mock_response(mock_resp)

        with patch.object(urllib.request, "urlopen", side_effect=fake_open):
            client.health()

        assert len(opened) == 1
        assert opened[0].get_method() == "GET"
        assert "/health" in opened[0].full_url


# ------------------------------------------------------------------
# Epoch
# ------------------------------------------------------------------

class TestEpoch:
    def test_epoch_returns_epoch_info(self, client):
        mock_resp = {
            "epoch": 92,
            "blocks_per_epoch": 144,
            "epoch_pot": 1.5,
            "slot": 13365,
        }

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = client.epoch()
            assert result["epoch"] == 92
            assert result["blocks_per_epoch"] == 144


# ------------------------------------------------------------------
# Miners
# ------------------------------------------------------------------

class TestMiners:
    def test_miners_returns_list(self, client):
        mock_resp = [
            {
                "miner": "test-miner-1",
                "antiquity_multiplier": 1.5,
                "device_arch": "x86_64",
                "device_family": "dell",
                "hardware_type": "laptop",
                "last_attest": "2026-03-26T10:00:00Z",
            },
            {
                "miner": "test-miner-2",
                "antiquity_multiplier": 2.0,
                "device_arch": "arm64",
                "device_family": "apple",
                "hardware_type": "mac",
                "last_attest": "2026-03-26T10:01:00Z",
            },
        ]

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = client.miners()
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["miner"] == "test-miner-1"

    def test_miners_with_limit(self, client):
        mock_resp = [{"miner": "test-miner-1"}]

        opened = []

        def fake_open(req, **kwargs):
            opened.append(req)
            return _mock_response(mock_resp)

        with patch.object(urllib.request, "urlopen", side_effect=fake_open):
            client.miners(limit=5)

        assert "limit=5" in opened[0].full_url

    def test_miners_with_offset(self, client):
        mock_resp = []

        opened = []

        def fake_open(req, **kwargs):
            opened.append(req)
            return _mock_response(mock_resp)

        with patch.object(urllib.request, "urlopen", side_effect=fake_open):
            client.miners(offset=10)

        assert "offset=10" in opened[0].full_url


# ------------------------------------------------------------------
# Balance
# ------------------------------------------------------------------

class TestBalance:
    def test_balance_returns_balance(self, client):
        mock_resp = {"balance": 100.5, "wallet_id": "test-wallet"}

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = client.balance("test-wallet")
            assert result["balance"] == 100.5
            assert result["wallet_id"] == "test-wallet"

    def test_balance_empty_wallet_id_raises(self, client):
        with pytest.raises(ValidationError):
            client.balance("")

    def test_balance_whitespace_wallet_id_raises(self, client):
        with pytest.raises(ValidationError):
            client.balance("   ")


# ------------------------------------------------------------------
# Transfer
# ------------------------------------------------------------------

class TestTransfer:
    def test_transfer_success(self, client):
        mock_resp = {"success": True, "tx_hash": "0xabc123"}

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = client.transfer(
                from_wallet="wallet-a",
                to_wallet="wallet-b",
                amount=10.0,
                signature="sig-xyz",
            )
            assert result["success"] is True
            assert result["tx_hash"] == "0xabc123"

    def test_transfer_negative_amount_raises(self, client):
        with pytest.raises(ValidationError):
            client.transfer("a", "b", amount=-5.0, signature="sig")

    def test_transfer_zero_amount_raises(self, client):
        with pytest.raises(ValidationError):
            client.transfer("a", "b", amount=0.0, signature="sig")

    def test_transfer_empty_from_raises(self, client):
        with pytest.raises(ValidationError):
            client.transfer("", "b", amount=1.0, signature="sig")

    def test_transfer_empty_to_raises(self, client):
        with pytest.raises(ValidationError):
            client.transfer("a", "", amount=1.0, signature="sig")


# ------------------------------------------------------------------
# Attestation Status
# ------------------------------------------------------------------

class TestAttestationStatus:
    def test_attestation_status_returns_info(self, client):
        mock_resp = {
            "miner_id": "test-miner",
            "last_attest": "2026-03-26T10:00:00Z",
            "consecutive_days": 15,
            "eligible": True,
        }

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = client.attestation_status("test-miner")
            assert result["consecutive_days"] == 15
            assert result["eligible"] is True

    def test_attestation_status_empty_miner_id_raises(self, client):
        with pytest.raises(ValidationError):
            client.attestation_status("")


# ------------------------------------------------------------------
# Lottery Eligibility
# ------------------------------------------------------------------

class TestLotteryEligibility:
    def test_lottery_eligibility_returns_info(self, client):
        mock_resp = {
            "eligible": True,
            "slot": 13365,
            "slot_producer": "producer-1",
            "rotation_size": 100,
        }

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = client.lottery_eligibility("test-miner")
            assert result["eligible"] is True
            assert result["slot"] == 13365


# ------------------------------------------------------------------
# Submit Attestation
# ------------------------------------------------------------------

class TestSubmitAttestation:
    def test_submit_attestation_success(self, client):
        mock_resp = {"success": True, "tx_hash": "0xdef456"}

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = client.submit_attestation(
                {"miner_id": "test-miner", "signature": "sig"}
            )
            assert result["success"] is True


# ------------------------------------------------------------------
# Stats
# ------------------------------------------------------------------

class TestStats:
    def test_stats_returns_network_stats(self, client):
        mock_resp = {
            "total_miners": 1234,
            "total_stake": 50000.0,
            "active_epochs": 92,
        }

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = client.stats()
            assert result["total_miners"] == 1234


# ------------------------------------------------------------------
# Async methods
# ------------------------------------------------------------------

class TestAsyncMethods:
    @pytest.mark.asyncio
    async def test_health_async_returns_dict(self, client):
        """Verify async health uses the same base URL as sync."""
        mock_resp = {"ok": True, "version": "2.2.1"}

        class MockResponse:
            status = 200
            reason = "OK"

            async def json(self):
                return mock_resp

            async def text(self):
                return json.dumps(mock_resp)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        class MockSession:
            def request(self, *args, **kwargs):
                return MockResponse()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        with patch("aiohttp.ClientSession", return_value=MockSession()):
            result = await client.health_async()
            assert result["ok"] is True


# ------------------------------------------------------------------
# Error handling
# ------------------------------------------------------------------

class TestErrorHandling:
    def test_api_error_raised_on_http_error(self, client):
        # Simulate HTTP 500
        error = urllib.error.HTTPError(
            url="https://test/health",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=None,
        )

        with patch.object(urllib.request, "urlopen", side_effect=error):
            with pytest.raises(APIError) as exc_info:
                client.health()
            assert exc_info.value.status_code == 500

    def test_network_error_raised_on_url_error(self, client):
        error = urllib.error.URLError("Connection refused")

        with patch.object(urllib.request, "urlopen", side_effect=error):
            with pytest.raises(NetworkError):
                client.health()

    def test_authentication_error_on_401(self, client):
        error = urllib.error.HTTPError(
            url="https://test/health",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=None,
        )

        with patch.object(urllib.request, "urlopen", side_effect=error):
            with pytest.raises(AuthenticationError):
                client.health()


# ------------------------------------------------------------------
# Test client configuration
# ------------------------------------------------------------------

class TestClientConfiguration:
    def test_default_base_url(self):
        client = RustChainClient()
        assert client.base_url == "https://50.28.86.131"

    def test_custom_base_url(self):
        client = RustChainClient(base_url="https://custom.example.com")
        assert client.base_url == "https://custom.example.com"

    def test_base_url_trailing_slash_stripped(self):
        client = RustChainClient(base_url="https://custom.example.com///")
        assert client.base_url == "https://custom.example.com"

    def test_create_factory(self):
        client = RustChainClient.create(base_url="https://custom.example.com")
        assert client.base_url == "https://custom.example.com"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _mock_response(data):
    """Create a mock HTTP response that returns JSON data."""
    mock = MagicMock()
    mock.__enter__ = Mock(return_value=mock)
    mock.__exit__ = Mock(return_value=False)
    mock.read.return_value = json.dumps(data).encode("utf-8")
    mock.__iter__ = Mock(return_value=iter([]))
    return mock


class AsyncContextManagerMock:
    def __init__(self, resp_data):
        self._data = resp_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def raise_for_status(self):
        pass

    async def json(self):
        return self._data

    @property
    def status(self):
        return 200

    @property
    def reason(self):
        return "OK"
