"""
RustChain MCP Server
Model Context Protocol server for RustChain
Publish to PyPI: pip install rustchain-mcp
"""

import json
import os
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import requests

# Configuration
NODE_URL = os.environ.get("RUSTCHAIN_NODE_URL", "https://50.28.86.131")
SERVER_NAME = "rustchain-mcp"
SERVER_VERSION = "1.0.0"

# Create server
server = Server(SERVER_NAME, SERVER_VERSION)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="rustchain_health",
            description="Check if RustChain node is healthy",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="rustchain_balance",
            description="Query wallet balance on RustChain",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet": {"type": "string", "description": "Wallet name to query"}
                },
                "required": ["wallet"]
            }
        ),
        Tool(
            name="rustchain_miners",
            description="List active miners on RustChain",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "description": "Max miners to return (default 10)"}
                }
            }
        ),
        Tool(
            name="rustchain_epoch",
            description="Get current epoch information",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="rustchain_bounties",
            description="List open RustChain bounties",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "description": "Max bounties to return (default 10)"}
                }
            }
        ),
        Tool(
            name="rustchain_create_wallet",
            description="Register a new agent wallet on RustChain",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet_name": {"type": "string", "description": "Name for the new wallet"}
                },
                "required": ["wallet_name"]
            }
        ),
        Tool(
            name="rustchain_submit_attestation",
            description="Submit hardware fingerprint attestation",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet": {"type": "string", "description": "Wallet name"},
                    "fingerprint": {"type": "string", "description": "Hardware fingerprint payload"}
                },
                "required": ["wallet", "fingerprint"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "rustchain_health":
        try:
            resp = requests.get(f"{NODE_URL}/health", timeout=10)
            resp.raise_for_status()
            return [TextContent(type="text", text=json.dumps(resp.json(), indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "rustchain_balance":
        wallet = arguments.get("wallet")
        if not wallet:
            return [TextContent(type="text", text="Error: wallet parameter required")]
        try:
            resp = requests.get(f"{NODE_URL}/wallet/balance", params={"wallet_id": wallet}, timeout=10)
            resp.raise_for_status()
            return [TextContent(type="text", text=json.dumps(resp.json(), indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "rustchain_miners":
        limit = arguments.get("limit", 10)
        try:
            resp = requests.get(f"{NODE_URL}/api/miners", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            miners = data.get("miners", [])[:limit]
            return [TextContent(type="text", text=json.dumps(miners, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "rustchain_epoch":
        try:
            resp = requests.get(f"{NODE_URL}/epoch", timeout=10)
            resp.raise_for_status()
            return [TextContent(type="text", text=json.dumps(resp.json(), indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "rustchain_bounties":
        limit = arguments.get("limit", 10)
        try:
            resp = requests.get(
                "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues",
                params={"state": "open", "per_page": limit},
                timeout=10
            )
            resp.raise_for_status()
            issues = resp.json()
            bounties = [
                {"number": i["number"], "title": i["title"], "url": i["html_url"]}
                for i in issues
                if "BOUNTY" in i.get("title", "").upper()
            ]
            return [TextContent(type="text", text=json.dumps(bounties, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "rustchain_create_wallet":
        wallet_name = arguments.get("wallet_name")
        if not wallet_name:
            return [TextContent(type="text", text="Error: wallet_name required")]
        try:
            resp = requests.post(
                f"{NODE_URL}/wallet/create",
                json={"name": wallet_name},
                timeout=10
            )
            resp.raise_for_status()
            return [TextContent(type="text", text=json.dumps(resp.json(), indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "rustchain_submit_attestation":
        wallet = arguments.get("wallet")
        fingerprint = arguments.get("fingerprint")
        if not wallet or not fingerprint:
            return [TextContent(type="text", text="Error: wallet and fingerprint required")]
        try:
            resp = requests.post(
                f"{NODE_URL}/attest/submit",
                json={"wallet": wallet, "fingerprint": fingerprint},
                timeout=10
            )
            resp.raise_for_status()
            return [TextContent(type="text", text=json.dumps(resp.json(), indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
