"""
rustchain.websocket
~~~~~~~~~~~~~~~~~~~

WebSocket client for real-time RustChain block and transaction feeds.

Bonus feature providing live streaming of new blocks and transactions
as they are confirmed on the network.

Usage::

    from rustchain.websocket import RustChainWebSocket

    async def on_block(block):
        print(f"New block #{block.height}")

    ws = RustChainWebSocket("wss://50.28.86.131/ws")
    ws.on_block(on_block)
    await ws.connect()  # runs until cancelled
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional

from rustchain.models import Block, Transaction

logger = logging.getLogger("rustchain.websocket")

# Type alias for event callbacks
BlockCallback = Callable[[Block], Coroutine[Any, Any, None]]
TransactionCallback = Callable[[Transaction], Coroutine[Any, Any, None]]
RawCallback = Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]


class RustChainWebSocket:
    """Async WebSocket client for real-time RustChain feeds.

    Parameters:
        ws_url: WebSocket endpoint, e.g. ``"wss://50.28.86.131/ws"``
            or ``"ws://localhost:8080/ws"``.
        reconnect: Automatically reconnect on disconnection (default True).
        reconnect_delay: Seconds to wait before reconnecting (default 5).
        max_reconnect_attempts: Maximum reconnect attempts (0 = unlimited).
        ping_interval: Seconds between keep-alive pings (default 30).
    """

    def __init__(
        self,
        ws_url: str,
        *,
        reconnect: bool = True,
        reconnect_delay: float = 5.0,
        max_reconnect_attempts: int = 0,
        ping_interval: float = 30.0,
        ssl_verify: bool = False,
    ) -> None:
        self._ws_url = ws_url
        self._reconnect = reconnect
        self._reconnect_delay = reconnect_delay
        self._max_reconnect_attempts = max_reconnect_attempts
        self._ping_interval = ping_interval
        self._ssl_verify = ssl_verify

        self._block_callbacks: List[BlockCallback] = []
        self._tx_callbacks: List[TransactionCallback] = []
        self._raw_callbacks: List[RawCallback] = []
        self._running = False
        self._ws: Any = None  # websockets connection

    # -- callback registration --

    def on_block(self, callback: BlockCallback) -> None:
        """Register a coroutine to be called on each new block."""
        self._block_callbacks.append(callback)

    def on_transaction(self, callback: TransactionCallback) -> None:
        """Register a coroutine to be called on each new transaction."""
        self._tx_callbacks.append(callback)

    def on_message(self, callback: RawCallback) -> None:
        """Register a coroutine to be called on every raw WebSocket message."""
        self._raw_callbacks.append(callback)

    # -- connection lifecycle --

    async def connect(self) -> None:
        """Connect and start listening. Blocks until :meth:`disconnect` is called.

        Requires the ``websockets`` package::

            pip install websockets
        """
        try:
            import websockets  # noqa: F401
        except ImportError:
            raise ImportError(
                "WebSocket support requires the 'websockets' package. "
                "Install it with: pip install rustchain-sdk[ws]"
            )

        self._running = True
        attempts = 0

        while self._running:
            try:
                await self._listen()
            except Exception as exc:
                if not self._running:
                    break
                attempts += 1
                logger.warning(
                    "WebSocket disconnected (%s). Attempt %d.",
                    exc,
                    attempts,
                )
                if not self._reconnect:
                    raise
                if self._max_reconnect_attempts and attempts >= self._max_reconnect_attempts:
                    logger.error("Max reconnect attempts (%d) reached.", attempts)
                    raise
                await asyncio.sleep(self._reconnect_delay)

    async def disconnect(self) -> None:
        """Gracefully close the WebSocket connection."""
        self._running = False
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    @property
    def is_connected(self) -> bool:
        """Whether the WebSocket connection is active."""
        return self._ws is not None and self._running

    # -- internal --

    async def _listen(self) -> None:
        """Open a single WebSocket connection and process messages."""
        import ssl as _ssl

        import websockets

        ssl_context: Optional[_ssl.SSLContext] = None
        if self._ws_url.startswith("wss://") and not self._ssl_verify:
            ssl_context = _ssl.SSLContext(_ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = _ssl.CERT_NONE

        async with websockets.connect(
            self._ws_url,
            ssl=ssl_context,
            ping_interval=self._ping_interval,
        ) as ws:
            self._ws = ws
            logger.info("Connected to %s", self._ws_url)

            # Subscribe to block and transaction feeds
            subscribe_msg = json.dumps({
                "action": "subscribe",
                "channels": ["blocks", "transactions"],
            })
            await ws.send(subscribe_msg)

            async for raw_message in ws:
                if not self._running:
                    break
                await self._handle_message(raw_message)

    async def _handle_message(self, raw: str) -> None:
        """Parse and dispatch a single WebSocket message."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.debug("Non-JSON message: %s", raw[:200])
            return

        # Fire raw callbacks
        for cb in self._raw_callbacks:
            try:
                await cb(data)
            except Exception:
                logger.exception("Error in raw message callback")

        msg_type = data.get("type", data.get("event", ""))

        if msg_type in ("block", "new_block"):
            block_data = data.get("data", data.get("block", data))
            block = Block.from_dict(block_data)
            for cb in self._block_callbacks:
                try:
                    await cb(block)
                except Exception:
                    logger.exception("Error in block callback")

        elif msg_type in ("transaction", "new_transaction", "tx"):
            tx_data = data.get("data", data.get("transaction", data))
            tx = Transaction.from_dict(tx_data)
            for cb in self._tx_callbacks:
                try:
                    await cb(tx)
                except Exception:
                    logger.exception("Error in transaction callback")

    # -- convenience --

    async def subscribe(self, channel: str) -> None:
        """Subscribe to an additional channel (e.g., 'miners', 'attestations')."""
        if self._ws is None:
            raise RuntimeError("Not connected. Call connect() first.")
        msg = json.dumps({"action": "subscribe", "channels": [channel]})
        await self._ws.send(msg)

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel."""
        if self._ws is None:
            raise RuntimeError("Not connected. Call connect() first.")
        msg = json.dumps({"action": "unsubscribe", "channels": [channel]})
        await self._ws.send(msg)
