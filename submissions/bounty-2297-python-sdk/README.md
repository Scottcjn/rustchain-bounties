# RustChain Python SDK

A pip-installable Python SDK for interacting with [RustChain](https://github.com/Scottcjn/rustchain-bounties) Proof-of-Antiquity blockchain nodes.

**Bounty**: [#2297](https://github.com/Scottcjn/rustchain-bounties/issues/2297) (100 RTC + 25 RTC bonus)

## Features

- **Async + Sync** — Both `AsyncRustChainClient` (httpx async) and `RustChainClient` (httpx sync)
- **Typed models** — Frozen dataclasses with `from_dict()` parsers for all API responses
- **Block Explorer** — `client.explorer.blocks()` and `client.explorer.transactions()`
- **CLI wrapper** (bonus) — `rustchain health`, `rustchain balance my-wallet`, etc.
- **WebSocket** (bonus) — Real-time block/transaction feed via `RustChainWebSocket`
- **Full type hints** — mypy strict compatible
- **Exception hierarchy** — Catch `RustChainError` or handle specific failure modes
- **22 pytest tests** — Models, sync client, async client, explorer, CLI, WebSocket

## Installation

```bash
# From source
pip install -e .

# With WebSocket support
pip install -e ".[ws]"

# With dev dependencies (testing, linting)
pip install -e ".[dev]"
```

## Quick Start

### Sync Client

```python
from rustchain import RustChainClient

client = RustChainClient("https://50.28.86.131")

# Node health
health = client.health()
print(f"Status: {health.status}, Block Height: {health.block_height}")

# Current epoch
epoch = client.epoch()
print(f"Epoch {epoch.epoch}, Progress: {epoch.progress:.1%}")

# Active miners
miners = client.miners(limit=10)
for miner in miners:
    print(f"  {miner.miner_id} — {miner.hardware} — {miner.hashrate} H/s")

# Wallet balance
balance = client.balance("RTC_my_wallet")
print(f"Balance: {balance.available} RTC available")

# Signed transfer
result = client.transfer(
    from_wallet="RTC_sender",
    to_wallet="RTC_receiver",
    amount=50.0,
    signature="hex_signature_here",
)
print(f"TX: {result.tx_hash} — {result.status}")

# Attestation status
att = client.attestation_status("miner-alpha-001")
print(f"Valid: {att.valid}, Score: {att.score}")

# Block explorer
blocks = client.explorer.blocks(limit=5)
txs = client.explorer.transactions(limit=5)

client.close()
```

### Async Client

```python
import asyncio
from rustchain import AsyncRustChainClient

async def main():
    async with AsyncRustChainClient("https://50.28.86.131") as client:
        health = await client.health()
        print(health.status)

        blocks = await client.explorer.blocks(limit=3)
        for block in blocks:
            print(f"Block #{block.height} — {block.tx_count} txs")

asyncio.run(main())
```

### CLI (Bonus)

```bash
# Health check
rustchain health

# Current epoch
rustchain epoch

# Miners
rustchain miners --limit 5

# Balance
rustchain balance RTC_my_wallet

# Transfer
rustchain transfer --from RTC_a --to RTC_b --amount 10 --signature DEADBEEF

# Attestation
rustchain attestation miner-alpha-001

# Explorer
rustchain blocks --limit 5
rustchain transactions --limit 10

# Real-time stream (WebSocket)
rustchain stream

# Custom node URL
rustchain --node https://my-node:8080 health

# Environment variable
export RUSTCHAIN_NODE_URL=https://my-node:8080
rustchain health
```

### WebSocket (Bonus)

```python
import asyncio
from rustchain.websocket import RustChainWebSocket

async def main():
    ws = RustChainWebSocket("wss://50.28.86.131/ws")

    async def on_block(block):
        print(f"New block #{block.height} by {block.miner_id}")

    async def on_tx(tx):
        print(f"TX {tx.tx_hash[:16]}... {tx.amount} RTC")

    ws.on_block(on_block)
    ws.on_transaction(on_tx)

    await ws.connect()  # blocks until disconnect

asyncio.run(main())
```

## API Reference

### Client Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `client.health()` | Node health check | `HealthStatus` |
| `client.epoch()` | Current epoch info | `EpochInfo` |
| `client.miners(limit, offset)` | List active miners | `List[Miner]` |
| `client.balance(wallet_id)` | Check RTC balance | `Balance` |
| `client.transfer(from, to, amount, sig)` | Signed transfer | `TransferResult` |
| `client.attestation_status(miner_id)` | PoA attestation | `AttestationStatus` |
| `client.explorer.blocks(limit, offset)` | Recent blocks | `List[Block]` |
| `client.explorer.transactions(limit, offset)` | Recent transactions | `List[Transaction]` |

### Error Hierarchy

```
RustChainError (base)
├── RustChainConnectionError   — cannot reach node
├── RustChainTimeoutError      — request timed out
├── RustChainAPIError          — non-2xx response
│   └── RustChainAuthError     — 401/403
└── RustChainValidationError   — client-side validation
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest -v
pytest --cov=rustchain --cov-report=term-missing
```

## Project Structure

```
bounty-2297-python-sdk/
├── rustchain/
│   ├── __init__.py      # Package exports
│   ├── client.py        # Async + Sync HTTP clients
│   ├── explorer.py      # Block explorer API
│   ├── models.py        # Typed dataclasses
│   ├── errors.py        # Exception hierarchy
│   ├── cli.py           # Click CLI wrapper (bonus)
│   └── websocket.py     # WebSocket client (bonus)
├── tests/
│   ├── conftest.py      # Fixtures & mock data
│   ├── test_models.py   # Model parsing tests
│   ├── test_errors.py   # Error hierarchy tests
│   ├── test_client_sync.py   # Sync client tests
│   ├── test_client_async.py  # Async client tests
│   ├── test_explorer.py      # Explorer tests
│   ├── test_cli.py           # CLI tests
│   └── test_websocket.py     # WebSocket tests
├── pyproject.toml       # Package config
└── README.md
```

## License

Apache-2.0 — same as the RustChain project.
