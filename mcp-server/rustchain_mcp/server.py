"""
RustChain MCP Server
====================
Exposes RustChain as MCP tools for Claude Code, Cursor, Windsurf, and any MCP-compatible IDE.

Install:
    pip install rustchain-mcp

Configure your MCP client (Claude Code, Cursor, etc.):
{
  "mcpServers": {
    "rustchain": {
      "command": "python",
      "args": ["-m", "rustchain_mcp"]
    }
  }
}
"""

import os
import json
import http.client
from typing import Any, Optional

# MCP Server
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

NODE_URL = os.environ.get("RUSTCHAIN_NODE_URL", "https://50.28.86.131")
PORT = int(os.environ.get("RUSTCHAIN_MCP_PORT", "3000"))


def api_get(path: str) -> Optional[dict]:
    """Make HTTPS GET request to RustChain node."""
    url = NODE_URL.replace("https://", "").replace("http://", "")
    is_https = NODE_URL.startswith("https")
    host = url.split("/")[0]
    path_full = "/" + "/".join(url.split("/")[1:]) + "/" + path if len(url.split("/")) > 1 else "/" + path
    if path_full == "//" + path:
        path_full = "/" + path

    try:
        if is_https:
            conn = http.client.HTTPSConnection(host, timeout=10)
        else:
            conn = http.client.HTTPConnection(host, timeout=10)
        conn.request("GET", path_full, headers={"Accept": "application/json"})
        resp = conn.getresponse()
        data = resp.read().decode()
        conn.close()
        if resp.status == 200:
            return json.loads(data)
    except Exception:
        pass
    return None


def api_gh_get(path: str) -> Optional[dict]:
    """Make HTTPS GET request to GitHub API."""
    try:
        conn = http.client.HTTPSConnection("api.github.com", timeout=10)
        conn.request("GET", path, headers={
            "Accept": "application/json",
            "User-Agent": "RustChain-MCP/1.0"
        })
        resp = conn.getresponse()
        data = resp.read().decode()
        conn.close()
        if resp.status == 200:
            return json.loads(data)
    except Exception:
        pass
    return None


# ── Tool Definitions ───────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "rustchain_health",
        "description": "Check RustChain node health and status",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "rustchain_balance",
        "description": "Query RTC wallet balance for a given wallet name",
        "inputSchema": {
            "type": "object",
            "properties": {"wallet": {"type": "string", "description": "Wallet/miner name (e.g. 'nox-ventures')"}},
            "required": ["wallet"]
        }
    },
    {
        "name": "rustchain_miners",
        "description": "List all active miners on the RustChain network",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "Max miners to return (default 10)"}},
            "required": []
        }
    },
    {
        "name": "rustchain_epoch",
        "description": "Get current epoch number and time to next settlement",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "rustchain_bounties",
        "description": "List all open RustChain bounty issues from GitHub",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "Max bounties to return (default 10)"}},
            "required": []
        }
    },
    {
        "name": "rustchain_network_stats",
        "description": "Get overall RustChain network statistics",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    }
]


async def rustchain_health() -> str:
    data = api_get("/health")
    if data:
        return json.dumps({
            "status": "online" if data.get("ok") else "offline",
            "version": data.get("version", "unknown"),
            "uptime_hours": round(data.get("uptime_s", 0) / 3600, 1),
            "node_url": NODE_URL
        }, indent=2)
    return '{"status": "error", "message": "Could not reach node"}'


async def rustchain_balance(wallet: str) -> str:
    data = api_get(f"/wallet/balance?wallet_id={wallet}")
    if data:
        return json.dumps({
            "wallet": wallet,
            "balance": data.get("amount_rtc", data.get("balance", 0)),
            "unit": "RTC"
        }, indent=2)
    return json.dumps({"error": f"Could not fetch balance for {wallet}"})


async def rustchain_miners(limit: int = 10) -> str:
    data = api_get("/api/miners")
    if data:
        miners = data.get("miners", [])[:limit]
        return json.dumps({
            "total": len(data.get("miners", [])),
            "returned": len(miners),
            "miners": [{
                "name": m.get("miner"),
                "active": m.get("is_active"),
                "antiquity": m.get("antiquity_multiplier", 0),
                "hardware": m.get("hardware_type")
            } for m in miners]
        }, indent=2)
    return json.dumps({"error": "Could not fetch miners"})


async def rustchain_epoch() -> str:
    data = api_get("/health")
    if data:
        uptime_s = data.get("uptime_s", 0)
        EPOCH_LENGTH = 2016
        SLOT_TIME_S = 15
        slots_elapsed = uptime_s / SLOT_TIME_S
        epoch = int(slots_elapsed / EPOCH_LENGTH)
        slot_in_epoch = int(slots_elapsed % EPOCH_LENGTH)
        remaining = EPOCH_LENGTH - slot_in_epoch
        remaining_s = remaining * SLOT_TIME_S
        h = int(remaining_s // 3600)
        m = int((remaining_s % 3600) // 60)
        return json.dumps({
            "current_epoch": epoch,
            "slots_in_epoch": slot_in_epoch,
            "slots_remaining": remaining,
            "time_to_next_epoch": f"{h}h {m}m" if h > 0 else f"{m}m",
            "uptime_seconds": uptime_s
        }, indent=2)
    return json.dumps({"error": "Could not fetch epoch"})


async def rustchain_bounties(limit: int = 10) -> str:
    data = api_gh_get("/repos/Scottcjn/rustchain-bounties/issues?state=open&labels=bounty&per_page=50")
    if data:
        bounties = [{
            "number": issue.get("number"),
            "title": issue.get("title", ""),
            "url": issue.get("html_url")
        } for issue in data[:limit]]
        return json.dumps({"count": len(bounties), "bounties": bounties}, indent=2)
    return json.dumps({"error": "Could not fetch bounties"})


async def rustchain_network_stats() -> str:
    health = api_get("/health")
    miners = api_get("/api/miners")
    miner_list = miners.get("miners", []) if miners else []
    return json.dumps({
        "node": {
            "url": NODE_URL,
            "online": health.get("ok", False) if health else False,
            "version": (health.get("version") if health else None)
        },
        "network": {
            "active_miners": len(miner_list),
            "top_antiquity": max([m.get("antiquity_multiplier", 0) for m in miner_list], default=0)
        }
    }, indent=2)


TOOL_HANDLERS = {
    "rustchain_health": lambda _: rustchain_health(),
    "rustchain_balance": lambda p: rustchain_balance(p.get("wallet", "")),
    "rustchain_miners": lambda p: rustchain_miners(p.get("limit", 10)),
    "rustchain_epoch": lambda _: rustchain_epoch(),
    "rustchain_bounties": lambda p: rustchain_bounties(p.get("limit", 10)),
    "rustchain_network_stats": lambda _: rustchain_network_stats()
}


if MCP_AVAILABLE:
    app = Server("rustchain-mcp")

    @app.list_tools()
    async def list_tools():
        return [Tool(name=t["name"], description=t["description"], inputSchema=t["inputSchema"]) for t in TOOLS]

    @app.call_tool()
    async def call_tool(name: str, arguments: Any):
        handler = TOOL_HANDLERS.get(name)
        if handler:
            result = await handler(arguments)
            return [TextContent(type="text", text=result)]
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

else:
    # Fallback: run as simple HTTP server
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path.strip("/")
            if path == "health":
                data = api_get("/health")
            elif path == "miners":
                data = api_get("/api/miners")
            elif path.startswith("balance/"):
                wallet = path.split("/", 1)[1]
                data = api_get(f"/wallet/balance?wallet_id={wallet}")
            elif path == "epoch":
                data = api_get("/health")
                if data:
                    uptime_s = data.get("uptime_s", 0)
                    EPOCH_LENGTH, SLOT_TIME_S = 2016, 15
                    slots_elapsed = uptime_s / SLOT_TIME_S
                    epoch = int(slots_elapsed / EPOCH_LENGTH)
                    slot_in_epoch = int(slots_elapsed % EPOCH_LENGTH)
                    remaining = EPOCH_LENGTH - slot_in_epoch
                    data = {"current_epoch": epoch, "slots_elapsed": slot_in_epoch, "slots_remaining": remaining}
            elif path == "stats":
                health = api_get("/health")
                miners = api_get("/api/miners")
                data = {"node": health, "total_miners": len(miners.get("miners", []) if miners else [])}
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "not found"}')
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())

        def log_message(self, fmt, *args):
            pass

    def main():
        print(f"RustChain MCP Server running on http://0.0.0.0:{PORT}")
        server = HTTPServer(("0.0.0.0", PORT), Handler)
        server.serve_forever()


if __name__ == "__main__":
    import asyncio
    if MCP_AVAILABLE:
        asyncio.run(main())
    else:
        main()
