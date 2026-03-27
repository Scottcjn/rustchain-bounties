from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


DEFAULT_PRIMARY = "https://50.28.86.131"
DEFAULT_FALLBACKS: List[str] = []


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
