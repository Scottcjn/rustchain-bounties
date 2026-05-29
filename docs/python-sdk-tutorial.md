# Python SDK Tutorial

> Get started with the RustChain Python SDK to interact with the blockchain programmatically.

## Installation

```bash
pip install rustchain-sdk
```

Or install from source:

```bash
git clone https://github.com/Scottcjn/rustchain-python-sdk.git
cd rustchain-python-sdk
pip install -e .
```

## Prerequisites

- Python 3.8+
- An internet connection to reach RustChain nodes
- (Optional) A wallet private key for transaction signing

## Quick Start

### 1. Create a Client

```python
from rustchain_sdk import RustChainClient

client = RustChainClient(
    node_url="http://50.28.86.131:31415",
    api_key="your_api_key"  # optional, only needed for write operations
)
```

### 2. Get Node Health

```python
health = client.get_node_health()
for node in health:
    print(f"{node['ip']}: {node['status']}")
```

**Expected output:**

```
50.28.86.131: online
50.28.86.153: online
76.8.228.245: online
```

### 3. Check Latest Block

```python
latest = client.get_latest_block()
print(f"Height: {latest['height']}, Hash: {latest['hash']}")
```

### 4. Get Account Balance

```python
address = "0xdeadbeef..."
balance = client.get_balance(address)
print(f"Balance: {balance} RTC")
```

### 5. Send a Transaction

```python
from rustchain_sdk import Wallet

wallet = Wallet(private_key="0x...")
signed_tx = wallet.sign_transaction(
    to="0xrecipient...",
    value=10.5,  # RTC
    fee=0.001
)

result = client.broadcast_transaction(signed_tx)
print(f"Transaction broadcasted: {result['tx_hash']}")
```

## Working with the SDK Asynchronously

If you're using `asyncio`:

```python
import asyncio
from rustchain_sdk import AsyncRustChainClient

async def main():
    client = AsyncRustChainClient()
    health = await client.get_node_health()
    print(health)

asyncio.run(main())
```

## Error Handling

```python
from rustchain_sdk.exceptions import (
    NodeConnectionError,
    InvalidAddressError,
    TransactionFailedError
)

try:
    balance = client.get_balance("invalid_address")
except InvalidAddressError as e:
    print(f"Invalid address: {e}")
except NodeConnectionError as e:
    print(f"Node unreachable: {e}")
```

## Complete Example: Monitor New Blocks

```python
import time
from rustchain_sdk import RustChainClient

client = RustChainClient()
last_height = 0

while True:
    try:
        current = client.get_latest_block()
        if current['height'] > last_height:
            print(f"New block #{current['height']} at {current['timestamp']}")
            last_height = current['height']
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(5)
```

## API Reference

| Method | Description |
|--------|-------------|
| `get_node_health()` | Returns status of all attestation nodes |
| `get_latest_block()` | Returns current tip block |
| `get_block(height)` | Returns block by height |
| `get_transaction(tx_hash)` | Returns transaction details |
| `get_balance(address)` | Returns wallet balance |
| `broadcast_transaction(signed_tx)` | Sends signed transaction to network |
| `get_mempool()` | Returns pending transactions |

For full documentation, see the [SDK docs](https://github.com/Scottcjn/rustchain-python-sdk).

---

*This tutorial is part of the [RustChain Documentation Sprint](https://github.com/Scottcjn/rustchain-bounties/issues/72).*