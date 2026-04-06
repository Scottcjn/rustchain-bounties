#!/usr/bin/env python3
"""
RustChain MCP Tool - Wallet Balance Checker

A simple MCP tool that queries RTC wallet balance from RustChain blockchain.
Task: #1602 - Create an MCP tool that interacts with RustChain
Value: 5 RTC
"""

import json
import sys
import ssl
import urllib.request
import urllib.error

# Disable SSL verification for self-signed certificates
ssl._create_default_https_context = ssl._create_unverified_context

def get_wallet_balance(miner_id: str) -> dict:
    """Query RTC wallet balance from RustChain API."""
    url = f"https://50.28.86.131/wallet/balance?miner_id={miner_id}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return {
                "success": True,
                "miner_id": data.get("miner_id", miner_id),
                "balance_rtc": data.get("amount_rtc", 0),
                "balance_i64": data.get("amount_i64", 0),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def mcp_tool_definition() -> dict:
    """Return MCP tool definition schema."""
    return {
        "name": "rustchain_balance",
        "description": "Query RTC wallet balance from RustChain blockchain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "miner_id": {"type": "string", "description": "RustChain miner ID"}
            },
            "required": ["miner_id"]
        }
    }

def execute_tool(args: dict) -> str:
    """Execute the MCP tool and return result."""
    miner_id = args.get("miner_id", "")
    if not miner_id:
        return json.dumps({"error": "miner_id is required"})
    return json.dumps(get_wallet_balance(miner_id), indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rustchain_balance_tool.py <miner_id>")
        print(json.dumps(mcp_tool_definition(), indent=2))
        sys.exit(1)
    print(execute_tool({"miner_id": sys.argv[1]}))
