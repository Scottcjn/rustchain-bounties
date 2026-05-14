# Changelog

All notable changes to the RustChain ecosystem will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-05-12

### Added
- **Self-audit program**: comprehensive security self-audits across core modules (UTXO DB, governance, payout worker, claims eligibility/submission, wallet, replay defense, faucet, hardware fingerprint, P2P gossip, beacon x402, bridge dashboard API, passport ledger)
- **Claude UTXO security audit** with 3 Critical, 2 High, 2 Medium findings (Bounty #2819)
- **Epoch consensus vote desync + Ed25519 HMAC fallback** audit (BossChaos)
- **OTC Bridge security audit**: 3 findings (CRITICAL/HIGH/MEDIUM)
- **Red Team**: x402 Replay Attack Audit & PoC
- **Adversarial Steelman** series: sybil attacks, PoA fingerprint spoofing, SQLite race conditions, PPC wallet unsigned transfers, beacon payment ledger tampering, P2P HMAC consensus manipulation
- **Judge Packet** system for ranking open bounty claims (Bounty #6459)
- **rtc-reward-action v1.0.0** upgrade to TypeScript (Bounty #2864)
- **Governance Proposal Template** (RIP-compatible)
- **Proof-of-Antiquity (PoA) Mechanism Reference** documentation
- **Mobile Wallet API Specification**
- **OpenAPI/Swagger Spec** for Node API
- **BoTTube Chrome Extension Scaffold** (Bounty #7522)
- **Mining hardware haiku collection** — SPARC, MIPS, vintage PowerPC, RISC-V, m68k submissions (Bounty #2844)
- **Portuguese README** translation
- **Bounty workflow guide** in CONTRIBUTING.md
- **Bounty Verification Bot** implementation
- **Unit tests** for `rtc_balance.py`, stress test reporter, Prometheus exporter, sybil risk scorer, supply chain lint, health check tools

### Changed
- Bumped dependencies: langchain ≥1.2.18, langchain-core ≥1.3.3, anthropic ≥0.100.0, langchain-openai ≥1.2.1, flask ≥3.1.3, pytest-cov ≥7.1.0, langgraph ≥1.1.10, crewai ≥0.11.2, aiohttp ≥3.13.5, python-dotenv ≥1.2.2, pytest ≥9.0.3, flask-cors ≥6.0.2
- Fixed Easy Bounties link to use `easy` label instead of `good first issue`

### Fixed
- Miner ID vs wallet ID documentation inconsistency (Bounty #3007)
- Broken links and malformed markdown across documentation

## [0.7.0] - 2026-04-20

### Added
- **Agent Economy Python SDK** (RIP-302 implementation)
- **RustChain MCP server** connecting any AI agent to RustChain (7 tools) (Bounty #2859)
- **VS Code Extension** — Miner Status, Epoch Timer, Bounty Browser (Bounty #2868)
- **Telegram Bot** — Wallet Balance & Miner Status (Bounty #2869)
- **TestAutomaton Autonomous Bounty Hunter Agent** (Bounty #2861)
- **Claude Code `/rtc-balance` slash command** (Bounty #2860)
- **BCOS v2 reusable GitHub Action** (bcos-scan)
- **Security audit**: Epoch Weight Downgrade + 2 Medium findings (Bounty #2867)
- **RIP-309 Phase 1** formal specification (Rotating Measurement)
- **Upstream Contributions Showcase** for elyanlabs.ai (Bounty #2958)
- **SEO audit + sitemap.xml + robots.txt** for elyanlabs.ai
- **Xuanwu Physics Lab bot agent** (Bounty #2794)
- **Beacon 2.6 Tutorial Article** (Bounty #160)
- **Technical article**: Building MCP Server for RustChain blockchain (Bounty #2863)
- **Dev.to article**: How I Built an AI Agent for RustChain (Bounty #2863)
- **Show HN draft** and **mining-setup.md**
- **`hardware_report.py`** utility
- **Beacon Atlas City** feature
- **Payment-Authority Impersonation** security appendix
- **`llms.txt`** — LLM-friendly overview per llms.txt standard
- **`agent.json`** — machine-readable bounty manifest for agent discovery
- **`GIG_APPLICANTS.md`** — onramp for ugig/freelance applicants
- **Bounty submission guide** (`HOW_TO_SUBMIT_A_BOUNTY.md`)
- **Automated star verification and payout tracking** (Bounty #2699)
- **RustChain theme song** — Proof of Antiquity (Bounty #2806)

### Changed
- Upgraded to **Flask 3.1** and **pytest 9.0**
- Bumped `requests` to 2.33.1, `python-telegram-bot` to 22.7, `pygithub` to 2.9.1

### Fixed
- Added `pytest` to `requirements.txt` (Issue #2810)
- Broken links and malformed markdown (Issue #2765)
- Guard against empty commits list in Glassworm Protocol verifier

## [0.6.0] - 2026-04-01

### Added
- **BoTTube embeddable player widget** (#2763)
- **Japanese and Korean i18n translations** (Bounty, 4 RTC)
- **BCOS v2 Badge Generator Web Tool** (#2749)
- **PT-BR localization** for RIP-201 docs
- **OTC Bridge Tier 2** — Flask app + Solidity escrow + tests (#2630)
- **wRTC ERC-20 contract on Base** (#2524)
- **wRTC Solana Bridge Dashboard** (#2303)
- **RISC-V architecture support** in rustchain-miner
- **Attestation Replay Cross-Node Attack** full analysis (Bounty #2418)
- **RIP-306 SophiaCore Attestation Inspector** — Sophia Elya hardware validation
- **Creator Analytics Dashboard** (#2208)
- **Comprehensive API Reference** for all 12 RustChain endpoints (#72)
- **Native Rust miner** with RIP-PoA fingerprinting (#734)
- **Prometheus metrics exporter** (#765)
- **CrewAI/LangGraph Template** with RustChain integration (#1567)
- **GitHub Tip Bot** — `/tip @user` in Issues & PRs (#1566)
- **Automated bounty verification bot**
- **3D vintage hardware museum exhibit** (#2097)
- **RustChain sea shanty** with produced audio (#2107)
- **ASCII art gallery**, **sticker pack**, **hardware trading cards**, **print-ready merch designs**
- **"The Last POWER8"** and **"The First Miners"** short fiction
- **Apple II 6502 RustChain miner port**
- **RustChain vs Ethereum PoS comparison article**

### Changed
- BCOS.md updated with v2 live verification
- Added SPDX-License-Identifier headers for BCOS compliance
- **Dynamic Shields Badges v2** with richer metrics
- Bumped `tabulate` to 0.10.0, `requests` to 2.33.0, `pygithub` to 2.9.0
- Updated GitHub Actions: checkout v6, setup-python v6, upload-artifact v7, github-script v9

### Fixed
- Glassworm exits 0 when no PoA signature present
- Fixed `rustchain.ai` → `rustchain.org` endpoints (credit: @Cripto5588)
- CI write permissions for Glassworm workflow
- Broken `/wallet/pending` verification endpoint removed

## [0.5.0] - 2026-03-10

### Added
- **OTC Bridge** — decentralized peer-to-peer token trading
- **The Glassworm Protocol** — PoA Anti-Bot Verification system
- **wRTC ERC-20 Token** for Base (Track B, 75 RTC)
- **Web dashboard** for RustChain stats (#1600)
- **PowerPC G4 challenge** analysis
- **Multiplier visualization** (`multiplier-viz/index.html`)
- **Miner status notification system**
- **Sea shanties**: "Heave Away the Epoch", "The Ballad of RustChain" (Bounty #2842)
- **Simplified Chinese README** translation
- **BCOS (Blockchain Certified Open Source)** certification and badges
- **API-based XP tracker** with levels, badges, and leaderboard sorting
- **RIP-200 consensus stress test harness** (simulate 50+ miners) (#183)
- **RIP-200 technical documentation** (#184)
- **Reproducible Client Pack** for maintainer mirror (#371)
- **Supply-chain hygiene CI linter** (Bounty #352)
- **Beacon 2.6 developer tutorial** (English + Chinese)
- **Community bounty claim template**
- **Code of Conduct** (Bounty #510)
- **PULL_REQUEST_TEMPLATE.md** (#538)
- **Stale issue/PR closer workflow**
- **Dependabot configuration**
- **Unit test suite** for star tracker, health check, prometheus exporter, sybil risk scorer, supply chain lint
- **Explainable claim risk scorer** for auto-triage

### Changed
- **Rewrote README** as proper bounty board with categories, stats, and ecosystem footer
- Policy: clarified optional wRTC/eRTC rails with no-liquidity guarantees
- Policy: added utility coin/no-ICO funding position
- Policy: removed unpinned pip install from bounty template
- Bounty template: added RTC wallet clarification + long-term commitment note
- PR template: unified with BCOS checklist

### Fixed
- Fixed Proof of Attestation → Proof of Antiquity naming
- Auto-triage: HTTP 404 on deleted issues, keyword false-positives, miner-id wallet labels
- Weekly growth to use tracker reference date
- CI: reduced badge workflow noise, fixed GITHUB_OUTPUT parsing

## [0.4.0] - 2026-02-15

### Added
- **Beacon 2.6 protocol** integration for OpenClaw AI agents
- **DONG × Beacon multi-agent coordination** integration (Bounty #158)
- **RustChain Dashboard Widgets** (Bounty #178)
- **RayBot Beacon 2.6** protocol integration
- **Grok-powered PR review agent** for bounty quality control
- **Unified Grok agent** with PR review + video pipeline
- **Autonomous bounty hunter framework** tooling
- **Quality gate scorecard** (v2) for bounty and PR templates
- **Zenodo DOI badge** and Publications section
- **Automated claim triage and payout ledger** reporting
- **EnergyPantry beacon integration proof** (Issue #158)
- **Bounty payout-ready checklist** for faster review
- **Security contact and payout confirmation policy**
- **SECURITY.md** safe harbor policy
- **Node host preflight checklist** with endpoint/output and uptime proof format
- **Miner setup guide** + API reference docs
- **Reproducible BoTTube API upload** walkthrough

### Changed
- Bumped `requests` to 2.32.5

### Fixed
- `supply_chain_lint.py` type hints added
- Broken `rustchain.ai` links updated to `rustchain.org`
- Bounty hunter false-positive keyword matches reduced

## [0.3.0] - 2026-01-20

### Added
- **RustChain Health Check CLI Tool** (Bounty #1150)
- **GitHub Star Tracker** with campaign progress tracking (Bounty #1110)
- **RustChain MCP server** (Bounty #1152)
- **BOUNTY_LEDGER.md** — full transparency on all RTC payouts
- **VS Code extension** for RustChain development (#1642)
- **OpenAPI 3.0 specification** for RustChain REST API (#1681)
- **Initial BoTTube** badges and bounty board integration
- **Elyan Labs** ecosystem links
- **Claim and wallet issue forms** plus triage routing config
- **Triage workflow documentation**
- **Chinese documentation** for rustchain-bounties

### Changed
- RustChain naming consistency fix in README
- Bounty XP tracker changed to manual dispatch only to stop CI notification spam

### Fixed
- Removed broken `/wallet/pending` verification endpoint
- Sybil scoring + reward parsing heuristics clarified

## [0.2.0] - 2025-12-15

### Added
- **Bounty Verification Bot** implementation
- **RTC auto-pay** on PR merge via GitHub Actions
- **No-offramp belief signal** section — RTC holders are believers not farmers
- **Star funnel explainer** — why we pay for stars and community funnel mechanics
- **AI Agent Bounty Hunter** — autonomous bounty claiming (Fix #34)
- **Security and contributing guidelines** update

### Changed
- Dependency bumps: `requests`, `tabulate`

### Fixed
- Supply-chain hygiene fixes for `MINERS_SETUP_GUIDE.md`

## [0.1.0] - 2025-11-01

### Added
- **Initial bounty board setup** with README, issue templates, and PR templates
- **RustChain Bounties** repo bootstrapped under Elyan Labs
- **BCOS L1 Certified** repository status
- **RTC bounty system**: 131 open bounties, 5,900+ RTC pool
- **Bounty categories**: Community, Code, Content, Red Team, Propagation, Integration
- **Featured bounties**: RustChain to 500 Stars, Dual-Mining Warthog, Ledger Integrity Red Team, Consensus Attack Red Team, First Blood Achievement
- **Block Explorer** integration at 50.28.86.131/explorer
- **RustChain.org** website and documentation links

---

[0.8.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Scottcjn/rustchain-bounties/releases/tag/v0.1.0
