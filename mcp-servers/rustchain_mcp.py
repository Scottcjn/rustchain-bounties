#!/usr/bin/env python3
"""
RustChain MCP Server — Query the RustChain blockchain from Claude Code.

Install: pip install mcp httpx
Add to Claude: claude mcp add rustchain python /path/to/rustchain_mcp.py
"""

import json
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# RustChain nodes (failover)
NODES = [
    "https://50.28.86.131",
    "https://rustchain-node2.example.com",  # Update when available
    "https://rustchain-node3.example.com",  # Update when available
]

app = Server("rustchain")


async def api_call(endpoint: str, params: dict = None) -> dict:
    """Make API call with failover to backup nodes."""
    for node in NODES:
        try:
            async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
                url = f"{node}{endpoint}"
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            continue
    return {"error": "All nodes unreachable"}


@app.list_tools()
async def list_tools():
    return [
        # Required tools (75 RTC)
        Tool(
            name="rustchain_balance",
            description="Check RTC balance for any wallet/miner",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet_id": {
                        "type": "string",
                        "description": "Wallet or miner ID to check balance for"
                    }
                },
                "required": ["wallet_id"]
            }
        ),
        Tool(
            name="rustchain_miners",
            description="List active miners with their hardware info and last attestation",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max number of miners to return (default: 20)"
                    }
                }
            }
        ),
        Tool(
            name="rustchain_epoch",
            description="Get current epoch info: slot, height, rewards, supply",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="rustchain_health",
            description="Check node health across attestation nodes",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="rustchain_transfer",
            description="Prepare RTC transfer (returns unsigned transaction)",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_wallet": {
                        "type": "string",
                        "description": "Source wallet ID"
                    },
                    "to_wallet": {
                        "type": "string",
                        "description": "Destination wallet ID"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount of RTC to transfer"
                    }
                },
                "required": ["from_wallet", "to_wallet", "amount"]
            }
        ),
        # Bonus tools (100 RTC)
        Tool(
            name="rustchain_ledger",
            description="Query recent transaction history",
            inputSchema={
                "type": "object",
                "properties": {
                    "wallet_id": {
                        "type": "string",
                        "description": "Filter by wallet ID (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max transactions to return (default: 10)"
                    }
                }
            }
        ),
        Tool(
            name="rustchain_register_wallet",
            description="Generate info for creating a new RustChain wallet",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Desired wallet name/identifier"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="rustchain_bounties",
            description="List open RustChain bounties from GitHub",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max bounties to return (default: 10)"
                    }
                }
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    
    if name == "rustchain_balance":
        wallet_id = arguments.get("wallet_id", "")
        data = await api_call("/wallet/balance", {"miner_id": wallet_id})
        if "error" in data:
            return [TextContent(type="text", text=f"Error: {data['error']}")]
        return [TextContent(
            type="text",
            text=f"💰 Wallet: {data.get('miner_id', wallet_id)}\n"
                 f"   Balance: {data.get('amount_rtc', 0):.4f} RTC"
        )]
    
    elif name == "rustchain_miners":
        limit = arguments.get("limit", 20)
        data = await api_call("/api/miners")
        if isinstance(data, dict) and "error" in data:
            return [TextContent(type="text", text=f"Error: {data['error']}")]
        
        miners = data[:limit] if isinstance(data, list) else []
        lines = ["⛏️ Active Miners:\n"]
        for m in miners:
            lines.append(
                f"• {m.get('miner', 'unknown')}\n"
                f"  Hardware: {m.get('hardware_type', 'unknown')}\n"
                f"  Multiplier: {m.get('antiquity_multiplier', 1.0)}x\n"
            )
        return [TextContent(type="text", text="\n".join(lines))]
    
    elif name == "rustchain_epoch":
        data = await api_call("/epoch")
        if "error" in data:
            return [TextContent(type="text", text=f"Error: {data['error']}")]
        return [TextContent(
            type="text",
            text=f"📊 RustChain Epoch Info:\n"
                 f"   Epoch: {data.get('epoch', '?')}\n"
                 f"   Slot: {data.get('slot', '?')}\n"
                 f"   Blocks/Epoch: {data.get('blocks_per_epoch', '?')}\n"
                 f"   Epoch Pot: {data.get('epoch_pot', '?')} RTC\n"
                 f"   Total Supply: {data.get('total_supply_rtc', '?'):,} RTC\n"
                 f"   Enrolled Miners: {data.get('enrolled_miners', '?')}"
        )]
    
    elif name == "rustchain_health":
        data = await api_call("/health")
        if "error" in data:
            return [TextContent(type="text", text=f"Error: {data['error']}")]
        
        status = "✅ Healthy" if data.get("ok") else "❌ Unhealthy"
        return [TextContent(
            type="text",
            text=f"🏥 Node Health: {status}\n"
                 f"   Version: {data.get('version', '?')}\n"
                 f"   Uptime: {data.get('uptime_s', 0) / 3600:.1f} hours\n"
                 f"   DB R/W: {'✅' if data.get('db_rw') else '❌'}\n"
                 f"   Tip Age: {data.get('tip_age_slots', '?')} slots\n"
                 f"   Backup Age: {data.get('backup_age_hours', '?'):.1f} hours"
        )]
    
    elif name == "rustchain_transfer":
        # Note: Actual transfer requires wallet key signing
        # This prepares the transaction info
        from_w = arguments.get("from_wallet", "")
        to_w = arguments.get("to_wallet", "")
        amount = arguments.get("amount", 0)
        
        # Check source balance
        balance_data = await api_call("/wallet/balance", {"miner_id": from_w})
        current = balance_data.get("amount_rtc", 0)
        
        if current < amount:
            return [TextContent(
                type="text",
                text=f"❌ Insufficient balance\n"
                     f"   Available: {current:.4f} RTC\n"
                     f"   Requested: {amount:.4f} RTC"
            )]
        
        return [TextContent(
            type="text",
            text=f"📝 Transfer Prepared:\n"
                 f"   From: {from_w}\n"
                 f"   To: {to_w}\n"
                 f"   Amount: {amount:.4f} RTC\n\n"
                 f"⚠️ Note: Actual transfer requires wallet key.\n"
                 f"   Use the RustChain CLI or web interface to sign and submit."
        )]
    
    elif name == "rustchain_ledger":
        # Query recent transfers (if endpoint exists)
        wallet_id = arguments.get("wallet_id")
        limit = arguments.get("limit", 10)
        
        # Try ledger endpoint
        params = {"limit": limit}
        if wallet_id:
            params["wallet"] = wallet_id
        
        data = await api_call("/api/ledger", params)
        if isinstance(data, dict) and "error" in data:
            # Fallback: return epoch rewards info
            epoch_data = await api_call("/epoch")
            return [TextContent(
                type="text",
                text=f"📜 Ledger query not available via API.\n"
                     f"   Epoch pot (current rewards): {epoch_data.get('epoch_pot', '?')} RTC\n"
                     f"   Check block explorer for full transaction history."
            )]
        
        return [TextContent(type="text", text=f"📜 Recent transactions:\n{json.dumps(data, indent=2)}")]
    
    elif name == "rustchain_register_wallet":
        name_arg = arguments.get("name", "new-wallet")
        return [TextContent(
            type="text",
            text=f"🆕 Wallet Registration:\n"
                 f"   Suggested ID: {name_arg}\n\n"
                 f"To register a wallet:\n"
                 f"1. Generate a keypair (ed25519)\n"
                 f"2. Start mining to register automatically\n"
                 f"3. Or use: curl -X POST {NODES[0]}/wallet/register -d '{{\"name\": \"{name_arg}\"}}'\n\n"
                 f"💡 Wallets are created automatically when you start mining with a new ID."
        )]
    
    elif name == "rustchain_bounties":
        limit = arguments.get("limit", 10)
        # Fetch from GitHub API
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(
                    "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues",
                    params={"labels": "bounty", "state": "open", "per_page": limit}
                )
                if resp.status_code == 200:
                    issues = resp.json()
                    lines = ["🎯 Open RustChain Bounties:\n"]
                    for issue in issues:
                        title = issue.get("title", "")
                        url = issue.get("html_url", "")
                        lines.append(f"• {title}\n  {url}\n")
                    return [TextContent(type="text", text="\n".join(lines))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error fetching bounties: {e}")]
        
        return [TextContent(type="text", text="Could not fetch bounties from GitHub")]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
