import asyncio
import json
import os
import urllib.error
import urllib.request

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool


BASE_URL = os.environ.get("RUSTCHAIN_BASE_URL", "http://rustchain.org:8088").rstrip("/")
# SECURITY: the default uses plaintext HTTP, which is MITM-vulnerable in any
# network where an attacker can observe or modify packets. Operators running
# against an HTTPS-capable endpoint should set RUSTCHAIN_BASE_URL=https://...
# For self-signed certs, set RUSTCHAIN_INSECURE_SKIP_TLS=1 to skip verification.
import warnings as _warnings
if BASE_URL.lower().startswith("http://"):
    _warnings.warn(
        ("RUSTCHAIN_BASE_URL is plaintext HTTP (" + BASE_URL +
         "). Responses can be tampered with in transit. Prefer HTTPS."),
        RuntimeWarning,
    )

_INSECURE_TLS = os.environ.get("RUSTCHAIN_INSECURE_SKIP_TLS") == "1"
if _INSECURE_TLS:
    _warnings.warn(
        "RUSTCHAIN_INSECURE_SKIP_TLS=1 — TLS certificate verification is disabled. Unsafe in production.",
        RuntimeWarning,
    )

app = Server("rustchain-read-mcp")


def fetch_json(path: str) -> dict:
    request = urllib.request.Request(f"{BASE_URL}{path}", headers={"Accept": "application/json"})
    # SECURITY: pass an SSL context that respects RUSTCHAIN_INSECURE_SKIP_TLS
    # so operators who switch to HTTPS can still use a self-signed cert.
    import ssl as _ssl
    ctx = _ssl.create_default_context()
    if _INSECURE_TLS:
        ctx.check_hostname = False
        ctx.verify_mode = _ssl.CERT_NONE
    with urllib.request.urlopen(request, timeout=15, context=ctx) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def as_text(payload: dict) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(payload))]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_health",
            description="Fetch RustChain node health from /health.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_epoch",
            description="Fetch current RustChain epoch data from /epoch.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_miners",
            description="Fetch current RustChain miner data from /api/miners.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "get_health":
            return as_text(fetch_json("/health"))
        if name == "get_epoch":
            return as_text(fetch_json("/epoch"))
        if name == "get_miners":
            return as_text(fetch_json("/api/miners"))
    except urllib.error.URLError as exc:
        raise ValueError(f"RustChain request failed: {exc}") from exc

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
