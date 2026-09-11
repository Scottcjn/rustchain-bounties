from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Literal

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class RustChainAPI:
    """Small read-only client for RustChain and its public bounty board."""

    def __init__(self, base_url: str = "https://rustchain.org", timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_url(self, url: str) -> Any:
        request = urllib.request.Request(url, headers={"User-Agent": "langchain-rustchain/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code} for {url}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Request failed for {url}: {exc.reason}") from exc

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        query = urllib.parse.urlencode(params or {})
        url = f"{self.base_url}{path}" + (f"?{query}" if query else "")
        return self._get_url(url)

    def check_balance(self, wallet_id: str) -> float:
        payload = self._get("/wallet/balance", {"miner_id": wallet_id})
        for key in ("amount_rtc", "balance", "balance_rtc"):
            if key in payload:
                return float(payload[key])
        raise RuntimeError("RustChain balance response did not contain a known balance field")

    def list_bounties(self, limit: int = 10) -> list[dict[str, Any]]:
        """List open bounty issues from RustChain's canonical public GitHub board."""
        safe_limit = max(1, min(limit, 100))
        params = urllib.parse.urlencode({
            "state": "open",
            "labels": "bounty",
            "per_page": safe_limit,
        })
        url = f"https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?{params}"
        payload = self._get_url(url)
        if not isinstance(payload, list):
            raise RuntimeError("RustChain bounty board response was not a list")
        return [
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "url": item.get("html_url"),
                "labels": [label.get("name") for label in item.get("labels", [])],
            }
            for item in payload[:safe_limit]
            if "pull_request" not in item
        ]

    def get_node_health(self) -> dict[str, Any]:
        payload = self._get("/health")
        if not isinstance(payload, dict):
            raise RuntimeError("RustChain health response was not an object")
        return payload

    def get_current_epoch(self) -> dict[str, Any]:
        payload = self._get("/epoch")
        if not isinstance(payload, dict):
            raise RuntimeError("RustChain epoch response was not an object")
        return payload


class RustChainInput(BaseModel):
    action: Literal["check_balance", "list_bounties", "get_node_health", "get_current_epoch"]
    wallet_id: str | None = None
    limit: int = Field(default=10, ge=1, le=100)


class RustChainTool(BaseTool):
    """Read-only RustChain tool suitable for LangChain agents."""

    name: str = "rustchain"
    description: str = (
        "Read public RustChain data. Actions: check_balance, list_bounties, "
        "get_node_health, get_current_epoch."
    )
    args_schema: type[BaseModel] = RustChainInput
    base_url: str = "https://rustchain.org"
    timeout: float = 10.0

    def _api(self) -> RustChainAPI:
        return RustChainAPI(self.base_url, self.timeout)

    def check_balance(self, wallet_id: str) -> float:
        return self._api().check_balance(wallet_id)

    def list_bounties(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._api().list_bounties(limit)

    def get_node_health(self) -> dict[str, Any]:
        return self._api().get_node_health()

    def get_current_epoch(self) -> dict[str, Any]:
        return self._api().get_current_epoch()

    def _run(self, action: str, wallet_id: str | None = None, limit: int = 10, **_: Any) -> Any:
        if action == "check_balance":
            if not wallet_id:
                raise ValueError("wallet_id is required for check_balance")
            return self.check_balance(wallet_id)
        if action == "list_bounties":
            return self.list_bounties(limit)
        if action == "get_node_health":
            return self.get_node_health()
        if action == "get_current_epoch":
            return self.get_current_epoch()
        raise ValueError(f"Unsupported RustChain action: {action}")
