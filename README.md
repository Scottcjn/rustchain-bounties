# RustChain MCP Server

Model Context Protocol (MCP) server for interacting with the RustChain blockchain.

## Features

- **rustchain_health**: Check node health.
- **rustchain_miners**: List active miners.
- **rustchain_epoch**: Get current epoch info.
- **rustchain_balance**: Check RTC balance.
- **rustchain_transfer**: Send RTC (requires key).
- **rustchain_ledger**: Transaction history.
- **rustchain_register_wallet**: Create a new wallet.
- **rustchain_bounties**: List open bounties.

## Installation

### For Claude Code

```bash
claude mcp add rustchain-mcp -- node /path/to/rustchain-mcp/dist/index.js
```

### Manual Build

```bash
npm install
npm run build
```

## Configuration

The server connects to `https://50.28.86.131` by default and bypasses SSL certificate validation for internal IP access.
