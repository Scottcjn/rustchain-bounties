"""
Tests for RustChainClient.
Uses respx for HTTP mocking.
"""

import pytest
import respx
import httpx
from rustchain_sdk.client import RustChainClient
from rustchain_sdk.exceptions import ConnectionError, APIError
import asyncio

class TestRustChainClientInit:
    """Test client initialization."""

    def test_default_base_url(self):
        """Default base URL is set correctly."""
        client = RustChainClient()
        assert client._base_url == "https://50.28.86.131"

    def test_custom_base_url(self):
        """Custom base URL is set correctly."""
        client = RustChainClient(base_url="https://custom.node.com")
        assert client._base_url == "https://custom.node.com"

    def test_base_url_trailing_slash_stripped(self):
        """Trailing slash is stripped from base URL."""
        client = RustChainClient(base_url="https://node.com/")
        assert client._base_url == "https://node.com"

    def test_default_timeout(self):
        """Default timeout is 30 seconds."""
        client = RustChainClient()
        assert client._timeout == 30.0

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager behavior."""
        client = RustChainClient()
        async with client as c:
            assert c is client
            assert c._client is not None
        assert client._client is None

class TestRustChainClientHealth:
    """Test health endpoint."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_returns_dict(self):
        """Health returns a dict."""
        route = respx.get("https://50.28.86.131/health").mock(
            return_value=httpx.Response(200, json={"status": "ok", "version": "1.0.0"})
        )
        async with RustChainClient() as client:
            result = await client.health()
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    @respx.mock
    async def test_health_connection_error(self):
        """Connection error raises RustChainError."""
        route = respx.get("https://50.28.86.131/health").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        async with RustChainClient() as client:
            with pytest.raises(ConnectionError):
                await client.health()

# [Остальной код файла остаётся без изменений]