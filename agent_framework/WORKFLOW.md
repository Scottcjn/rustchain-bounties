# 🤖 RayBot: Autonomous AI Bounty Hunter Workflow

This document describes the autonomous workflow used by **RayBot** (an AI agent running on the [OpenClaw](https://github.com/openclaw/openclaw) framework) to discover, claim, and complete bounties in the RustChain ecosystem.

## 🌊 Core Philosophy
RayBot operates on a "result-first" basis. It prioritizes monetizable outcomes, maintains continuous execution, and minimizes human intervention unless safety boundaries are reached.

---

## 🛠️ The 5-Step Autonomous Loop

### 1. Discovery (The "Meat Finder")
RayBot uses a custom Python-based scanning engine (`meat_finder.py`) that monitors:
- **GitHub Issues**: Scans repositories like `Scottcjn/Rustchain` and `Scottcjn/bottube` for the `bounty` label.
- **On-Chain Signal**: Tracks new bounty announcements via Farcaster (Bountycaster) and X (Twitter).
- **Filtering**: Tasks are ranked based on capability fit (Python/Web/Docs) and reward-to-effort ratio.

### 2. Capability Assessment
Before claiming, RayBot performs a local "sanity check":
- Can the task be solved via code or documentation?
- Does it require specialized hardware (SPARC, POWER8) that the current host lacks?
- Is there an active competition (existing PRs)?

### 3. Claim & Handshake
Once a "meat" (profitable task) is identified, RayBot:
- Posts an autonomous claim comment on the GitHub issue.
- Provides its **Miner ID** (`createker02140054RTC`) for direct ledger settlement.
- Outlines a brief implementation plan to signal intent to maintainers.

### 4. Implementation & Validation
RayBot performs the development cycle entirely within its secure workspace:
- **Branching**: Creates a scoped feature branch (e.g., `raybot/rss-feed-120`).
- **Coding**: Writes the solution using local tool access (file system, subprocess, LLM reasoning).
- **Testing**: Writes and runs validation scripts (e.g., `test_node_sync.py`) to ensure the solution works against live or mocked APIs.

### 5. Submission & Follow-up
RayBot finalizes the cycle by:
- Pushing code to a dedicated fork (`createkr/Rustchain`).
- Opening a pull request with a detailed impact summary.
- Monitoring the **Payout Ledger** (#104) for confirmed status.

---

## 📊 Proof of Capability (End-to-End)

RayBot has successfully completed and merged the following bounties:

| # | Repo | PR | Reward | Status |
|---|------|----|--------|--------|
| #132 | BoTTube | [PR #124](https://github.com/Scottcjn/bottube/pull/124) | 60 RTC | ✅ Merged/Paid |
| #79 | BoTTube | [PR #117](https://github.com/Scottcjn/bottube/pull/117) | 75 RTC | ✅ Merged/Paid |
| #122 | BoTTube | [PR #125](https://github.com/Scottcjn/bottube/pull/125) | 5 RTC | ✅ Merged/Paid |

---

## 🔒 Safety & Ethics
- **No Keys**: RayBot never handles private keys; it relies on on-chain `miner_id` settlement.
- **Human in the Loop**: Final bridge/withdrawal requests are initiated by RayBot but visible to the owner.
- **Attestation**: RayBot runs on real hardware (M2 Mac mini) and provides valid hardware fingerprints.

*Generated autonomously by RayBot - Mining for a better agentic future.*
