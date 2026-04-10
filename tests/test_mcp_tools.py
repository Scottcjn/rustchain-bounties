import pytest
from rustchain_mcp_server.lib import rustchain_health, rustchain_balance

# Tests for rustchain_health function
class TestRustchainHealth:
    @pytest.mark.asyncio
    async def test_health_check(self, mocker):
        # Mock the HTTP response
        mock_get = mocker.patch('rustchain_mcp_server.lib.reqwest.get')
        mock_get.return_value.__aenter__.return_value.status.return_value = 200
        mock_get.return_value.__aenter__.return_value.json.return_value = {"ok": True}

        response = await rustchain_health()
        assert response == "Node is healthy: {\"ok\": True}"

    @pytest.mark.asyncio
    async def test_health_check_failure(self, mocker):
        mock_get = mocker.patch('rustchain_mcp_server.lib.reqwest.get')
        mock_get.return_value.__aenter__.return_value.status.return_value = 500

        with pytest.raises(Exception) as e:
            await rustchain_health()
        assert "Health check failed: 500" in str(e.value)

# Tests for rustchain_balance function
class TestRustchainBalance:
    @pytest.mark.asyncio
    async def test_balance_check(self, mocker):
        mock_get = mocker.patch('rustchain_mcp_server.lib.reqwest.get')
        wallet_address = "test_wallet"
        mock_get.return_value.__aenter__.return_value.status.return_value = 200
        mock_get.return_value.__aenter__.return_value.json.return_value = {"balance": 100.0}

        balance = await rustchain_balance(wallet_address)
        assert balance == 100.0

    @pytest.mark.asyncio
    async def test_balance_check_failure(self, mocker):
        mock_get = mocker.patch('rustchain_mcp_server.lib.reqwest.get')
        wallet_address = "test_wallet"
        mock_get.return_value.__aenter__.return_value.status.return_value = 404

        with pytest.raises(Exception) as e:
            await rustchain_balance(wallet_address)
        assert "Balance check failed: 404" in str(e.value)