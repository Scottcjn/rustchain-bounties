#!/usr/bin/env python3
"""
RustChain MCP Server
Query the RustChain blockchain from Claude Code
"""

import json
import requests
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# RustChain Node Configuration
PRIMARY_NODE = "https://50.28.86.131"
NODES = [
    PRIMARY_NODE,
    "https://50.28.86.132",  # Node 2 (fallback)
    "https://50.28.86.133",  # Node 3 (fallback)
]

app = Server("rustchain-mcp")


def get_node_url() -> str:
    """Get working node URL with health check"""
    for node in NODES:
        try:
            resp = requests.get(f"{node}/health", timeout=3)
            if resp.status_code == 200:
                return node
        except:
            continue
    return PRIMARY_NODE  # Fallback to primary


def make_request(endpoint: str, params: dict = None) -> dict:
    """Make request to RustChain node"""
    node = get_node_url()
    url = f"{node}{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=10, verify=False)
        return {"success": True, "data": resp.json(), "node": node}
    except Exception as e:
        return {"success": False, "error": str(e), "node": node}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="rustchain_balance",
            description="Check RTC balance for any wallet",
            inputSchema={
                "type": "object",
                "properties": {
                    "miner_id": {"type": "string", "description": "Wallet name or miner ID"}
                },
                "required": ["miner_id"]
            }
        ),
        Tool(
            name="rustchain_miners",
            description="List active miners and their architectures",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="rustchain_epoch",
            description="Get current epoch info (slot, height, rewards)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="rustchain_health",
            description="Check node health across all 3 attestation nodes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="rustchain_transfer",
            description="Send RTC (requires wallet key)",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_wallet": {"type": "string", "description": "Sender wallet name"},
                    "to_wallet": {"type": "string", "description": "Recipient wallet name"},
                    "amount": {"type": "number", "description": "Amount in RTC"},
                    "memo": {"type": "string", "description": "Optional memo"}
                },
                "required": ["from_wallet", "to_wallet", "amount"]
            }
        ),
        # Bonus tools
        Tool(
            name="rustchain_ledger",
            description="Query transaction history",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet": {"type": "string", "description": "Wallet name (optional)"},
                    "limit": {"type": "number", "description": "Max transactions (default 50)"}
                }
            }
        ),
        Tool(
            name="rustchain_register_wallet",
            description="Create a new wallet",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet_name": {"type": "string", "description": "Desired wallet name"},
                    "public_key": {"type": "string", "description": "Public key (optional)"}
                },
                "required": ["wallet_name"]
            }
        ),
        Tool(
            name="rustchain_bounties",
            description="List open bounties with rewards",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    result = None
    
    if name == "rustchain_balance":
        miner_id = arguments.get("miner_id")
        result = make_request(f"/wallet/balance", {"miner_id": miner_id})
        
    elif name == "rustchain_miners":
        result = make_request("/api/miners")
        
    elif name == "rustchain_epoch":
        result = make_request("/epoch")
        
    elif name == "rustchain_health":
        health_results = {}
        for i, node in enumerate(NODES):
            try:
                resp = requests.get(f"{node}/health", timeout=3)
                health_results[f"node_{i+1}"] = {
                    "status": "healthy" if resp.status_code == 200 else "unhealthy",
                    "url": node
                }
            except Exception as e:
                health_results[f"node_{i+1}"] = {"status": "error", "error": str(e), "url": node}
        result = {"success": True, "nodes": health_results}
        
    elif name == "rustchain_transfer":
        from_wallet = arguments.get("from_wallet")
        to_wallet = arguments.get("to_wallet")
        amount = arguments.get("amount")
        memo = arguments.get("memo", "")
        result = make_request("/wallet/transfer", {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "memo": memo
        })
        
    elif name == "rustchain_ledger":
        wallet = arguments.get("wallet")
        limit = arguments.get("limit", 50)
        params = {"limit": limit}
        if wallet:
            params["wallet"] = wallet
        result = make_request("/api/ledger", params)
        
    elif name == "rustchain_register_wallet":
        wallet_name = arguments.get("wallet_name")
        public_key = arguments.get("public_key", "")
        result = make_request("/wallet/register", {
            "name": wallet_name,
            "public_key": public_key
        })
        
    elif name == "rustchain_bounties":
        result = make_request("/api/bounties")
        
    else:
        result = {"success": False, "error": f"Unknown tool: {name}"}
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Run the MCP server"""
    async with stdio_server() as server:
        server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
