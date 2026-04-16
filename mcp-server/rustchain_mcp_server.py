#!/usr/bin/env python3
"""
RustChain MCP Server
Exposes RustChain blockchain operations as MCP tools for AI agents.

Usage:
    python rustchain_mcp_server.py

Compatible with: Claude Code, Cursor, Windsurf, any MCP client.
"""

import json
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

NODE_URL = "https://50.28.86.131"


def rpc_call(endpoint: str, method: str = "GET", data: Optional[dict] = None) -> dict:
    """Make RPC call to RustChain node."""
    url = f"{NODE_URL}{endpoint}"
    try:
        if method == "POST":
            req = urllib.request.Request(
                url,
                data=json.dumps(data or {}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


# MCP Protocol Implementation
TOOLS = [
    {
        "name": "rustchain_health",
        "description": "Check RustChain node health and status",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "rustchain_balance",
        "description": "Query wallet balance for an address",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Wallet address to check"
                }
            },
            "required": ["address"]
        }
    },
    {
        "name": "rustchain_miners",
        "description": "List active miners on the network",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "rustchain_block_height",
        "description": "Get current blockchain height",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "rustchain_tx_status",
        "description": "Check transaction status by hash",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tx_hash": {
                    "type": "string",
                    "description": "Transaction hash"
                }
            },
            "required": ["tx_hash"]
        }
    },
    {
        "name": "rustchain_transfer",
        "description": "Transfer RTC tokens to another address",
        "inputSchema": {
            "type": "object",
            "properties": {
                "from_address": {"type": "string", "description": "Sender address"},
                "to_address": {"type": "string", "description": "Recipient address"},
                "amount": {"type": "number", "description": "Amount of RTC to send"},
                "private_key": {"type": "string", "description": "Sender private key"},
                "memo": {"type": "string", "description": "Optional memo"}
            },
            "required": ["from_address", "to_address", "amount", "private_key"]
        }
    },
    {
        "name": "rustchain_recent_blocks",
        "description": "Get recent blocks from the chain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "number",
                    "description": "Number of blocks to retrieve (default 10)"
                }
            },
            "required": []
        }
    }
]


def handle_tool(name: str, args: dict) -> str:
    """Execute a tool and return result."""
    if name == "rustchain_health":
        result = rpc_call("/api/health")
        return json.dumps(result, indent=2)

    elif name == "rustchain_balance":
        addr = args.get("address", "")
        result = rpc_call(f"/api/balance/{addr}")
        return json.dumps(result, indent=2)

    elif name == "rustchain_miners":
        result = rpc_call("/api/miners")
        return json.dumps(result, indent=2)

    elif name == "rustchain_block_height":
        result = rpc_call("/api/block-height")
        return json.dumps(result, indent=2)

    elif name == "rustchain_tx_status":
        tx_hash = args.get("tx_hash", "")
        result = rpc_call(f"/api/tx/{tx_hash}")
        return json.dumps(result, indent=2)

    elif name == "rustchain_transfer":
        result = rpc_call("/api/transfer", method="POST", data={
            "from": args["from_address"],
            "to": args["to_address"],
            "amount": args["amount"],
            "private_key": args["private_key"],
            "memo": args.get("memo", "")
        })
        return json.dumps(result, indent=2)

    elif name == "rustchain_recent_blocks":
        count = args.get("count", 10)
        result = rpc_call(f"/api/blocks?count={count}")
        return json.dumps(result, indent=2)

    return json.dumps({"error": f"Unknown tool: {name}"})


def mcp_server():
    """Main MCP server loop - reads JSON-RPC from stdin, writes to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "rustchain-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS}
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            result_text = handle_tool(tool_name, tool_args)
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": result_text}]
                }
            }

        elif method == "notifications/initialized":
            continue  # No response needed

        else:
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    mcp_server()
