#!/usr/bin/env python3
"""
RustChain MCP Server
A Model Context Protocol server for interacting with RustChain blockchain.
"""

import json
import urllib.request
import urllib.error
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl


# RustChain Node URLs
NODES = [
    "https://50.28.86.131",  # Primary
    "https://50.28.86.153",  # Beta
    "https://76.8.228.245",  # Gamma
]


def make_request(endpoint: str, timeout: int = 10) -> dict | None:
    """Make request to RustChain node with fallback."""
    for node in NODES:
        url = f"{node}{endpoint}"
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'RustChain-MCP/1.0')
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode())
        except Exception:
            continue
    return None


def rustchain_health() -> dict:
    """Check node health across all attestation nodes."""
    result = make_request("/health")
    if result:
        return {"status": "ok", "data": result, "node": "primary"}
    return {"status": "error", "message": "All nodes unreachable"}


def rustchain_miners() -> dict:
    """List active miners and their architectures."""
    result = make_request("/api/miners")
    if result:
        return {"status": "ok", "miners": result, "count": len(result.get("miners", []))}
    return {"status": "error", "message": "Failed to fetch miners"}


def rustchain_epoch() -> dict:
    """Get current epoch info."""
    result = make_request("/epoch")
    if result:
        return {"status": "ok", "epoch": result}
    return {"status": "error", "message": "Failed to fetch epoch"}


def rustchain_balance(miner_id: str) -> dict:
    """Check RTC balance for a wallet."""
    if not miner_id:
        return {"status": "error", "message": "miner_id is required"}
    result = make_request(f"/wallet/balance?miner_id={miner_id}")
    if result:
        return {"status": "ok", "miner_id": miner_id, "balance": result}
    return {"status": "error", "message": "Failed to fetch balance"}


def rustchain_transfer(wallet: str, to: str, amount: float, key: str) -> dict:
    """Send RTC to another wallet (requires admin key)."""
    if not all([wallet, to, amount, key]):
        return {"status": "error", "message": "wallet, to, amount, and key are required"}
    
    data = json.dumps({
        "wallet": wallet,
        "to": to,
        "amount": amount,
        "key": key
    }).encode()
    
    for node in NODES:
        url = f"{node}/wallet/transfer"
        try:
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=10) as response:
                return {"status": "ok", "tx": json.loads(response.read().decode())}
        except Exception as e:
            continue
    
    return {"status": "error", "message": "Transfer failed on all nodes"}


def rustchain_ledger(miner_id: str = None, limit: int = 50) -> dict:
    """Query transaction history."""
    endpoint = f"/wallet/ledger?limit={limit}"
    if miner_id:
        endpoint += f"&miner_id={miner_id}"
    result = make_request(endpoint)
    if result:
        return {"status": "ok", "transactions": result}
    return {"status": "error", "message": "Failed to fetch ledger"}


def rustchain_register_wallet(wallet_name: str) -> dict:
    """Register a new wallet."""
    data = json.dumps({"wallet": wallet_name}).encode()
    for node in NODES:
        url = f"{node}/wallet/register"
        try:
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=10) as response:
                return {"status": "ok", "result": json.loads(response.read().decode())}
        except Exception:
            continue
    return {"status": "error", "message": "Registration failed"}


def rustchain_bounties() -> dict:
    """List open bounties from rustchain-bounties repo."""
    # This would need GitHub API integration
    # Simplified for now
    return {
        "status": "ok",
        "message": "Visit https://github.com/Scottcjn/rustchain-bounties for open bounties"
    }


# MCP Server Setup
app = Server("rustchain-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="rustchain_health",
            description="Check node health across all RustChain attestation nodes",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="rustchain_miners",
            description="List active miners and their hardware architectures",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="rustchain_epoch",
            description="Get current epoch info including slot, height, and rewards",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="rustchain_balance",
            description="Check RTC balance for any wallet",
            inputSchema={
                "type": "object",
                "properties": {
                    "miner_id": {"type": "string", "description": "Wallet name to check"}
                },
                "required": ["miner_id"]
            }
        ),
        Tool(
            name="rustchain_transfer",
            description="Send RTC to another wallet (requires admin key)",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet": {"type": "string", "description": "Source wallet"},
                    "to": {"type": "string", "description": "Destination wallet"},
                    "amount": {"type": "number", "description": "Amount to send"},
                    "key": {"type": "string", "description": "Admin key for transfer"}
                },
                "required": ["wallet", "to", "amount", "key"]
            }
        ),
        Tool(
            name="rustchain_ledger",
            description="Query transaction history",
            inputSchema={
                "type": "object",
                "properties": {
                    "miner_id": {"type": "string", "description": "Filter by wallet (optional)"},
                    "limit": {"type": "integer", "description": "Max transactions (default 50)"}
                }
            }
        ),
        Tool(
            name="rustchain_register_wallet",
            description="Create a new wallet on RustChain",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet_name": {"type": "string", "description": "Desired wallet name"}
                },
                "required": ["wallet_name"]
            }
        ),
        Tool(
            name="rustchain_bounties",
            description="Get information about open bounties",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls."""
    try:
        if name == "rustchain_health":
            result = rustchain_health()
        elif name == "rustchain_miners":
            result = rustchain_miners()
        elif name == "rustchain_epoch":
            result = rustchain_epoch()
        elif name == "rustchain_balance":
            result = rustchain_balance(arguments.get("miner_id"))
        elif name == "rustchain_transfer":
            result = rustchain_transfer(
                arguments.get("wallet"),
                arguments.get("to"),
                arguments.get("amount"),
                arguments.get("key")
            )
        elif name == "rustchain_ledger":
            result = rustchain_ledger(
                arguments.get("miner_id"),
                arguments.get("limit", 50)
            )
        elif name == "rustchain_register_wallet":
            result = rustchain_register_wallet(arguments.get("wallet_name"))
        elif name == "rustchain_bounties":
            result = rustchain_bounties()
        else:
            result = {"status": "error", "message": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}))]


async def main():
    """Main entry point."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
