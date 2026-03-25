"""Unit tests for RustChain Python SDK — 25 tests."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from rustchain import RustChainClient, AsyncRustChainClient
from rustchain.exceptions import APIError, ConnectionError, ValidationError
import requests

@pytest.fixture
def client():
    return RustChainClient(base_url="https://test-node.example.com", verify_ssl=False)

def mock_response(json_data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = json_data
    resp.text = str(json_data)
    return resp

class TestRustChainClient:
    def test_init_default(self):
        c = RustChainClient()
        assert c.base_url == "https://50.28.86.131"
        assert c.timeout == 30

    def test_init_custom(self):
        c = RustChainClient(base_url="http://localhost:8080/", timeout=5)
        assert c.base_url == "http://localhost:8080"
        assert c.timeout == 5

    @patch.object(requests.Session, "get")
    def test_health(self, mock_get, client):
        mock_get.return_value = mock_response({"status": "ok"})
        assert client.health() == {"status": "ok"}

    @patch.object(requests.Session, "get")
    def test_epoch(self, mock_get, client):
        mock_get.return_value = mock_response({"epoch": 42, "started": "2026-01-01"})
        result = client.epoch()
        assert result["epoch"] == 42

    @patch.object(requests.Session, "get")
    def test_miners(self, mock_get, client):
        mock_get.return_value = mock_response([{"id": "m1"}, {"id": "m2"}])
        miners = client.miners()
        assert len(miners) == 2

    @patch.object(requests.Session, "get")
    def test_balance(self, mock_get, client):
        mock_get.return_value = mock_response({"wallet": "abc", "balance": 100.5})
        result = client.balance("abc")
        assert result["balance"] == 100.5

    def test_balance_empty_wallet(self, client):
        with pytest.raises(ValidationError):
            client.balance("")

    @patch.object(requests.Session, "post")
    def test_transfer(self, mock_post, client):
        mock_post.return_value = mock_response({"tx_id": "tx123"})
        result = client.transfer("a", "b", 10.0, "sig")
        assert result["tx_id"] == "tx123"

    def test_transfer_negative_amount(self, client):
        with pytest.raises(ValidationError):
            client.transfer("a", "b", -5, "sig")

    def test_transfer_zero_amount(self, client):
        with pytest.raises(ValidationError):
            client.transfer("a", "b", 0, "sig")

    @patch.object(requests.Session, "get")
    def test_attestation_status(self, mock_get, client):
        mock_get.return_value = mock_response({"miner": "m1", "attested": True})
        result = client.attestation_status("m1")
        assert result["attested"] is True

    @patch.object(requests.Session, "get")
    def test_api_error_404(self, mock_get, client):
        mock_get.return_value = mock_response("Not found", 404)
        with pytest.raises(APIError) as exc:
            client.health()
        assert exc.value.status_code == 404

    @patch.object(requests.Session, "get")
    def test_api_error_500(self, mock_get, client):
        mock_get.return_value = mock_response("Server error", 500)
        with pytest.raises(APIError) as exc:
            client.miners()
        assert exc.value.status_code == 500

    @patch.object(requests.Session, "get")
    def test_connection_error(self, mock_get, client):
        mock_get.side_effect = requests.ConnectionError("refused")
        with pytest.raises(ConnectionError):
            client.health()

    @patch.object(requests.Session, "get")
    def test_timeout_error(self, mock_get, client):
        mock_get.side_effect = requests.Timeout("timed out")
        with pytest.raises(ConnectionError):
            client.health()

    @patch.object(requests.Session, "get")
    def test_explorer_blocks(self, mock_get, client):
        mock_get.return_value = mock_response([{"block": 1}, {"block": 2}])
        blocks = client.explorer.blocks(limit=2)
        assert len(blocks) == 2

    @patch.object(requests.Session, "get")
    def test_explorer_transactions(self, mock_get, client):
        mock_get.return_value = mock_response([{"tx": "a"}])
        txns = client.explorer.transactions(limit=1)
        assert len(txns) == 1

    @patch.object(requests.Session, "get")
    def test_explorer_block_by_id(self, mock_get, client):
        mock_get.return_value = mock_response({"id": "b1", "height": 100})
        block = client.explorer.block("b1")
        assert block["height"] == 100

    def test_context_manager(self):
        with RustChainClient() as c:
            assert c.base_url == "https://50.28.86.131"

    @patch.object(requests.Session, "post")
    def test_post_connection_error(self, mock_post, client):
        mock_post.side_effect = requests.ConnectionError("refused")
        with pytest.raises(ConnectionError):
            client.transfer("a", "b", 1, "sig")

    @patch.object(requests.Session, "post")
    def test_post_api_error(self, mock_post, client):
        mock_post.return_value = mock_response("Bad request", 400)
        with pytest.raises(APIError):
            client.transfer("a", "b", 1, "sig")

class TestExceptions:
    def test_api_error_str(self):
        e = APIError(404, "Not found")
        assert "404" in str(e)
        assert "Not found" in str(e)

    def test_validation_error_inherits(self):
        from rustchain.exceptions import RustChainError
        assert issubclass(ValidationError, RustChainError)

    def test_connection_error_inherits(self):
        from rustchain.exceptions import RustChainError
        assert issubclass(ConnectionError, RustChainError)

class TestImports:
    def test_package_imports(self):
        from rustchain import RustChainClient, AsyncRustChainClient, Explorer
        assert RustChainClient is not None

    def test_version(self):
        import rustchain
        assert rustchain.__version__ == "0.1.0"
