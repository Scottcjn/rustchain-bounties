# RustChain Python SDK

A clean, async-first Python SDK for the [RustChain Proof-of-Antiquity](https://rustchain.org) blockchain network.

**Install:**

```bash
pip install rustchain
```

## Quickstart

```python
import asyncio
from rustchain import RustChainClient, ExplorerClient

# Sync usage
client = RustChainClient()
health = client.health()
print(f"Node healthy: {health['ok']}")

# Async usage
async def main():
    client = RustChainClient()
    health = await client.health_async()
    epoch = await client.epoch_async()
    miners = await client.miners_async(limit=10)
    balance = await client.balance_async("my-wallet")

asyncio.run(main())

# Block explorer
explorer = ExplorerClient()
blocks = explorer.blocks(limit=20)
txs = explorer.transactions(wallet_id="my-wallet")
```

## Features

- **Async throughout** — All methods have `async` equivalents (`*_async`)
- **Full type hints** — Typed inputs and outputs for IDE support
- **20+ unit tests** — Well-tested with mocked HTTP responses
- **CLI tool** — `rustchain balance <wallet>` from your terminal
- **Clean error hierarchy** — `APIError`, `ValidationError`, `TransferError`, etc.

## API Reference

### `RustChainClient`

| Method | Description |
|--------|-------------|
| `health()` | Node health check |
| `epoch()` | Current epoch info |
| `miners(limit, offset)` | List active miners |
| `balance(wallet_id)` | Check RTC balance for a wallet |
| `transfer(from, to, amount, signature)` | Submit a signed RTC transfer |
| `attestation_status(miner_id)` | Check attestation status for a miner |
| `lottery_eligibility(miner_id)` | Check lottery eligibility |
| `submit_attestation(payload)` | Submit attestation to the network |
| `stats()` | Network-wide statistics |

### `ExplorerClient`

| Method | Description |
|--------|-------------|
| `blocks(limit)` | Recent blocks |
| `transactions(wallet_id, block_hash, limit)` | Transactions, optionally filtered |
| `block_detail(block_hash)` | Detailed block info |
| `transaction_detail(tx_hash)` | Detailed transaction info |

## CLI

```bash
# Check node health
rustchain health

# Get current epoch
rustchain epoch

# List active miners
rustchain miners
rustchain miners --limit 50

# Check wallet balance
rustchain balance my-wallet

# Explore recent blocks
rustchain blocks
rustchain blocks --limit 100

# Explore transactions
rustchain txs
rustchain txs my-wallet --limit 50
```

## Error Handling

```python
from rustchain import RustChainClient
from rustchain.exceptions import (
    RustChainError,
    APIError,
    ValidationError,
    TransferError,
    NetworkError,
)

client = RustChainClient()

try:
    balance = client.balance("my-wallet")
except ValidationError as e:
    print(f"Invalid wallet ID: {e.message}")
except APIError as e:
    print(f"API error ({e.status_code}): {e.message}")
except NetworkError as e:
    print(f"Network issue: {e.message}")
```

## WebSocket Support (Bonus)

For real-time block feeds, use the standard `websockets` library alongside the SDK:

```python
import asyncio
import websockets
import json

async def watch_blocks():
    uri = "wss://50.28.86.131/ws/blocks"
    async with websockets.connect(uri) as ws:
        async for msg in ws:
            block = json.loads(msg)
            print(f"New block: {block['height']}")

asyncio.run(watch_blocks())
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=rustchain

# Build package
pip install build
python -m build
```

## License

MIT
