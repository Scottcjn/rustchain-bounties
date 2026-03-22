# RustChain Python SDK

[![PyPI version](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org/project/rustchain/)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

Python SDK for interacting with [RustChain](https://github.com/Scottcjn/rustchain-bounties) nodes. Provides both async (`aiohttp`) and sync (`requests`) interfaces with full type hints.

## Install

```bash
pip install rustchain
```

## Quickstart

### Async

```python
import asyncio
from rustchain import RustChainClient

async def main():
    async with RustChainClient() as client:
        health = await client.health()
        print(f"Node OK: {health.version}")

        epoch = await client.epoch()
        print(f"Epoch {epoch.epoch}, Slot {epoch.slot}")

        balance = await client.balance("0xYourPublicKey")
        print(f"Balance: {balance} RTC")

        blocks = await client.explorer.blocks()
        for block in blocks:
            print(f"Block: {block}")

asyncio.run(main())
```

### Sync

```python
from rustchain.client import RustChainSyncClient

with RustChainSyncClient() as client:
    health = client.health()
    print(f"OK: {health.ok}")

    stats = client.stats()
    print(f"Miners: {stats.total_miners}")
    print(f"Supply: {stats.total_supply_rtc} RTC")
```

### CLI

```bash
# Check node health
rustchain health

# System statistics
rustchain stats

# Current epoch
rustchain epoch

# Check balance
rustchain balance 0xYourPublicKey

# List miners
rustchain miners

# Custom node
rustchain --node https://your-node.example.com health
```

## API Methods

| Method | Description |
|--------|-------------|
| `health()` | Node health check |
| `stats()` | System-wide statistics |
| `epoch()` | Current epoch info |
| `balance(miner_pk)` | Check RTC balance |
| `miners()` | List active miners |
| `attest_challenge(miner_pk)` | Get attestation challenge |
| `attest_submit(...)` | Submit attestation |
| `epoch_enroll(miner_pk)` | Enroll in current epoch |
| `withdraw_register(...)` | Register withdrawal key |
| `withdraw_request(...)` | Request withdrawal |
| `withdraw_history(miner_pk)` | Withdrawal history |
| `withdraw_status(id)` | Check withdrawal status |
| `metrics()` | Prometheus metrics |
| `explorer.blocks()` | Recent blocks |
| `explorer.transactions()` | Recent transactions |

## Error Handling

```python
from rustchain import (
    RustChainError,
    NodeUnhealthyError,
    MinerNotFoundError,
    RateLimitError,
    BadRequestError,
)

try:
    balance = await client.balance("0xinvalid")
except MinerNotFoundError:
    print("Miner not found")
except RateLimitError:
    print("Rate limited — slow down")
```

## Configuration

```python
# Custom node URL
client = RustChainClient(base_url="https://your-node.local")

# Enable SSL verification
client = RustChainClient(verify_ssl=True)

# Custom timeout
client = RustChainClient(timeout=60)
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT License — Copyright (c) 2026 思捷娅科技 (SJYKJ)
