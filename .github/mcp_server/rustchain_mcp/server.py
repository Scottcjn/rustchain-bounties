```python
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
                        "description": "Sender wallet name"
                    },
                    "to_wallet": {
                        "type": "string",
                        "description": "Recipient wallet name"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount of RTC to transfer"
                    }
                },
                "required": ["from_wallet", "to_wallet", "amount"]
            }
        }
    ]
}
```
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
                        "description": "Sender wallet name"
                    },
                    "to_wallet": {
                        "type": "string",
                        "description": "Recipient wallet name"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount of RTC to transfer"
                    }
                },
                "required": ["from_wallet", "to_wallet", "amount"]
            }
        }
    ]
}
