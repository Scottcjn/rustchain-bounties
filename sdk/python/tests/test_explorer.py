"""
Unit tests for ExplorerClient.
"""

import json
import pytest
import urllib.error
from unittest.mock import MagicMock, patch, Mock

from rustchain.explorer import ExplorerClient
from rustchain.exceptions import APIError, NetworkError


@pytest.fixture
def explorer():
    """Create an explorer client with SSL verification disabled."""
    return ExplorerClient(
        base_url="https://test.rustchain.org",
        verify_ssl=False,
        timeout=10,
        retry_count=1,
    )


# ------------------------------------------------------------------
# Blocks
# ------------------------------------------------------------------

class TestExplorerBlocks:
    def test_blocks_returns_list(self, explorer):
        mock_resp = [
            {
                "block_hash": "0xabc",
                "height": 100,
                "timestamp": "2026-03-26T10:00:00Z",
                "tx_count": 5,
                "miner": "miner-1",
                "reward": 1.5,
            }
        ]

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = explorer.blocks()
            assert isinstance(result, list)
            assert result[0]["height"] == 100

    def test_blocks_with_limit(self, explorer):
        opened = []

        def fake_open(req, **kwargs):
            opened.append(req)
            return _mock_response([])

        with patch.object(urllib.request, "urlopen", side_effect=fake_open):
            explorer.blocks(limit=50)

        assert "limit=50" in opened[0].full_url

    def test_blocks_default_limit(self, explorer):
        opened = []

        def fake_open(req, **kwargs):
            opened.append(req)
            return _mock_response([])

        with patch.object(urllib.request, "urlopen", side_effect=fake_open):
            explorer.blocks()

        assert "limit=20" in opened[0].full_url


# ------------------------------------------------------------------
# Transactions
# ------------------------------------------------------------------

class TestExplorerTransactions:
    def test_transactions_returns_list(self, explorer):
        mock_resp = [
            {
                "tx_hash": "0xtx1",
                "from": "wallet-a",
                "to": "wallet-b",
                "amount": 10.0,
                "fee": 0.001,
                "timestamp": "2026-03-26T10:00:00Z",
                "block_height": 100,
            }
        ]

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = explorer.transactions()
            assert isinstance(result, list)
            assert result[0]["tx_hash"] == "0xtx1"

    def test_transactions_filter_by_wallet(self, explorer):
        opened = []

        def fake_open(req, **kwargs):
            opened.append(req)
            return _mock_response([])

        with patch.object(urllib.request, "urlopen", side_effect=fake_open):
            explorer.transactions(wallet_id="my-wallet")

        assert "wallet_id=my-wallet" in opened[0].full_url

    def test_transactions_filter_by_block(self, explorer):
        opened = []

        def fake_open(req, **kwargs):
            opened.append(req)
            return _mock_response([])

        with patch.object(urllib.request, "urlopen", side_effect=fake_open):
            explorer.transactions(block_hash="0xblock")

        assert "block_hash=0xblock" in opened[0].full_url

    def test_transactions_combined_filters(self, explorer):
        opened = []

        def fake_open(req, **kwargs):
            opened.append(req)
            return _mock_response([])

        with patch.object(urllib.request, "urlopen", side_effect=fake_open):
            explorer.transactions(wallet_id="w1", block_hash="0xb1", limit=10)

        url = opened[0].full_url
        assert "wallet_id=w1" in url
        assert "block_hash=0xb1" in url
        assert "limit=10" in url


# ------------------------------------------------------------------
# Block Detail
# ------------------------------------------------------------------

class TestBlockDetail:
    def test_block_detail_returns_dict(self, explorer):
        mock_resp = {
            "block_hash": "0xabc",
            "height": 100,
            "txs": [{"tx_hash": "0xtx1"}, {"tx_hash": "0xtx2"}],
        }

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = explorer.block_detail("0xabc")
            assert result["block_hash"] == "0xabc"
            assert len(result["txs"]) == 2


# ------------------------------------------------------------------
# Transaction Detail
# ------------------------------------------------------------------

class TestTransactionDetail:
    def test_transaction_detail_returns_dict(self, explorer):
        mock_resp = {
            "tx_hash": "0xtx1",
            "from": "wallet-a",
            "to": "wallet-b",
            "amount": 10.0,
        }

        with patch.object(
            urllib.request, "urlopen", return_value=_mock_response(mock_resp)
        ):
            result = explorer.transaction_detail("0xtx1")
            assert result["tx_hash"] == "0xtx1"


# ------------------------------------------------------------------
# Error handling
# ------------------------------------------------------------------

class TestExplorerErrors:
    def test_api_error_on_http_error(self, explorer):
        error = urllib.error.HTTPError(
            url="https://test/explorer/blocks",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )

        with patch.object(urllib.request, "urlopen", side_effect=error):
            with pytest.raises(APIError) as exc_info:
                explorer.blocks()
            assert exc_info.value.status_code == 404

    def test_network_error_on_url_error(self, explorer):
        error = urllib.error.URLError("Connection refused")

        with patch.object(urllib.request, "urlopen", side_effect=error):
            with pytest.raises(NetworkError):
                explorer.blocks()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _mock_response(data):
    mock = MagicMock()
    mock.__enter__ = Mock(return_value=mock)
    mock.__exit__ = Mock(return_value=False)
    mock.read.return_value = json.dumps(data).encode("utf-8")
    mock.__iter__ = Mock(return_value=iter([]))
    return mock
