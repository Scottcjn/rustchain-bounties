# clawrtc Test Suite

Comprehensive pytest suite for the `clawrtc` Python package.

## Coverage

- **Wallet creation** — Coinbase Base wallet creation, linking, validation
- **Balance checking** — Network balance queries with error handling
- **Miner attestation flow** — Challenge/response attestation with mocked RPC
- **Hardware fingerprint checks** — 7 RIP-PoA checks (clock drift, cache timing, SIMD identity, thermal drift, instruction jitter, anti-emulation, ROM fingerprint)
- **PoW miner detection** — Multi-chain dual-mining proof generation
- **BCOS engine** — Beacon Certified Open Source verification engine
- **Full lifecycle integration** — attest → enroll → balance end-to-end

## Running Tests

```bash
pip install pytest requests
python -m pytest clawrtc/tests/ -v
```

## Requirements

- Python 3.10+
- pytest
- requests
- cryptography (installed by clawrtc)
