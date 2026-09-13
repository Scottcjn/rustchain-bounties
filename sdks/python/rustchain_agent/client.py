"""Typed client for the RIP-302 wallet, payment, and reputation APIs."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from urllib.parse import quote, urlsplit
from uuid import uuid4

import requests

BASE_URL = "https://rustchain.org"
RTC_WALLET_RE = re.compile(r"^RTC[0-9A-Fa-f]{40}$")
AGENT_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


class RustChainAPIError(RuntimeError):
    """Raised when a RustChain endpoint returns an invalid or failed response."""

    def __init__(self, message: str, *, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def validate_wallet_address(wallet_address: str) -> str:
    """Validate the canonical RustChain address format required by the maintainer."""

    if not isinstance(wallet_address, str) or not RTC_WALLET_RE.fullmatch(
        wallet_address
    ):
        raise ValueError(
            "wallet_address must be RTC followed by exactly 40 hex characters"
        )
    return wallet_address


def validate_agent_id(agent_id: str) -> str:
    """Validate the RIP-302 3-64 character lowercase agent identifier."""

    if (
        not isinstance(agent_id, str)
        or not 3 <= len(agent_id) <= 64
        or not AGENT_ID_RE.fullmatch(agent_id)
    ):
        raise ValueError(
            "agent_id must be 3-64 lowercase alphanumeric/hyphen characters, "
            "start with a letter, and contain no consecutive hyphens"
        )
    return agent_id


def _required_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _positive_amount(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("amount must be a finite positive number")
    amount = float(value)
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("amount must be a finite positive number")
    return amount


def _limit(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 1000:
        raise ValueError("limit must be an integer between 1 and 1000")
    return value


class RustChainAgent:
    """Client for the official RIP-302 endpoint families.

    The client implements only the wallet, payment, and reputation routes listed
    by RIP-302. Mutating methods are ordinary SDK wrappers; unit tests mock every
    request, and the checked-in live evidence uses GET requests only.
    """

    def __init__(
        self,
        *,
        agent_id: str,
        wallet_address: str,
        api_key: Optional[str] = None,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ):
        self.agent_id = validate_agent_id(agent_id)
        self.wallet_address = validate_wallet_address(wallet_address)
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url must be an absolute HTTP(S) URL")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "rustchain-agent/0.2.0 (RIP-302)",
            }
        )
        if api_key:
            self.session.headers["X-API-Key"] = api_key

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json_payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            raise RustChainAPIError(
                f"{method.upper()} {endpoint} failed",
                status_code=status_code,
            ) from exc

        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise RustChainAPIError(
                f"{method.upper()} {endpoint} returned non-JSON data",
                status_code=response.status_code,
            ) from exc
        if not isinstance(payload, dict):
            raise RustChainAPIError(
                f"{method.upper()} {endpoint} returned a non-object JSON payload",
                status_code=response.status_code,
            )
        return payload

    @staticmethod
    def _segment(value: str, field: str) -> str:
        return quote(_required_text(value, field), safe="")

    # Wallet endpoints -----------------------------------------------------

    def create_wallet(
        self,
        *,
        name: Optional[str] = None,
        base_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "agent_id": self.agent_id,
            "wallet_address": self.wallet_address,
            "name": name or self.agent_id,
        }
        if base_address is not None:
            payload["base_address"] = _required_text(base_address, "base_address")
        return self._request(
            "POST",
            "/api/agent/wallet/create",
            json_payload=payload,
        )

    def get_wallet(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        target = validate_agent_id(agent_id or self.agent_id)
        return self._request(
            "GET",
            f"/api/agent/wallet/{self._segment(target, 'agent_id')}",
        )

    # Payment endpoints ----------------------------------------------------

    def send_payment(
        self,
        *,
        to_agent: str,
        amount: float,
        memo: Optional[str] = None,
        resource: Optional[str] = None,
        payment_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        recipient = validate_agent_id(to_agent)
        if recipient == self.agent_id:
            raise ValueError("to_agent must be different from agent_id")
        pid = payment_id or f"pay_{uuid4().hex[:16]}"
        payload: Dict[str, Any] = {
            "payment_id": _required_text(pid, "payment_id"),
            "from_agent": self.agent_id,
            "to_agent": recipient,
            "amount": _positive_amount(amount),
        }
        if memo is not None:
            payload["memo"] = memo
        if resource is not None:
            payload["resource"] = _required_text(resource, "resource")
        return self._request(
            "POST",
            "/api/agent/payment/send",
            json_payload=payload,
        )

    def request_payment(
        self,
        *,
        from_agent: str,
        amount: float,
        description: str,
        resource: Optional[str] = None,
        intent_id: Optional[str] = None,
        expires_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        payer = validate_agent_id(from_agent)
        iid = intent_id or f"intent_{uuid4().hex[:12]}"
        expiry = (
            expires_at
            or (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        )
        payload = {
            "intent_id": _required_text(iid, "intent_id"),
            "from_agent": payer,
            "to_agent": self.agent_id,
            "amount": _positive_amount(amount),
            "description": _required_text(description, "description"),
            "resource": resource or f"/api/agent/payment/{iid}",
            "expires_at": _required_text(expiry, "expires_at"),
        }
        return self._request(
            "POST",
            "/api/agent/payment/request",
            json_payload=payload,
        )

    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        return self._request(
            "GET",
            f"/api/agent/payment/{self._segment(payment_id, 'payment_id')}",
        )

    def get_payment_history(
        self,
        *,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": _limit(limit)}
        if status is not None:
            params["status"] = _required_text(status, "status")
        return self._request("GET", "/api/agent/payment/history", params=params)

    def create_x402_challenge(
        self,
        *,
        resource: str,
        required_amount: float,
    ) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/api/agent/payment/x402/challenge",
            json_payload={
                "resource": _required_text(resource, "resource"),
                "amount": _positive_amount(required_amount),
                "recipient": self.agent_id,
            },
        )

    # Reputation endpoints -------------------------------------------------

    def get_reputation(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        target = validate_agent_id(agent_id or self.agent_id)
        return self._request(
            "GET",
            f"/api/agent/reputation/{self._segment(target, 'agent_id')}",
        )

    def submit_attestation(
        self,
        *,
        to_agent: str,
        rating: int,
        comment: Optional[str] = None,
        transaction_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if (
            isinstance(rating, bool)
            or not isinstance(rating, int)
            or not 1 <= rating <= 5
        ):
            raise ValueError("rating must be an integer between 1 and 5")
        payload: Dict[str, Any] = {
            "from_agent": self.agent_id,
            "to_agent": validate_agent_id(to_agent),
            "rating": rating,
        }
        if comment is not None:
            payload["comment"] = comment
        if transaction_id is not None:
            payload["transaction_id"] = _required_text(
                transaction_id,
                "transaction_id",
            )
        return self._request(
            "POST",
            "/api/agent/reputation/attest",
            json_payload=payload,
        )

    def get_reputation_leaderboard(
        self,
        *,
        limit: int = 100,
        tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": _limit(limit)}
        if tier is not None:
            params["tier"] = _required_text(tier, "tier")
        return self._request(
            "GET",
            "/api/agent/reputation/leaderboard",
            params=params,
        )

    def get_trust_proof(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        target = validate_agent_id(agent_id or self.agent_id)
        return self._request(
            "GET",
            f"/api/agent/reputation/{self._segment(target, 'agent_id')}/proof",
        )

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "RustChainAgent":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
