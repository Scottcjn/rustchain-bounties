# LangChain + MCP Tool for Staked Self-Improvement
## Bounty #14383 (100 RTC)

## Overview
A LangChain-compatible tool and MCP server that wraps the Elyan staking SDK, enabling AI agents in the LangChain and MCP ecosystems to stake for self-improvement in a single call.

## Architecture
```
elyan-staking-mcp/
  src/
    client.ts       - StakingClient (shared SDK)
    langchain.ts    - LangChain tool wrapper
    mcp-server.ts   - MCP server implementation
    types.ts        - Shared types
  package.json
  README.md
```

## LangChain Integration
```typescript
import { ElyanStakingTool } from "elyan-staking-mcp";

const tool = new ElyanStakingTool({
    rpcUrl: "https://api.elyan.network"
});

// Use with any LangChain agent
const result = await tool.call({
    action: "stake",
    amount: 100,
    agentId: "my-agent"
});
```

## MCP Server
```bash
# Start MCP server
npx elyan-staking-mcp --mcp

# Configure in Claude Code / Cursor
# {
#   "mcpServers": {
#     "elyan-staking": {
#       "command": "npx",
#       "args": ["elyan-staking-mcp", "--mcp"]
#     }
#   }
# }
```

## Features
- ✅ LangChain tool with full schema
- ✅ MCP server with tools/list, tools/call
- ✅ Stake, unstake, claim, balance, status
- ✅ Zero-config setup
- ✅ TypeScript + ESM support

## Wallet
ETH: 0xde67FD4b7fC0d02d43AA3A8b5c8c5a80c823d0c6
