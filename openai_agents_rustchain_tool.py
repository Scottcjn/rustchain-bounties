"""OpenAI Agents SDK tools for public RustChain data."""

from typing import Any, Dict, List, Optional, Sequence

import requests
from agents import Agent, FunctionTool, function_tool


DEFAULT_NODE_URL = "https://rustchain.org"
DEFAULT_BOUNTIES_URL = (
    "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
)


class RustChainClient:
    """Small HTTP client used by the agent tools."""

    def __init__(
        self,
        node_url: str = DEFAULT_NODE_URL,
        bounties_url: str = DEFAULT_BOUNTIES_URL,
        timeout: float = 10.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.node_url = node_url.rstrip("/")
        self.bounties_url = bounties_url
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "User-Agent": "rustchain-openai-agents-tool",
            }
        )

    def _get_json(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return {"ok": True, "data": response.json()}
        except requests.RequestException as exc:
            return {"ok": False, "error": f"RustChain request failed: {exc}"}
        except ValueError as exc:
            return {"ok": False, "error": f"RustChain returned invalid JSON: {exc}"}

    def check_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Return the RTC balance payload for a wallet or miner handle."""
        wallet_id = wallet_id.strip()
        if not wallet_id:
            return {"ok": False, "error": "wallet_id must not be empty"}

        result = self._get_json(
            f"{self.node_url}/wallet/balance",
            params={"miner_id": wallet_id},
        )
        if result["ok"]:
            result["wallet_id"] = wallet_id
        return result

    def list_bounties(self, limit: int = 10) -> Dict[str, Any]:
        """Return open RustChain bounty issues from the project repository."""
        if not 1 <= limit <= 100:
            return {"ok": False, "error": "limit must be between 1 and 100"}

        result = self._get_json(
            self.bounties_url,
            params={"state": "open", "labels": "bounty", "per_page": limit},
        )
        if not result["ok"]:
            return result

        payload = result["data"]
        if not isinstance(payload, list):
            return {"ok": False, "error": "Bounty API returned an unexpected payload"}

        bounties = [item for item in payload if "pull_request" not in item][:limit]
        return {"ok": True, "count": len(bounties), "bounties": bounties}

    def get_node_health(self) -> Dict[str, Any]:
        """Return the RustChain node health payload."""
        return self._get_json(f"{self.node_url}/health")

    def get_current_epoch(self) -> Dict[str, Any]:
        """Return the current RustChain epoch payload."""
        return self._get_json(f"{self.node_url}/epoch")


def create_rustchain_tools(
    client: Optional[RustChainClient] = None,
) -> Sequence[FunctionTool]:
    """Create four OpenAI Agents SDK tools backed by a RustChain client."""
    rustchain = client or RustChainClient()

    @function_tool
    def check_balance(wallet_id: str) -> Dict[str, Any]:
        """Check the RTC balance for a RustChain wallet or miner handle.

        Args:
            wallet_id: RustChain wallet identifier or registered miner handle.
        """
        return rustchain.check_balance(wallet_id)

    @function_tool
    def list_bounties(limit: int = 10) -> Dict[str, Any]:
        """List open RustChain bounty issues.

        Args:
            limit: Maximum number of bounties to return, from 1 through 100.
        """
        return rustchain.list_bounties(limit)

    @function_tool
    def get_node_health() -> Dict[str, Any]:
        """Get the current health payload from the public RustChain node."""
        return rustchain.get_node_health()

    @function_tool
    def get_current_epoch() -> Dict[str, Any]:
        """Get the current epoch payload from the public RustChain node."""
        return rustchain.get_current_epoch()

    return (
        check_balance,
        list_bounties,
        get_node_health,
        get_current_epoch,
    )


def create_rustchain_agent(
    client: Optional[RustChainClient] = None,
) -> Agent:
    """Create an agent that can inspect public RustChain state and bounties."""
    return Agent(
        name="RustChain assistant",
        instructions=(
            "Use the RustChain tools to answer questions about wallet balances, "
            "open bounties, node health, and the current epoch. Report tool "
            "errors clearly and do not invent unavailable blockchain data."
        ),
        tools=list(create_rustchain_tools(client)),
    )


RUSTCHAIN_TOOLS: List[FunctionTool] = list(create_rustchain_tools())
