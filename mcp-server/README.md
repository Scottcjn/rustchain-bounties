# RustChain MCP Server

A Model Context Protocol (MCP) server that exposes RustChain blockchain operations as tools for AI agents.

## Supported Tools

| Tool | Description |
|------|-------------|
| `rustchain_health` | Check node health and status |
| `rustchain_balance` | Query wallet balance |
| `rustchain_miners` | List active miners |
| `rustchain_block_height` | Get current block height |
| `rustchain_tx_status` | Check transaction status |
| `rustchain_transfer` | Send RTC tokens |
| `rustchain_recent_blocks` | View recent blocks |

## Setup

### Claude Code
Add to your `.claude/settings.json`:
```json
{"mcpServers": {"rustchain": {"command": "python3", "args": ["rustchain_mcp_server.py"]}}}
```

### Requirements
- Python 3.8+
- No external dependencies (stdlib only)
- Network access to RustChain node

## License
MIT
