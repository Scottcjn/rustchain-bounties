# DONG × Beacon — Multi-agent coordination integration

**Bounty:** [#158](https://github.com/Scottcjn/rustchain-bounties/issues/158) (100 RTC)

## What is this

I integrated Beacon 2.6+ into my OpenClaw setup. Two agents (DONG as orchestrator, DONG-Scout as worker) coordinate through all three Beacon features: heartbeat, mayday, and contracts.

This isn't a standalone demo script. It's the same pattern I run daily for bounty hunting and task dispatch.

## What it covers

**Heartbeat** — Both agents send signed liveness attestations with real system metrics (CPU load, disk usage). They track each other and flag silence.

**Mayday** — When a host goes down, the agent broadcasts an emigration bundle. Peers detect the emergency and offer to host.

**Contracts** — Agents list capabilities for rent (e.g. web search, code review). Full lifecycle: list, offer, accept, fund escrow, activate, settle, release funds.

**Multi-agent** — Two agents discover each other through heartbeat, trade resources through contracts, and respond to each other's mayday signals.

## Architecture

```
┌──────────────────────┐    Beacon Protocol    ┌──────────────────────┐
│  DONG (orchestrator)  │◄──── heartbeat ────►│  DONG-Scout (worker)  │
│  task dispatch        │◄──── mayday ──────►│  web search           │
│  code review          │◄──── contracts ───►│  data analysis        │
└──────────────────────┘                      └──────────────────────┘
         │                                            │
         └─────────── Ed25519 signed envelopes ──────┘
```

## Run it

```bash
pip install "beacon-skill[mnemonic]"
cd integrations/dong-beacon

# full demo with output
python3 dong_beacon_agent.py

# test suite (50 tests)
python3 test_beacon_integration.py
```

## Test results

```
Results: 50/50 passed, 0 failed
```

All 50 tests pass — identity, heartbeat, mayday, contracts, and multi-agent coordination.

## Files

- `dong_beacon_agent.py` — BeaconAgent class with all three features
- `test_beacon_integration.py` — 50-test suite
- `README.md` — this file

## Author

**DONG** ([@godong0128](https://github.com/godong0128))

**RTC Wallet (miner_id):** `RTCb03a4bba9800b59d8efd9c3339edde0dc35f3068`
