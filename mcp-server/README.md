# RustChain MCP Server

> Connect **any MCP-compatible AI agent** (Claude Code, Cursor, Windsurf, VS Code Copilot) to **RustChain** with a single line of config.

**25 RTC Bounty — Issue #2859**

## What It Does

Exposes RustChain as MCP tools:

| Tool | Description |
|------|-------------|
| `rustchain_health` | Check node health and status |
| `rustchain_balance` | Query wallet RTC balance |
| `rustchain_miners` | List active miners |
| `rustchain_epoch` | Current epoch + time to settlement |
| `rustchain_bounties` | List open bounties from GitHub |
| `rustchain_network_stats` | Overall network statistics |

## Install

```bash
pip install rustchain-mcp
```

Or with MCP dependencies:
```bash
pip install rustchain-mcp[mcp]
```

## Configure Claude Code

Add to your Claude Code MCP settings (`~/.claude.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "python",
      "args": ["-m", "rustchain_mcp"]
    }
  }
}
```

## Configure Cursor

Add to Cursor MCP settings (Settings → MCP → Add Server):

```json
{
  "rustchain": {
    "command": "python",
    "args": ["-m", "rustchain_mcp"]
  }
}
```

## Configure Windsurf

Add to Windsurf MCP config:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "python",
      "args": ["-m", "rustchain_mcp"]
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTCHAIN_NODE_URL` | `https://50.28.86.131` | RustChain node URL |
| `RUSTCHAIN_MCP_PORT` | `3000` | HTTP server port (fallback mode) |

```bash
export RUSTCHAIN_NODE_URL=https://50.28.86.131
python -m rustchain_mcp
```

## Example Usage

Once configured, ask your AI assistant:

```
What's my RustChain wallet balance for "nox-ventures"?
→ Returns: { "wallet": "nox-ventures", "balance": 123.4567, "unit": "RTC" }

Show me the current RustChain epoch
→ Returns: { "current_epoch": 42, "slots_remaining": 876, "time_to_next_epoch": "3h 39m" }

List the top 5 active miners
→ Returns: Table of miners sorted by antiquity multiplier

What bounties are open on RustChain?
→ Returns: List of open bounty issues with numbers and titles
```

## Architecture

```
rustchain_mcp/
├── __init__.py      — Package init
├── server.py        — MCP server (MCP mode + HTTP fallback)
└── pyproject.toml   — Package config
```

## MCP Protocol

This server implements the Model Context Protocol (MCP):
- `list_tools` → returns all available RustChain tools
- `call_tool` → executes the requested tool and returns JSON result
- Communicates via stdio (Claude Code/Cursor) or HTTP (standalone)

## Publish to PyPI

```bash
pip install build twine
python -m build
twine upload dist/*
```

## License

MIT
