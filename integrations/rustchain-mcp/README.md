# RustChain MCP Server

A Model Context Protocol (MCP) server for RustChain. This server allows AI agents (like Claude) to interact with the RustChain blockchain via standard tools.

## Features

- **Network Metrics**: Fetch epoch, slot, and block height data.
- **Miner Status**: List active miners and their hashrates.
- **Wallet Integration**: Query RTC balances and submit signed transfers.
- **Multi-Node Support**: Built-in failover and health monitoring across multiple nodes.

## Tools

1.  `rustchain_balance`: Get the RTC balance for a specific wallet or miner ID.
2.  `rustchain_miners`: List active miners on the RustChain network.
3.  `rustchain_epoch`: Get current epoch, slot, and reward information.
4.  `rustchain_health`: Check the health of all RustChain nodes.
5.  `rustchain_transfer`: Submit a signed transfer payload to the network.

## Setup

### Prerequisites

- [Bun](https://bun.sh/) installed.

### Installation

1.  Navigate to the integration directory:
    ```bash
    cd integrations/rustchain-mcp
    ```
2.  Install dependencies:
    ```bash
    bun install
    ```

### Usage with Claude Desktop

Add the following to your `claude_desktop_config.json`:

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

## Direct Execution

```bash
bun run index.ts
```

The server communicates over `stdio`.

## Development

To run the verification tests:
```bash
bun run verify_api.ts
bun run test_mcp.ts
```

---
*Developed for the RustChain Bounty Program.*
