from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

DEFAULT_PRIMARY = "https://50.28.86.131"
DEFAULT_FALLBACKS: List[str] = []


@dataclass
class RustChainClient:
    primary_url: str
    fallback_urls: List[str] = field(default_factory=list)
    timeout_s: float = 10.0

    @classmethod
    def from_env(cls) -> "RustChainClient":
        primary = os.getenv("RUSTCHAIN_PRIMARY_URL", DEFAULT_PRIMARY).rstrip("/")
        fallbacks_raw = os.getenv("RUSTCHAIN_FALLBACK_URLS", "")
        fallbacks = [u.strip().rstrip("/") for u in fallbacks_raw.split(",") if u.strip()]
        return cls(primary_url=primary, fallback_urls=fallbacks or DEFAULT_FALLBACKS)

    def _urls(self) -> List[str]:
        return [self.primary_url] + [u for u in self.fallback_urls if u != self.primary_url]

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        last_err: Optional[Exception] = None
        for base in self._urls():
            try:
                async with httpx.AsyncClient(verify=False, timeout=self.timeout_s) as c:
                    r = await c.get(f"{base}{path}", params=params)
                    r.raise_for_status()
                    return r.json()
            except Exception as e:
                last_err = e
        raise RuntimeError(f"All RustChain nodes failed for GET {path}: {last_err}")

    async def health(self) -> Any:
        return await self._get("/health")

    async def epoch(self) -> Any:
        return await self._get("/epoch")

    async def miners(self) -> Any:
        return await self._get("/api/miners")

    async def balance(self, wallet_id: str) -> Any:
        return await self._get("/wallet/balance", params={"wallet_id": wallet_id})

    async def network_stats(self) -> Any:
        return await self._get("/api/stats")
