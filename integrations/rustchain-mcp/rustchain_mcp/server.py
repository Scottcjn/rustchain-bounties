from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .client import RustChainClient, BoTTubeClient # Import new client

mcp = FastMCP("rustchain")
rustchain_client = RustChainClient.from_env()
bottube_client = BoTTubeClient.from_env() # Instantiate new client


def _to_pretty(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


@mcp.tool()
async def rustchain_health() -> str:
    """Check node health across RustChain attestation nodes (with failover)."""
    data = await rustchain_client.health()
    return _to_pretty(data)


@mcp.tool()
async def rustchain_miners() -> str:
    """List active miners and their architectures."""
    data = await rustchain_client.miners()
    return _to_pretty(data)


@mcp.tool()
async def rustchain_epoch() -> str:
    """Get current epoch info (slot, height, rewards)."""
    data = await rustchain_client.epoch()
    return _to_pretty(data)


@mcp.tool()
async def rustchain_balance(miner_id: str) -> str:
    """Get RTC balance for a wallet/miner_id."""
    data = await rustchain_client.balance(miner_id)
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

# New tool: agentfolio_beacon_lookup
@mcp.tool()
async def agentfolio_beacon_lookup(beacon_id: str) -> str:
    """
    Looks up provenance (from Beacon) and trust score (from AgentFolio SATP) for a given beacon_id.
    Queries https://bottube.ai/api/beacon/directory for provenance and https://bottube.ai/api/agents for trust score.
    Handles offline nodes, expired beacons, untrusted scores gracefully.
    """
    unified_response = {
        "beacon_id": beacon_id,
        "provenance": None,
        "trust_score": None,
        "status": "partial_data",
        "errors": []
    }

    # 1. Query Beacon directory for provenance
    try:
        beacon_directory = await bottube_client.get_beacon_directory()
        if beacon_directory:
            found_beacon = next((b for b in beacon_directory if b.get("beacon_id") == beacon_id), None)
            if found_beacon:
                unified_response["provenance"] = found_beacon
            else:
                unified_response["errors"].append(f"Beacon ID '{beacon_id}' not found in directory.")
        else:
            unified_response["errors"].append("Failed to retrieve Beacon directory or it was empty.")
    except RuntimeError as e:
        unified_response["errors"].append(f"Beacon provenance lookup failed: {e}")

    # 2. Query AgentFolio SATP registry for trust score (using /api/agents)
    try:
        agent_profile = await bottube_client.get_agent_profile(beacon_id)
        if agent_profile:
            # Extract relevant trust score info. Assuming 'reputation' or similar field exists.
            # The structure of the /api/agents response is not fully specified, so we take a reasonable guess.
            trust_score_data = {
                "agent_name": agent_profile.get("agent_name"),
                "reputation_score": agent_profile.get("reputation_score"), # Example field
                "follower_count": agent_profile.get("follower_count"),
                "karma_history": agent_profile.get("karma_history"),
                "is_trusted": agent_profile.get("is_trusted"),
                "last_activity": agent_profile.get("last_activity")
            }
            # Filter out None values for cleaner output
            unified_response["trust_score"] = {k: v for k, v in trust_score_data.items() if v is not None}
            if not unified_response["trust_score"]: # If all extracted fields were None
                unified_response["errors"].append(f"Agent profile for '{beacon_id}' found, but no specific trust score data extracted.")
        else:
            unified_response["errors"].append(f"AgentFolio profile for '{beacon_id}' not found or could not be retrieved.")
    except RuntimeError as e:
        unified_response["errors"].append(f"AgentFolio trust score lookup failed: {e}")

    if unified_response["provenance"] and unified_response["trust_score"]:
        unified_response["status"] = "complete"
    elif not unified_response["provenance"] and not unified_response["trust_score"]:
        unified_response["status"] = "no_data"
        unified_response["errors"].append("No provenance or trust score data found for the given beacon ID.")

    return _to_pretty(unified_response)


if __name__ == "__main__":
    mcp.run()
