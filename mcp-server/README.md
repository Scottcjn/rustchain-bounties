# RustChain MCP Server

Query the RustChain blockchain directly from Claude Code.

**Reward: 75-100 RTC**

## Installation

```bash
# Install dependencies
pip install mcp

# Clone this repository
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties/mcp-server

# Test it works
python server.py health
python server.py balance Ivan-houzhiwen
```

## Claude Code Integration

Add to your Claude Code config:

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "python",
      "args": ["/path/to/rustchain-bounties/mcp-server/server.py"]
    }
  }
}
```

Or use `claude mcp add`:

```bash
claude mcp add rustchain python /path/to/rustchain-bounties/mcp-server/server.py
```

## Available Tools

### rustchain_health
Check node health across all 3 attestation nodes.

### rustchain_miners
List active miners and their architectures.

### rustchain_epoch
Get current epoch info (slot, height, rewards).

### rustchain_balance
Check RTC balance for any wallet.

### rustchain_hall_of_fame
Query the hall of fame for top miners.

### rustchain_fee_pool
Check the fee pool statistics.

### rustchain_stats
Get chain statistics.

## Usage Examples

```bash
# Check node health
$ python server.py health
{
  "primary": {"ok": true, "data": {"ok": true, "version": "2.2.1-rip200"}},
  "summary": "3/3 nodes healthy"
}

# Check balance
$ python server.py balance Ivan-houzhiwen
{"amount_rtc": 155.0, "miner_id": "Ivan-houzhiwen"}

# List miners
$ python server.py miners 5
{"miners": [...], "total_shown": 5}
```

## API Endpoints

- Primary Node: `https://50.28.86.131`
- Node 2: `https://50.28.86.132`
- Node 3: `https://50.28.86.133`

## License

MIT
