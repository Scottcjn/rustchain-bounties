"""
RustChain MCP Server
A Model Context Protocol server for interacting with RustChain blockchain.
"""

import json
import requests
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# RustChain node endpoints
NODES = [
    "https://50.28.86.131",
    "https://node2.rustchain.org",
    "https://node3.rustchain.org",
]


def get_node_url() -> str:
    """Get the primary node URL."""
    return NODES[0]


def make_request(endpoint: str, params: dict = None) -> dict:
    """Make a request to the RustChain node with fallback."""
    for node in NODES:
        try:
            url = f"{node}{endpoint}"
            response = requests.get(url, params=params, timeout=10, verify=False)
            if response.status_code == 200:
                return response.json()
        except Exception:
            continue
    raise Exception(f"Failed to connect to any RustChain node")


# MCP Server setup
app = Server("rustchain-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="rustchain_health",
            description="Check the health status of all RustChain attestation nodes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="rustchain_balance",
            description="Check the RTC balance for any wallet address",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet": {
                        "type": "string",
                        "description": "Wallet name or address to check balance for"
                    }
                },
                "required": ["wallet"]
            }
        ),
        Tool(
            name="rustchain_miners",
            description="List active miners and their hardware architectures",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of miners to return",
                        "default": 20
                    }
                }
            }
        ),
        Tool(
            name="rustchain_epoch",
            description="Get current epoch information including slot, height, and rewards",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="rustchain_ledger",
            description="Query transaction history for a wallet",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet": {
                        "type": "string",
                        "description": "Wallet name to query ledger for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of transactions to return",
                        "default": 10
                    }
                },
                "required": ["wallet"]
            }
        ),
        Tool(
            name="rustchain_bounties",
            description="List open RustChain bounties with their rewards",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of bounties to return",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="rustchain_register_wallet",
            description="Register a new wallet on RustChain",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet_name": {
                        "type": "string",
                        "description": "Desired wallet name"
                    }
                },
                "required": ["wallet_name"]
            }
        ),
        Tool(
            name="rustchain_transfer",
            description="Transfer RTC to another wallet (requires private key)",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_wallet": {
                        "type": "string",
                        "description": "Sender wallet name"
                    },
                    "to_wallet": {
                        "type": "string",
                        "description": "Recipient wallet name"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount of RTC to transfer"
                    },
                    "private_key": {
                        "type": "string",
                        "description": "Private key for signing (will be used locally)"
                    }
                },
                "required": ["from_wallet", "to_wallet", "amount", "private_key"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls."""
    try:
        if name == "rustchain_health":
            result = make_request("/health")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "rustchain_balance":
            wallet = arguments.get("wallet")
            result = make_request("/wallet/balance", {"miner_id": wallet})
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "rustchain_miners":
            limit = arguments.get("limit", 20)
            result = make_request("/api/miners", {"limit": limit})
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "rustchain_epoch":
            result = make_request("/epoch")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "rustchain_ledger":
            wallet = arguments.get("wallet")
            limit = arguments.get("limit", 10)
            result = make_request("/wallet/ledger", {"miner_id": wallet, "limit": limit})
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "rustchain_bounties":
            limit = arguments.get("limit", 10)
            result = make_request("/agent/jobs", {"limit": limit})
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "rustchain_register_wallet":
            wallet_name = arguments.get("wallet_name")
            # This would require a POST request with wallet creation
            result = {"status": "error", "message": "Wallet registration requires wallet creation via the RustChain wallet module"}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "rustchain_transfer":
            # This would require signing and submitting a transaction
            result = {"status": "error", "message": "Transfer requires signing via RustChain wallet crypto module"}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


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
