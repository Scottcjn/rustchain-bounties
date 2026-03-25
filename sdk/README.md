# RustChain Python SDK

Python SDK for interacting with [RustChain](https://github.com/Scottcjn/rustchain-bounties) nodes — the Proof of Antiquity blockchain.

## Install

```bash
pip install rustchain
```

For async support:
```bash
pip install rustchain[async]
```

## Quick Start

```python
from rustchain import RustChainClient

client = RustChainClient()

# Check node health
health = client.health()
print(health)

# Current epoch
epoch = client.epoch()
print(f"Epoch: {epoch}")

# List miners
miners = client.miners()
for m in miners:
    print(m)

# Check balance
balance = client.balance("my-wallet-id")
print(f"Balance: {balance}")

# Attestation status
status = client.attestation_status("miner-123")

# Explorer
blocks = client.explorer.blocks(limit=5)
txns = client.explorer.transactions(limit=5)
```

## Async Usage

```python
import asyncio
from rustchain import AsyncRustChainClient

async def main():
    async with AsyncRustChainClient() as client:
        health = await client.health()
        miners = await client.miners()
        blocks = await client.explorer.blocks()
        print(health, miners, blocks)

asyncio.run(main())
```

## CLI

```bash
rustchain health
rustchain epoch
rustchain miners
rustchain balance my-wallet-id
rustchain blocks --limit 5
rustchain transactions --limit 10
```

## Error Handling

```python
from rustchain import RustChainClient
from rustchain.exceptions import APIError, ConnectionError, ValidationError

try:
    client = RustChainClient()
    balance = client.balance("")  # raises ValidationError
except ValidationError as e:
    print(f"Bad input: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
except ConnectionError as e:
    print(f"Can't connect: {e}")
```

## License

MIT
