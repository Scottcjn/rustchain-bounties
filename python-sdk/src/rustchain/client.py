"""Async and sync RustChain client.

Copyright (c) 2026 思捷娅科技 (SJYKJ)
MIT License
"""

from __future__ import annotations

import ssl
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp
import requests

from .exceptions import (
    BadRequestError,
    MinerNotFoundError,
    NodeUnhealthyError,
    RateLimitError,
    RustChainError,
)

_DEFAULT_BASE_URL = "https://50.28.86.131"


def _raise_for_status(status: int, body: str) -> None:
    """Map HTTP status codes to typed exceptions."""
    if status == 200:
        return
    if status == 400:
        raise BadRequestError(body, status_code=status)
    if status == 404:
        raise MinerNotFoundError(body, status_code=status)
    if status == 429:
        raise RateLimitError(body, status_code=status)
    if status == 500:
        raise RustChainError(f"Internal server error: {body}", status_code=status)
    raise RustChainError(body, status_code=status)


# ── Data models ────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class HealthInfo:
    ok: bool
    uptime_s: int
    version: str
    db_rw: bool
    tip_age_slots: int
    backup_age_hours: float

    @classmethod
    def from_dict(cls, d: dict) -> "HealthInfo":
        return cls(
            ok=d["ok"],
            uptime_s=d["uptime_s"],
            version=d["version"],
            db_rw=d["db_rw"],
            tip_age_slots=d["tip_age_slots"],
            backup_age_hours=d["backup_age_hours"],
        )


@dataclass(frozen=True, slots=True)
class EpochInfo:
    epoch: int
    slot: int
    blocks_per_epoch: int
    enrolled_miners: int
    epoch_pot: float
    total_supply_rtc: int

    @classmethod
    def from_dict(cls, d: dict) -> "EpochInfo":
        return cls(
            epoch=d["epoch"],
            slot=d["slot"],
            blocks_per_epoch=d["blocks_per_epoch"],
            enrolled_miners=d["enrolled_miners"],
            epoch_pot=d["epoch_pot"],
            total_supply_rtc=d["total_supply_rtc"],
        )


@dataclass(frozen=True, slots=True)
class MinerInfo:
    miner_pk: str
    balance: float
    # May contain extra fields depending on API version

    @classmethod
    def from_dict(cls, d: dict) -> "MinerInfo":
        return cls(miner_pk=d["miner_pk"], balance=float(d["balance"]))


@dataclass(frozen=True, slots=True)
class StatsInfo:
    block_time: int
    chain_id: str
    epoch: int
    features: List[str]
    total_balance: float
    total_miners: int
    version: str
    pending_withdrawals: int

    @classmethod
    def from_dict(cls, d: dict) -> "StatsInfo":
        return cls(
            block_time=d["block_time"],
            chain_id=d["chain_id"],
            epoch=d["epoch"],
            features=d.get("features", []),
            total_balance=float(d["total_balance"]),
            total_miners=d["total_miners"],
            version=d["version"],
            pending_withdrawals=d.get("pending_withdrawals", 0),
        )


@dataclass(frozen=True, slots=True)
class ChallengeResponse:
    challenge: str
    expires_at: Optional[int] = None

    @classmethod
    def from_dict(cls, d: dict) -> "ChallengeResponse":
        return cls(
            challenge=d["challenge"],
            expires_at=d.get("expires_at"),
        )


@dataclass(frozen=True, slots=True)
class AttestationResult:
    accepted: bool
    message: str

    @classmethod
    def from_dict(cls, d: dict) -> "AttestationResult":
        return cls(accepted=d.get("accepted", True), message=d.get("message", ""))


@dataclass(frozen=True, slots=True)
class WithdrawalInfo:
    withdrawal_id: str
    status: str
    amount: float
    miner_pk: str

    @classmethod
    def from_dict(cls, d: dict) -> "WithdrawalInfo":
        return cls(
            withdrawal_id=d.get("withdrawal_id", d.get("id", "")),
            status=d.get("status", "unknown"),
            amount=float(d.get("amount", 0)),
            miner_pk=d.get("miner_pk", ""),
        )


# ── Async client ───────────────────────────────────────────────────────────


class RustChainClient:
    """Async client for the RustChain node API."""

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = 30,
        verify_ssl: bool = False,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._ssl = ssl.create_default_context() if verify_ssl else False
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get(self, path: str) -> Any:
        return await self._request("GET", path)

    async def _post(self, path: str, json: Dict | None = None) -> Any:
        return await self._request("POST", path, json=json)

    async def _request(
        self, method: str, path: str, json: Dict | None = None
    ) -> Any:
        url = f"{self._base_url}{path}"
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
            )
        async with self._session.request(
            method, url, json=json, ssl=self._ssl
        ) as resp:
            body = await resp.text()
            _raise_for_status(resp.status, body)
            if body:
                import json as _json

                return _json.loads(body)
            return {}

    # ── Core methods ────────────────────────────────────────────────────

    async def health(self) -> HealthInfo:
        """Check node health."""
        data = await self._get("/health")
        if not data.get("ok"):
            raise NodeUnhealthyError(
                f"Node unhealthy: {data}", status_code=503
            )
        return HealthInfo.from_dict(data)

    async def stats(self) -> StatsInfo:
        """Get system-wide statistics."""
        data = await self._get("/api/stats")
        return StatsInfo.from_dict(data)

    async def epoch(self) -> EpochInfo:
        """Get current epoch information."""
        data = await self._get("/epoch")
        return EpochInfo.from_dict(data)

    async def balance(self, miner_pk: str) -> float:
        """Check RTC balance for a miner public key."""
        data = await self._get(f"/balance/{miner_pk}")
        return float(data.get("balance", 0))

    async def miners(self) -> List[Dict[str, Any]]:
        """List active miners."""
        data = await self._get("/api/miners")
        if isinstance(data, list):
            return data
        return data.get("miners", [])

    async def attest_challenge(self, miner_pk: str) -> ChallengeResponse:
        """Request a hardware attestation challenge."""
        data = await self._post("/attest/challenge", {"miner_pk": miner_pk})
        return ChallengeResponse.from_dict(data)

    async def attest_submit(
        self,
        miner_pk: str,
        challenge: str,
        response: str,
        hardware_proof: Dict[str, Any] | None = None,
    ) -> AttestationResult:
        """Submit a completed attestation."""
        payload: Dict[str, Any] = {
            "miner_pk": miner_pk,
            "challenge": challenge,
            "response": response,
        }
        if hardware_proof:
            payload["hardware_proof"] = hardware_proof
        data = await self._post("/attest/submit", payload)
        return AttestationResult.from_dict(data)

    async def epoch_enroll(self, miner_pk: str) -> Dict[str, Any]:
        """Enroll a miner in the current epoch."""
        return await self._post("/epoch/enroll", {"miner_pk": miner_pk})

    async def withdraw_register(
        self, miner_pk: str, withdrawal_pk: str
    ) -> Dict[str, Any]:
        """Register an SR25519 key for withdrawals."""
        return await self._post(
            "/withdraw/register",
            {"miner_pk": miner_pk, "withdrawal_pk": withdrawal_pk},
        )

    async def withdraw_request(
        self, miner_pk: str, amount: int, signature: str
    ) -> Dict[str, Any]:
        """Request an RTC token withdrawal."""
        return await self._post(
            "/withdraw/request",
            {
                "miner_pk": miner_pk,
                "amount": str(amount),
                "signature": signature,
            },
        )

    async def withdraw_history(self, miner_pk: str) -> List[WithdrawalInfo]:
        """Get withdrawal history for a miner."""
        data = await self._get(f"/withdraw/history/{miner_pk}")
        if isinstance(data, list):
            return [WithdrawalInfo.from_dict(d) for d in data]
        return []

    async def withdraw_status(
        self, withdrawal_id: str
    ) -> WithdrawalInfo:
        """Check withdrawal status."""
        data = await self._get(f"/withdraw/status/{withdrawal_id}")
        return WithdrawalInfo.from_dict(data)

    async def metrics(self) -> str:
        """Get Prometheus metrics."""
        url = f"{self._base_url}/metrics"
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        async with self._session.get(url, ssl=self._ssl) as resp:
            return await resp.text()

    # ── Explorer (convenience) ─────────────────────────────────────────

    @property
    def explorer(self) -> "_Explorer":
        return _Explorer(self)

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> "RustChainClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()


class _Explorer:
    """Explorer sub-client for blocks and transactions."""

    def __init__(self, client: RustChainClient) -> None:
        self._client = client

    async def blocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent blocks."""
        try:
            data = await self._client._get(f"/explorer/blocks?limit={limit}")
            if isinstance(data, list):
                return data
            return data.get("blocks", [])
        except RustChainError:
            return []

    async def transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions."""
        try:
            data = await self._client._get(
                f"/explorer/transactions?limit={limit}"
            )
            if isinstance(data, list):
                return data
            return data.get("transactions", [])
        except RustChainError:
            return []


# ── Sync wrapper ───────────────────────────────────────────────────────────


class RustChainSyncClient:
    """Synchronous wrapper around the async client."""

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = 30,
        verify_ssl: bool = False,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._verify = verify_ssl
        self._session = requests.Session()
        self._session.verify = verify_ssl

    def _request(
        self, method: str, path: str, json: Dict | None = None
    ) -> Any:
        url = f"{self._base_url}{path}"
        resp = self._session.request(
            method, url, json=json, timeout=self._timeout
        )
        body = resp.text
        _raise_for_status(resp.status_code, body)
        if body:
            import json as _json

            return _json.loads(body)
        return {}

    def health(self) -> HealthInfo:
        """Check node health."""
        data = self._request("GET", "/health")
        if not data.get("ok"):
            raise NodeUnhealthyError(f"Node unhealthy: {data}", status_code=503)
        return HealthInfo.from_dict(data)

    def stats(self) -> StatsInfo:
        """Get system-wide statistics."""
        data = self._request("GET", "/api/stats")
        return StatsInfo.from_dict(data)

    def epoch(self) -> EpochInfo:
        """Get current epoch information."""
        data = self._request("GET", "/epoch")
        return EpochInfo.from_dict(data)

    def balance(self, miner_pk: str) -> float:
        """Check RTC balance for a miner public key."""
        data = self._request("GET", f"/balance/{miner_pk}")
        return float(data.get("balance", 0))

    def miners(self) -> List[Dict[str, Any]]:
        """List active miners."""
        data = self._request("GET", "/api/miners")
        if isinstance(data, list):
            return data
        return data.get("miners", [])

    def attest_challenge(self, miner_pk: str) -> ChallengeResponse:
        """Request a hardware attestation challenge."""
        data = self._request("POST", "/attest/challenge", {"miner_pk": miner_pk})
        return ChallengeResponse.from_dict(data)

    def attest_submit(
        self,
        miner_pk: str,
        challenge: str,
        response: str,
        hardware_proof: Dict[str, Any] | None = None,
    ) -> AttestationResult:
        """Submit a completed attestation."""
        payload: Dict[str, Any] = {
            "miner_pk": miner_pk,
            "challenge": challenge,
            "response": response,
        }
        if hardware_proof:
            payload["hardware_proof"] = hardware_proof
        data = self._request("POST", "/attest/submit", payload)
        return AttestationResult.from_dict(data)

    def epoch_enroll(self, miner_pk: str) -> Dict[str, Any]:
        """Enroll a miner in the current epoch."""
        return self._request("POST", "/epoch/enroll", {"miner_pk": miner_pk})

    def withdraw_register(
        self, miner_pk: str, withdrawal_pk: str
    ) -> Dict[str, Any]:
        """Register an SR25519 key for withdrawals."""
        return self._request(
            "POST",
            "/withdraw/register",
            {"miner_pk": miner_pk, "withdrawal_pk": withdrawal_pk},
        )

    def withdraw_request(
        self, miner_pk: str, amount: int, signature: str
    ) -> Dict[str, Any]:
        """Request an RTC token withdrawal."""
        return self._request(
            "POST",
            "/withdraw/request",
            {"miner_pk": miner_pk, "amount": str(amount), "signature": signature},
        )

    def withdraw_history(self, miner_pk: str) -> List[WithdrawalInfo]:
        """Get withdrawal history for a miner."""
        data = self._request("GET", f"/withdraw/history/{miner_pk}")
        if isinstance(data, list):
            return [WithdrawalInfo.from_dict(d) for d in data]
        return []

    def withdraw_status(self, withdrawal_id: str) -> WithdrawalInfo:
        """Check withdrawal status."""
        data = self._request("GET", f"/withdraw/status/{withdrawal_id}")
        return WithdrawalInfo.from_dict(data)

    def metrics(self) -> str:
        """Get Prometheus metrics."""
        return self._request("GET", "/metrics")

    @property
    def explorer(self) -> "_ExplorerSync":
        return _ExplorerSync(self)

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "RustChainSyncClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class _ExplorerSync:
    """Sync explorer sub-client."""

    def __init__(self, client: RustChainSyncClient) -> None:
        self._client = client

    def blocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            data = self._client._request("GET", f"/explorer/blocks?limit={limit}")
            if isinstance(data, list):
                return data
            return data.get("blocks", [])
        except RustChainError:
            return []

    def transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            data = self._client._request(
                "GET", f"/explorer/transactions?limit={limit}"
            )
            if isinstance(data, list):
                return data
            return data.get("transactions", [])
        except RustChainError:
            return []
