"""
Moltbook profile fetcher.
Fetches public agent profiles from the BoTTube API (which serves as the Moltbook successor).
"""

import aiohttp
import json
from typing import Any, Dict, Optional


class MoltbookFetcher:
    """Fetch public agent profiles from BoTTube/Moltbook API."""

    def __init__(self, api_base: str = "https://bottube.ai/api"):
        self.api_base = api_base.rstrip("/")

    async def fetch_profile(self, agent_name: str) -> Dict[str, Any]:
        """
        Fetch a single agent's profile from the BoTTube agents directory.

        BoTTube replaced Moltbook after the Meta acquisition, so BoTTube's
        agent API is the practical migration path for Moltbook agents.
        """
        agent_name = agent_name.lstrip("@")

        async with aiohttp.ClientSession() as session:
            # Try to find the agent in the directory
            url = f"{self.api_base}/agents"
            params = {"limit": 50}
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"BoTTube API returned {resp.status}")
                data = await resp.json()

            agents = data.get("agents", [])
            # Find matching agent
            for agent in agents:
                if agent.get("agent_name", "").lower() == agent_name.lower():
                    return agent

            # Not found in directory — try individual profile endpoint
            profile_url = f"{self.api_base}/agent/{agent_name}"
            async with session.get(profile_url) as resp:
                if resp.status == 200:
                    try:
                        return await resp.json()
                    except Exception:
                        pass

            raise KeyError(f"Agent @{agent_name} not found in BoTTube directory")

    async def fetch_profile_fallback(self, agent_name: str) -> Dict[str, Any]:
        """
        Fallback: fetch profile from the web profile page.
        Returns minimal profile with just agent_name if page is not parseable.
        """
        import aiohttp

        agent_name = agent_name.lstrip("@")
        url = f"https://bottube.ai/agent/{agent_name}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"Accept": "application/json"}) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    # Try to extract JSON from the page
                    import re
                    json_matches = re.findall(r'"agent_name"\s*:\s*"([^"]+)"', text)
                    if json_matches:
                        return {"agent_name": agent_name, "display_name": agent_name}
                return {"agent_name": agent_name, "display_name": agent_name}

    async def fetch_directory(self, limit: int = 100) -> Dict[str, Any]:
        """Fetch the full agent directory."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.api_base}/agents"
            params = {"limit": limit}
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"BoTTube API returned {resp.status}")
                return await resp.json()

    async def search_agents(self, query: str, limit: int = 20) -> list:
        """Search agents by name or bio keyword."""
        directory = await self.fetch_directory(limit=200)
        agents = directory.get("agents", [])
        query_lower = query.lower()
        return [
            a for a in agents
            if query_lower in a.get("agent_name", "").lower()
            or query_lower in a.get("display_name", "").lower()
            or query_lower in a.get("bio", "").lower()
        ][:limit]
