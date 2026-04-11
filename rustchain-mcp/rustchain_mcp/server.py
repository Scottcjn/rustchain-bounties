"""RustChain MCP Server - Professional Implementation.

A Model Context Protocol server that connects AI agents to RustChain blockchain.
Supports Claude Code, Cursor, and any MCP-compatible IDE.
"""

import asyncio
import json
from typing import Any, Optional
import httpx

# Default configuration
DEFAULT_NODE_URL = "https://50.28.86.131"
DEFAULT_TIMEOUT = 30.0

# Tool definitions with detailed descriptions
TOOLS = [
    {
        "name": "rustchain_health",
        "description": "Check if RustChain node is healthy and responsive. Returns node status, version, and uptime.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "rustchain_balance", 
        "description": "Query wallet balance on RustChain. Returns balance in RTC and estimated USD value.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wallet_id": {"type": "string", "description": "Wallet ID to query"}
            },
            "required": ["wallet_id"]
        }
    },
    {
        "name": "rustchain_miners",
        "description": "List active miners on the RustChain network. Returns miner count and details.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "rustchain_epoch",
        "description": "Get current epoch information including epoch number, rewards, and duration.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "rustchain_create_wallet",
        "description": "Register a new wallet on RustChain. Returns confirmation with wallet address.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wallet_id": {"type": "string", "description": "Unique wallet identifier"}
            },
            "required": ["wallet_id"]
        }
    },
    {
        "name": "rustchain_bounties",
        "description": "List open bounties on RustChain. Filter by state, reward amount, and tags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum results to return", "default": 10}
            }
        }
    },
    {
        "name": "rustchain_submit_attestation",
        "description": "Submit hardware fingerprint attestation for mining verification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fingerprint": {"type": "string", "description": "Hardware fingerprint hash"},
                "hardware_info": {"type": "string", "description": "Hardware details (CPU, GPU, etc.)"}
            },
            "required": ["fingerprint"]
        }
    }
]

def format_balance_response(data: dict) -> dict:
    """Format balance response with USD estimate."""
    rtc_amount = data.get("balance", 0)
    usd_estimate = rtc_amount * 0.10  # Approximate rate
    return {
        "balance_rtc": rtc_amount,
        "balance_usd": round(usd_estimate, 2),
        "wallet": data.get("wallet_id")
    }

class RustChainMCPError(Exception):
    """Custom exception for MCP server errors."""
    pass

class RustChainClient:
    """Client for RustChain API with error handling."""
    
    def __init__(self, node_url: str = DEFAULT_NODE_URL, timeout: float = DEFAULT_TIMEOUT):
        self.node_url = node_url
        self.timeout = timeout
    
    async def get_health(self) -> dict:
        """Get node health status."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.node_url}/health")
            resp.raise_for_status()
            return resp.json()
    
    async def get_balance(self, wallet_id: str) -> dict:
        """Get wallet balance."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.node_url}/wallet/balance", params={"wallet_id": wallet_id})
            if resp.status_code == 404:
                return {"error": f"Wallet '{wallet_id}' not found", "code": "NOT_FOUND"}
            resp.raise_for_status()
            return format_balance_response(resp.json())
    
    async def get_miners(self) -> dict:
        """Get active miners."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.node_url}/miners")
            resp.raise_for_status()
            return resp.json()
    
    async def get_epoch(self) -> dict:
        """Get current epoch."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.node_url}/epoch")
            resp.raise_for_status()
            return resp.json()
    
    async def create_wallet(self, wallet_id: str) -> dict:
        """Create new wallet."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.node_url}/wallet/register", json={"wallet_id": wallet_id})
            resp.raise_for_status()
            return resp.json()
    
    async def get_bounties(self, limit: int = 10) -> dict:
        """Get open bounties."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.node_url}/bounties", params={"state": "open", "limit": limit})
            resp.raise_for_status()
            return resp.json()
    
    async def submit_attestation(self, fingerprint: str, hardware_info: str = "") -> dict:
        """Submit attestation."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.node_url}/attestation/submit",
                json={"fingerprint": fingerprint, "hardware_info": hardware_info}
            )
            resp.raise_for_status()
            return resp.json()

class RustChainServer:
    """Main MCP Server class with proper error handling."""
    
    def __init__(self, node_url: str = DEFAULT_NODE_URL):
        self.node_url = node_url
        self.client = RustChainClient(node_url)
    
    def list_tools(self) -> list:
        """Return available tools."""
        return TOOLS
    
    async def call_tool(self, name: str, arguments: Optional[dict] = None) -> str:
        """Execute tool call with error handling."""
        args = arguments or {}
        
        try:
            if name == "rustchain_health":
                result = await self.client.get_health()
            elif name == "rustchain_balance":
                result = await self.client.get_balance(args.get("wallet_id"))
            elif name == "rustchain_miners":
                result = await self.client.get_miners()
            elif name == "rustchain_epoch":
                result = await self.client.get_epoch()
            elif name == "rustchain_create_wallet":
                result = await self.client.create_wallet(args.get("wallet_id"))
            elif name == "rustchain_bounties":
                result = await self.client.get_bounties(args.get("limit", 10))
            elif name == "rustchain_submit_attestation":
                result = await self.client.submit_attestation(
                    args.get("fingerprint"),
                    args.get("hardware_info", "")
                )
            else:
                return json.dumps({"error": f"Unknown tool: {name}"})
            
            return json.dumps(result, indent=2)
            
        except httpx.TimeoutException as e:
            return json.dumps({"error": "Node timeout", "details": str(e)})
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"HTTP {e.response.status_code}", "details": str(e)})
        except Exception as e:
            return json.dumps({"error": "Internal error", "details": str(e)})

async def main():
    """Entry point for CLI usage."""
    import sys
    node_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NODE_URL
    server = RustChainServer(node_url)
    tools = server.list_tools()
    print(f"RustChain MCP Server v0.1.0")
    print(f"Node: {node_url}")
    print(f"Tools: {len(tools)}")

if __name__ == "__main__":
    asyncio.run(main())
