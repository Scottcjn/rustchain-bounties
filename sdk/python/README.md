# RustChain Python SDK

> A full-featured Python SDK for the RustChain blockchain. Interact with the chain from any Python script, bot, or AI agent.

**pip install rustchain-sdk**

## Features

- **Full API Coverage**: health, wallet, miners, epoch, attestation, transfer, lottery
- **Zero Dependencies**: Uses only Python stdlib (`http.client`)
- **SSL Flexibility**: Handles self-signed certificates automatically
- **Type Hints**: Full type annotations for IDE support
- **Retry Logic**: Built-in retry with exponential backoff
- **Rich Errors**: Custom exception hierarchy

## Quick Start

```python
from rustchain import RustChain

rc = RustChain()

# Check node health
health = rc.health()
print(f"Node online: {health['ok']}")
print(f"Version: {health['version']}")

# Get wallet balance
balance = rc.get_balance("nox-ventures")
print(f"Balance: {balance['balance']} RTC")

# Check miners
miners = rc.get_miners(limit=5)
for m in miners["miners"]:
    print(f"  {m['miner']} — ×{m['antiquity_multiplier']:.3f}")

# Get epoch info
epoch = rc.get_epoch()
print(f"Epoch {epoch['current_epoch']} — next in {epoch['time_to_next_epoch']}")
```

## Installation

```bash
pip install rustchain-sdk
```

Or from source:

```bash
git clone https://github.com/Scottcjn/rustchain-bounties
cd rustchain-bounties/sdk
pip install -e .
```

## Configuration

```python
from rustchain import RustChain

# Default: connects to https://50.28.86.131
rc = RustChain()

# Custom node URL
rc = RustChain(node_url="https://your-node.example.com:8099")

# Longer timeout
rc = RustChain(timeout=30)
```

## API Reference

### `RustChain.node_url`

The URL of the RustChain node. Default: `https://50.28.86.131`.

### Health

```python
rc.health()          # Full health check — returns node status dict
rc.is_online()       # Boolean — is the node reachable?
```

### Wallet

```python
rc.get_balance(wallet)        # Get RTC balance for a wallet
rc.create_wallet(name)        # Register a new wallet
```

### Miners

```python
rc.get_miners(limit=10)       # List miners (sorted by antiquity)
rc.get_miner(miner_id)       # Get specific miner info
rc.is_miner_active(miner_id) # Bool — is miner attesting?
```

### Epoch

```python
rc.get_epoch()  # Returns:
                # {
                #   "current_epoch": int,
                #   "slots_elapsed": int,
                #   "slots_remaining": int,
                #   "time_to_next_epoch": "3h 21m",
                #   "uptime_seconds": int
                # }
```

### Network

```python
rc.network_stats()  # Full network overview (node + miners + epoch)
```

### Lottery

```python
rc.lottery_eligibility(wallet)  # Check if wallet is lottery-eligible
```

### Attestation

```python
rc.submit_attestation(wallet, hardware_fingerprint, signature)
```

### Transfer

```python
rc.transfer(from_wallet, to_wallet, amount)
```

### Retry

```python
rc.get_with_retry("/api/miners", retries=3, delay=1.0)
```

## Error Handling

```python
from rustchain import RustChain, RustChainError, NodeOfflineError, APIError

rc = RustChain()

try:
    balance = rc.get_balance("my-wallet")
except NodeOfflineError:
    print("Node is offline — try again later")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
except RustChainError as e:
    print(f"RustChain error: {e}")
```

## Architecture

```
sdk/
├── src/
│   └── rustchain/
│       ├── __init__.py      — Package init + public exports
│       ├── client.py        — RustChain client (core API)
│       └── exceptions.py     — Custom exceptions
├── tests/
│   └── test_client.py       — Unit tests
├── pyproject.toml            — Package config
└── README.md                — This file
```

## Use Cases

**AI Agents**: Give your agent a RustChain wallet:

```python
rc = RustChain()
agent_wallet = "my-agent-001"
balance = rc.get_balance(agent_wallet)
```

**Monitoring Scripts**: Monitor your miners:

```python
rc = RustChain()
for miner in rc.get_miners()["miners"]:
    if not miner["is_active"]:
        print(f"ALERT: {miner['miner']} is offline!")
```

**Bounty Hunters**: Track earnings automatically:

```python
rc = RustChain()
my_balance = rc.get_balance("my-bounty-wallet")
print(f"Total earned: {my_balance['balance']} RTC")
```

## License

MIT
