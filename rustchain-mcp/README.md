# RustChain MCP Server

Connect Claude Code, Cursor, Windsurf, and any MCP-compatible AI IDE to RustChain.

## Installation

```bash
pip install rustchain-mcp
# or
npm install -g rustchain-mcp
```

## Quick Start

### Claude Code Config

Add to your `CLAUDE.md` or `.mcp.json`:

\`\`\`json
{
  "mcpServers": {
    "rustchain": {
      "command": "uvx",
      "args": ["rustchain-mcp"]
    }
  }
}
\`\`\`

### VS Code

The `.vscode/settings.json` configures the MCP server automatically.

## Available Tools

| Tool | Description |
|------|-------------|
| `rustchain_health` | Check node health |
| `rustchain_balance` | Query wallet balance |
| `rustchain_epoch` | Get epoch info |
| `rustchain_miners` | List active miners |
| `rustchain_create_wallet` | Register new wallet |
| `rustchain_submit_attestation` | Submit attestation |

## Configuration

Set `RUSTCHAIN_NODE_URL` env var (default: https://50.28.86.131)

## License

MIT
