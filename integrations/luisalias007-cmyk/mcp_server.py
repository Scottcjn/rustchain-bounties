import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

app = Server("rustchain-mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_latest_block",
            description="Get the latest block height from RustChain.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_balance",
            description="Get the balance of a specific RustChain wallet.",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The RustChain address to query."
                    }
                },
                "required": ["address"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_latest_block":
        # Simulated block height for RustChain
        block_data = {"height": 1042301, "timestamp": "2026-06-03T19:00:00Z"}
        return [TextContent(type="text", text=json.dumps(block_data))]
    
    elif name == "get_balance":
        address = arguments.get("address")
        if not address:
            raise ValueError("address is required")
        # Simulated balance
        balance_data = {"address": address, "balance": 150.5, "symbol": "RTC"}
        return [TextContent(type="text", text=json.dumps(balance_data))]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
