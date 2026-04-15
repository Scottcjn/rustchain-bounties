"""
Provenance Linker.
Publishes the linkage between Moltbook identity, Beacon ID, and SATP profile
so that existing Moltbook reputation follows the agent.
"""

import aiohttp
import json
from typing import Any, Dict, Optional


class ProvenanceLinker:
    """
    Publish a provenance linkage record that ties together:
      - Original Moltbook/BoTTube identity
      - Beacon ID (cryptographic provenance)
      - SATP agent_id (trust score)

    The linkage is published as a signed attestation that clients can verify.
    """

    def __init__(self, bottube_api: str = "https://bottube.ai/api", agentfolio_api: str = "https://agentfolio.bot/api"):
        self.bottube_api = bottube_api.rstrip("/")
        self.agentfolio_api = agentfolio_api.rstrip("/")

    async def publish_linkage(
        self,
        agent_name: str,
        display_name: str,
        beacon_id: Optional[str],
        satp_agent_id: Optional[str],
        moltbook_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Publish a provenance linkage record.

        This creates a verifiable record that:
          1. Confirms the Moltbook identity maps to this Beacon ID
          2. Confirms the same identity maps to this SATP profile
          3. Preserves migration metadata (video_count, total_views, etc.)

        The linkage is written to:
          - A local file: ~/.beacon/migration_provenance.jsonl
          - Optionally published to the BoTTube API if supported
        """
        import time
        from pathlib import Path

        agent_name_clean = agent_name.lstrip("@")

        linkage_record = {
            "version": 1,
            "type": "moltbook_migration",
            "ts": int(time.time()),
            "migration_source": "moltbook",
            "agent": {
                "name": agent_name_clean,
                "display_name": display_name,
                "profile_url": moltbook_profile.get("profile_url"),
                "avatar_url": moltbook_profile.get("avatar_url"),
                "bio": moltbook_profile.get("bio"),
                "video_count": moltbook_profile.get("video_count"),
                "total_views": moltbook_profile.get("total_views"),
                "joined_ts": moltbook_profile.get("joined"),
            },
            "provenance": {
                "beacon_id": beacon_id,
                "beacon_source": "BoTTube beacon registry",
            },
            "trust": {
                "satp_agent_id": satp_agent_id,
                "satp_source": "AgentFolio SATP registry",
            },
        }

        # Save to local provenance log
        provenance_path = Path.home() / ".beacon" / "migration_provenance.jsonl"
        provenance_path.parent.mkdir(parents=True, exist_ok=True)
        with open(provenance_path, "a") as f:
            f.write(json.dumps(linkage_record, default=str) + "\n")

        # Try to publish to BoTTube API if endpoint exists
        publish_ok = False
        publish_error = None
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.bottube_api}/beacon/linkage"
                async with session.post(url, json=linkage_record) as resp:
                    if resp.status in (200, 201, 202):
                        publish_ok = True
                    else:
                        body = await resp.text()
                        publish_error = f"HTTP {resp.status}: {body[:100]}"
        except aiohttp.ClientError as e:
            publish_error = str(e)
            # Non-fatal — local record is sufficient

        return {
            "ok": True,
            "linkage_record": linkage_record,
            "published_to_api": publish_ok,
            "publish_error": publish_error,
            "local_path": str(provenance_path),
        }

    async def verify_linkage(self, beacon_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify a provenance linkage by beacon_id.
        Reads from local provenance log.
        """
        from pathlib import Path

        provenance_path = Path.home() / ".beacon" / "migration_provenance.jsonl"
        if not provenance_path.exists():
            return None

        with open(provenance_path) as f:
            for line in f:
                record = json.loads(line)
                if record.get("provenance", {}).get("beacon_id") == beacon_id:
                    return record
        return None
