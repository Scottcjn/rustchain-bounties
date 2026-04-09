from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .client import RustChainClient

mcp = FastMCP("rustchain")
client = RustChainClient.from_env()


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


if __name__ == "__main__":
    mcp.run()
