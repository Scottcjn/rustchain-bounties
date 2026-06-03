# RustChain Live Balance Verifier

Stdlib-only Python integration for the RustChain T2 bounty.

## What it checks

- `/health` returns a healthy live node.
- `/epoch` returns current epoch and slot data.
- `/api/miners` returns the live miner list.
- `/wallet/balance?miner_id=<wallet>` returns a balance for the requested native RTC wallet.
- The balance response is verified by wallet identity, numeric amount, and active-miner presence when applicable.

## Requirements

- Python 3.9 or newer.
- No third-party dependencies.

## Run

From this folder:

```bash
python rustchain_verify.py --wallet RTC14f06ee294f327f5685d3de5e1ed501cffab33e7
```

Or from the repository root:

```bash
python integrations/exal-gh-33/rustchain_verify.py --wallet RTC14f06ee294f327f5685d3de5e1ed501cffab33e7
```

Use a different native RTC wallet with `--wallet RTC...`.

## Payout

Native RTC payout wallet:

```text
RTCc0ffae7b0e9511b78551f71151f0e1819015a1c0
```

