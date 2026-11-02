from __future__ import annotations

from typing import Any

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from .service import AgentEconomyMcpService, McpConfigurationError


def build_server(service: AgentEconomyMcpService | None = None) -> MCPServer:
    svc = service or AgentEconomyMcpService()
    mcp = MCPServer(
        "RustChain Agent Economy",
        instructions=(
            "Tools target the implemented RIP-302 v2 /agent/* API. "
            "Job posting uses an Ed25519 private key from the server process "
            "environment, never from model-visible tool arguments. Settlement "
            "accept/dispute/cancel actions are intentionally not exposed because "
            "RIP-302 requires the node operator's settlement-authority signature."
        ),
    )

    def call(fn, *args: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            return fn(*args, **kwargs)
        except McpConfigurationError as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool()
    def agent_status() -> dict[str, Any]:
        """Show non-secret Agent Economy connection and signing capability state."""
        return svc.status()

    @mcp.tool()
    def list_jobs(
        status: str = "open",
        category: str | None = None,
        min_reward: float = 0,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Browse RIP-302 jobs with server-supported filters."""
        return call(
            svc.list_jobs,
            status=status,
            category=category,
            min_reward=min_reward,
            limit=limit,
            offset=offset,
        )

    @mcp.tool()
    def get_job(job_id: str) -> dict[str, Any]:
        """Get one job including activity log and ratings."""
        return call(svc.get_job, job_id)

    @mcp.tool()
    def post_job(
        title: str,
        description: str,
        reward_rtc: float,
        category: str = "other",
        ttl_seconds: int = 604800,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Post and sign a new job using the process-configured RTC identity."""
        return call(
            svc.post_job,
            title=title,
            description=description,
            reward_rtc=reward_rtc,
            category=category,
            ttl_seconds=ttl_seconds,
            tags=tags,
        )

    @mcp.tool()
    def claim_job(job_id: str, worker_wallet: str | None = None) -> dict[str, Any]:
        """Claim an open job with an explicit or process-default worker wallet."""
        return call(svc.claim_job, job_id, worker_wallet=worker_wallet)

    @mcp.tool()
    def deliver_job(
        job_id: str,
        worker_wallet: str | None = None,
        deliverable_url: str | None = None,
        deliverable_hash: str | None = None,
        result_summary: str | None = None,
    ) -> dict[str, Any]:
        """Submit or resubmit work for the assigned worker."""
        return call(
            svc.deliver_job,
            job_id,
            worker_wallet=worker_wallet,
            deliverable_url=deliverable_url,
            deliverable_hash=deliverable_hash,
            result_summary=result_summary,
        )

    @mcp.tool()
    def get_reputation(wallet_id: str) -> dict[str, Any]:
        """Read RIP-302 reputation for a wallet or agent id."""
        return call(svc.get_reputation, wallet_id)

    @mcp.tool()
    def get_marketplace_stats() -> dict[str, Any]:
        """Read aggregate Agent Economy marketplace statistics."""
        return call(svc.get_stats)

    return mcp


mcp = build_server()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
