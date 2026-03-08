# RustChain MCP Server

A Model Context Protocol (MCP) server that allows Claude Code users to interact with RustChain directly from their terminal.

## Features

### Required Tools (75 RTC)
- `rustchain_balance` - Check RTC balance for any wallet
- `rustchain_miners` - List active miners and their architectures
- `rustchain_epoch` - Get current epoch info (slot, height, rewards)
- `rustchain_health` - Check node health across all 3 attestation nodes
- `rustchain_transfer` - Send RTC (requires wallet key)

### Bonus Tools (100 RTC)
- `rustchain_ledger` - Query transaction history
- `rustchain_register_wallet` - Create a new wallet
- `rustchain_bounties` - List open bounties with rewards

## Installation

```bash
# Clone the repository
git clone https://github.com/sososonia-cyber/rustchain-mcp.git
cd rustchain-mcp

# Install dependencies
pip install -e .

# Add to Claude Code
claude mcp add rustchain-mcp python /path/to/rustchain-mcp/server.py
```

## Usage

Once installed, you can use the following commands in Claude Code:

```
Check my RTC balance: rustchain_balance miner_id=your-wallet-name
List active miners: rustchain_miners
Get epoch info: rustchain_epoch
Check node health: rustchain_health
```

## API Endpoints

The server connects to:
- Primary: https://50.28.86.131
- Fallback: 50.28.86.153, 76.8.228.245

## License

MIT
