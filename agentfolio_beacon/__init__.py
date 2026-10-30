"""AgentFolio <-> Beacon dual-layer trust integration (reference implementation)."""

from agentfolio_beacon.agentfolio_beacon_tool import (
    MCP_TOOL,
    AgentFolioBeaconClient,
    TTLCache,
    agentfolio_lookup_beacon,
    handle_mcp_tool_call,
)

__all__ = [
    "MCP_TOOL",
    "AgentFolioBeaconClient",
    "TTLCache",
    "agentfolio_lookup_beacon",
    "handle_mcp_tool_call",
]
