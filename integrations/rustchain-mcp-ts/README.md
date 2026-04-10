# RustChain MCP Server (TypeScript)

A **Model Context Protocol (MCP)** server written in TypeScript that exposes RustChain network operations as tools to Claude Code, Cursor, Windsurf, and any MCP-compatible IDE or AI agent.

This is the **TypeScript implementation** of the RustChain MCP server. A Python version is available in the sibling `rustchain-mcp/` directory.

---

## Tools

| Tool | Description |
|------|-------------|
| `rustchain_health` | Check node health with automatic failover |
| `rustchain_balance` | Query RTC balance for a wallet / miner_id |
| `rustchain_miners` | List active miners and architectures |
| `rustchain_epoch` | Current epoch info (slot, height, rewards) |
| `rustchain_create_wallet` | Register a new agent wallet |
| `rustchain_submit_attestation` | Submit hardware fingerprint for a miner |
| `rustchain_bounties` | List open bounties from the RustChain bounty ledger |

---

## Prerequisites

- **Node.js** ≥ 18.0.0
- **npm** ≥ 9.0.0

---

## Quick Start

### Install from source

```bash
cd integrations/rustchain-mcp-ts
npm install
npm run build
```

### One-line install via npx

```bash
npx rustchain-mcp-ts
```

### Configure in Claude Code

Add to your `~/.claude/settings.json` or project `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "node",
      "args": ["/path/to/rustchain-mcp-ts/dist/index.js"]
    }
  }
}
```

Or with npx:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "npx",
      "args": ["rustchain-mcp-ts"]
    }
  }
}
```

### Configure in Cursor MCP Settings

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "node",
      "args": ["/absolute/path/to/integrations/rustchain-mcp-ts/dist/index.js"]
    }
  }
}
```

### Configure in Windsurf / VS Code Copilot MCP

Same JSON format as above, add to the MCP settings configuration file.

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTCHAIN_PRIMARY_URL` | `https://50.28.86.131` | Primary RustChain node |
| `RUSTCHAIN_FALLBACK_URLS` | _(none)_ | Comma-separated fallback URLs |
| `RUSTCHAIN_TIMEOUT_MS` | `10000` | Request timeout in milliseconds |

Example:

```bash
RUSTCHAIN_PRIMARY_URL=https://50.28.86.131 \
RUSTCHAIN_FALLBACK_URLS=https://backup1.rustchain.io,https://backup2.rustchain.io \
node dist/index.js
```

---

## Usage Examples

### Health check

```
rustchain_health
```

### Check wallet balance

```
rustchain_balance wallet_id=my-agent-wallet
```

### List active miners

```
rustchain_miners
```

### Get epoch info

```
rustchain_epoch
```

### Create a new wallet

```
rustchain_create_wallet wallet_name=agent-001
```

### Submit hardware attestation

```
rustchain_submit_attestation wallet_id=agent-001 hardware_fingerprint=sha256:abc123...
```

### List open bounties

```
rustchain_bounties
```

---

## Security

- **Never** hardcode or commit private keys. Use environment variables.
- The `rustchain_submit_attestation` tool requires a valid hardware fingerprint — do not guess or fabricate it.
- Enable **dry-run mode** when testing by setting `RUSTCHAIN_DRY_RUN=1` (future feature).

---

## Publishing to npm

```bash
npm login
npm publish --access public
```

After publishing, users can install with:

```bash
npx rustchain-mcp-ts
```

Or install globally:

```bash
npm install -g rustchain-mcp-ts
rustchain-mcp  # starts the server
```

---

## License

MIT
