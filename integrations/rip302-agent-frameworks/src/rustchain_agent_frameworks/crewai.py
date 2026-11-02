from __future__ import annotations

from typing import Any, Callable

from .core import AgentEconomyToolkit


def _tool_decorator() -> Callable[[str], Callable[[Callable[..., Any]], Any]]:
    try:
        from crewai.tools import tool
    except ImportError:
        try:
            from crewai import tool
        except ImportError as exc:  # pragma: no cover - optional package
            raise ImportError(
                "Install rustchain-agent-frameworks[crewai] to build CrewAI tools"
            ) from exc
    return tool


def build_crewai_tools(toolkit: AgentEconomyToolkit | None = None) -> list[Any]:
    """Return CrewAI tools backed by a shared current-protocol toolkit."""
    tk = toolkit or AgentEconomyToolkit()
    tool = _tool_decorator()

    def agent_status() -> dict[str, Any]:
        """Show non-secret RustChain Agent Economy connection/signing state."""
        return tk.status()

    def list_jobs(
        status: str = "open",
        category: str | None = None,
        min_reward: float = 0,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Browse RIP-302 jobs by status, category, reward and pagination."""
        return tk.list_jobs(status, category, min_reward, limit, offset)

    def get_job(job_id: str) -> dict[str, Any]:
        """Get one RIP-302 job including its activity log and ratings."""
        return tk.get_job(job_id)

    def post_job(
        title: str,
        description: str,
        reward_rtc: float,
        category: str = "other",
        ttl_seconds: int = 604800,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Post a signed job using the process-configured RTC identity."""
        return tk.post_job(title, description, reward_rtc, category, ttl_seconds, tags)

    def claim_job(job_id: str, worker_wallet: str | None = None) -> dict[str, Any]:
        """Claim an open job with an explicit or process-default worker wallet."""
        return tk.claim_job(job_id, worker_wallet)

    def deliver_job(
        job_id: str,
        worker_wallet: str | None = None,
        deliverable_url: str | None = None,
        deliverable_hash: str | None = None,
        result_summary: str | None = None,
    ) -> dict[str, Any]:
        """Deliver or redeliver work for the assigned worker."""
        return tk.deliver_job(
            job_id,
            worker_wallet,
            deliverable_url,
            deliverable_hash,
            result_summary,
        )

    def get_reputation(wallet_id: str) -> dict[str, Any]:
        """Read RIP-302 reputation for a wallet or agent id."""
        return tk.get_reputation(wallet_id)

    def marketplace_stats() -> dict[str, Any]:
        """Read aggregate Agent Economy marketplace statistics."""
        return tk.get_marketplace_stats()

    functions = [
        ("rustchain_agent_status", agent_status),
        ("rustchain_list_jobs", list_jobs),
        ("rustchain_get_job", get_job),
        ("rustchain_post_job", post_job),
        ("rustchain_claim_job", claim_job),
        ("rustchain_deliver_job", deliver_job),
        ("rustchain_get_reputation", get_reputation),
        ("rustchain_marketplace_stats", marketplace_stats),
    ]
    tools = [tool(name)(fn) for name, fn in functions]
    for built_tool in tools:
        # Marketplace state changes between calls; cached mutations must never
        # replace another posting, claim or delivery operation.
        built_tool.cache_function = lambda _arguments, _result: False
    return tools
