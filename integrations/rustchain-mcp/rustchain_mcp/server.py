from __future__ import annotations

import json
import os
import ssl
import urllib.request
import urllib.error
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .client import RustChainClient

mcp = FastMCP("rustchain")
client = RustChainClient.from_env()

GITHUB_BOUNTIES_URL = (
    "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
    "?state=open&labels=bounty&per_page=20"
)


def _to_pretty(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


# ── Core network tools ────────────────────────────────────────────────────────

@mcp.tool()
async def rustchain_health() -> str:
    """Check RustChain node health (uptime, DB status, backup age)."""
    data = await client.health()
    return _to_pretty(data)


@mcp.tool()
async def rustchain_balance(wallet_id: str) -> str:
    """
    Query RTC balance for a wallet or miner ID.

    Args:
        wallet_id: Wallet name or miner ID (e.g. "my-wallet", "miner-abc123").
    """
    data = await client.balance(wallet_id)
    balance = float(data.get("balance", 0))
    usd = balance * 0.10
    return json.dumps({
        "wallet_id": wallet_id,
        "balance_rtc": balance,
        "balance_usd": round(usd, 4),
        "rate": "$0.10 per RTC",
        **{k: v for k, v in data.items() if k != "balance"},
    }, ensure_ascii=False, indent=2)


@mcp.tool()
async def rustchain_miners() -> str:
    """List active miners with antiquity multipliers and device info."""
    data = await client.miners()
    return _to_pretty(data)


@mcp.tool()
async def rustchain_epoch() -> str:
    """Get current epoch info: slot, height, enrolled miners, epoch pot."""
    data = await client.epoch()
    return _to_pretty(data)


@mcp.tool()
async def rustchain_network_stats() -> str:
    """
    Get overall RustChain network statistics.

    Returns total balance, miner count, supported RIPs, version, and security features.
    """
    data = await client.network_stats()
    return _to_pretty(data)


# ── Wallet management tools ───────────────────────────────────────────────────

@mcp.tool()
async def rustchain_create_wallet(wallet_id: str) -> str:
    """
    Register a new wallet on RustChain.

    Args:
        wallet_id: Desired wallet name (alphanumeric, hyphens, underscores).

    Note: Wallet registration is handled via the bounty submission workflow.
    Submit a PR to Scottcjn/rustchain-bounties with your wallet name to register.
    """
    # The node does not expose a public wallet-creation REST endpoint.
    # Registration happens through the bounty/PR workflow.
    return json.dumps({
        "wallet_id": wallet_id,
        "status": "registration_required",
        "message": (
            f"To register wallet '{wallet_id}', submit a PR to "
            "https://github.com/Scottcjn/rustchain-bounties with your wallet name "
            "in the PR body. The maintainer will register it and credit your RTC."
        ),
        "docs": "https://github.com/Scottcjn/rustchain-bounties/blob/main/CONTRIBUTING.md",
    }, indent=2)


@mcp.tool()
async def rustchain_submit_attestation(
    miner_id: str,
    device_arch: str,
    device_family: str,
    antiquity_year: int,
) -> str:
    """
    Submit a hardware attestation for Proof-of-Antiquity mining.

    Args:
        miner_id: Your miner/wallet ID.
        device_arch: CPU architecture (e.g. "arm64", "x86_64", "powerpc").
        device_family: Device family (e.g. "Apple M1", "Intel Core i7").
        antiquity_year: Year the device was manufactured (older = higher multiplier).

    Note: Full attestation requires running the RustChain miner binary which
    submits hardware fingerprints directly to the node. This tool shows what
    an attestation would contain.
    """
    multiplier = max(1.0, 1.0 + (2026 - antiquity_year) * 0.01)
    return json.dumps({
        "miner_id": miner_id,
        "device_arch": device_arch,
        "device_family": device_family,
        "antiquity_year": antiquity_year,
        "estimated_multiplier": round(multiplier, 3),
        "status": "preview",
        "message": (
            "To submit a live attestation, run the RustChain miner: "
            "https://github.com/Scottcjn/rustchain-bounties/tree/main/rustchain-miner"
        ),
    }, indent=2)


# ── Discovery tools ───────────────────────────────────────────────────────────

@mcp.tool()
async def rustchain_bounties(min_rtc: int = 0) -> str:
    """
    List open RustChain bounties from GitHub.

    Args:
        min_rtc: Minimum RTC reward to include (default: 0 = show all).
    """
    import re

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {"User-Agent": "rustchain-mcp/1.0", "Accept": "application/vnd.github.v3+json"}
    gh_token = os.getenv("GITHUB_TOKEN", "")
    if gh_token:
        headers["Authorization"] = f"token {gh_token}"

    req = urllib.request.Request(GITHUB_BOUNTIES_URL, headers=headers)
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        issues = json.loads(resp.read().decode())
    except Exception as e:
        return json.dumps({"error": str(e), "fallback": "Visit https://github.com/Scottcjn/rustchain-bounties/issues"})

    bounties = []
    for issue in issues:
        title = issue.get("title", "")
        rtc_match = re.search(r"(\d+)\s*RTC", title)
        rtc = int(rtc_match.group(1)) if rtc_match else 0
        if rtc < min_rtc:
            continue
        bounties.append({
            "number": issue["number"],
            "title": title,
            "rtc_reward": rtc,
            "usd_value": round(rtc * 0.10, 2),
            "url": issue["html_url"],
            "created_at": issue["created_at"][:10],
        })

    bounties.sort(key=lambda x: -x["rtc_reward"])
    return json.dumps({
        "open_bounties": len(bounties),
        "total_rtc_available": sum(b["rtc_reward"] for b in bounties),
        "bounties": bounties,
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
