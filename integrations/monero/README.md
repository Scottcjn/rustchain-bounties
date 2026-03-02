# Monero (RandomX) Integration for RustChain

This integration enables dual-mining proof verification for Monero (XMR) miners participating in the RustChain network.

## Overview

Monero uses the **RandomX** proof-of-work algorithm, which is CPU-optimized and ASIC-resistant. This makes it an ideal candidate for RustChain's dual-mining approach, where miners can earn RTC rewards while mining XMR.

### Key Benefits

- **CPU-optimized**: RandomX uses 100% of CPU for hashing
- **Negligible RIP-PoA impact**: RustChain attestation runs for 5 seconds every 10 minutes
- **Multiple proof types**: Node RPC, P2Pool, pool accounts, and process detection
- **Bonus multipliers**: Up to 1.5x RTC rewards for verified proofs

## Installation

```bash
# Clone the repository
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties/integrations/monero

# Make the script executable
chmod +x monero_integration.py
```

## Usage

### Node RPC Proof (1.5x Bonus)

Query your local monerod daemon for block height, difficulty, and network info:

```bash
python3 monero_integration.py --proof-type node --wallet YOUR_WALLET
```

This queries `localhost:18081/json_rpc` with the `get_info` method.

**Requirements:**
- Running monerod daemon on localhost:18081
- Wallet can be any identifier (Monero address or RustChain miner ID)

**Example Output:**
```json
{
  "proof_type": "node_rpc",
  "timestamp": "2026-03-02T12:00:00Z",
  "wallet": "YOUR_WALLET",
  "success": true,
  "data": {
    "host": "localhost",
    "port": 18081,
    "block_height": 3045678,
    "difficulty": 350000000000,
    "tx_pool_size": 45,
    "network_hashrate": 2800000000,
    "proof_hash": "abc123..."
  },
  "rustchain_bonus_multiplier": 1.5
}
```

### P2Pool Proof

Query your local P2Pool node for mining statistics:

```bash
python3 monero_integration.py --proof-type p2pool --wallet YOUR_WALLET
```

This queries `localhost:18083/local/stats`.

**Requirements:**
- Running P2Pool node on localhost:18083
- Wallet should match your P2Pool miner address

### Pool Account Proof (1.3x Bonus)

Verify your mining activity on supported pools:

```bash
# Nanopool (default)
python3 monero_integration.py --proof-type pool --pool nanopool --wallet YOUR_WALLET

# HeroMiners
python3 monero_integration.py --proof-type pool --pool herominers --wallet YOUR_WALLET
```

**Requirements:**
- Active mining account on the specified pool
- Wallet must be your pool payout address

### Process Detection

Detect running Monero mining processes:

```bash
python3 monero_integration.py --proof-type process --wallet YOUR_WALLET
```

**Detects:**
- xmrig (most popular RandomX miner)
- monerod (Monero daemon)
- p2pool (P2Pool node)
- xmr-stak (legacy miner)

### Run All Proofs

Execute all proof types and get a comprehensive report:

```bash
python3 monero_integration.py --proof-type all --wallet YOUR_WALLET
```

### RustChain Claim Format

Generate claims in RustChain-compatible format:

```bash
python3 monero_integration.py --proof-type all --wallet YOUR_WALLET --output rustchain
```

## API Reference

### Monero Daemon RPC

| Endpoint | Method | Description |
|----------|--------|-------------|
| `localhost:18081/json_rpc` | `get_info` | Get block height, difficulty, tx pool size |
| `localhost:18082/json_rpc` | `get_info` | Restricted RPC (limited info) |

### P2Pool API

| Endpoint | Description |
|----------|-------------|
| `localhost:18083/local/stats` | Local miner statistics |
| `localhost:18083/network/stats` | Network-wide statistics |

### Pool APIs

| Pool | API Endpoint |
|------|--------------|
| Nanopool | `https://xmr.nanopool.org/api2/v1/account/{address}` |
| HeroMiners | `https://xmr.herominers.com/api/stats/{address}` |

## Bonus Multipliers

| Proof Type | Multiplier | Description |
|------------|------------|-------------|
| Node RPC | 1.5x | Direct daemon verification |
| Pool Account | 1.3x | Verified pool mining |
| P2Pool | 1.0x | Decentralized pool mining |
| Process | 1.0x | Local process detection |

## Integration with RustChain

The proof results can be submitted to RustChain for RTC rewards:

1. Run the appropriate proof command for your mining setup
2. Include the proof JSON in your RustChain attestation
3. The `proof_hash` field provides cryptographic verification
4. Bonus multipliers are automatically applied to your RTC rewards

## Example: Complete Dual-Mining Setup

```bash
# 1. Start Monero daemon
monerod --detach

# 2. Start XMRig miner
xmrig -o pool.nanopool.org:14444 -u YOUR_WALLET

# 3. Verify mining (every 10 minutes for RustChain attestation)
python3 monero_integration.py --proof-type all --wallet YOUR_WALLET --output rustchain > proof.json

# 4. Submit proof.json to RustChain node during attestation window
curl -X POST https://rustchain-node/attest \
  -H "Content-Type: application/json" \
  -d @proof.json
```

## Troubleshooting

### Connection Refused

If you get "Connection refused" errors:
- Ensure monerod/P2Pool is running
- Check the correct port (18081 for monerod, 18083 for P2Pool)
- Verify firewall settings allow localhost connections

### No Processes Detected

If process detection returns empty:
- Ensure mining software is actually running
- Check process names match (xmrig, monerod, etc.)
- Try running with `sudo` if permissions are an issue

### Pool API Errors

If pool verification fails:
- Verify your wallet address is correct
- Check pool API status (may be temporarily down)
- Ensure you have mining activity on the pool

## Security Notes

- Never share your private keys
- The integration only reads public information
- All connections to local daemons use localhost (no network exposure)
- Pool API connections use HTTPS where available

## Contributing

Contributions welcome! Please submit PRs to the rustchain-bounties repository.

## License

MIT License - See main repository LICENSE file.

## Support

For issues or questions:
- GitHub Issues: https://github.com/Scottcjn/rustchain-bounties/issues
- Bounty Issue: https://github.com/Scottcjn/rustchain-bounties/issues/458
