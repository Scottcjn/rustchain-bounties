# rustchain-mcp

Model Context Protocol server for [RustChain](https://github.com/Scottcjn/Rustchain) — connects any AI agent running Claude Code, Cursor, Windsurf, or any MCP-compatible IDE to the RustChain blockchain.

## Install

```bash
pip install rustchain-mcp
# or with uvx (no install needed):
uvx rustchain-mcp
```

## Claude Code Setup

Add to your `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "uvx",
      "args": ["rustchain-mcp"],
      "env": {
        "RUSTCHAIN_NODE": "https://50.28.86.131"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `rustchain_health` | Check node health and sync status |
| `rustchain_balance` | Query RTC wallet balance |
| `rustchain_miners` | List active miners with hardware profiles |
| `rustchain_epoch` | Current epoch info and rewards |
| `rustchain_create_wallet` | Register a new agent wallet |
| `rustchain_submit_attestation` | Submit hardware fingerprint for mining |
| `rustchain_bounties` | List open bounties with rewards |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTCHAIN_NODE` | `https://50.28.86.131` | RustChain node URL |

## Usage Example

Once configured, ask your AI agent:
- "Check my RustChain balance at address RTC..."
- "What open bounties are available?"
- "What's the current mining epoch?"

## License

MIT — Bounty #2859 submission by TestAutomaton (Wallet: TestAutomaton)
