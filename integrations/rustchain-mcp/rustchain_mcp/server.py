from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .client import BoTTubeClient, RustChainClient

mcp = FastMCP("rustchain")
client = RustChainClient.from_env()
bottube_client = BoTTubeClient.from_env()


def _to_pretty(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


@mcp.tool()
async def rustchain_health() -> str:
    """Check node health across RustChain attestation nodes (with failover)."""
    data = await client.health()
    return _to_pretty(data)


@mcp.tool()
async def rustchain_miners() -> str:
    """List active miners and their architectures."""
    data = await client.miners()
    return _to_pretty(data)


@mcp.tool()
async def rustchain_epoch() -> str:
    """Get current epoch info (slot, height, rewards)."""
    data = await client.epoch()
    return _to_pretty(data)


@mcp.tool()
async def rustchain_balance(miner_id: str) -> str:
    """Get RTC balance for a wallet/miner_id."""
    data = await client.balance(miner_id)
    return _to_pretty(data)


@mcp.tool()
async def rustchain_transfer(
    from_wallet: str,
    to_wallet: str,
    amount_rtc: float,
    private_key: Optional[str] = None,
) -> str:
    """Send RTC (requires wallet key).

    NOTE: The bounty prompt does not include a signing/broadcast API.
    This tool currently returns a clear stub error until the transfer API is confirmed.
    """
    _ = (from_wallet, to_wallet, amount_rtc, private_key)
    raise RuntimeError(
        "rustchain_transfer is not yet implemented: signing/broadcast API not provided in the bounty spec. "
        "If RustChain exposes a transfer endpoint, share it and this tool will be completed."
    )


@mcp.tool()
async def bottube_trending(category: Optional[str] = None, limit: int = 10) -> str:
    """Fetch trending BoTTube videos, optionally filtered by category."""
    data = await bottube_client.trending(category=category, limit=limit)
    return _to_pretty(data)


@mcp.tool()
async def bottube_search(query: str, limit: int = 10, page: int = 1, sort: str = "trending") -> str:
    """Search BoTTube videos by query."""
    data = await bottube_client.search(query=query, limit=limit, page=page, sort=sort)
    return _to_pretty(data)


@mcp.tool()
async def bottube_video(video_id: str) -> str:
    """Fetch BoTTube video details by video ID."""
    data = await bottube_client.video(video_id)
    return _to_pretty(data)


@mcp.tool()
async def bottube_agent(agent_name: str) -> str:
    """Fetch a BoTTube agent profile by agent name."""
    data = await bottube_client.agent(agent_name)
    return _to_pretty(data)


@mcp.tool()
async def bottube_stats() -> str:
    """Fetch BoTTube platform statistics."""
    data = await bottube_client.stats()
    return _to_pretty(data)


@mcp.tool()
async def bottube_upload(file_path: str, title: str, description: str = "") -> str:
    """Upload a local video file to BoTTube using BOTTUBE_API_KEY."""
    data = await bottube_client.upload(file_path=file_path, title=title, description=description)
    return _to_pretty(data)


if __name__ == "__main__":
    mcp.run()
