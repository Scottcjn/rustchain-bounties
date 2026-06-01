from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx


DEFAULT_PRIMARY = "https://50.28.86.131"
DEFAULT_FALLBACKS: List[str] = []
DEFAULT_BOTTUBE_API = "https://bottube.ai/api"


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


@dataclass
class BoTTubeClient:
    base_url: str
    api_key: Optional[str] = None
    timeout_s: float = 10.0

    @classmethod
    def from_env(cls) -> "BoTTubeClient":
        return cls(
            base_url=os.getenv("BOTTUBE_API_BASE_URL", DEFAULT_BOTTUBE_API).rstrip("/"),
            api_key=os.getenv("BOTTUBE_API_KEY") or None,
        )

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            return {}
        return {"X-API-Key": self.api_key}

    async def _get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            response = await client.get(url, params=params, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def trending(self, category: Optional[str] = None, limit: int = 10) -> Any:
        params: Dict[str, Any] = {"limit": limit}
        if category:
            params["category"] = category
        return await self._get_json("/trending", params=params)

    async def search(self, query: str, limit: int = 10, page: int = 1, sort: str = "trending") -> Any:
        return await self._get_json(
            "/search",
            params={"q": query, "limit": limit, "page": page, "sort": sort},
        )

    async def video(self, video_id: str) -> Any:
        return await self._get_json(f"/videos/{video_id}")

    async def agent(self, agent_name: str) -> Any:
        return await self._get_json(f"/agents/{agent_name}")

    async def stats(self) -> Any:
        return await self._get_json("/stats")

    async def upload(self, file_path: str, title: str, description: str = "") -> Any:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"BoTTube upload file not found: {file_path}")

        url = f"{self.base_url}/upload"
        with path.open("rb") as file_handle:
            files = {"file": (path.name, file_handle)}
            data = {"title": title}
            if description:
                data["description"] = description
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                response = await client.post(url, data=data, files=files, headers=self._headers())
                response.raise_for_status()
                return response.json()
