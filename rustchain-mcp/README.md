# RustChain MCP Server

Connect Claude Code, Cursor, or any MCP-compatible IDE to RustChain.

## Installation

```bash
pip install rustchain-mcp
```

## Usage

### Claude Code Configuration

Add to `CLAUDE.md` or `.claude/settings.json`:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "rustchain-mcp",
      "args": ["https://50.28.86.131"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| rustchain_health | Check node health |
| rustchain_balance | Query wallet balance |
| rustchain_miners | List active miners |
| rustchain_epoch | Get epoch info |
| rustchain_create_wallet | Register new wallet |
| rustchain_bounties | List open bounties |

## Configuration

Default node URL: `https://50.28.86.131`

Override via argument: `rustchain-mcp <node-url>`
