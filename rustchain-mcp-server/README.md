# RustChain MCP Server

Connect **any AI agent** (Claude Code, Cursor, Windsurf) to the **RustChain blockchain** via MCP.

## Quick Install

```bash
pip install rustchain-mcp
```

## Claude Code Config

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "uvx",
      "args": ["rustchain-mcp"],
      "env": { "RUSTCHAIN_NODE_URL": "https://50.28.86.131" }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `rustchain_health` | Check node health |
| `rustchain_balance` | Query wallet balance |
| `rustchain_miners` | List active miners |
| `rustchain_epoch` | Current epoch info |
| `rustchain_bounties` | List open bounties |

## Bounty

- **Issue**: [#2859](https://github.com/Scottcjn/rustchain-bounties/issues/2859)
- **Reward**: 25 RTC (~.50 USD)
- **Author**: 大鹏 (YPC0813)
