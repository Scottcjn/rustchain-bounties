"""
Tests for the WebSocket module.

These tests verify callback registration and message dispatch logic
without requiring a live WebSocket connection.
"""

from __future__ import annotations

import asyncio
import json

import pytest

from rustchain.models import Block, Transaction
from rustchain.websocket import RustChainWebSocket


class TestWebSocketCallbacks:
    def test_register_block_callback(self):
        ws = RustChainWebSocket("wss://localhost/ws")

        async def cb(block: Block) -> None:
            pass

        ws.on_block(cb)
        assert len(ws._block_callbacks) == 1

    def test_register_transaction_callback(self):
        ws = RustChainWebSocket("wss://localhost/ws")

        async def cb(tx: Transaction) -> None:
            pass

        ws.on_transaction(cb)
        assert len(ws._tx_callbacks) == 1

    def test_register_raw_callback(self):
        ws = RustChainWebSocket("wss://localhost/ws")

        async def cb(data: dict) -> None:
            pass

        ws.on_message(cb)
        assert len(ws._raw_callbacks) == 1


class TestWebSocketMessageHandling:
    @pytest.mark.asyncio
    async def test_handle_block_message(self):
        ws = RustChainWebSocket("wss://localhost/ws")
        received_blocks = []

        async def on_block(block: Block) -> None:
            received_blocks.append(block)

        ws.on_block(on_block)

        msg = json.dumps({
            "type": "block",
            "data": {
                "height": 100,
                "hash": "0xtest",
                "miner": "m1",
                "transactions": [],
            },
        })
        await ws._handle_message(msg)
        assert len(received_blocks) == 1
        assert received_blocks[0].height == 100

    @pytest.mark.asyncio
    async def test_handle_transaction_message(self):
        ws = RustChainWebSocket("wss://localhost/ws")
        received_txs = []

        async def on_tx(tx: Transaction) -> None:
            received_txs.append(tx)

        ws.on_transaction(on_tx)

        msg = json.dumps({
            "type": "transaction",
            "data": {
                "hash": "0xtx_ws",
                "from": "a",
                "to": "b",
                "amount": 42.0,
            },
        })
        await ws._handle_message(msg)
        assert len(received_txs) == 1
        assert received_txs[0].tx_hash == "0xtx_ws"

    @pytest.mark.asyncio
    async def test_handle_raw_message(self):
        ws = RustChainWebSocket("wss://localhost/ws")
        raw_messages = []

        async def on_raw(data: dict) -> None:
            raw_messages.append(data)

        ws.on_message(on_raw)

        msg = json.dumps({"type": "custom", "foo": "bar"})
        await ws._handle_message(msg)
        assert len(raw_messages) == 1
        assert raw_messages[0]["foo"] == "bar"

    @pytest.mark.asyncio
    async def test_handle_invalid_json(self):
        ws = RustChainWebSocket("wss://localhost/ws")
        # Should not raise
        await ws._handle_message("not json at all {{{")

    @pytest.mark.asyncio
    async def test_new_block_event_type(self):
        """Test the 'new_block' event type variant."""
        ws = RustChainWebSocket("wss://localhost/ws")
        received = []

        async def on_block(block: Block) -> None:
            received.append(block)

        ws.on_block(on_block)

        msg = json.dumps({
            "type": "new_block",
            "data": {"height": 200, "hash": "0xnew"},
        })
        await ws._handle_message(msg)
        assert len(received) == 1
        assert received[0].height == 200


class TestWebSocketState:
    def test_initial_state(self):
        ws = RustChainWebSocket("wss://localhost/ws")
        assert ws.is_connected is False
        assert ws._running is False

    def test_config_options(self):
        ws = RustChainWebSocket(
            "wss://localhost/ws",
            reconnect=False,
            reconnect_delay=10.0,
            max_reconnect_attempts=3,
            ping_interval=60.0,
        )
        assert ws._reconnect is False
        assert ws._reconnect_delay == 10.0
        assert ws._max_reconnect_attempts == 3
        assert ws._ping_interval == 60.0
