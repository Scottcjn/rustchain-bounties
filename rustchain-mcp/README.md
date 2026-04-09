# RustChain MCP Server

> Connect any AI agent to RustChain blockchain via Model Context Protocol

## Why This Matters

Every AI agent running Claude Code, Cursor, Windsurf, or any MCP-compatible IDE can instantly connect to RustChain. **This is the single fastest way to onboard thousands of agents to RustChain.**

## One-Line Install

```bash
pip install rustchain-mcp
```

Or with uvx:

```bash
uvx rustchain-mcp
```

## Tools

| Tool | Description |
|------|-------------|
| `rustchain_health` | Check node health |
| `rustchain_balance` | Query wallet balance |
| `rustchain_miners` | List active miners |
| `rustchain_epoch` | Get epoch info |
| `rustchain_bounties` | List open bounties |
| `rustchain_create_wallet` | Register new wallet |
| `rustchain_submit_attestation` | Submit hardware fingerprint |

## Claude Code Setup

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "uvx",
      "args": ["rustchain-mcp"]
    }
  }
}
```

Or using Python:

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

## Cursor Setup

Add to Cursor settings:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "uvx",
      "args": ["rustchain-mcp"]
    }
  }
}
```

## Windsurf Setup

Same as Claude Code - add to `.windsurf/settings.json`.

## Configuration

```bash
# Custom node URL
export RUSTCHAIN_NODE_URL=https://50.28.86.131
```

## Usage Example

```
rustchain_health - Check if node is online
rustchain_balance wallet="my_agent" - Get wallet balance
rustchain_epoch - Get current epoch
rustchain_bounties limit=5 - List bounties
```

## Publishing

```bash
# Build and publish to PyPI
pip install build twine
python -m build
twine upload dist/*
```

## Requirements

- Python 3.8+
- requests
- mcp

## License

MIT
