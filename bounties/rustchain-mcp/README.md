# RustChain MCP Server

A Model Context Protocol (MCP) server for interacting with the RustChain blockchain from Claude Code.

## Installation

```bash
# Install dependencies
pip install mcp requests

# Add to Claude Code
claude mcp add rustchain-mcp python /path/to/rustchain_mcp/server.py
```

## Required Tools (75 RTC)

| Tool | Description |
|------|-------------|
| `rustchain_balance` | Check RTC balance for any wallet |
| `rustchain_miners` | List active miners and their architectures |
| `rustchain_epoch` | Get current epoch info (slot, height, rewards) |
| `rustchain_health` | Check node health across all 3 attestation nodes |
| `rustchain_transfer` | Send RTC (requires wallet key) |

## Bonus Tools (100 RTC)

| Tool | Description |
|------|-------------|
| `rustchain_ledger` | Query transaction history |
| `rustchain_register_wallet` | Create a new wallet |
| `rustchain_bounties` | List open bounties with rewards |

## Node Configuration

- **Primary Node:** `https://50.28.86.131`
- **Fallback:** Node 2/3 (automatic failover)

## API Reference

```bash
# Health check
curl -sk https://50.28.86.131/health

# Get miners
curl -sk https://50.28.86.131/api/miners

# Get epoch
curl -sk https://50.28.86.131/epoch

# Check balance
curl -sk "https://50.28.86.131/wallet/balance?miner_id=WALLET_NAME"
```

## Usage Example

Once installed, you can use these tools in Claude Code:

```
Check the balance of wallet "testwallet"
→ rustchain_balance(miner_id="testwallet")

List all active miners
→ rustchain_miners()

Get current epoch info
→ rustchain_epoch()

Check health of all nodes
→ rustchain_health()

Send 10 RTC to another wallet
→ rustchain_transfer(from_wallet="sender", to_wallet="receiver", amount=10)
```

## Requirements

- Python 3.8+
- `mcp` package
- `requests` package

## License

MIT
