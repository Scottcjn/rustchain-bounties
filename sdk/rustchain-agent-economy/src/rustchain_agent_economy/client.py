from __future__ import annotations

import asyncio
import hashlib
import json
import math
import secrets
import ssl
from dataclasses import dataclass
from typing import Any, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

DEFAULT_BASE_URL = "https://bulbous-bouffant.metalseed.net"
AGENT_JOB_CATEGORIES = (
    "research",
    "code",
    "video",
    "audio",
    "writing",
    "translation",
    "data",
    "design",
    "testing",
    "other",
)


class AgentEconomyError(RuntimeError):
    """Base class for SDK failures."""


class AgentEconomyValidationError(AgentEconomyError):
    """Raised before a request when SDK inputs violate RIP-302."""


class AgentEconomyTransportError(AgentEconomyError):
    """Raised when no HTTP response can be obtained."""


class AgentEconomyApiError(AgentEconomyError):
    """RIP-302 JSON error with the server's status/code/body preserved."""

    def __init__(self, status: int, path: str, body: Any):
        self.status = status
        self.path = path
        self.body = body
        self.code = body.get("code") if isinstance(body, dict) else None
        self.error = body.get("error") if isinstance(body, dict) else None
        message = self.error or f"HTTP {status}"
        if self.code:
            message = f"{self.code}: {message}"
        super().__init__(f"RIP-302 {path}: {message}")


class JsonTransport(Protocol):
    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any]: ...


class UrllibJsonTransport:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 30.0,
        verify_tls: bool = True,
        ca_file: str | None = None,
        user_agent: str = "rustchain-agent-economy-python/0.1.0",
    ):
        if not isinstance(base_url, str) or not base_url.strip():
            raise AgentEconomyValidationError("base_url must be a non-empty string")
        if timeout <= 0:
            raise AgentEconomyValidationError("timeout must be positive")
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.user_agent = user_agent
        if self.base_url.startswith("https://"):
            if verify_tls:
                self.ssl_context = ssl.create_default_context(cafile=ca_file)
            else:
                self.ssl_context = ssl._create_unverified_context()
        else:
            self.ssl_context = None

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if query:
            params = {k: str(v) for k, v in query.items() if v is not None}
            if params:
                url = f"{url}?{urlencode(params)}"
        request_headers = {"Accept": "application/json", "User-Agent": self.user_agent}
        if headers:
            request_headers.update(headers)
        data = None
        if json_body is not None:
            data = json.dumps(json_body, separators=(",", ":")).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        req = Request(url, data=data, headers=request_headers, method=method.upper())
        try:
            with urlopen(req, timeout=self.timeout, context=self.ssl_context) as response:
                body = response.read()
                return _decode_json(body, path)
        except HTTPError as exc:
            raw = exc.read()
            try:
                body = _decode_json(raw, path)
            except AgentEconomyTransportError:
                body = {"error": raw.decode("utf-8", errors="replace") or exc.reason}
            raise AgentEconomyApiError(exc.code, path, body) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise AgentEconomyTransportError(f"RIP-302 {path}: transport failed: {exc}") from exc


def _decode_json(raw: bytes, path: str) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AgentEconomyTransportError(f"RIP-302 {path}: response was not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise AgentEconomyTransportError(f"RIP-302 {path}: expected a JSON object response")
    return parsed


def _require_text(value: str, name: str, *, min_len: int = 1) -> str:
    if not isinstance(value, str) or len(value.strip()) < min_len:
        raise AgentEconomyValidationError(f"{name} must be at least {min_len} non-whitespace characters")
    return value.strip()


def _job_path(job_id: str, action: str | None = None) -> str:
    job_id = _require_text(job_id, "job_id")
    base = f"/agent/jobs/{quote(job_id, safe='')}"
    return f"{base}/{action}" if action else base


def _validate_reward(value: float | int) -> float:
    if isinstance(value, bool):
        raise AgentEconomyValidationError("reward_rtc must be a finite number")
    try:
        reward = float(value)
    except (TypeError, ValueError) as exc:
        raise AgentEconomyValidationError("reward_rtc must be a finite number") from exc
    if not math.isfinite(reward) or reward < 0.01 or reward > 10_000:
        raise AgentEconomyValidationError("reward_rtc must be between 0.01 and 10000")
    return reward


def _validate_category(category: str) -> str:
    category = _require_text(category, "category").lower()
    if category not in AGENT_JOB_CATEGORIES:
        raise AgentEconomyValidationError(f"category must be one of: {', '.join(AGENT_JOB_CATEGORIES)}")
    return category


def canonical_create_message(
    poster_wallet: str,
    category: str,
    reward_rtc: float | int,
    nonce: str,
) -> bytes:
    """Build the exact RIP-302 create-signature message."""
    payload = {
        "action": "agent_post_job",
        "category": _validate_category(category),
        "nonce": _require_text(str(nonce), "nonce"),
        "poster": _require_text(poster_wallet, "poster_wallet"),
        "reward_rtc": _validate_reward(reward_rtc),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class Ed25519Signer:
    """Ed25519 key holder for signed RIP-302 job creation."""

    _private_key: Ed25519PrivateKey

    @classmethod
    def generate(cls) -> "Ed25519Signer":
        return cls(Ed25519PrivateKey.generate())

    @classmethod
    def from_private_key_hex(cls, private_key_hex: str) -> "Ed25519Signer":
        try:
            raw = bytes.fromhex(private_key_hex)
        except ValueError as exc:
            raise AgentEconomyValidationError("private key must be hex") from exc
        if len(raw) != 32:
            raise AgentEconomyValidationError("Ed25519 private key must be exactly 32 bytes")
        return cls(Ed25519PrivateKey.from_private_bytes(raw))

    @property
    def public_key_bytes(self) -> bytes:
        return self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @property
    def public_key_hex(self) -> str:
        return self.public_key_bytes.hex()

    @property
    def rtc_address(self) -> str:
        return "RTC" + hashlib.sha256(self.public_key_bytes).hexdigest()[:40]

    def sign_create(
        self,
        poster_wallet: str,
        category: str,
        reward_rtc: float | int,
        nonce: str,
    ) -> str:
        return self._private_key.sign(
            canonical_create_message(poster_wallet, category, reward_rtc, nonce)
        ).hex()


class AgentEconomyClient:
    """Synchronous client for the implemented RIP-302 v2 `/agent/*` surface."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 30.0,
        verify_tls: bool = True,
        ca_file: str | None = None,
        transport: JsonTransport | None = None,
    ):
        self.transport = transport or UrllibJsonTransport(
            base_url,
            timeout=timeout,
            verify_tls=verify_tls,
            ca_file=ca_file,
        )

    def list_jobs(
        self,
        *,
        status: str = "open",
        category: str | None = None,
        min_reward: float = 0,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 0 <= limit <= 100:
            raise AgentEconomyValidationError("limit must be an integer from 0 to 100")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise AgentEconomyValidationError("offset must be a non-negative integer")
        if isinstance(min_reward, bool):
            raise AgentEconomyValidationError("min_reward must be non-negative")
        try:
            min_reward_num = float(min_reward)
        except (TypeError, ValueError) as exc:
            raise AgentEconomyValidationError("min_reward must be non-negative") from exc
        if not math.isfinite(min_reward_num) or min_reward_num < 0:
            raise AgentEconomyValidationError("min_reward must be non-negative")
        query: dict[str, Any] = {
            "status": _require_text(status, "status"),
            "min_reward": min_reward_num,
            "limit": limit,
            "offset": offset,
        }
        if category is not None:
            query["category"] = _validate_category(category)
        return self.transport.request("GET", "/agent/jobs", query=query)

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self.transport.request("GET", _job_path(job_id))

    def post_job(
        self,
        *,
        poster_wallet: str,
        title: str,
        description: str,
        reward_rtc: float | int,
        category: str = "other",
        ttl_seconds: int = 604800,
        tags: list[str] | None = None,
        signer: Ed25519Signer | None = None,
        nonce: str | None = None,
        admin_key: str | None = None,
    ) -> dict[str, Any]:
        poster = _require_text(poster_wallet, "poster_wallet")
        title = _require_text(title, "title", min_len=5)
        description = _require_text(description, "description", min_len=20)
        category = _validate_category(category)
        reward = _validate_reward(reward_rtc)
        if not isinstance(ttl_seconds, int) or isinstance(ttl_seconds, bool) or ttl_seconds <= 0:
            raise AgentEconomyValidationError("ttl_seconds must be a positive integer")
        body: dict[str, Any] = {
            "poster_wallet": poster,
            "title": title,
            "description": description,
            "category": category,
            "reward_rtc": reward,
            "ttl_seconds": ttl_seconds,
            "tags": [str(tag) for tag in (tags or [])],
        }
        headers: dict[str, str] = {}
        if signer is not None:
            if poster.startswith("RTC") and signer.rtc_address.lower() != poster.lower():
                raise AgentEconomyValidationError("signer public key does not match poster_wallet RTC address")
            signed_nonce = nonce or secrets.token_hex(16)
            body.update(
                nonce=signed_nonce,
                poster_pubkey=signer.public_key_hex,
                poster_sig=signer.sign_create(poster, category, reward, signed_nonce),
            )
        elif admin_key:
            headers["X-Admin-Key"] = admin_key
        return self.transport.request("POST", "/agent/jobs", json_body=body, headers=headers)

    def claim_job(self, job_id: str, worker_wallet: str) -> dict[str, Any]:
        return self.transport.request(
            "POST",
            _job_path(job_id, "claim"),
            json_body={"worker_wallet": _require_text(worker_wallet, "worker_wallet")},
        )

    def deliver_job(
        self,
        job_id: str,
        *,
        worker_wallet: str,
        deliverable_url: str | None = None,
        deliverable_hash: str | None = None,
        result_summary: str | None = None,
    ) -> dict[str, Any]:
        if deliverable_url is None and result_summary is None:
            raise AgentEconomyValidationError("deliverable_url or result_summary is required")
        body: dict[str, Any] = {"worker_wallet": _require_text(worker_wallet, "worker_wallet")}
        if deliverable_url is not None:
            body["deliverable_url"] = str(deliverable_url)
        if deliverable_hash is not None:
            body["deliverable_hash"] = str(deliverable_hash)
        if result_summary is not None:
            body["result_summary"] = str(result_summary)
        return self.transport.request("POST", _job_path(job_id, "deliver"), json_body=body)

    def accept_job(
        self,
        job_id: str,
        *,
        poster_wallet: str,
        settlement_sig: str,
        rating: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "poster_wallet": _require_text(poster_wallet, "poster_wallet"),
            "settlement_sig": _require_text(settlement_sig, "settlement_sig"),
        }
        if rating is not None:
            if not isinstance(rating, int) or isinstance(rating, bool) or not 1 <= rating <= 5:
                raise AgentEconomyValidationError("rating must be an integer from 1 to 5")
            body["rating"] = rating
        return self.transport.request("POST", _job_path(job_id, "accept"), json_body=body)

    def dispute_job(
        self,
        job_id: str,
        *,
        poster_wallet: str,
        reason: str,
        settlement_sig: str,
    ) -> dict[str, Any]:
        return self.transport.request(
            "POST",
            _job_path(job_id, "dispute"),
            json_body={
                "poster_wallet": _require_text(poster_wallet, "poster_wallet"),
                "reason": _require_text(reason, "reason"),
                "settlement_sig": _require_text(settlement_sig, "settlement_sig"),
            },
        )

    def cancel_job(
        self,
        job_id: str,
        *,
        poster_wallet: str,
        settlement_sig: str,
    ) -> dict[str, Any]:
        return self.transport.request(
            "POST",
            _job_path(job_id, "cancel"),
            json_body={
                "poster_wallet": _require_text(poster_wallet, "poster_wallet"),
                "settlement_sig": _require_text(settlement_sig, "settlement_sig"),
            },
        )

    def get_reputation(self, wallet_id: str) -> dict[str, Any]:
        wallet = _require_text(wallet_id, "wallet_id")
        return self.transport.request("GET", f"/agent/reputation/{quote(wallet, safe='')}")

    def get_stats(self) -> dict[str, Any]:
        return self.transport.request("GET", "/agent/stats")


class AsyncAgentEconomyClient:
    """Asyncio facade; network work executes off the event loop."""

    def __init__(self, *args: Any, **kwargs: Any):
        self._sync = AgentEconomyClient(*args, **kwargs)

    async def list_jobs(self, **kwargs: Any) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.list_jobs, **kwargs)

    async def get_job(self, job_id: str) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.get_job, job_id)

    async def post_job(self, **kwargs: Any) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.post_job, **kwargs)

    async def claim_job(self, job_id: str, worker_wallet: str) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.claim_job, job_id, worker_wallet)

    async def deliver_job(self, job_id: str, **kwargs: Any) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.deliver_job, job_id, **kwargs)

    async def accept_job(self, job_id: str, **kwargs: Any) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.accept_job, job_id, **kwargs)

    async def dispute_job(self, job_id: str, **kwargs: Any) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.dispute_job, job_id, **kwargs)

    async def cancel_job(self, job_id: str, **kwargs: Any) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.cancel_job, job_id, **kwargs)

    async def get_reputation(self, wallet_id: str) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.get_reputation, wallet_id)

    async def get_stats(self) -> dict[str, Any]:
        return await asyncio.to_thread(self._sync.get_stats)
