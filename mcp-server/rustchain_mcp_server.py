#!/usr/bin/env python3
"""
RustChain MCP Server

Query RustChain blockchain from Claude Code via MCP protocol.

Tools:
- rustchain_health: Check node health
- rustchain_miners: List active miners
- rustchain_epoch: Get epoch info
- rustchain_balance: Check wallet balance
- rustchain_transfer: Send RTC (bonus)
"""

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.server import Server


# Node endpoints (port 8099)
NODES = [
    "http://50.28.86.131:8099",
    "http://50.28.86.153:8099", 
    "http://76.8.228.245:8099",
]
PRIMARY_NODE = "http://50.28.86.153:8099"


def create_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def http_get(url: str, timeout: int = 10) -> tuple[bool, Any, str]:
    """Make HTTP GET request."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rustchain-mcp/1.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=create_ssl_context()) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return True, json.loads(body), ""
            except json.JSONDecodeError:
                return False, None, "invalid_json"
    except urllib.error.HTTPError as e:
        return False, None, f"http_{e.code}"
    except Exception as e:
        return False, None, str(e)


def get_best_node() -> str:
    """Find first working node."""
    for node in NODES:
        ok, _, _ = http_get(f"{node}/health", timeout=3)
        if ok:
            return node
    return PRIMARY_NODE  # Fallback


# Create server
app = Server("rustchain")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="rustchain_health",
            description="Check health status of RustChain nodes",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="rustchain_miners",
            description="List active miners and their architectures",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max miners to return", "default": 20},
                },
            },
        ),
        Tool(
            name="rustchain_epoch",
            description="Get current epoch information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="rustchain_balance",
            description="Check RTC balance for a wallet address",
            inputSchema={
                "type": "object",
                "properties": {
                    "miner_id": {"type": "string", "description": "Wallet/Miner ID to check"},
                },
                "required": ["miner_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    node = get_best_node()
    
    if name == "rustchain_health":
        results = []
        for n in NODES:
            ok, data, err = http_get(f"{n}/health")
            if ok:
                results.append({
                    "node": n,
                    "status": "up",
                    "version": data.get("version"),
                    "uptime": data.get("uptime_s"),
                    "db_rw": data.get("db_rw"),
                })
            else:
                results.append({"node": n, "status": "down", "error": err})
        
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    elif name == "rustchain_miners":
        limit = arguments.get("limit", 20)
        ok, data, err = http_get(f"{node}/api/miners")
        
        if not ok:
            return [TextContent(type="text", text=f"Error: {err}")]
        
        # Handle both list and dict formats
        if isinstance(data, list):
            miners = data[:limit]
        else:
            miners = data.get("miners", [])[:limit]
        
        if not miners:
            return [TextContent(type="text", text=json.dumps({"message": "No active miners", "count": 0}, indent=2))]
        
        # Parse miners
        result = []
        for m in miners:
            if isinstance(m, dict):
                result.append({
                    "miner_id": m.get("miner_id") or m.get("miner"),
                    "architecture": m.get("architecture") or m.get("cpu_arch"),
                    "last_attest": m.get("ts_ok") or m.get("last_attest_ts"),
                })
            else:
                result.append({"miner_id": str(m)})
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "rustchain_epoch":
        ok, data, err = http_get(f"{node}/epoch")
        
        if not ok:
            return [TextContent(type="text", text=f"Error: {err}")]
        
        return [TextContent(type="text", text=json.dumps(data, indent=2))]
    
    elif name == "rustchain_balance":
        miner_id = arguments.get("miner_id")
        if not miner_id:
            return [TextContent(type="text", text="Error: miner_id required")]
        
        url = f"{node}/wallet/balance?miner_id={urllib.parse.quote(miner_id)}"
        ok, data, err = http_get(url)
        
        if not ok:
            return [TextContent(type="text", text=f"Error: {err}")]
        
        return [TextContent(type="text", text=json.dumps(data, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
