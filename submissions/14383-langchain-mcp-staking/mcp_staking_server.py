#!/usr/bin/env python3
"""
rustchain-staking-mcp  —  Model Context Protocol server
Bounty #14383: https://github.com/Scottcjn/rustchain-bounties/issues/14383

Exposes the RustChain stake-and-acquire flow as an MCP tool so any MCP-capable
agent (Claude Code, Cursor, Windsurf, Continue, …) can stake for self-improvement
in a single tool call.

Protocol : MCP 2024-11-05  (JSON-RPC 2.0 over stdio)
Transport : stdin / stdout  (standard MCP stdio transport)

Usage:
    python mcp_staking_server.py

Claude Code integration (claude_desktop_config.json):
    {
      "mcpServers": {
        "rustchain-staking": {
          "command": "python",
          "args": ["/path/to/mcp_staking_server.py"],
          "env": {
            "RUSTCHAIN_NODE": "https://50.28.86.131",
            "RUSTCHAIN_PRIVATE_KEY": "<64-char-hex-ed25519-key>"
          }
        }
      }
    }
"""

from __future__ import annotations

import json
import sys
import traceback
from typing import Any

# Import from the co-located staking SDK
from staking_sdk import stake_and_acquire, NODE_URL, CHAIN_ID

# ── MCP server metadata ────────────────────────────────────────────────────────

SERVER_INFO = {
    "name": "rustchain-staking-mcp",
    "version": "1.0.0",
    "description": (
        "RustChain staked self-improvement gateway. "
        "Stake RTC and acquire skills in one MCP tool call."
    ),
}

PROTOCOL_VERSION = "2024-11-05"

# ── Tool schema ────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "stake_and_acquire",
        "description": (
            "Stake RTC on the RustChain network and acquire a skill from the "
            "reference skill gate in a single call.\n\n"
            "Fail-safe: if the gate is unavailable the stake is automatically "
            "refunded and the error is surfaced — no RTC is ever silently lost.\n\n"
            "Returns a JSON object with:\n"
            "  • verdict   – 'acquired' | 'denied' | 'error'\n"
            "  • success   – true when skill was granted and attestation verified\n"
            "  • refunded  – true when stake was returned (gate down or denied)\n"
            "  • attestation – signed attestation envelope (when success=true)\n"
            "  • error     – human-readable reason (when success=false)"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill": {
                    "type": "string",
                    "description": (
                        "Skill identifier to acquire, e.g. 'rust_async', "
                        "'zero_knowledge', 'p2p_networking'."
                    ),
                },
                "bond_rtc": {
                    "type": "number",
                    "description": "RTC amount to bond (stake). Must be > 0. Default: 1.0.",
                    "default": 1.0,
                    "exclusiveMinimum": 0,
                },
                "private_key_hex": {
                    "type": "string",
                    "description": (
                        "Optional 64-char hex Ed25519 private key for signing. "
                        "Falls back to RUSTCHAIN_PRIVATE_KEY env var; "
                        "if neither is set an HMAC stub is used (offline testing only)."
                    ),
                },
            },
            "required": ["skill"],
        },
    },
    {
        "name": "rustchain_health",
        "description": "Check RustChain node health and current epoch.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# ── Tool handlers ──────────────────────────────────────────────────────────────

def handle_stake_and_acquire(arguments: dict) -> dict:
    """Execute stake_and_acquire and return MCP content block."""
    skill = arguments.get("skill", "").strip()
    if not skill:
        return _error_content("'skill' is required")

    bond_rtc = float(arguments.get("bond_rtc", 1.0))
    private_key_hex = arguments.get("private_key_hex") or None

    result = stake_and_acquire(skill=skill, bond_rtc=bond_rtc,
                               private_key_hex=private_key_hex)
    result_dict = result.to_dict()

    # Build a human-readable summary alongside the raw JSON
    if result.success:
        summary = (
            f"✅ Skill '{skill}' acquired for {bond_rtc} RTC.\n"
            f"   Attestation algorithm : {result.attestation.get('algorithm','?')}\n"
            f"   Signature (truncated)  : "
            f"{result.attestation.get('sig_hex','?')[:32]}…"
        )
    elif result.refunded:
        summary = (
            f"↩️  Gate unavailable for '{skill}'. "
            f"{bond_rtc} RTC refunded.\n   Reason: {result.error}"
        )
    else:
        summary = f"❌ Skill '{skill}' denied. Reason: {result.error}"

    content_text = f"{summary}\n\nFull result:\n{json.dumps(result_dict, indent=2)}"

    return {
        "content": [{"type": "text", "text": content_text}],
        "isError": not result.success and not result.refunded,
    }


def handle_rustchain_health(_arguments: dict) -> dict:
    """Fetch node health and epoch info."""
    import urllib.request, urllib.error
    results = {}
    for path in ["/health", "/epoch"]:
        try:
            req = urllib.request.Request(
                f"{NODE_URL}{path}",
                headers={"User-Agent": "rustchain-staking-mcp/1.0"},
            )
            # self-signed cert → use urllib with ssl context
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
                results[path.lstrip("/")] = json.loads(r.read().decode())
        except urllib.error.HTTPError as exc:
            results[path.lstrip("/")] = {"error": f"HTTP {exc.code}"}
        except Exception as exc:
            results[path.lstrip("/")] = {"error": str(exc)}

    text = (
        f"Node: {NODE_URL}\n"
        f"Chain: {CHAIN_ID}\n\n"
        + json.dumps(results, indent=2)
    )
    return {"content": [{"type": "text", "text": text}]}


# ── MCP protocol ───────────────────────────────────────────────────────────────

def _error_content(message: str) -> dict:
    return {
        "content": [{"type": "text", "text": f"Error: {message}"}],
        "isError": True,
    }


def handle_initialize(_params: dict) -> dict:
    return {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {"tools": {}},
        "serverInfo": SERVER_INFO,
    }


def handle_tools_list(_params: dict) -> dict:
    return {"tools": TOOLS}


def handle_tool_call(params: dict) -> dict:
    name = params.get("name", "")
    arguments = params.get("arguments", {})
    try:
        if name == "stake_and_acquire":
            return handle_stake_and_acquire(arguments)
        elif name == "rustchain_health":
            return handle_rustchain_health(arguments)
        else:
            return _error_content(f"Unknown tool: '{name}'")
    except Exception:
        tb = traceback.format_exc()
        return _error_content(f"Internal error in '{name}':\n{tb}")


# ── Main loop ──────────────────────────────────────────────────────────────────

def main() -> None:
    """
    MCP stdio event loop.
    Reads newline-delimited JSON-RPC 2.0 messages from stdin,
    writes responses to stdout.
    """
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue

        try:
            msg = json.loads(raw)
        except json.JSONDecodeError as exc:
            _write({"jsonrpc": "2.0", "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {exc}"}})
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
                result = handle_tool_call(params)
            elif method in ("notifications/initialized", "notifications/cancelled"):
                continue  # no response required
            else:
                _write({
                    "jsonrpc": "2.0", "id": msg_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                })
                continue

            _write({"jsonrpc": "2.0", "id": msg_id, "result": result})

        except Exception:
            tb = traceback.format_exc()
            _write({
                "jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32603, "message": f"Internal error:\n{tb}"},
            })


def _write(obj: Any) -> None:
    print(json.dumps(obj), flush=True)


if __name__ == "__main__":
    main()
