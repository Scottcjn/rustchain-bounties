# SPDX-License-Identifier: MIT
"""Sync and async HTTP clients for RustChain nodes."""

import json
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

from .exceptions import APIError, ConnectionError as RCConnectionError
from .models import Health, Epoch, Miner, Balance, Block, Transaction


class RustChainClient:
    """Synchronous RustChain API client (stdlib only, zero dependencies)."""

    def __init__(self, node_url: str = "https://50.28.86.131", timeout: int = 15,
                 verify_ssl: bool = False):
        self.node_url = node_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        if not verify_ssl:
            import ssl
            self._ctx = ssl.create_default_context()
            self._ctx.check_hostname = False
            self._ctx.verify_mode = ssl.CERT_NONE
        else:
            self._ctx = None

    def _get(self, endpoint: str) -> Any:
        url = f"{self.node_url}{endpoint}"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx) as resp:
                data = json.loads(resp.read().decode())
                return data
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
        """Check node health status."""
        data = self._get("/health")
        return Health(**data)

    def epoch(self) -> Epoch:
        """Get current epoch information."""
        data = self._get("/epoch")
        return Epoch(**data)

    def miners(self) -> List[Miner]:
        """List all active miners."""
        data = self._get("/api/miners")
        return [Miner(**m) for m in data]

    def balance(self, wallet_id: str) -> Balance:
        """Check RTC balance for a wallet."""
        data = self._get(f"/wallet/balance?miner_id={wallet_id}")
        return Balance(
            wallet_id=wallet_id,
            balance=data.get("amount_rtc", 0.0),
            amount_rtc=data.get("amount_rtc", 0.0),
            amount_i64=data.get("amount_i64", 0),
            miner_id=data.get("miner_id", wallet_id),
        )

    def transfer(self, from_wallet: str, to_wallet: str, amount: float,
                 signature: str) -> Dict[str, Any]:
        """Execute a signed RTC transfer."""
        return self._post("/wallet/transfer", {
            "from": from_wallet, "to": to_wallet,
            "amount": amount, "signature": signature,
        })

    def attestation_status(self, miner_id: str) -> Dict[str, Any]:
        """Check attestation status for a miner."""
        data = self._get(f"/api/miners")
        for m in data:
            if m.get("miner") == miner_id:
                return {"miner_id": miner_id, "last_attest": m.get("last_attest"),
                        "antiquity_multiplier": m.get("antiquity_multiplier")}
        return {"miner_id": miner_id, "status": "not_found"}

    class explorer:
        """Namespace for explorer endpoints."""
        @staticmethod
        def blocks(client: "RustChainClient", limit: int = 10) -> List[Block]:
            data = client._get(f"/explorer/blocks?limit={limit}")
            if isinstance(data, list):
                return [Block(**b) for b in data]
            return []

        @staticmethod
        def transactions(client: "RustChainClient", limit: int = 10) -> List[Transaction]:
            data = client._get(f"/explorer/transactions?limit={limit}")
            if isinstance(data, list):
                return [Transaction(**t) for t in data]
            return []


class AsyncRustChainClient:
    """Async RustChain client (requires aiohttp)."""

    def __init__(self, node_url: str = "https://50.28.86.131", timeout: int = 15,
                 verify_ssl: bool = False):
        self.node_url = node_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    async def _get(self, endpoint: str) -> Any:
        import aiohttp, ssl as _ssl
        ssl_ctx = False if not self.verify_ssl else None
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{self.node_url}{endpoint}", ssl=ssl_ctx) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    raise APIError(resp.status, text)
                return await resp.json()

    async def health(self) -> Health:
        data = await self._get("/health")
        return Health(**data)

    async def epoch(self) -> Epoch:
        data = await self._get("/epoch")
        return Epoch(**data)

    async def miners(self) -> List[Miner]:
        data = await self._get("/api/miners")
        return [Miner(**m) for m in data]

    async def balance(self, wallet_id: str) -> Balance:
        data = await self._get(f"/wallet/balance?miner_id={wallet_id}")
        return Balance(wallet_id=wallet_id, **data)
