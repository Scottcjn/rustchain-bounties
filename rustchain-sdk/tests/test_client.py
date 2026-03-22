"""Tests for RustChain client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from rustchain import RustChainClient
from rustchain.exceptions import (
    ConnectionError,
    TimeoutError,
    ValidationError,
    NotFoundError,
    ServerError,
    RateLimitError,
    InsufficientFundsError,
    InvalidSignatureError,
)
from rustchain.models import (
    HealthStatus,
    EpochInfo,
    Miner,
    Balance,
    TransferResult,
    AttestationStatus,
)


class TestRustChainClient:
    """Tests for RustChainClient class."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = RustChainClient(base_url="http://test.com", timeout=10.0)
        assert client.base_url == "http://test.com"
        assert client.timeout == 10.0
        assert client._client is None
    
    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test client as async context manager."""
        async with RustChainClient() as client:
            assert client._client is not None
    
    @pytest.mark.asyncio
    async def test_health_success(self):
        """Test health check success."""
        mock_response = {
            "status": "healthy",
            "version": "1.0.0",
            "uptime": 3600,
            "peers": 10
        }
        
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 200
                mock_http_response.json.return_value = mock_response
                mock_http_response.raise_for_status = MagicMock()
                mock_request.return_value = mock_http_response
                
                result = await client.health()
                
                assert isinstance(result, HealthStatus)
                assert result.status == "healthy"
                assert result.version == "1.0.0"
                assert result.uptime == 3600
    
    @pytest.mark.asyncio
    async def test_epoch_success(self):
        """Test epoch info success."""
        mock_response = {
            "current_epoch": 100,
            "start_height": 1000,
            "end_height": 2000,
            "active_miners": 50
        }
        
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 200
                mock_http_response.json.return_value = mock_response
                mock_http_response.raise_for_status = MagicMock()
                mock_request.return_value = mock_http_response
                
                result = await client.epoch()
                
                assert isinstance(result, EpochInfo)
                assert result.current_epoch == 100
                assert result.start_height == 1000
    
    @pytest.mark.asyncio
    async def test_miners_success(self):
        """Test miners list success."""
        mock_response = {
            "miners": [
                {
                    "id": "miner1",
                    "address": "addr1",
                    "stake": 100.0,
                    "blocks_mined": 50
                },
                {
                    "id": "miner2",
                    "address": "addr2",
                    "stake": 200.0,
                    "blocks_mined": 100
                }
            ]
        }
        
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 200
                mock_http_response.json.return_value = mock_response
                mock_http_response.raise_for_status = MagicMock()
                mock_request.return_value = mock_http_response
                
                result = await client.miners(limit=100, active_only=True)
                
                assert len(result) == 2
                assert all(isinstance(m, Miner) for m in result)
                assert result[0].id == "miner1"
                assert result[1].id == "miner2"
    
    @pytest.mark.asyncio
    async def test_balance_success(self):
        """Test balance check success."""
        mock_response = {
            "wallet_id": "wallet1",
            "address": "addr1",
            "balance": 150.5
        }
        
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 200
                mock_http_response.json.return_value = mock_response
                mock_http_response.raise_for_status = MagicMock()
                mock_request.return_value = mock_http_response
                
                result = await client.balance("wallet1")
                
                assert isinstance(result, Balance)
                assert result.wallet_id == "wallet1"
                assert result.balance == 150.5
    
    @pytest.mark.asyncio
    async def test_transfer_success(self):
        """Test transfer success."""
        mock_response = {
            "tx_hash": "tx123",
            "from_address": "addr1",
            "to_address": "addr2",
            "amount": 10.0,
            "status": "pending"
        }
        
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 200
                mock_http_response.json.return_value = mock_response
                mock_http_response.raise_for_status = MagicMock()
                mock_request.return_value = mock_http_response
                
                result = await client.transfer("addr1", "addr2", 10.0, "sig123")
                
                assert isinstance(result, TransferResult)
                assert result.tx_hash == "tx123"
                assert result.amount == 10.0
    
    @pytest.mark.asyncio
    async def test_attestation_status_success(self):
        """Test attestation status success."""
        mock_response = {
            "miner_id": "miner1",
            "status": "active",
            "score": 0.95
        }
        
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 200
                mock_http_response.json.return_value = mock_response
                mock_http_response.raise_for_status = MagicMock()
                mock_request.return_value = mock_http_response
                
                result = await client.attestation_status("miner1")
                
                assert isinstance(result, AttestationStatus)
                assert result.miner_id == "miner1"
                assert result.status == "active"
    
    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test connection error handling."""
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_request.side_effect = httpx.ConnectError("Connection failed")
                
                with pytest.raises(ConnectionError):
                    await client.health()
    
    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test timeout error handling."""
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_request.side_effect = httpx.TimeoutException("Timeout")
                
                with pytest.raises(TimeoutError):
                    await client.health()
    
    @pytest.mark.asyncio
    async def test_validation_error(self):
        """Test validation error handling (400)."""
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 400
                mock_http_response.content = b'{"message": "Invalid input"}'
                mock_http_response.json.return_value = {"message": "Invalid input"}
                mock_request.return_value = mock_http_response
                
                with pytest.raises(ValidationError) as exc_info:
                    await client.health()
                
                assert "Invalid input" in str(exc_info.value.message)
    
    @pytest.mark.asyncio
    async def test_not_found_error(self):
        """Test not found error handling (404)."""
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 404
                mock_request.return_value = mock_http_response
                
                with pytest.raises(NotFoundError):
                    await client.balance("nonexistent")
    
    @pytest.mark.asyncio
    async def test_rate_limit_error(self):
        """Test rate limit error handling (429)."""
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 429
                mock_http_response.headers = {"Retry-After": "60"}
                mock_request.return_value = mock_http_response
                
                with pytest.raises(RateLimitError) as exc_info:
                    await client.health()
                
                assert exc_info.value.retry_after == 60
    
    @pytest.mark.asyncio
    async def test_server_error(self):
        """Test server error handling (5xx)."""
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 500
                mock_request.return_value = mock_http_response
                
                with pytest.raises(ServerError):
                    await client.health()
    
    @pytest.mark.asyncio
    async def test_insufficient_funds_error(self):
        """Test insufficient funds error."""
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 400
                mock_http_response.content = b'{"message": "Insufficient funds"}'
                mock_http_response.json.return_value = {"message": "Insufficient funds"}
                mock_request.return_value = mock_http_response
                
                with pytest.raises(InsufficientFundsError):
                    await client.transfer("addr1", "addr2", 100.0, "sig123")
    
    @pytest.mark.asyncio
    async def test_invalid_signature_error(self):
        """Test invalid signature error."""
        async with RustChainClient() as client:
            with patch.object(client._client, "request", new_callable=AsyncMock) as mock_request:
                mock_http_response = MagicMock(spec=httpx.Response)
                mock_http_response.status_code = 400
                mock_http_response.content = b'{"message": "Invalid signature"}'
                mock_http_response.json.return_value = {"message": "Invalid signature"}
                mock_request.return_value = mock_http_response
                
                with pytest.raises(InvalidSignatureError):
                    await client.transfer("addr1", "addr2", 10.0, "bad_sig")