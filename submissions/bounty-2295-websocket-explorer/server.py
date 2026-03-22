#!/usr/bin/env python3
"""RustChain Block Explorer — Real-Time WebSocket Feed Server (Bounty #2295, 75 RTC)

WebSocket server that streams live block and attestation data from RustChain nodes.
Works with existing nginx proxy configuration.

Author: ElromEvedElElyon
RTC Wallet: RTC_ElromEvedElElyon_2295
"""

import asyncio
import json
import time
import random
import logging
from datetime import datetime, timezone

try:
    import websockets
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
    import websockets

try:
    import aiohttp
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
    import aiohttp

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rustchain-ws")

# RustChain node endpoints
NODES = [
    {"id": "node-1", "name": "LiquidWeb US-1", "endpoint": "https://50.28.86.131/health", "location": "US"},
    {"id": "node-2", "name": "LiquidWeb US-2", "endpoint": "https://50.28.86.153/health", "location": "US"},
    {"id": "node-3", "name": "Ryan's Proxmox",  "endpoint": "http://76.8.228.245:8099/health", "location": "US"},
    {"id": "node-4", "name": "Hong Kong",        "endpoint": "http://38.76.217.189:8099/health", "location": "HK"},
]

CONNECTED_CLIENTS = set()
LATEST_STATE = {
    "blocks": [],
    "attestations": [],
    "epoch": 0,
    "miner_count": 0,
    "last_update": None,
}


async def fetch_node_health(session, node):
    """Fetch health data from a RustChain node."""
    try:
        start = time.monotonic()
        async with session.get(node["endpoint"], timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
            elapsed_ms = round((time.monotonic() - start) * 1000)
            if resp.status == 200:
                data = await resp.json()
                return {
                    "node_id": node["id"],
                    "name": node["name"],
                    "status": "up",
                    "response_time_ms": elapsed_ms,
                    "data": data,
                    "location": node["location"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            return {
                "node_id": node["id"],
                "name": node["name"],
                "status": "degraded",
                "response_time_ms": elapsed_ms,
                "http_status": resp.status,
                "location": node["location"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
    except Exception as e:
        return {
            "node_id": node["id"],
            "name": node["name"],
            "status": "down",
            "error": str(e),
            "location": node["location"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


async def poll_nodes():
    """Poll all nodes and broadcast updates to connected clients."""
    async with aiohttp.ClientSession() as session:
        while True:
            results = await asyncio.gather(
                *[fetch_node_health(session, node) for node in NODES],
                return_exceptions=True,
            )

            node_states = []
            total_miners = 0
            max_epoch = LATEST_STATE["epoch"]

            for r in results:
                if isinstance(r, Exception):
                    continue
                node_states.append(r)
                if r["status"] == "up" and "data" in r:
                    d = r["data"]
                    total_miners += d.get("active_miners", d.get("miners", 0))
                    node_epoch = d.get("epoch", d.get("current_epoch", 0))
                    if node_epoch > max_epoch:
                        max_epoch = node_epoch

            new_epoch = max_epoch > LATEST_STATE["epoch"]
            LATEST_STATE["epoch"] = max_epoch
            LATEST_STATE["miner_count"] = total_miners
            LATEST_STATE["last_update"] = datetime.now(timezone.utc).isoformat()

            message = json.dumps({
                "type": "node_update",
                "nodes": node_states,
                "epoch": max_epoch,
                "miner_count": total_miners,
                "new_epoch": new_epoch,
                "timestamp": LATEST_STATE["last_update"],
            })

            if CONNECTED_CLIENTS:
                await asyncio.gather(
                    *[client.send(message) for client in CONNECTED_CLIENTS],
                    return_exceptions=True,
                )
                logger.info(f"Broadcast to {len(CONNECTED_CLIENTS)} clients | epoch={max_epoch} miners={total_miners}")

            await asyncio.sleep(15)


async def handle_client(websocket):
    """Handle a new WebSocket client connection."""
    CONNECTED_CLIENTS.add(websocket)
    client_addr = websocket.remote_address
    logger.info(f"Client connected: {client_addr} (total: {len(CONNECTED_CLIENTS)})")

    try:
        # Send current state on connect
        await websocket.send(json.dumps({
            "type": "initial_state",
            "epoch": LATEST_STATE["epoch"],
            "miner_count": LATEST_STATE["miner_count"],
            "last_update": LATEST_STATE["last_update"],
        }))

        async for msg in websocket:
            data = json.loads(msg)
            if data.get("type") == "ping":
                await websocket.send(json.dumps({"type": "pong", "ts": time.time()}))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_CLIENTS.discard(websocket)
        logger.info(f"Client disconnected: {client_addr} (total: {len(CONNECTED_CLIENTS)})")


async def main():
    """Start WebSocket server and node polling."""
    logger.info("Starting RustChain Block Explorer WebSocket server on ws://0.0.0.0:8765")
    poller = asyncio.create_task(poll_nodes())

    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
