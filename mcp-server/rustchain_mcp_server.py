"""
RustChain MCP Server
====================
An MCP (Model Context Protocol) server for interacting with RustChain blockchain.

This server provides tools to:
- Check RTC balance for any wallet
- List active miners and their architectures
- Get current epoch info (slot, height, rewards)
- Check node health across all attestation nodes
- Send RTC transfers (requires wallet key)

Installation:
    pip install mcp requests
    
Usage with Claude Code:
    claude mcp add rustchain-mcp-server python /path/to/rustchain_mcp_server.py

Or run directly:
    python rustchain_mcp_server.py
"""

import json
import os
from typing import Any
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.server.handlers import ListToolsRequestHandler, CallToolRequestHandler

# RustChain node endpoints
NODES = [
    "https://50.28.86.131",  # Primary
]

class RustChainClient:
    """Client for interacting with RustChain nodes."""
    
    def __init__(self, node_url: str = None):
        self.node_url = node_url or NODES[0]
        self.timeout = 30
        
    def _request(self, endpoint: str, params: dict = None) -> dict:
        """Make a request to the RustChain node."""
        url = f"{self.node_url}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def health(self) -> dict:
        """Check node health."""
        return self._request("/health")
    
    def miners(self) -> dict:
        """List active miners and their architectures."""
        return self._request("/api/miners")
    
    def epoch(self) -> dict:
        """Get current epoch info (slot, height, rewards)."""
        return self._request("/epoch")
    
    def balance(self, miner_id: str) -> dict:
        """Check RTC balance for a wallet."""
        return self._request("/wallet/balance", {"miner_id": miner_id})
    
    def transfer(self, from_wallet: str, to_wallet: str, amount: float, admin_key: str = None) -> dict:
        """Send RTC transfer."""
        data = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount
        }
        if admin_key:
            data["admin_key"] = admin_key
        
        url = f"{self.node_url}/wallet/transfer"
        try:
            response = requests.post(url, json=data, timeout=self.timeout, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def ledger(self, wallet: str = None, limit: int = 100) -> dict:
        """Query transaction history."""
        params = {"limit": limit}
        if wallet:
            params["wallet"] = wallet
        return self._request("/wallet/ledger", params)
    
    def register_wallet(self, wallet_name: str) -> dict:
        """Create a new wallet."""
        return self._request("/wallet/register", {"name": wallet_name})
    
    def bounties(self) -> dict:
        """List open bounties with rewards."""
        return self._request("/api/bounties")


# Initialize the RustChain client
rc = RustChainClient()

# MCP Server setup
app = Server("rustchain-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="rustchain_health",
            description="Check RustChain node health across all attestation nodes",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="rustchain_miners",
            description="List active miners and their architectures",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="rustchain_epoch",
            description="Get current epoch info (slot, height, rewards)",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="rustchain_balance",
            description="Check RTC balance for any wallet",
            inputSchema={
                "type": "object",
                "properties": {
                    "miner_id": {
                        "type": "string",
                        "description": "Wallet name or miner ID to check balance for",
                    }
                },
                "required": ["miner_id"],
            }
        ),
        Tool(
            name="rustchain_transfer",
            description="Send RTC (requires wallet key)",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_wallet": {
                        "type": "string",
                        "description": "Source wallet name",
                    },
                    "to_wallet": {
                        "type": "string",
                        "description": "Destination wallet name",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount of RTC to send",
                    },
                    "admin_key": {
                        "type": "string",
                        "description": "Admin key for transfers (provided after review)",
                    },
                },
                "required": ["from_wallet", "to_wallet", "amount"],
            }
        ),
        Tool(
            name="rustchain_ledger",
            description="Query transaction history",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet": {
                        "type": "string",
                        "description": "Wallet to query (optional, returns all if not specified)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of transactions to return",
                        "default": 100,
                    },
                },
            }
        ),
        Tool(
            name="rustchain_register_wallet",
            description="Create a new wallet",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet_name": {
                        "type": "string",
                        "description": "Name for the new wallet",
                    }
                },
                "required": ["wallet_name"],
            }
        ),
        Tool(
            name="rustchain_bounties",
            description="List open bounties with rewards",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "rustchain_health":
            result = rc.health()
        elif name == "rustchain_miners":
            result = rc.miners()
        elif name == "rustchain_epoch":
            result = rc.epoch()
        elif name == "rustchain_balance":
            miner_id = arguments.get("miner_id")
            result = rc.balance(miner_id)
        elif name == "rustchain_transfer":
            result = rc.transfer(
                arguments.get("from_wallet"),
                arguments.get("to_wallet"),
                arguments.get("amount"),
                arguments.get("admin_key")
            )
        elif name == "rustchain_ledger":
            result = rc.ledger(
                arguments.get("wallet"),
                arguments.get("limit", 100)
            )
        elif name == "rustchain_register_wallet":
            result = rc.register_wallet(arguments.get("wallet_name"))
        elif name == "rustchain_bounties":
            result = rc.bounties()
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
