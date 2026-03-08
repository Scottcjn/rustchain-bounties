# RustChain MCP Server 🦀⛓️

Query the RustChain blockchain directly from Claude Code.

## Installation

```bash
# Clone or download
git clone https://github.com/ai-carti/rustchain-mcp.git
cd rustchain-mcp

# Install dependencies
pip install mcp httpx

# Add to Claude Code
claude mcp add rustchain python rustchain_mcp.py
```

## Available Tools

### Required (75 RTC)

| Tool | Description |
|------|-------------|
| `rustchain_balance` | Check RTC balance for any wallet |
| `rustchain_miners` | List active miners and their hardware |
| `rustchain_epoch` | Get current epoch info (slot, rewards, supply) |
| `rustchain_health` | Check node health and uptime |
| `rustchain_transfer` | Prepare RTC transfer (unsigned) |

### Bonus (100 RTC)

| Tool | Description |
|------|-------------|
| `rustchain_ledger` | Query transaction history |
| `rustchain_register_wallet` | Get wallet registration info |
| `rustchain_bounties` | List open bounties from GitHub |

## Usage Examples

Once installed, ask Claude:

```
Check the balance of wallet "achieve-github-bounty"
```

```
Show me the current RustChain epoch info
```

```
List the top 10 active miners
```

```
Is the RustChain node healthy?
```

```
What bounties are available?
```

## Demo

```bash
# Test the server locally
python rustchain_mcp.py

# Or run with MCP inspector
npx @modelcontextprotocol/inspector python rustchain_mcp.py
```

## Configuration

The server connects to the primary RustChain node at `https://50.28.86.131`. Failover nodes are configured for redundancy.

## Requirements

- Python 3.10+
- `mcp` package
- `httpx` package

## Author

Built by [Playboi Carti](https://github.com/ai-carti) 🦋

## License

MIT
