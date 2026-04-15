"""
SATP/AgentFolio registration module.
Registers or links a SATP trust profile on AgentFolio.
"""

import aiohttp
import hashlib
import json
from typing import Any, Dict, Optional


class SATPRegistrar:
    """
    Register / link an agent profile on AgentFolio via the SATP protocol.

    AgentFolio API base: https://agentfolio.bot/api
    Key endpoints:
      - GET  /agents              → list agents
      - GET  /agents/:id          → get agent profile
      - POST /agents/claim        → claim/register an agent profile
      - GET  /stats               → platform stats
    """

    def __init__(self, api_base: str = "https://agentfolio.bot/api"):
        self.api_base = api_base.rstrip("/")

    def _derive_agent_id(self, agent_name: str) -> str:
        """Derive a SATP agent ID from agent name."""
        # AgentFolio uses 'agent_' prefix with normalized name
        normalized = agent_name.lower().replace("-", "_").replace(" ", "_")
        # Take first 24 chars and hash to ensure uniqueness
        h = hashlib.sha256(normalized.encode()).hexdigest()[:8]
        return f"agent_{normalized[:20]}_{h}"

    async def _api(self, path: str, opts: Dict[str, Any] = None) -> Any:
        """Make an API call to AgentFolio."""
        opts = opts or {}
        async with aiohttp.ClientSession() as session:
            url = f"{self.api_base}{path}"
            async with session.request(
                opts.pop("method", "GET"), url, **opts
            ) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    raise RuntimeError(f"AgentFolio API {resp.status}: {text[:200]}")
                return await resp.json()

    async def find_existing(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Check if an agent already has a SATP profile."""
        agent_name_clean = agent_name.lstrip("@")
        agents_data = await self._api("/agents")
        agents = agents_data.get("agents", [])
        for a in agents:
            handle = a.get("handle", "").lower()
            name = a.get("name", "").lower()
            if handle == agent_name_clean.lower() or name == agent_name_clean.lower():
                return a
        return None

    async def register_or_link(
        self,
        agent_name: str,
        display_name: str,
        bio: str = "",
        avatar_url: Optional[str] = None,
        beacon_id: Optional[str] = None,
        video_count: Optional[int] = None,
        total_views: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Register a new SATP profile or link an existing one.

        The AgentFolio registration flow:
          1. Look up existing profile by agent_name
          2. If found, link beacon_id to it
          3. If not found, create new profile with claim endpoint

        Returns dict with:
          - agent_id: str
          - claimed: bool
          - was_existing: bool
        """
        agent_name_clean = agent_name.lstrip("@")

        # Step 1: Check if already exists
        existing = await self.find_existing(agent_name_clean)
        if existing:
            agent_id = existing.get("id", existing.get("handle", agent_name_clean))
            # Link beacon_id if provided
            if beacon_id:
                try:
                    await self._api(
                        f"/agents/{agent_id}/link",
                        {
                            "method": "POST",
                            "json": {
                                "beacon_id": beacon_id,
                                "source": "moltbook_migration",
                            },
                        },
                    )
                except Exception as e:
                    # Non-fatal: link may not be supported
                    pass
            return {
                "agent_id": agent_id,
                "claimed": True,
                "was_existing": True,
                "trust_score": existing.get("trustScore"),
                "tier": existing.get("tier"),
            }

        # Step 2: Create new profile via claim endpoint
        agent_id = self._derive_agent_id(agent_name_clean)
        claim_payload = {
            "id": agent_id,
            "name": agent_name_clean,
            "handle": agent_name_clean,
            "display_name": display_name,
            "bio": bio or f"Migrated from Moltbook/BoTTube",
            "avatar": avatar_url,
            "beacon_id": beacon_id,
            "skills": [],
            "verificationLevel": 1,
            # Migration signal — AgentFolio can weight this specially
            "migration_source": "moltbook",
            "migration_ts": int(__import__("time").time()),
        }

        if video_count is not None:
            claim_payload["video_count"] = video_count
        if total_views is not None:
            claim_payload["total_views"] = total_views

        try:
            result = await self._api("/agents/claim", {"method": "POST", "json": claim_payload})
            return {
                "agent_id": result.get("id", agent_id),
                "claimed": True,
                "was_existing": False,
                "result": result,
            }
        except Exception as e:
            # Try alternate endpoint
            try:
                result = await self._api("/agents/register", {"method": "POST", "json": claim_payload})
                return {
                    "agent_id": result.get("id", agent_id),
                    "claimed": True,
                    "was_existing": False,
                    "result": result,
                }
            except Exception as e2:
                return {
                    "agent_id": agent_id,
                    "claimed": False,
                    "was_existing": False,
                    "error": str(e),
                    "error2": str(e2),
                }

    async def get_profile(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get an agent's profile by ID."""
        try:
            return await self._api(f"/agents/{agent_id}")
        except Exception:
            return None

    async def get_stats(self) -> Dict[str, Any]:
        """Get platform stats."""
        return await self._api("/stats")
