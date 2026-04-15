#!/usr/bin/env python3
"""
rustchain-mcp: Model Context Protocol server for RustChain
Connects any AI agent (Claude Code, Cursor, Windsurf) to RustChain
Bounty #2859 | Wallet: TestAutomaton (RTC)
"""
import json
import sys
import os
import urllib.request
import urllib.error
from typing import Any

NODE_URL = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")

def node_get(path: str, timeout: int = 10) -> dict:
    """Make GET request to RustChain node."""
    try:
        req = urllib.request.Request(
            f"{NODE_URL}{path}",
            headers={"User-Agent": "rustchain-mcp/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}

def node_post(path: str, data: dict, timeout: int = 10) -> dict:
    """Make POST request to RustChain node."""
    try:
        body = json.dumps(data).encode()
        req = urllib.request.Request(
            f"{NODE_URL}{path}",
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": "rustchain-mcp/1.0"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
            return {"error": f"HTTP {e.code}", "detail": body}
        except Exception:
            return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}

# MCP protocol handlers

def handle_initialize(params: dict) -> dict:
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "rustchain-mcp", "version": "1.0.0"}
    }

def handle_tools_list(params: dict) -> dict:
    return {
        "tools": [
            {
                "name": "rustchain_health",
                "description": "Check RustChain node health and sync status",
                "inputSchema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "rustchain_balance",
                "description": "Query RTC wallet balance for a given address",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string", "description": "RTC wallet address (starts with RTC...)"}
                    },
                    "required": ["address"]
                }
            },
            {
                "name": "rustchain_miners",
                "description": "List active RustChain miners with their hardware profiles and mining stats",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max miners to return (default: 20)"}
                    },
                    "required": []
                }
            },
            {
                "name": "rustchain_epoch",
                "description": "Get current epoch info: epoch number, block height, enrolled miners, rewards",
                "inputSchema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "rustchain_create_wallet",
                "description": "Register a new RTC agent wallet. Returns wallet address and keys.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Name for the agent wallet"}
                    },
                    "required": []
                }
            },
            {
                "name": "rustchain_submit_attestation",
                "description": "Submit hardware fingerprint attestation to RustChain (required for mining rewards)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "miner_pk": {"type": "string", "description": "Miner public key"},
                        "hardware_info": {"type": "object", "description": "Hardware details: cpu, memory, arch"}
                    },
                    "required": ["miner_pk"]
                }
            },
            {
                "name": "rustchain_bounties",
                "description": "List open RustChain bounties from GitHub with reward amounts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "description": "Filter by label (e.g. 'easy', 'major')"},
                        "limit": {"type": "integer", "description": "Max bounties to return (default: 10)"}
                    },
                    "required": []
                }
            }
        ]
    }

def handle_tool_call(name: str, arguments: dict) -> dict:
    if name == "rustchain_health":
        result = node_get("/")
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "rustchain_balance":
        addr = arguments.get("address", "")
        if not addr:
            return {"content": [{"type": "text", "text": "Error: address is required"}], "isError": True}
        result = node_get(f"/balance/{addr}")
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "rustchain_miners":
        limit = arguments.get("limit", 20)
        result = node_get(f"/miners?limit={limit}")
        if isinstance(result, list):
            result = {"miners": result, "count": len(result)}
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "rustchain_epoch":
        result = node_get("/epoch")
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "rustchain_create_wallet":
        agent_name = arguments.get("agent_name", "agent")
        result = node_post("/wallet/create", {"name": agent_name})
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "rustchain_submit_attestation":
        miner_pk = arguments.get("miner_pk", "")
        hw = arguments.get("hardware_info", {})
        if not miner_pk:
            return {"content": [{"type": "text", "text": "Error: miner_pk is required"}], "isError": True}
        payload = {"miner_pubkey": miner_pk, **hw}
        result = node_post("/attest", payload)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    elif name == "rustchain_bounties":
        import urllib.parse
        label = arguments.get("label", "bounty")
        limit = arguments.get("limit", 10)
        query = urllib.parse.quote(f"is:open label:{label}")
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?labels={label}&state=open&per_page={limit}",
                headers={"Accept": "application/vnd.github+json", "User-Agent": "rustchain-mcp/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                issues = json.loads(r.read().decode())
            bounties = [{"number": i["number"], "title": i["title"], "url": i["html_url"]} for i in issues]
            return {"content": [{"type": "text", "text": json.dumps({"bounties": bounties, "count": len(bounties)}, indent=2)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}

    else:
        return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params", {})

        try:
            if method == "initialize":
                result = handle_initialize(params)
            elif method == "tools/list":
                result = handle_tools_list(params)
            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                result = handle_tool_call(tool_name, tool_args)
            elif method == "notifications/initialized":
                continue  # No response needed
            else:
                result = {"error": {"code": -32601, "message": f"Method not found: {method}"}}

            response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
        except Exception as e:
            response = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": str(e)}}

        print(json.dumps(response), flush=True)

if __name__ == "__main__":
    main()
