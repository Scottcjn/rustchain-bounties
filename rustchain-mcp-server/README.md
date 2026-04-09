# RustChain MCP Server

Model Context Protocol server that connects AI agents to RustChain.

## Tools

| Tool | Description |
|------|-------------|
| `rustchain_health` | Check node health |
| `rustchain_balance` | Query wallet balance |
| `rustchain_miners` | List active miners |
| `rustchain_epoch` | Current epoch info |
| `rustchain_bounties` | List open bounties |

## Installation

```bash
pip install rustchain-mcp
```

## Claude Code Setup

Add to your Claude Code configuration (`.claude/settings.json` or global):

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

Or using uvx:

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

## Usage

Once installed, Claude Code can use these tools:

```
rustchain_health - Check if the node is online
rustchain_balance wallet="my_wallet" - Get wallet balance
rustchain_miners limit=10 - List active miners
rustchain_epoch - Get epoch info
rustchain_bounties limit=5 - List open bounties
```

## Configuration

Set environment variable for custom node URL:

```bash
export RUSTCHAIN_NODE_URL=https://50.28.86.131
```

## License

MIT
