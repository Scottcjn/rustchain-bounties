import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("RustChain")

PRIMARY_NODE = "https://50.28.86.131"

@mcp.tool()
async def rustchain_balance(wallet_name: str) -> str:
    """Check RTC balance for any wallet."""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(f"{PRIMARY_NODE}/wallet/balance?miner_id={wallet_name}")
        return response.text

@mcp.tool()
async def rustchain_miners() -> str:
    """List active miners and their architectures."""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(f"{PRIMARY_NODE}/api/miners")
        return response.text

@mcp.tool()
async def rustchain_epoch() -> str:
    """Get current epoch info (slot, height, rewards)."""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(f"{PRIMARY_NODE}/epoch")
        return response.text

@mcp.tool()
async def rustchain_health() -> str:
    """Check node health across all attestation nodes."""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(f"{PRIMARY_NODE}/health")
        return response.text

if __name__ == "__main__":
    mcp.run()
