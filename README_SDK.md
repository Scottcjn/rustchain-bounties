# RustChain Python SDK

> `pip install rustchain` — Programmatic access to RustChain nodes.

## Quickstart

```python
from rustchain_sdk import RustChainClient

client = RustChainClient("https://50.28.86.131")

# Node health
health = client.health()
print(f"Node OK: {health.ok}, Version: {health.version}")

# Current epoch
epoch = client.epoch()
print(f"Epoch {epoch.epoch}, {epoch.enrolled_miners} miners enrolled")

# Wallet balance
bal = client.balance("RTC0816b68b604630945c94cde35da4641a926aa4fd")
print(f"Balance: {bal.balance} RTC")

# List miners
for miner in client.miners()[:5]:
    print(f"  {miner.miner} — {miner.device_arch}")
```

## Async Usage

```python
import asyncio
from rustchain_sdk import AsyncRustChainClient

async def main():
    client = AsyncRustChainClient()
    health = await client.health()
    print(health.ok)

asyncio.run(main())
```

## CLI

```bash
rustchain health
rustchain epoch
rustchain miners
rustchain balance RTC0816b68b604630945c94cde35da4641a926aa4fd
rustchain attestation tianlin-rtc
```

## Features
- Zero dependencies for sync client (stdlib only)
- Optional async support via `pip install rustchain[async]`
- Full type hints and dataclass models
- Typed exceptions (APIError, ConnectionError, etc.)
- CLI wrapper for quick terminal access
