# RustChain MCP Server

A Model Context Protocol (MCP) server for interacting with RustChain blockchain from Claude Code and other MCP-compatible AI assistants.

## Installation

```bash
pip install rustchain-mcp
```

Or install from source:

```bash
cd mcp-server
pip install -e .
```

## Claude Code Usage

```bash
claude mcp add rustchain python -m rustchain_mcp.server
```

## Available Tools

### Required Tools (75 RTC)

| Tool | Description |
|------|-------------|
| `rustchain_balance` | Check RTC balance for any wallet |
| `rustchain_miners` | List active miners and their architectures |
| `rustchain_epoch` | Get current epoch info (slot, height, rewards) |
| `rustchain_health` | Check node health across all 3 attestation nodes |
| `rustchain_transfer` | Send RTC (requires wallet key) |

### Bonus Tools (100 RTC total)

| Tool | Description |
|------|-------------|
| `rustchain_ledger` | Query transaction history |
| `rustchain_register_wallet` | Create a new wallet |
| `rustchain_bounties` | List open bounties with rewards |

## API Endpoints

The server connects to:
- Primary: `https://50.28.86.131`
- Fallback: Node 2 and Node 3

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```
