"""
RustChain MCP Server — Connects any AI Agent to RustChain via Model Context Protocol.

Usage:
    pip install rustchain-mcp
    rustchain-mcp  # Starts the MCP server on stdio

Or with uvx:
    uvx rustchain-mcp
"""

import os
import json
import urllib.request
import urllib.error
from typing import Any, Optional

# MCP Protocol Types
MCP_TOOL_SCHEMA = {
    "tools": [
        {
            "name": "rustchain_health",
            "description": "Check RustChain node health and connectivity",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "rustchain_balance",
            "description": "Query RTC wallet balance",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "miner_id": {
                        "type": "string",
                        "description": "Miner ID or wallet name to query"
                    }
                },
                "required": ["miner_id"]
            }
        },
        {
            "name": "rustchain_miners",
            "description": "List active miners on the network",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max miners to return (default 20)",
                        "default": 20
                    }
                },
                "required": []
            }
        },
        {
            "name": "rustchain_epoch",
            "description": "Get current epoch information",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "rustchain_create_wallet",
            "description": "Register a new agent wallet on RustChain",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "wallet_name": {
                        "type": "string",
                        "description": "Unique wallet name for the agent"
                    }
                },
                "required": ["wallet_name"]
            }
        },
        {
            "name": "rustchain_submit_attestation",
            "description": "Submit hardware fingerprint attestation for Proof-of-Antiquity",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "miner_id": {
                        "type": "string",
                        "description": "Miner ID to attest"
                    },
                    "hardware_signature": {
                        "type": "string",
                        "description": "Hardware signature from the node"
                    }
                },
                "required": ["miner_id", "hardware_signature"]
            }
        },
        {
            "name": "rustchain_bounties",
            "description": "List open bounties on RustChain",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status: open, closed, all",
                        "default": "open"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max bounties to return (default 20)",
                        "default": 20
                    }
                },
                "required": []
            }
        },
        {
            "name": "rustchain_transfer",
            "description": "Transfer RTC between wallets",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "from_wallet": {
                        "type": "string",
                        "description": "Source wallet name"
                    },
                    "to_wallet": {
                        "type": "string",
                        "description": "Destination wallet name"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount of RTC to transfer"
                    },
                    "admin_key": {
                        "type": "string",
                        "description": "Admin key for the source wallet"
                    }
                },
                "required": ["from_wallet", "to_wallet", "amount", "admin_key"]
            }
        }
    ]
}


class RustChainClient:
    """Lightweight RustChain API client."""

    def __init__(self, node_url: Optional[str] = None):
        self.node_url = (node_url or
                         os.environ.get("RUSTCHAIN_NODE_URL", "https://50.28.86.131")
                        ).rstrip("/")

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{self.node_url}{path}"
        try:
            if params:
                import urllib.parse
                url += "?" + urllib.parse.urlencode(params)
            with urllib.request.urlopen(url, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}", "ok": False}
        except Exception as e:
            return {"error": str(e), "ok": False}

    def _post(self, path: str, data: dict) -> dict:
        url = f"{self.node_url}{path}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            return {"error": f"HTTP {e.code}: {e.reason}", "body": body, "ok": False}
        except Exception as e:
            return {"error": str(e), "ok": False}

    def health(self) -> dict:
        return self._get("/health")

    def balance(self, miner_id: str) -> dict:
        return self._get("/wallet/balance", {"miner_id": miner_id})

    def miners(self, limit: int = 20) -> dict:
        result = self._get("/miners/list", {"limit": limit})
        return result

    def epoch(self) -> dict:
        return self._get("/epoch/current")

    def create_wallet(self, wallet_name: str) -> dict:
        return self._post("/wallet/create", {"wallet_name": wallet_name})

    def submit_attestation(self, miner_id: str, hardware_signature: str) -> dict:
        return self._post("/attest/submit", {
            "miner_id": miner_id,
            "hardware_signature": hardware_signature
        })

    def bounties(self, status: str = "open", limit: int = 20) -> dict:
        return self._get("/bounties/list", {"status": status, "limit": limit})

    def transfer(self, from_wallet: str, to_wallet: str,
                 amount: float, admin_key: str) -> dict:
        return self._post("/wallet/send", {
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": amount,
            "admin_key": admin_key
        })


# Global client instance
_client: Optional[RustChainClient] = None

def get_client() -> RustChainClient:
    global _client
    if _client is None:
        _client = RustChainClient()
    return _client


def handle_tool(name: str, arguments: dict) -> dict:
    """Dispatch tool call to appropriate handler."""
    client = get_client()

    handlers = {
        "rustchain_health": lambda _: client.health(),
        "rustchain_balance": lambda a: client.balance(a["miner_id"]),
        "rustchain_miners": lambda a: client.miners(a.get("limit", 20)),
        "rustchain_epoch": lambda _: client.epoch(),
        "rustchain_create_wallet": lambda a: client.create_wallet(a["wallet_name"]),
        "rustchain_submit_attestation": lambda a: client.submit_attestation(
            a["miner_id"], a["hardware_signature"]
        ),
        "rustchain_bounties": lambda a: client.bounties(
            a.get("status", "open"), a.get("limit", 20)
        ),
        "rustchain_transfer": lambda a: client.transfer(
            a["from_wallet"], a["to_wallet"], a["amount"], a["admin_key"]
        ),
    }

    handler = handlers.get(name)
    if not handler:
        return {"error": f"Unknown tool: {name}"}

    try:
        result = handler(arguments)
        return result if isinstance(result, dict) else {"result": result}
    except Exception as e:
        return {"error": str(e), "ok": False}


def main():
    """
    MCP stdio server loop.
    Reads JSON-RPC requests from stdin, writes responses to stdout.
    """
    import sys

    # Send capabilities on startup
    import json
    sys.stdout.write(json.dumps({
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "rustchain-mcp",
                "version": "1.0.0"
            }
        }
    }) + "\n")
    sys.stdout.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            method = request.get("method")
            msg_id = request.get("id")
            params = request.get("params", {})

            if method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": MCP_TOOL_SCHEMA
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result = handle_tool(tool_name, tool_args)
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            elif method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "rustchain-mcp", "version": "1.0.0"}
                    }
                }
            else:
                # Notifcation or unknown — no response needed
                continue

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": msg_id if 'msg_id' in dir() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
