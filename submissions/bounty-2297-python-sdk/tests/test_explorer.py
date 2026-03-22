"""
Tests for the block explorer API (sync and async).
"""

from __future__ import annotations

import pytest
import respx

from rustchain.client import AsyncRustChainClient, RustChainClient
from rustchain.models import Block, Transaction

from .conftest import BLOCKS_RESPONSE, NODE_URL, TRANSACTIONS_RESPONSE


class TestSyncExplorer:
    def test_blocks(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            blocks = client.explorer.blocks(limit=2)
        assert len(blocks) == 2
        assert all(isinstance(b, Block) for b in blocks)
        assert blocks[0].height == 142857
        assert blocks[0].block_hash == "0xblock_hash_142857"

    def test_transactions(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            txs = client.explorer.transactions(limit=2)
        assert len(txs) == 2
        assert all(isinstance(t, Transaction) for t in txs)
        assert txs[0].tx_hash == "0xtx_001"
        assert txs[0].amount == 50.0

    def test_block_contains_transactions(self, mock_api):
        with RustChainClient(NODE_URL) as client:
            blocks = client.explorer.blocks()
        block = blocks[0]
        assert len(block.transactions) == 1
        assert block.transactions[0].from_wallet == "RTC_a"

    def test_single_block(self):
        single_block = {
            "height": 100,
            "hash": "0xsingle",
            "miner": "m1",
            "transactions": [],
        }
        with respx.mock(base_url=NODE_URL) as router:
            router.get("/api/explorer/blocks/100").respond(json=single_block)
            with RustChainClient(NODE_URL) as client:
                block = client.explorer.block(100)
            assert block.height == 100
            assert block.block_hash == "0xsingle"

    def test_single_transaction(self):
        single_tx = {
            "hash": "0xtx_specific",
            "from": "w1",
            "to": "w2",
            "amount": 42.0,
        }
        with respx.mock(base_url=NODE_URL) as router:
            router.get("/api/explorer/transactions/0xtx_specific").respond(json=single_tx)
            with RustChainClient(NODE_URL) as client:
                tx = client.explorer.transaction("0xtx_specific")
            assert tx.tx_hash == "0xtx_specific"
            assert tx.amount == 42.0


@pytest.mark.asyncio
class TestAsyncExplorer:
    async def test_blocks(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            blocks = await client.explorer.blocks(limit=2)
        assert len(blocks) == 2
        assert blocks[0].height == 142857

    async def test_transactions(self, mock_api):
        async with AsyncRustChainClient(NODE_URL) as client:
            txs = await client.explorer.transactions()
        assert len(txs) == 2
        assert txs[1].tx_hash == "0xtx_002"

    async def test_single_block(self):
        single = {"height": 200, "hash": "0xasync_block", "transactions": []}
        with respx.mock(base_url=NODE_URL) as router:
            router.get("/api/explorer/blocks/200").respond(json=single)
            async with AsyncRustChainClient(NODE_URL) as client:
                block = await client.explorer.block(200)
            assert block.height == 200
