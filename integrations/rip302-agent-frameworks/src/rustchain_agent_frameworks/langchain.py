from __future__ import annotations

from typing import Any

from .core import AgentEconomyToolkit


def build_langchain_tools(toolkit: AgentEconomyToolkit | None = None) -> list[Any]:
    """Return LangChain StructuredTool objects for the current RIP-302 surface."""
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as exc:  # pragma: no cover - depends on optional package
        raise ImportError(
            "Install rustchain-agent-frameworks[langchain] to build LangChain tools"
        ) from exc

    tk = toolkit or AgentEconomyToolkit()
    specs = [
        ("rustchain_agent_status", tk.status),
        ("rustchain_list_jobs", tk.list_jobs),
        ("rustchain_get_job", tk.get_job),
        ("rustchain_post_job", tk.post_job),
        ("rustchain_claim_job", tk.claim_job),
        ("rustchain_deliver_job", tk.deliver_job),
        ("rustchain_get_reputation", tk.get_reputation),
        ("rustchain_marketplace_stats", tk.get_marketplace_stats),
    ]
    return [
        StructuredTool.from_function(
            func=fn,
            name=name,
            description=(fn.__doc__ or name).strip(),
        )
        for name, fn in specs
    ]
