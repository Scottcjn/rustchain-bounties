# RustChain Python SDK

[![PyPI version](https://badge.fury.io/py/rustchain.svg)](https://badge.fury.io/py/rustchain)
[![Python Support](https://img.shields.io/pypi/pyversions/rustchain.svg)](https://pypi.org/project/rustchain/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python SDK for interacting with [RustChain](https://github.com/Scottcjn/RustChain) nodes. Provides clean programmatic access to all public API endpoints with async support, type hints, and comprehensive error handling.

## Features

- 🚀 **Async Support** - Built on `httpx` with full async/await support
- 📝 **Type Hints** - Complete type annotations throughout
- 🔒 **Error Handling** - Typed exceptions for all error scenarios
- 🔧 **CLI Tool** - Command-line interface for quick interactions
- 📦 **Easy to Use** - Intuitive API design with context manager support

## Installation

```bash
pip install rustchain
```

## Quick Start

```python
import asyncio
from rustchain import RustChainClient

async def main():
    async with RustChainClient() as client:
        # Check node health
        health = await client.health()
        print(f"Node status: {health.status}")
        
        # Get current epoch
        epoch = await client.epoch()
        print(f"Current epoch: {epoch.current_epoch}")
        
        # Check wallet balance
        balance = await client.balance("my-wallet-id")
        print(f"Balance: {balance.balance} RTC")
        
        # List active miners
        miners = await client.miners(limit=10)
        for miner in miners:
            print(f"Miner {miner.id}: {miner.stake} RTC stake")
        
        # Get recent blocks
        blocks = await client.explorer.blocks(limit=5)
        for block in blocks.blocks:
            print(f"Block #{block.height} by {block.miner}")

asyncio.run(main())
```

## API Reference

### Client Initialization

```python
from rustchain import RustChainClient

# Default node URL
client = RustChainClient()

# Custom node URL
client = RustChainClient(base_url="http://custom-node:9100")

# With timeout and headers
client = RustChainClient(
    base_url="http://50.28.86.131:9100",
    timeout=60.0,
    headers={"X-Custom-Header": "value"}
)

# As context manager (recommended)
async with RustChainClient() as client:
    # Use client
    pass
```

### Methods

#### `health()`
Check node health status.

```python
health = await client.health()
# Returns: HealthStatus(status="healthy", version="1.0.0", uptime=3600, ...)
```

#### `epoch()`
Get current epoch information.

```python
epoch = await client.epoch()
# Returns: EpochInfo(current_epoch=100, start_height=1000, ...)
```

#### `miners(limit=100, active_only=True)`
List active miners.

```python
miners = await client.miners(limit=10)
# Returns: List[Miner]
```

#### `balance(wallet_id)`
Check wallet RTC balance.

```python
balance = await client.balance("wallet-id")
# Returns: Balance(wallet_id="...", balance=150.5, ...)
```

#### `transfer(from_address, to_address, amount, signature, fee=None)`
Transfer RTC between wallets.

```python
result = await client.transfer(
    from_address="sender-address",
    to_address="recipient-address",
    amount=10.0,
    signature="tx-signature"
)
# Returns: TransferResult(tx_hash="...", amount=10.0, ...)
```

#### `attestation_status(miner_id)`
Check miner attestation status.

```python
status = await client.attestation_status("miner-id")
# Returns: AttestationStatus(miner_id="...", status="active", ...)
```

### Explorer API

Access blockchain explorer methods via `client.explorer`.

```python
# Get recent blocks
blocks = await client.explorer.blocks(limit=10, page=1)

# Get specific block
block = await client.explorer.block(height=1000)

# Get recent transactions
txs = await client.explorer.transactions(limit=10, wallet="wallet-id")

# Get specific transaction
tx = await client.explorer.transaction(tx_hash="tx-hash")
```

## CLI Usage

The SDK includes a command-line interface for quick interactions:

```bash
# Check node health
rustchain health

# Get epoch info
rustchain epoch

# List miners
rustchain miners --limit 20

# Check wallet balance
rustchain balance WALLET_ID

# Transfer RTC
rustchain transfer FROM_ADDR TO_ADDR AMOUNT SIGNATURE

# Check attestation status
rustchain attestation MINER_ID

# Explorer commands
rustchain explorer blocks --limit 10
rustchain explorer block 1000
rustchain explorer transactions --limit 10
rustchain explorer transaction TX_HASH
```

### CLI Options

All commands support:

- `--url`: Custom RustChain node URL (default: http://50.28.86.131:9100)
- `--help`: Show command help

```bash
rustchain balance WALLET_ID --url http://custom-node:9100
```

## Error Handling

The SDK provides typed exceptions for all error scenarios:

```python
from rustchain import RustChainClient
from rustchain.exceptions import (
    ConnectionError,
    TimeoutError,
    ValidationError,
    NotFoundError,
    InsufficientFundsError,
    InvalidSignatureError,
)

async def safe_transfer():
    async with RustChainClient() as client:
        try:
            result = await client.transfer("from", "to", 100.0, "sig")
        except InsufficientFundsError:
            print("Not enough funds")
        except InvalidSignatureError:
            print("Invalid signature")
        except ValidationError as e:
            print(f"Validation error: {e.message}")
        except ConnectionError:
            print("Failed to connect to node")
        except TimeoutError:
            print("Request timed out")
```

### Exception Types

| Exception | Description |
|-----------|-------------|
| `ConnectionError` | Failed to connect to RustChain node |
| `TimeoutError` | Request timed out |
| `ValidationError` | Input validation failed (400) |
| `AuthenticationError` | Authentication failed (401) |
| `NotFoundError` | Resource not found (404) |
| `RateLimitError` | Rate limit exceeded (429) |
| `ServerError` | Server error (5xx) |
| `TransferError` | Transfer operation failed |
| `InsufficientFundsError` | Insufficient balance |
| `InvalidSignatureError` | Invalid signature |
| `AttestationError` | Attestation operation failed |

## Data Models

All responses are typed using Pydantic models:

```python
from rustchain.models import (
    HealthStatus,
    EpochInfo,
    Miner,
    Balance,
    TransferResult,
    Block,
    Transaction,
    AttestationStatus,
)
```

## Development

### Setup

```bash
git clone https://github.com/HuiNeng6/rustchain-bounties
cd rustchain-bounties/rustchain-sdk
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v --cov=rustchain
```

### Code Formatting

```bash
black rustchain/ tests/
isort rustchain/ tests/
```

### Type Checking

```bash
mypy rustchain/
```

## Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [RustChain GitHub](https://github.com/Scottcjn/RustChain)
- [RustChain Bounties](https://github.com/Scottcjn/rustchain-bounties)
- [PyPI Package](https://pypi.org/project/rustchain/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- [GitHub Issues](https://github.com/HuiNeng6/rustchain-bounties/issues)
- [RustChain Discord](https://discord.gg/VqVVS2CW9Q)