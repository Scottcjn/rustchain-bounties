"""RustChain MCP Server implementation."""

import asyncio
import json
import httpx

DEFAULT_NODE_URL = "https://50.28.86.131"

TOOLS = [
    {"name": "rustchain_health", "description": "Check if RustChain node is healthy", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "rustchain_balance", "description": "Query wallet balance", "inputSchema": {"type": "object", "properties": {"wallet_id": {"type": "string"}}, "required": ["wallet_id"]}},
    {"name": "rustchain_miners", "description": "List active miners", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "rustchain_epoch", "description": "Get current epoch info", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "rustchain_create_wallet", "description": "Register a new wallet", "inputSchema": {"type": "object", "properties": {"wallet_id": {"type": "string"}}, "required": ["wallet_id"]}},
    {"name": "rustchain_bounties", "description": "List open bounties", "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 10}}}},
    {"name": "rustchain_submit_attestation", "description": "Submit hardware fingerprint attestation", "inputSchema": {"type": "object", "properties": {"fingerprint": {"type": "string"}, "hardware_info": {"type": "string"}}, "required": ["fingerprint"]}}
]

class RustChainServer:
    """RustChain MCP Server."""
    
    def __init__(self, node_url: str = DEFAULT_NODE_URL):
        self.node_url = node_url
    
    def list_tools(self):
        """List available tools."""
        return TOOLS
    
    async def call_tool(self, name: str, args: dict) -> str:
        """Handle tool call."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if name == "rustchain_health":
                    resp = await client.get(f"{self.node_url}/health")
                    return json.dumps(resp.json())
                elif name == "rustchain_balance":
                    resp = await client.get(f"{self.node_url}/wallet/balance", params={"wallet_id": args.get("wallet_id")})
                    return json.dumps(resp.json())
                elif name == "rustchain_miners":
                    resp = await client.get(f"{self.node_url}/miners")
                    return json.dumps(resp.json())
                elif name == "rustchain_epoch":
                    resp = await client.get(f"{self.node_url}/epoch")
                    return json.dumps(resp.json())
                elif name == "rustchain_create_wallet":
                    resp = await client.post(f"{self.node_url}/wallet/register", json={"wallet_id": args.get("wallet_id")})
                    return json.dumps(resp.json())
                elif name == "rustchain_bounties":
                    resp = await client.get(f"{self.node_url}/bounties", params={"state": "open", "limit": args.get("limit", 10)})
                    return json.dumps(resp.json())
                elif name == "rustchain_submit_attestation":
                    resp = await client.post(f"{self.node_url}/attestation/submit", json={"fingerprint": args.get("fingerprint"), "hardware_info": args.get("hardware_info", "")})
                    return json.dumps(resp.json())
                return json.dumps({"error": f"Unknown tool: {name}"})
            except Exception as e:
                return json.dumps({"error": str(e)})

async def main():
    """Main entry point."""
    server = RustChainServer()
    tools = server.list_tools()
    print(f"Loaded {len(tools)} tools")

if __name__ == "__main__":
    asyncio.run(main())