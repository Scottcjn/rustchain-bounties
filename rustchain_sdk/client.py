# SPDX-License-Identifier: MIT
"""Sync and async HTTP clients for RustChain nodes."""

import json
import ssl
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Dict, List, Optional

from .exceptions import APIError, ConnectionError as RCConnectionError
from .models import Health, Epoch, Miner, Balance, Block, Transaction


class _Explorer:
    """Explorer endpoint namespace, bound to a client instance."""

    def __init__(self, client: Any):
        self._client = client

    def blocks(self, limit: int = 10) -> List[Block]:
        data = self._client._get(f"/explorer/blocks?limit={limit}")
        return [Block(**b) for b in data] if isinstance(data, list) else []

    def transactions(self, limit: int = 10) -> List[Transaction]:
        data = self._client._get(f"/explorer/transactions?limit={limit}")
        return [Transaction(**t) for t in data] if isinstance(data, list) else []


class RustChainClient:
    """Synchronous RustChain API client (stdlib only, zero dependencies)."""

    def __init__(self, node_url: str = "https://50.28.86.131", timeout: int = 15,
                 verify_ssl: bool = True):
        self.node_url = node_url.rstrip("/")
        self.timeout = timeout
        self._ctx: Optional[ssl.SSLContext] = None
        if not verify_ssl:
            self._ctx = ssl.create_default_context()
            self._ctx.check_hostname = False
            self._ctx.verify_mode = ssl.CERT_NONE
        self.explorer = _Explorer(self)

    def _get(self, endpoint: str) -> Any:
        url = f"{self.node_url}{endpoint}"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else str(e)
            raise APIError(e.code, body)
        except urllib.error.URLError as e:
            raise RCConnectionError(f"Failed to connect to {url}: {e}")

    def _post(self, endpoint: str, payload: dict) -> Any:
        url = f"{self.node_url}{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else str(e)
            raise APIError(e.code, body)
        except urllib.error.URLError as e:
            raise RCConnectionError(f"Failed to connect to {url}: {e}")

    def health(self) -> Health:
        return Health(**self._get("/health"))

    def epoch(self) -> Epoch:
        return Epoch(**self._get("/epoch"))

    def miners(self) -> List[Miner]:
        return [Miner(**m) for m in self._get("/api/miners")]

    def balance(self, wallet_id: str) -> Balance:
        safe_id = urllib.parse.quote(wallet_id, safe="")
        data = self._get(f"/wallet/balance?miner_id={safe_id}")
        return Balance(
            wallet_id=wallet_id,
            balance=data.get("amount_rtc", 0.0),
            amount_rtc=data.get("amount_rtc", 0.0),
            amount_i64=data.get("amount_i64", 0),
            miner_id=data.get("miner_id", wallet_id),
        )

    def transfer(self, from_wallet: str, to_wallet: str, amount: float,
                 signature: str) -> Dict[str, Any]:
        return self._post("/wallet/transfer", {
            "from": from_wallet, "to": to_wallet,
            "amount": amount, "signature": signature,
        })

    def attestation_status(self, miner_id: str) -> Dict[str, Any]:
        for m in self._get("/api/miners"):
            if m.get("miner") == miner_id:
                return {"miner_id": miner_id, "last_attest": m.get("last_attest"),
                        "antiquity_multiplier": m.get("antiquity_multiplier")}
        return {"miner_id": miner_id, "status": "not_found"}


class AsyncRustChainClient:
    """Async RustChain client (requires aiohttp). Supports context manager."""

    def __init__(self, node_url: str = "https://50.28.86.131", timeout: int = 15,
                 verify_ssl: bool = True):
        self.node_url = node_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._session = None

    async def __aenter__(self):
        import aiohttp
        ssl_ctx = None if self.verify_ssl else False
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            connector=aiohttp.TCPConnector(ssl=ssl_ctx),
        )
        return self

    async def __aexit__(self, *exc):
        if self._session:
            await self._session.close()
            self._session = None

    async def _get(self, endpoint: str) -> Any:
        import aiohttp
        if not self._session:
            raise RCConnectionError("Use 'async with' to create a session first.")
        try:
            async with self._session.get(f"{self.node_url}{endpoint}") as resp:
                if resp.status >= 400:
                    raise APIError(resp.status, await resp.text())
                return await resp.json()
        except aiohttp.ClientError as e:
            raise RCConnectionError(str(e))

    async def health(self) -> Health:
        return Health(**await self._get("/health"))

    async def epoch(self) -> Epoch:
        return Epoch(**await self._get("/epoch"))

    async def miners(self) -> List[Miner]:
        return [Miner(**m) for m in await self._get("/api/miners")]

    async def balance(self, wallet_id: str) -> Balance:
        safe_id = urllib.parse.quote(wallet_id, safe="")
        data = await self._get(f"/wallet/balance?miner_id={safe_id}")
        return Balance(
            wallet_id=wallet_id,
            balance=data.get("amount_rtc", 0.0),
            amount_rtc=data.get("amount_rtc", 0.0),
            amount_i64=data.get("amount_i64", 0),
            miner_id=data.get("miner_id", wallet_id),
        )

    async def transfer(self, from_wallet: str, to_wallet: str, amount: float,
                       signature: str) -> Dict[str, Any]:
        import aiohttp
        if not self._session:
            raise RCConnectionError("Use 'async with' to create a session first.")
        try:
            async with self._session.post(
                f"{self.node_url}/wallet/transfer",
                json={"from": from_wallet, "to": to_wallet, "amount": amount, "signature": signature},
            ) as resp:
                if resp.status >= 400:
                    raise APIError(resp.status, await resp.text())
                return await resp.json()
        except aiohttp.ClientError as e:
            raise RCConnectionError(str(e))

    async def attestation_status(self, miner_id: str) -> Dict[str, Any]:
        for m in await self._get("/api/miners"):
            if m.get("miner") == miner_id:
                return {"miner_id": miner_id, "last_attest": m.get("last_attest"),
                        "antiquity_multiplier": m.get("antiquity_multiplier")}
        return {"miner_id": miner_id, "status": "not_found"}
