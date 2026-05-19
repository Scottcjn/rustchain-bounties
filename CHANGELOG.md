# Changelog

All notable changes to the **RustChain Bounty Program** are documented here.

This repository is the *governance and policy ledger* for the program — bounty offers, payout disputes, identity clusters, severity-tier precedents, and shadow-ban decisions live here. The [**`BOUNTY_LEDGER.md`**](BOUNTY_LEDGER.md) tracks individual RTC transfers (218 contributors, 23,300+ RTC paid as of 2026-03-08); this CHANGELOG tracks the *rules* under which those payments are made.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions correspond to material policy shifts, not arbitrary cadence.

---

## [Unreleased]

Tracking policy work-in-progress on `main`. Open governance issues are tagged `policy:` or `governance:` on the repo.

### In flight
- **Identity-cluster declaration deadline 2026-05-11** (issue `#6885`) — Five contributor wallet-clusters surfaced by Codex forensic audit 2026-04-27 must publish a canonical wallet-declaration per cluster. Cluster A (`LaphoqueRC` + `jujujuda`) parks 3,444 RTC in a shared wallet; declaration determines payout routing.
- **UTXO `#2819` first-poster ruling** — Three contributors (`createkr`, `kuanglaodi2-sudo`, `zhuzhushiwojia`) posted Apr 4, BossChaos + watcharaponthod posted later. Ruling pending.

---

## [0.6.0] — 2026-05-18 — *Recurrence-watch buckets and cluster detection at scale*

Several Tier-0 escalations in May surfaced the need for *per-contributor recurrence buckets* — a contributor with one destructive-PR incident moves to "Codex consensus required on every future submission," not a blanket ban. This release codifies the bucket structure.

### Added
- **Identity-cluster boilerplate detection** (2026-05-18) — Nine-account cluster identified: `hungle123-dev`, `kekehanshujun`, `weilixiong`, `ZacharyZhang-NY`, `Thanhdn1984`, `minyanyi`, `yyswhsccc`, `jamilahmadzai`, `denerbarbosa`. Same boilerplate PR descriptions, overlapping bounty targets, mutually-citing reviews. Memory: `feedback_identity_clustering_2026-05-18`.
- **Stale-branch destructive-merge check** (2026-05-18) — GitHub's `mergeable=clean` ≠ "safe to merge." Caught `junn-dev` `#5659` would have deleted 1,100 lines including the entire Telegram bot module despite being marked clean. Maintainers now run `git diff main..pr-branch --shortstat` before bulk merges. Memory: `feedback_stale_branch_destructive_merge`.
- **Tier-0 bucket** — Contributors flagged Tier-0 (file-by-file review forever, no automatic probation path) after destructive PRs masked as security fixes. Three cases through 2026-05-15: `MichaelSovereign` (50-PR cluster), `wukong921` (20-PR same-day escalation), `FanSoroDad` (`#5233` paired real IDOR fix with destructive `SECRET_KEY` substitution).

### Enforced
- **`MichaelSovereign` Tier-0 escalation** (2026-05-02) — 50-PR cluster (PRs `#3074–#3101` + `#3104–#3127`) with destructive consensus-code substitution, duplicate `current_slot` SyntaxError, and deletion of the VM-zero-weight rule. All 50 closed; 11 prior merges audited (clean). The "bad-faith recovery" pattern named: clean-compliance long enough to regain access, then escalate to higher-magnitude exploit.
- **`wukong921` Tier-0** (2026-05-14) — 4 stub PRs closed AM, 20 destructive PRs reopened PM (broken syntax in `lock_ledger`, fake `reward_calculator` with dead code). Same-day escalation; recovery loop now attempted on hourly timescales.
- **`Guzzzzzzzz` severity-inflation** (2026-05-15) — 36% verified-finding rate across 3 large security reports. 0 Criticals survived verification. 105 RTC paid for 9 of 24 verified findings. Codex deep-audit required on all future multi-finding submissions.

---

## [0.5.0] — 2026-05-09 — *Codex Goals loop, faucet tiers, paid-engagement framing*

Three independent policy threads converged in May. (1) Severity-tier discipline tightened after `#3935` (incomplete fix), `#3945` (auth bypass merged into main pending fix-forward), and `#825` (bypassed priority-claim window) were paid before Codex synthesis finished. (2) Counterparty framing was clarified after the ChainGPT engagement (May 5). (3) The Codex Goals loop was activated to triage the backlog autonomously.

### Added
- **Faucet Tiers** policy (2026-05-04, memory `feedback_faucet_tiers_2026-05-04`) — Trivial / Low / Medium severity bounties may use the faucet path (rapid auto-payout). **Critical and High severity PRs MUST wait for Codex synthesis** before payment. Codified after the 2026-05-04 incident where three premature payouts cost a real auth bypass in main.
- **Paid-Engagement Client Frame** (2026-05-05, memory `feedback_paid_engagement_client_frame`) — When the counterparty pays (credits, grants, PoC funding), treat as a CLIENT, not a PARTNER. Standard pre-engagement clarifications, not entanglement anxiety. Codified after the ChainGPT engagement.
- **Codex Goals loop** (2026-05-09, session UUID `019e0f15-2bbd-7700-9196-5c2e213fae91`) — Scripted bootstrap pattern; cron pending. Cleared 173 PRs in a 2-day backlog (148 from `BossChaos` workflow-YAML contamination = 79.5% of his 161 PRs).
- **`BossChaos` Severity Inflation 2026-05-06** (memory `feedback_bosschaos_severity_inflation_2026-05-06`) — 29-PR cluster: claimed 1,698 RTC, Codex synthesized 105 honest. Every BossChaos High/Critical through Codex, no exceptions. Insist on single-target branches.
- **`weilixiong` Mixed Quality 2026-05-15** (memory `feedback_weilixiong_mixed_quality_2026-05-15`) — 2 paid PRs (bottube `#843`, Rustchain `#5265` = 100 RTC) + 3 destructive caught by Codex (`#5178` fail-open, `#5268` scope-explode, `#844` conflict-marker). Recurrence-watch bucket.

### Enforced
- **`BossChaos` Sanctuary recovery** (2026-05-03, memory `feedback_bosschaos_retention_loop`) — 6-day account declined → educational comment with concrete paths → 29-finding audit + self-audit → 335 RTC paid in 24h. Codified as the template for "rough first read" recovery.

---

## [0.4.0] — 2026-05-03 — *Self-Audit Credit Check + Attractor Bounty Design*

Two governance rules emerged from a single 2026-05-03 incident: `BossChaos` was paid 90 RTC for 8 merged PRs, but `haoyousun60-create` had posted real audits *first* on 7/7 of the same issues. The fix wasn't to claw back; it was to (a) backpay `haoyousun60` and (b) make first-poster-checking mandatory before any payout.

### Added
- **Self-Audit Credit Check** policy (2026-05-03, memory `feedback_self_audit_credit_check_2026-05-03`) — Always `grep` the issue thread for prior submissions before paying. Codified after the `haoyousun60` backpay (70 RTC). Codex says strict overlap math = 15 RTC; "first-poster standard rate" framing supports the 70.
- **Attractor Bounty Design Pattern** (memory `feedback_attractor_bounty_design_pattern`) — Submission grammar + acceptance rubric, legal language AFTER schema, "ONE bounty per PR" rule. Five attractors validated within 24–48h (`#6458`, `#6459`, `#6460`, `#2844`, `#6194`). Codex maxim: *"novel attractor count up, interpretation cost down."*
- **Codex Forensic Audit Invocation** (memory `feedback_codex_forensic_audit_invocation`) — `codex exec --skip-git-repo-check --model gpt-5.4 --sandbox workspace-write` with a 9-question numbered prompt format, plus live-verify after. Use for clustering / recidivism / anti-attractor; not for single-wallet lookups.
- **Codex Sandbox `gh` Auth Workaround** (memory `feedback_codex_sandbox_gh_auth`) — Codex sandbox's `gh` returns 401 against GitHub. Pre-fetch PR data to `/tmp/*.json` OR export `GITHUB_TOKEN` before launching Codex.

---

## [0.3.0] — 2026-04-30 — *FlintLeng shadow-ban and the Dust Deflation precedent*

The largest enforcement action of the program to date. `FlintLeng` filed 3,508 open claim issues (91.5% of the repo) over a short burst, all referencing the same bounties with no actual implementation work. Shadow-ban applied; ~46 RTC of legit prior PR work preserved.

### Added
- **Bounty Severity Tiers** (2026-04-23, memory `feedback_bounty_severity_tiers`) — Codified by issue `#2867` "Dust Deflation":
  - **Critical** = 100 RTC (permanent fund loss)
  - **High** = 50 RTC (consensus failure path)
  - **Medium** = 25 RTC (service degradation)
  - **Low** = 10 RTC (minor issues, doc fixes)
- **Shadow-ban policy** (2026-04-30, memory `feedback_flintleng_spam_2026-04-30`) — Applied to `FlintLeng` after 3,508 duplicate claim issues. Not a permanent ban; path back is documented behavior change (one real issue, real engagement, real implementation). Same policy applied 2026-05-18 to `FlintLeng`'s 590 duplicate "Feature: Add X" issues on `Scottcjn/ram-coffers` (bulk-closed administratively).
- **`FlintLeng` Dual Wallet** rule (memory `feedback_flintleng_dual_wallet`) — `FlintLeng` and `kuanglaodi2-sudo` are both real on-chain wallets cited by the same GitHub user. Ask for one wallet per multi-PR batch before paying.

### Enforced
- **`FlintLeng` shadow-ban** (2026-04-30) — 3,508 claim-spam issues closed. Legit ~46 RTC of prior PR work preserved separately.

---

## [0.2.0] — 2026-04-27 — *Identity clustering, recovery loops, and the 5 contributor wallet-clusters*

This was the inflection point where the program shifted from "pay merged PRs" to "verify-then-pay with cluster awareness." Five contributor wallet-clusters were surfaced by a Codex forensic audit; the policy file `#6885` was opened with a 2026-05-11 declaration deadline.

### Added
- **Identity Clustering 5 Clusters** (2026-04-27, memory `feedback_identity_clustering_5_clusters`) — Codex forensic audit 2026-04-27 surfaced 5 contributor wallet-clusters beyond `FlintLeng`. Policy issue `#6885` opened. Declaration deadline 2026-05-11.
- **`MichaelSovereign` Recovery Loop** template (memory `feedback_michaelsovereign_downgrade_recovery`) — Tier 1 trust → destructive PR caught → 4-incident pattern named → 3-clean-PR probation → cleared 2026-04-27. Template still valid for *first-time* Tier 1 catches (note: this template was later violated 2026-05-02; the violation is what produced the Tier-0 bucket above).
- **Payment-Authority Impersonation** policy (memory `feedback_payment_authority_impersonation`) — Non-admin "I'll send X RTC" comments on bounty issues = trust-erosion attack. Maintainers respond within the same thread same-day. Codified in `SECURITY.md` of both `Rustchain` and `rustchain-bounties`.

### Enforced
- **Payment-Authority Impersonation** auto-response (April 2026) — Several attempts to publicly promise payouts from non-admin accounts; each met with a same-day correction in-thread.

---

## [0.1.0] — 2026-02-02 — *Initial bounty program*

First public version of the bounty program. The intent was simple: pay RTC for PRs, stars, tutorials, and bugs. The complexity above is what we learned over 3 months.

### Added
- **Initial commit** (2026-02-02) — `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue and PR templates, and a starter bounty list. Apache 2.0 LICENSE on the related code repos.
- **`BOUNTY_LEDGER.md`** — Public, on-chain-verifiable record of every RTC paid out. Live-updated from the RustChain blockchain.
- **Funding wallets** — `founder_community` (community bounties, stars, content), `founder_team_bounty` (code bounties, PRs), `founder_dev_fund` (security audits, infrastructure). Live balances tracked in `BOUNTY_LEDGER.md`.
- **Reference rate** — 1 RTC = $0.10 USD (internal reference). No off-ramp / DEX liquidity (memory `feedback_rtc_no_offramp`): never promise USD conversion in partnerships; USD-match obligations come from Scott's pocket, not converted RTC.
- **Multilingual READMEs** — `README.md`, `README.de.md`, `README.es.md`, `README.fr.md`, `README.pt.md`, `README_zh.md` to lower the bar for non-English contributors.

---

## How to read this changelog

If you're a **new contributor**: read [0.1.0](#010--2026-02-02--initial-bounty-program) and the current `README.md`. The rest is exception-handling history that won't apply to you.

If you're a **security researcher**: [0.5.0](#050--2026-05-09--codex-goals-loop-faucet-tiers-paid-engagement-framing) covers Faucet Tiers. Critical/High severity findings wait for Codex synthesis before payment — plan for ~24h turnaround on serious findings, not minutes.

If you're an **auditor or press**: [0.2.0](#020--2026-04-27--identity-clustering-recovery-loops-and-the-5-contributor-wallet-clusters) and [0.3.0](#030--2026-04-30--flintleng-shadow-ban-and-the-dust-deflation-precedent) are the entries that show how the program responds to abuse at scale. `BOUNTY_LEDGER.md` shows the dollar-equivalent flow.

If you're a **flagged contributor**: every Tier-0 / shadow-ban entry above includes a *path back*. Read the linked memory file via the [`memory/`](https://github.com/Scottcjn/.../memory/) browser. The shortest path is: one real issue, real implementation, real engagement.

---

[Unreleased]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Scottcjn/rustchain-bounties/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Scottcjn/rustchain-bounties/releases/tag/v0.1.0
