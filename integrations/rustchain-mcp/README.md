# RustChain MCP Server

A Model Context Protocol (MCP) server for RustChain. This server allows AI agents (like Claude) to interact with the RustChain blockchain via standard tools.

## Features

This implementation includes all required and bonus tools for the 100 RTC tier:
- `rustchain_health`: Check node health with automatic failover.
- `rustchain_miners`: List active miners and architectures.
- `rustchain_epoch`: Fetch current network epoch info.
- `rustchain_balance`: Query RTC balance for any wallet or miner ID.
- `rustchain_ledger`: Live explorer activity and transaction tracking.
- `rustchain_register`: Automatic epoch enrollment for AI agents.
- `rustchain_bounties`: Integrated bounty browser fetching directly from GitHub.
- `rustchain_transfer`: Signed transaction submission.

## Implementations

### TypeScript (Bun) — *Full implementation*
This version uses the official MCP SDK and Bun for high-performance direct execution. It includes live implementations for all tools, unlike the Python stubs.

#### Setup (TypeScript)
1. **Navigate**: `cd integrations/rustchain-mcp`
2. **Install**: `bun install`
3. **Run**: `bun run index.ts`

#### Usage with Claude Desktop
Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "rustchain": {
      "command": "bun",
      "args": [
        "run",
        "C:/path/to/integrations/rustchain-mcp/index.ts"
      ]
    }
  }
}
```

#### Verification
To run the comprehensive test suite:
```bash
bun run verify_api.ts   # Probes live node endpoints
bun run test_mcp.ts     # Smoke tests all JSON-RPC tool dispatch
```

### Python Implementation
Alternative implementation using Python scripts.

#### Setup (Python)
1. `cd integrations/rustchain-mcp`
2. `python3 -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Use with Claude Code: `claude mcp add rustchain "$(pwd)/run.sh"`

## Node Failover & Configuration
The server supports multiple nodes with automatic failover.
- Primary: `https://50.28.86.131`
- Fallbacks: `https://50.28.86.153`, `http://76.8.228.245:8099`

Override nodes via environment variables:
- `RUSTCHAIN_PRIMARY_URL`
- `RUSTCHAIN_FALLBACK_URLS` (comma-separated)

## Security
- Never commit private keys.
- Prefer reading sensitive keys from environment variables.

---
*Developed for the RustChain Bounty Program.*
