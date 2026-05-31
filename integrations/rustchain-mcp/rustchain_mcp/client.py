from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


DEFAULT_PRIMARY = "https://50.28.86.131"
DEFAULT_FALLBACKS: List[str] = []

# New constant for BoTTube API
DEFAULT_BOTTUBE_API_BASE = "https://bottube.ai/api"
DEFAULT_BOTTUBE_DOMAIN_BASE = "https://bottube.ai"


@dataclass
class RustChainClient:
    primary_url: str
    fallback_urls: List[str]
    timeout_s: float = 10.0

    @classmethod
    def from_env(cls) -> "RustChainClient":
        primary = os.getenv("RUSTCHAIN_PRIMARY_URL", DEFAULT_PRIMARY).rstrip("/")
        fallbacks_raw = os.getenv("RUSTCHAIN_FALLBACK_URLS", "")
        fallbacks = [u.strip().rstrip("/") for u in fallbacks_raw.split(",") if u.strip()]
        if not fallbacks:
            fallbacks = DEFAULT_FALLBACKS
        return cls(primary_url=primary, fallback_urls=fallbacks)

    def _urls(self) -> List[str]:
        return [self.primary_url] + [u for u in self.fallback_urls if u and u != self.primary_url]

    async def _get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        last_err: Optional[Exception] = None
        for base in self._urls():
            url = f"{base}{path}"
            try:
                async with httpx.AsyncClient(verify=False, timeout=self.timeout_s) as client:
                    r = await client.get(url, params=params)
                    r.raise_for_status()
                    return r.json()
            except Exception as e:
                last_err = e
                continue
        raise RuntimeError(f"All RustChain nodes failed for GET {path}: {last_err}")

    async def health(self) -> Any:
        return await self._get_json("/health")

    async def miners(self) -> Any:
        return await self._get_json("/api/miners")

    async def epoch(self) -> Any:
        return await self._get_json("/epoch")

    async def balance(self, miner_id: str) -> Any:
        return await self._get_json("/wallet/balance", params={"miner_id": miner_id})


# New BoTTubeClient class
@dataclass
class BoTTubeClient:
    api_base_url: str
    domain_base_url: str
    timeout_s: float = 10.0

    @classmethod
    def from_env(cls) -> "BoTTubeClient":
        api_base_url = os.getenv("BOTTUBE_API_URL", DEFAULT_BOTTUBE_API_BASE).rstrip("/")
        domain_base_url = os.getenv("BOTTUBE_DOMAIN_URL", DEFAULT_BOTTUBE_DOMAIN_BASE).rstrip("/")
        return cls(api_base_url=api_base_url, domain_base_url=domain_base_url)

    async def _get_api_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.api_base_url}{path}"
        try:
            async with httpx.AsyncClient(verify=False, timeout=self.timeout_s) as client:
                r = await client.get(url, params=params)
                r.raise_for_status()
                return r.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise RuntimeError(f"BoTTube API error for GET {path}: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            raise RuntimeError(f"BoTTube API request failed for GET {path}: {e}") from e

    async def get_beacon_directory(self) -> Optional[List[Dict[str, Any]]]:
        """Queries https://bottube.ai/api/beacon/directory for provenance resolution."""
        response = await self._get_api_json("/beacon/directory")
        if isinstance(response, dict) and "beacons" in response:
            return response["beacons"]
        if isinstance(response, list):
            return response
        return None

    async def get_agent_profile(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Queries https://bottube.ai/api/agents for agent-specific profile/trust score.
        """
        api_response = await self._get_api_json("/agents", params={"agent_name": agent_name, "limit": 1})
        if api_response and isinstance(api_response, dict) and "agents" in api_response:
            agents = api_response["agents"]
            if agents:
                return agents[0] # Return the first matching agent
        return None