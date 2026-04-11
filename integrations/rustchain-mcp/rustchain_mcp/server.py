from __future__ import annotations

import json
import os
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .client import RustChainClient

mcp = FastMCP("rustchain")
client = RustChainClient.from_env()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_OWNER = "Scottcjn"
REPO_NAME = "rustchain-bounties"


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
async def rustchain_register_wallet(wallet_name: str) -> str:
    """Register a new RustChain wallet for an AI agent.

    Calls POST /wallet/register on the BCOS node.
    The wallet is identified by wallet_name (used as wallet_id).
    """
    result = await client.register_wallet(wallet_name)
    return _to_pretty(result)


@mcp.tool()
async def rustchain_submit_attestation(wallet_name: str, hardware_signature: str = "") -> str:
    """Submit a hardware fingerprint / proof-of-physical-AI attestation.

    The attestation proves the agent is running on real hardware.
    hardware_signature is optional metadata about the hardware.
    """
    result = await client.submit_attestation(wallet_name, hardware_signature)
    return _to_pretty(result)


@mcp.tool()
async def rustchain_bounties(
    label: Optional[str] = None,
    max_results: int = 10,
) -> str:
    """List open RustChain bounties from the GitHub issue tracker.

    Filter by optional label (e.g. 'bounty', 'easy', 'major').
    Returns issue number, title, reward, and URL.
    """
    import httpx

    query = f"repo:{REPO_OWNER}/{REPO_NAME} is:issue state:open label:bounty"
    if label:
        query += f" label:{label}"

    query_url = "https://api.github.com/search/issues"
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.get(
                query_url,
                headers=headers,
                params={"q": query, "per_page": max_results, "sort": "created", "order": "desc"},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        return json.dumps({"error": f"GitHub API error: {e}"})

    items = []
    for issue in data.get("items", []):
        bounty_label = next((l["name"] for l in issue["labels"] if "bounty" in l["name"].lower()), "")
        items.append({
            "number": issue["number"],
            "title": issue["title"],
            "url": issue["html_url"],
            "state": issue["state"],
            "label": bounty_label,
            "comments": issue["comments"],
            "created": issue["created_at"][:10],
        })

    return _to_pretty({
        "total": data.get("total_count", 0),
        "returned": len(items),
        "bounties": items,
    })


if __name__ == "__main__":
    mcp.run()
