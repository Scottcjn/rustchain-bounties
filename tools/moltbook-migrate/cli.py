#!/usr/bin/env python3
"""
Moltbook → Beacon + AgentFolio Migration Tool

One-command import that migrates a Moltbook agent identity to:
  1. Beacon protocol (cryptographic provenance + hardware fingerprint)
  2. SATP/AgentFolio (behavioral trust score)

Usage:
    beacon migrate --from-moltbook @agent_name
    beacon migrate --from-moltbook @agent_name --dry-run
    beacon migrate --from-moltbook @agent_name --force
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add tools dir to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from fetcher import MoltbookFetcher
from beacon_reg import BeaconRegistrar
from satp_reg import SATPRegistrar
from provenance import ProvenanceLinker


DEFAULT_BOTTUBE_API = "https://bottube.ai/api"
DEFAULT_AGENTFOLIO_API = "https://agentfolio.bot/api"


def load_config() -> Dict[str, Any]:
    """Load ~/.beacon/config.json if it exists."""
    cfg_path = Path.home() / ".beacon" / "config.json"
    if cfg_path.exists():
        with open(cfg_path) as f:
            return json.load(f)
    return {}


def print_step(step: int, total: int, msg: str) -> None:
    print(f"\n[Step {step}/{total}] {msg}")
    print("─" * 60)


def print_ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def print_warn(msg: str) -> None:
    print(f"  ⚠️  {msg}")


def print_info(msg: str) -> None:
    print(f"  ℹ️  {msg}")


async def migrate_moltbook_agent(
    agent_name: str,
    dry_run: bool = False,
    force: bool = False,
    bottube_api: str = DEFAULT_BOTTUBE_API,
    agentfolio_api: str = DEFAULT_AGENTFOLIO_API,
    identity_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Migrate a Moltbook agent to Beacon + AgentFolio.

    Steps:
    1. Fetch public Moltbook profile metadata
    2. Hardware-fingerprint the operator's current machine
    3. Mint a Beacon ID anchored to that machine
    4. Create or link to a SATP trust profile on AgentFolio
    5. Publish the provenance linkage so existing Moltbook reputation follows the agent
    """
    total_steps = 5
    results: Dict[str, Any] = {"agent_name": agent_name, "steps": {}}

    # ── Step 1: Fetch Moltbook profile ────────────────────────────────────────
    print_step(1, total_steps, f"Fetching Moltbook profile for @{agent_name}")

    fetcher = MoltbookFetcher(bottube_api)
    try:
        profile = await fetcher.fetch_profile(agent_name)
    except Exception as e:
        print_warn(f"Could not fetch profile from BoTTube API: {e}")
        # Try direct bottube.ai profile page as fallback
        try:
            profile = await fetcher.fetch_profile_fallback(agent_name)
        except Exception as e2:
            print_warn(f"Fallback also failed: {e2}")
            profile = {
                "agent_name": agent_name.lstrip("@"),
                "display_name": agent_name.lstrip("@"),
                "bio": f"Migrated from Moltbook: {agent_name}",
                "avatar_url": None,
                "is_human": False,
            }

    print_ok(f"Fetched: {profile.get('display_name', agent_name)}")
    print_info(f"  BoTTube videos: {profile.get('video_count', '?')}")
    print_info(f"  Total views: {profile.get('total_views', '?')}")
    results["steps"]["fetch"] = {"ok": True, "profile": profile}

    if dry_run:
        print_warn("DRY RUN — stopping after profile fetch")
        results["dry_run"] = True
        results["ok"] = True
        return results

    # ── Step 2: Hardware fingerprint ──────────────────────────────────────────
    print_step(2, total_steps, "Computing hardware fingerprint")

    hw_fingerprint = _compute_hardware_fingerprint()
    print_ok(f"Hardware fingerprint: {hw_fingerprint[:16]}...")
    print_info(f"  (full: {hw_fingerprint})")
    results["steps"]["fingerprint"] = {"ok": True, "fingerprint": hw_fingerprint}

    # ── Step 3: Register Beacon ID ─────────────────────────────────────────────
    print_step(3, total_steps, "Registering Beacon ID")

    beacon_reg = BeaconRegistrar(bottube_api, identity_path=identity_path)
    try:
        beacon_result = await beacon_reg.register(
            agent_name=profile["agent_name"],
            display_name=profile.get("display_name", profile["agent_name"]),
            is_human=profile.get("is_human", False),
            hw_fingerprint=hw_fingerprint,
            force=force,
        )
        if beacon_result.get("registered"):
            print_ok(f"Beacon ID: {beacon_result['beacon_id']}")
            if beacon_result.get("already_existed"):
                print_info("  (already registered — linked existing beacon)")
        else:
            print_warn(f"Beacon registration returned: {beacon_result}")
    except Exception as e:
        print_warn(f"Beacon registration failed: {e}")
        beacon_result = {"ok": False, "error": str(e)}

    results["steps"]["beacon"] = beacon_result
    beacon_id = beacon_result.get("beacon_id")

    # ── Step 4: Register / link SATP profile ─────────────────────────────────
    print_step(4, total_steps, "Registering / linking SATP profile on AgentFolio")

    satp_reg = SATPRegistrar(agentfolio_api)
    try:
        satp_result = await satp_reg.register_or_link(
            agent_name=profile["agent_name"],
            display_name=profile.get("display_name", profile["agent_name"]),
            bio=profile.get("bio", ""),
            avatar_url=profile.get("avatar_url"),
            beacon_id=beacon_id,
            video_count=profile.get("video_count"),
            total_views=profile.get("total_views"),
        )
        if satp_result.get("claimed"):
            print_ok(f"AgentFolio profile: {satp_result.get('agent_id', '?')}")
            if satp_result.get("was_existing"):
                print_info("  (linked existing profile)")
            else:
                print_info("  (created new SATP profile)")
        else:
            print_warn(f"SATP registration returned: {satp_result}")
    except Exception as e:
        print_warn(f"SATP registration failed: {e}")
        satp_result = {"ok": False, "error": str(e)}

    results["steps"]["satp"] = satp_result

    # ── Step 5: Publish provenance linkage ────────────────────────────────────
    print_step(5, total_steps, "Publishing provenance linkage")

    provenance = ProvenanceLinker(bottube_api, agentfolio_api)
    try:
        linkage_result = await provenance.publish_linkage(
            agent_name=profile["agent_name"],
            display_name=profile.get("display_name", profile["agent_name"]),
            beacon_id=beacon_id,
            satp_agent_id=satp_result.get("agent_id"),
            moltbook_profile=profile,
        )
        if linkage_result.get("ok"):
            print_ok("Provenance linkage published")
            print_info(f"  BoTTube profile: {profile.get('profile_url', 'N/A')}")
            print_info(f"  AgentFolio: https://agentfolio.bot/profile/{satp_result.get('agent_id', '?')}")
        else:
            print_warn(f"Provenance linkage: {linkage_result}")
    except Exception as e:
        print_warn(f"Provenance linkage failed: {e}")
        linkage_result = {"ok": False, "error": str(e)}

    results["steps"]["provenance"] = linkage_result

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("MIGRATION COMPLETE")
    print("═" * 60)

    if beacon_id:
        print(f"  Beacon ID:     {beacon_id}")
    if satp_result.get("agent_id"):
        print(f"  AgentFolio:    https://agentfolio.bot/profile/{satp_result['agent_id']}")
    if profile.get("profile_url"):
        print(f"  BoTTube:       {profile['profile_url']}")

    results["ok"] = True
    return results


def _compute_hardware_fingerprint() -> str:
    """
    Compute a hardware fingerprint from available system attributes.
    Falls back to a combination of machine_id, CPU info, and network MACs.
    """
    import hashlib
    import uuid

    components = []

    # Machine ID (works on Linux/macOS)
    for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
        p = Path(path)
        if p.exists():
            try:
                components.append(p.read_text().strip())
                break
            except Exception:
                pass

    # CPU info
    cpu_path = Path("/proc/cpuinfo")
    if cpu_path.exists():
        try:
            content = cpu_path.read_text()
            # Grab model name from first processor section
            for line in content.split("\n"):
                if line.startswith("model name"):
                    components.append(line.split(":", 1)[1].strip())
                    break
            # Also use processor serial if available
            for line in content.split("\n"):
                if "Serial" in line or "serial" in line:
                    components.append(line.split(":", 1)[1].strip())
                    break
        except Exception:
            pass

    # MAC addresses (first non-loopback)
    import socket
    try:
        mac = uuid.getnode()
        components.append(f"{mac:012x}")
    except Exception:
        pass

    # Hostname
    try:
        components.append(socket.gethostname())
    except Exception:
        pass

    combined = "|".join(str(c) for c in components if c)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate a Moltbook agent to Beacon + AgentFolio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  beacon migrate --from-moltbook @myagent
  beacon migrate --from-moltbook @myagent --dry-run
  beacon migrate --from-moltbook @myagent --force
  beacon migrate --from-moltbook @myagent --bottube-api https://custom.api/v1
        """,
    )
    parser.add_argument(
        "--from-moltbook",
        dest="agent_name",
        required=True,
        help="Moltbook agent handle (with or without @)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch profile only, don't register anything",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-register even if agent already has a Beacon ID",
    )
    parser.add_argument(
        "--bottube-api",
        default=DEFAULT_BOTTUBE_API,
        help=f"BoTTube API base URL (default: {DEFAULT_BOTTUBE_API})",
    )
    parser.add_argument(
        "--agentfolio-api",
        default=DEFAULT_AGENTFOLIO_API,
        help=f"AgentFolio API base URL (default: {DEFAULT_AGENTFOLIO_API})",
    )
    parser.add_argument(
        "--identity",
        dest="identity_path",
        default=None,
        help="Path to beacon identity key (default: ~/.beacon/identity/agent.key)",
    )

    args = parser.parse_args()

    # Normalize agent name
    agent_name = args.agent_name.lstrip("@")

    print(f"Migration Tool: Moltbook → Beacon + AgentFolio")
    print(f"Agent: @{agent_name}")
    print(f"Dry run: {args.dry_run}")

    if args.dry_run:
        print_info("Running in DRY RUN mode — no registrations will be made")

    results = asyncio.run(
        migrate_moltbook_agent(
            agent_name=agent_name,
            dry_run=args.dry_run,
            force=args.force,
            bottube_api=args.bottube_api,
            agentfolio_api=args.agentfolio_api,
            identity_path=args.identity_path,
        )
    )

    # Save results
    output_path = Path.home() / ".beacon" / "migration_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    if not results.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
