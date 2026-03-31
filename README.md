# RustChain Python SDK

> Python SDK for the [RustChain](https://github.com/Scottcjn/Rustchain) Proof-of-Antiquity blockchain node API.
> Bounty issue: [#36 – RustChain Python SDK](https://github.com/Scottcjn/rustchain-bounties/issues/36)

## Install

```bash
# Install from GitHub (recommended for latest version)
pip install git+https://github.com/Scottcjn/rustchain-bounties.git

# Or clone and install locally
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties
pip install -e .
```

## Quick Start

```python
from rustchain import RustChainClient

# Connect to the public RustChain node
# (SSL verification disabled for self-signed certificates)
client = RustChainClient(
    base_url="https://rustchain.org",
    verify_ssl=False,
)

# Check node health
health = client.health()
print(f"Node OK: {health.ok}, version: {health.version}")
print(f"Uptime: {health.uptime_s}s, DB writable: {health.db_rw}")

# Get current epoch
epoch = client.get_epoch()
print(f"Epoch {epoch.epoch}, slot {epoch.slot}/{epoch.blocks_per_epoch}")
print(f"Pot: {epoch.epoch_pot} RTC  |  Enrolled miners: {epoch.enrolled_miners}")

# List active miners
miners = client.get_miners()
for m in miners:
    print(f"  {m.miner[:30]:<30} {m.hardware_type:<30} mult={m.antiquity_multiplier}x")

# Check wallet balance
bal = client.get_balance("eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC")
print(f"Balance: {bal.amount_rtc} RTC  ({bal.amount_i64} micro-RTC)")

# Check lottery eligibility
le = client.get_lottery_eligibility("eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC")
print(f"Eligible: {le.eligible}, reason: {le.reason}")
print(f"Rotation size: {le.rotation_size} miners, slot: {le.slot}")

# View transfer history
history = client.get_wallet_history("eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC", limit=10)
for tx in history:
    print(f"  {tx.direction} {tx.amount_rtc} RTC → {tx.counterparty} [{tx.status}]")

client.close()  # or use `with` block
```

## Attestation

```python
from rustchain.models import Fingerprint
from rustchain.exceptions import AttestationError

# Build hardware fingerprint from probe results
fp = Fingerprint(
    clock_skew={"value_ns": 1234, "drift_ppm": 12.3},
    cache_timing={"l1_latency_ns": 1.2, "l2_latency_ns": 4.5},
    simd_identity={"alv": True, "simd_width": 128},
    thermal_entropy={"drift": 0.5, "sample_count": 100},
    instruction_jitter={"jitter_ps": 10.0, "std_dev": 0.3},
    behavioral_heuristics={"hypervisor": False, "container": False},
)

try:
    result = client.submit_attestation(
        miner_id="my-miner-id",
        fingerprint=fp,
        signature="<base64_ed25519_signature>",
    )
    print(f"Enrolled: {result.enrolled}, multiplier: {result.multiplier}x")
    print(f"Next settlement slot: {result.next_settlement_slot}")
except AttestationError as e:
    print(f"Attestation failed: {e.code} — {e.check_failed}: {e.detail}")
```

## Signed Transfer

```python
from rustchain.exceptions import TransferError, InsufficientBalanceError

try:
    tx = client.signed_transfer(
        from_address="RTCaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        to_address="RTCbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        amount_rtc=1.0,
        nonce=12345,           # must be incrementing per sender
        public_key="<ed25519_public_key_hex>",
        signature="<ed25519_signature_hex>",
        memo="payment",
        chain_id="rustchain-mainnet-v2",
    )
    print(f"Tx submitted: {tx.tx_hash}")
    print(f"Verified: {tx.verified}, phase: {tx.phase}")
    print(f"Confirmations in: {tx.confirms_in_hours}h")
except InsufficientBalanceError as e:
    print(f"Not enough RTC: have {e.available}, need {e.required}")
except TransferError as e:
    print(f"Transfer failed: {e.tx_hash}")
```

## Exception Handling

```python
from rustchain import RustChainClient
from rustchain.exceptions import (
    RustChainError,
    NodeUnreachableError,
    RateLimitError,
    AttestationError,
    TransferError,
    MinerNotFoundError,
    InvalidSignatureError,
    InsufficientBalanceError,
)

client = RustChainClient(base_url="https://rustchain.org", verify_ssl=False)

try:
    client.get_balance("non-existent-miner")
except MinerNotFoundError as e:
    print(f"Unknown miner: {e.miner_id}")
except RateLimitError:
    print("Slow down — rate limited")
except NodeUnreachableError:
    print("Node is down or unreachable")
except RustChainError as e:
    print(f"RustChain error {e.code}: {e}")
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_url` | `https://rustchain.org` | RustChain node base URL |
| `verify_ssl` | `True` | Set `False` for self-signed certificates |
| `timeout` | `30` | Request timeout in seconds |
| `max_retries` | `5` | Max retry attempts for 5xx/429 errors |

## SSL / Self-Signed Certificates

Private nodes often use self-signed TLS certificates. Pass `verify_ssl=False` to disable verification:

```python
client = RustChainClient(
    base_url="https://50.28.86.131",
    verify_ssl=False,
)
```

For production, prefer installing the node's CA certificate system-wide instead of disabling verification.

## Retry Behavior

The SDK uses exponential back-off with jitter for transient failures (HTTP 429, 5xx). The default retry strategy:

- **Total attempts**: 5
- **Back-off factor**: 0.5s × (2 ^ attempt)
- **Retried status codes**: 429, 500, 502, 503, 504

## Supported Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `client.health()` | `GET /health` | Node health and version |
| `client.get_epoch()` | `GET /epoch` | Current epoch details |
| `client.get_miners()` | `GET /api/miners` | Active enrolled miners |
| `client.get_balance(miner_id)` | `GET /wallet/balance` | Wallet RTC balance |
| `client.get_wallet_history(miner_id)` | `GET /wallet/history` | Transfer history |
| `client.get_lottery_eligibility(miner_id)` | `GET /lottery/eligibility` | Lottery eligibility |
| `client.submit_attestation(...)` | `POST /attest/submit` | Hardware attestation |
| `client.signed_transfer(...)` | `POST /wallet/transfer/signed` | Signed RTC transfer |

## Running Tests

```bash
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

## Wallet Address for Bounty Payout

```
0x4304329306B8Ab663888705818A0baAA8297f1E9
```

## License

MIT
