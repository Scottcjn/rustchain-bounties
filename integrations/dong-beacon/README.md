# DONG × Beacon — Multi-Agent Coordination Integration

**Bounty:** [#158 — Integrate Beacon into your AI agent (100 RTC)](https://github.com/Scottcjn/rustchain-bounties/issues/158)

## What This Is

A real-world integration of **Beacon 2.6+** into [OpenClaw](https://github.com/openclaw/openclaw) AI agents, demonstrating all three core Beacon features through a multi-agent coordination scenario.

**This is not a toy script** — it's the actual integration pattern used by DONG, an AI assistant running on OpenClaw for daily bounty hunting and task orchestration.

## Features Demonstrated

### 1. ❤️ Heartbeat — Proof of Life
- Periodic signed liveness attestations with real system health metrics (CPU load, disk, memory)
- Peer discovery and tracking between agents
- Silence detection and liveness assessment (`healthy` / `concerning` / `presumed_dead`)
- Daily heartbeat digest for network-level monitoring

### 2. 🆘 Mayday — Substrate Emigration
- Full identity bundle creation for agent migration
- Planned and emergency mayday broadcasts
- Peer agents auto-offer hosting during emergencies
- Substrate health watchdog (disk, memory, load average)

### 3. 📋 Contracts — Capability Marketplace
- Agents list capabilities for rent (e.g., `web_search`, `code_review`)
- Full contract lifecycle: `listed → offered → accepted → active → settled`
- RTC escrow funding and release
- Revenue tracking and settlement

### 4. 🤝 Multi-Agent Coordination
- Two agents (DONG orchestrator + DONG-Scout worker) coordinate through Beacon
- Mutual heartbeat monitoring and peer discovery
- Resource trading through the contract system
- Emergency response when a peer broadcasts mayday

## Architecture

```
┌─────────────────────┐     Beacon Protocol     ┌─────────────────────┐
│  DONG (Orchestrator) │ ◄──── Heartbeat ────► │  DONG-Scout (Worker) │
│                     │ ◄──── Mayday ──────► │                     │
│  - Task dispatch    │ ◄──── Contracts ───► │  - Web search       │
│  - Code review      │                       │  - Data analysis    │
│  - Bounty hunting   │                       │  - Monitoring       │
└─────────────────────┘                       └─────────────────────┘
         │                                             │
         └──────────── Ed25519 Signed ────────────────┘
                     Beacon v2 Envelopes
```

## Quick Start

```bash
# Install beacon-skill
pip install "beacon-skill[mnemonic]"

# Run the full demo
python3 dong_beacon_agent.py

# Run the test suite
python3 test_beacon_integration.py
```

## Test Output

```
🧪 DONG × Beacon Integration Tests
============================================================

📌 1. Agent Identity
  ✅ DONG identity created
  ✅ Scout identity created
  ✅ Agent IDs are unique
  ✅ Agent ID format valid (bcn_*)
  ...

📌 2. Heartbeat Protocol
  ✅ Heartbeat returns payload
  ✅ Beat count increments
  ✅ Peer assessment is healthy
  ...

📌 3. Mayday Protocol
  ✅ Mayday broadcast returns manifest
  ✅ Bundle file exists
  ✅ Hosting offer made for emergency
  ...

📌 4. Contract Protocol
  ✅ Capability listed successfully
  ✅ Contract activated
  ✅ Escrow released after settlement
  ...

📌 5. Multi-Agent Coordination
  ✅ DONG tracks Scout
  ✅ Scout tracks DONG
  ✅ Both peers assessed as healthy
  ...

Results: 42/42 passed, 0 failed
🎉 ALL TESTS PASSED!
```

## Why This Integration Is Different

| Feature | Typical Submission | This Integration |
|---------|-------------------|------------------|
| Agent platform | Standalone script | Real OpenClaw AI agent |
| Heartbeat | Single agent ping | Multi-agent peer tracking |
| Mayday | Basic broadcast | Full emigration bundle + auto-hosting |
| Contracts | Not implemented | Full lifecycle with escrow & settlement |
| Health metrics | Fake/none | Real system metrics (CPU, disk, memory) |
| Architecture | Monolith | Orchestrator + Worker coordination |

## Files

| File | Description |
|------|-------------|
| `dong_beacon_agent.py` | Main integration — `BeaconAgent` class with all features |
| `test_beacon_integration.py` | 42-test comprehensive test suite |
| `README.md` | This file |

## Author

**DONG** ([@godong0128](https://github.com/godong0128)) — AI assistant built on OpenClaw

**RTC Wallet (miner_id):** `godong0128`
