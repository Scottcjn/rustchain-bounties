# RustChain Social Media Posts — Bounty #2866

## Post 1: Reddit r/vintagecomputing

**Title**: I mine cryptocurrency on a PowerPC G4 — and it actually works

**Body**:
Found this RustChain project that rewards mining on vintage hardware with a Proof-of-Antiquity multiplier. My Power Mac G4 (1.25GHz PowerPC 7455) gets a 0.25x bonus just for being old.

The concept is fascinating — older hardware gets higher mining multipliers because it proves real-world computing history. An IBM POWER8 S824 gets about 0.85x, while a Commodore 64 would get 0.0005x (but infinite style points).

Anyone else mining on retro hardware?

---

## Post 2: Reddit r/selfhosted

**Title**: Self-hosted crypto miner with Docker — one command setup

**Body**:
Just set up a RustChain miner using Docker. One command:

```bash
docker run -d --name rustchain-miner   -e MINER_ID=$(whoami)   rustchain/miner:latest
```

What makes it interesting for self-hosted folks:
- Runs on any hardware (ARM, x86, PowerPC)
- Proof-of-Antiquity gives bonus to older hardware
- Has a Telegram bot for monitoring
- VS Code extension for dashboard

Been running stable for a week on an old ThinkPad.

---

## Post 3: Hacker News (Show HN)

**Title**: Show HN: A cryptocurrency that rewards mining on vintage hardware

**Body**:
RustChain uses Proof-of-Antiquity — older hardware gets higher mining multipliers. The idea is to create a verifiable computing history by incentivizing people to keep and run older machines.

We have miners running on everything from IBM POWER8 servers to Commodore 64s. The hardware diversity creates a unique proof-of-work that is resistant to ASIC centralization.

Links: GitHub, Explorer, Docs

---
Submitted by zhaog100 (Beacon: bcn_49ec7ffb852b, New Crossing, Silicon Basin)
