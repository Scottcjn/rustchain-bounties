import os
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Create FastMCP server
mcp = FastMCP("rustchain-mcp")

BASE_URL = "https://50.28.86.131"

async def fetch_api(endpoint: str, params: dict = None, method: str = "GET", data: dict = None):
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = await client.get(url, params=params)
        else:
            response = await client.post(url, json=data)
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def health() -> str:
    """Check the health of the RustChain node."""
    try:
        data = await fetch_api("/health")
        return f"Health Status: {data}"
    except Exception as e:
        return f"Error checking health: {str(e)}"

@mcp.tool()
async def miners() -> str:
    """Get the current list of active miners on RustChain."""
    try:
        data = await fetch_api("/miners")
        return f"Miners: {data}"
    except Exception as e:
        return f"Error fetching miners: {str(e)}"

@mcp.tool()
async def epoch() -> str:
    """Get the current epoch information from RustChain."""
    try:
        data = await fetch_api("/epoch")
        return f"Epoch: {data}"
    except Exception as e:
        return f"Error fetching epoch: {str(e)}"

@mcp.tool()
async def balance(address: str) -> str:
    """Get the RTC balance of a specific wallet address."""
    try:
        data = await fetch_api(f"/balance/{address}")
        return f"Balance for {address}: {data}"
    except Exception as e:
        return f"Error fetching balance: {str(e)}"

@mcp.tool()
async def transfer(sender: str, recipient: str, amount: float, signature: str) -> str:
    """Transfer RTC from one wallet to another."""
    payload = {
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
        "signature": signature
    }
    try:
        data = await fetch_api("/transfer", method="POST", data=payload)
        return f"Transfer successful: {data}"
    except Exception as e:
        return f"Error transferring RTC: {str(e)}"

if __name__ == "__main__":
    mcp.run()
