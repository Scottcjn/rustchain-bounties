"""
RustChain Staking MCP Server
Bounty #14383: LangChain + MCP tool for staked self-improvement

Exposes stake_and_acquire as an MCP tool.
"""

import os
import time
import requests
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("rustchain-staking")
GATE_ENDPOINT = os.getenv("ELYAN_GATE_ENDPOINT", "https://gate.elyan.ai/api/v1")
API_KEY = os.getenv("ELYAN_API_KEY", "")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="stake_and_acquire",
            description="Stake RTC to acquire a skill on RustChain.",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill": {"type": "string", "description": "Skill name"},
                    "bond_rtc": {"type": "integer", "description": "RTC amount"},
                    "wallet": {"type": "string", "description": "Wallet address"},
                },
                "required": ["skill", "bond_rtc"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "stake_and_acquire":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    if not API_KEY:
        return [TextContent(type="text", text='{"error": "Missing ELYAN_API_KEY"}')]

    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {"skill": arguments["skill"], "bond_rtc": arguments["bond_rtc"],
               "wallet": arguments.get("wallet", "default"), "timestamp": time.time() * 1000}

    try:
        resp = requests.post(f"{GATE_ENDPOINT}/stake", json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            return [TextContent(type="text", text=str({"success": True, "verdict": resp.json()}))]
        return [TextContent(type="text", text=str({"success": False, "error": f"HTTP {resp.status_code}"}))]
    except requests.exceptions.ConnectionError:
        return [TextContent(type="text", text=str({"success": False, "fail_safe": True}))]
    except Exception as e:
        return [TextContent(type="text", text=str({"success": False, "error": str(e)}))]


if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server

    async def main():
        async with stdio_server() as (read, write):
            await app.run(read, write, app.create_initialization_options())
    asyncio.run(main())
