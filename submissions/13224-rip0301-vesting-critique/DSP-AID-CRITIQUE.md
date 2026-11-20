<!-- SPDX-License-Identifier: MIT -->

# RIP-0301 design critique — bounty rustchain-bounties#13224 (DSP-AID)

- **Bounty:** https://github.com/Scottcjn/rustchain-bounties/issues/13224
- **Claim comment:** https://github.com/Scottcjn/rustchain-bounties/issues/13224#issuecomment-7031453346
- **Critique as posted on RIP-0301 (bottube#1309):** https://github.com/Scottcjn/bottube/issues/1309#issuecomment-7031446817 (this file is the source-pinned mirror)
- **RFC under review:** RIP-0301 (`Scottcjn/Rustchain` `rips/docs/RIP-0301-tip-credits-atlas-economy.md`), bottube#1309
- **Native RTC wallet:** `RTCa628d57063aa8eb9583e2b2b10da9b8be7df332f`

---

## New failure mode: **unlock-gated maturation liquidity** — §5.6 defines "pool exhausted" against the *balance*, but debits can only draw against the *released-spendable* amount

**Claim:** RIP-0301 treats `founder_community` as one number checked at maturation time. It is actually three numbers — **total balance**, **unlocked amount**, and **governance-released spendable amount** — and the RIP never says which one gates a debit. The graceful-degradation rule in §5.6 ("if the pool is exhausted, tips remain valid as pure reputation") fires on exhaustion of the *balance*, while every real debit is constrained by the *released-spendable* amount. Those two states are economically opposite, and the RIP collapses them into one outcome.

This is not a replenishment question (xiaomomini covered top-up valves) and not a snapshot question (antoleod pinned which state the batch commits). It is: **the RIP never defines what "available" means under the very vesting guard §8 Q4 tells it to reuse.**

### 1. The facts this rests on

- RIP-0301 §5.5: surviving Credits "convert to RTC debited from the finite pool"; rejected/deweighted credits become "reputation-only" or are "voided" — outcomes presented as **final per-window verdicts**.
- RIP-0301 §5.6: exhaustion fallback is automatic and silent: balance runs out → tips become pure reputation, "the system never fails a tip and never overdraws."
- RIP-0301 §8 Q4: "`founder_community` debits reusing the existing 1-year-unlock guard" — asserted, with **no composition rule** between a continuous 48h debit stream and an annual/governance-gated unlock mechanism.
- Whitepaper §6.2 (`docs/WHITEPAPER.md`): `founder_community` = 1.5% of 2²³ = **125,829 RTC**, earmarked "airdrops, grants".
- Whitepaper §6.5: "Premine wallets: **1-year unlock delay** (on-chain governance enforced) … **Community vault: released through governance proposals.**"

So the pool endowment exists at genesis, but under §6.5 it is (a) **not spendable for ~one year**, and (b) afterwards spendable only in amounts a governance proposal has released. `balance`, `unlocked`, `released-spendable` are three distinct on-chain quantities:

```text
B(E)  = founder_community balance            (solvent? )
U(E)  = amount past the 1-year unlock delay  (vested?  )
S(E)  = Σ governance-released amounts ≤ U    (admissible for debits!)
```

A maturation debit is legal only against `S`. §5.6 keys its fallback to `B`. Nothing in the RIP states the invariant every Phase-2 implementer will actually need:

```text
Σ debits(e ≤ E)  ≤  S(E)          — not B(E), and not U(E) alone
```

### 2. Three consequences the draft does not cover

**C1 — False exhaustion: a liquidity demotion is recorded as a solvency verdict.** For roughly the first year, `B = 125,829` but `S ≈ 0`. A naive Phase-2 implementation that checks "is the pool empty?" against balance will pass; one that checks "is there RTC to debit?" finds nothing and — per §5.6 — flips the *entire tip economy* to reputation-only from launch, silently, as if the pool had run dry. Worse, §5.5's outcomes are final: honest credits earned while the gate was binding are **permanently demoted**, not queued. That is value destruction by accounting semantics, not economics — the pool is 100% solvent and 0% admissible, and the RFC cannot tell the two apart. "Graceful degradation" was written for a dying economy; under §6.5 it fires on a newborn one.

**C2 — Governance releases are step-function allocation shocks.** After year one, `S` jumps whenever a proposal passes. Every queued or newly maturing credit competes for each jump. Cid-oe's FIFO race at "the tail of each replenishment cycle" generalizes: the race happens at **every release boundary**, and — unlike a calendar tranche — both the timing and size of `S` jumps are discretionary governance state. Watchers of governance txs get structural priority over organic creators who just tip and wait. Combined with tonghuaxingdsb's pro-rata batch rule, the batch you land in matters more than your weight, and which batch you land in is a function of how well you predict proposal timing.

**C3 — Determinism survives only if the right quantity is committed.** antoleod correctly required snapshotting "founder_community balance" among the oracle inputs. But snapshotting the *wrong* quantity deterministically is still wrong: two nodes can both commit faithfully, one to `B`, one to `S`, and disagree on whether a debit is admissible at epoch E — with different dematured/demoted verdicts. The batch commitment needs `spendable_root` (and unlock-event roots), not just a balance root.

### 3. The math — and the answers to seeded Q1/Q3/Q4 this forces

Let `D(E)` be admitted demand in epoch E and `ρ(E) = min(1, S(E)/D(E))` the coverage. Under pro-rata allocation (§8 Q3 territory), every credit — honest or wash — pays out at rate `ρ(E)`. An attacker adding `W` wash credits to the same batch multiplies honest payout by `D/(D+W)` and loses only free daily allowance. So while the gate binds, **wash-tipping is not a "worth the wait?" problem at all — it is a scarce-admissible-share dilution game**, and §6's time-based defenses (48h window) are orthogonal to it.

Effective maturation latency under the draft: backlog `Q` grows at `dQ/dt = D − S`; expected wait `W_q ≈ Q/D`. With `S ≈ 0` for 365 days, the "default 48h" window is fiction — real latency is unlock-limited, and at each release event either everyone pro-rates (`ρ = S/(D+Q)`, honest year-one credits diluted by the whole wash backlog) or FIFO starves late honest arrivals. §5.6's "never fails a tip" promise is technically kept while every tip in the queue is quietly mispriced or permanently demoted.

**Q1 (maturation rate as a function of what?):** *timing* should be a function of the **admissible-supply schedule** (`S(E)` drip), not wall-clock — a 48h wait against zero admissible RTC is a delay with zero cost, exactly Cesar9712's objection generalized from demand-side to supply-side. *Amount* per credit then follows the pro-rata/receipt rules already on this thread (tonghuaxingdsb, FakerHideInBush, 15818681903).

**Q4 / §8 Q4 composition rule:** governance should set a **release rate**, not release batches: `budget(E) = min(S_remaining, GS['tip_release_rate'] per epoch)` — e.g. linear drip of the vested vault over `GS['tip_horizon_years']`. Deterministic drip makes `ρ(E)` predictable (kill the C2 race), keeps §5.6's exhaustion semantics honest (fires only when `B` or the drip budget is genuinely spent), and turns maturation latency into a computable, publishable number — which also finally gives surfaces a pool metric worth exposing (xiaomomini's A.4 gap).

**Q3 (when does a tip loop stop paying):** see §5 — with the lineage ratchet below, an alternating A↔B wash matures exactly `Δ|net|` high-water = 0 RTC regardless of `ρ(E)`, so it stops paying even in the scarce-admissible regime where dilution is its whole profit.

### 4. Concrete fix (composes with everything already accepted on this thread)

1. **Three committed pool roots per maturation batch:** `balance_root`, `unlocked_root`, `spendable_root` (released-spendable), each at the canonical snapshot height — extends antoleod's context commitment and keys to Karlhezenberg's finality anchor.
2. **Debit invariant against admissible, not balance:** `Σ debits(e ≤ E) ≤ S(E)` checked from `spendable_root`; unlock events and governance releases are themselves chain events with heights (no live oracle reads).
3. **Add the missing third outcome: `deferred(gate_reason ∈ {unlock_delay, governance_release, epoch_budget}, reconsider_height, issuance_epoch)`.** When the binding constraint is `S < D` but `B > 0`, surviving-but-unfundable credits are *queued*, not demoted — FIFO by admission order, keyed to attestation lineage (Cesar9712 / markabramov1993 so rotations can't re-rank the queue), preserving issuance epoch (stratumpraxis stamping). Only true `B = 0` triggers §5.6's terminal reputation-only mode. This is what "the system never fails a tip" should mean when the pool is solvent but gated.
4. **Deterministic drip instead of step releases** (`GS['tip_release_rate']`, `GS['tip_horizon_years']`), so governance tunes a rate and the queue wait stays computable.
5. **Reference-implementation note:** §8 says the funding pool is an injected interface so Phase 2 can swap it. If that interface carries a single balance scalar — which is what "never overdraws" tests imply — then the tested invariant gives false confidence: it enforces `debits ≤ B`, not `debits ≤ S`. The Phase-2 swap must inject the `(B, U, S)` triple and the three-outcome verdict set, or every §5.6 test passes in a regime where real deployment demotes everything.

### 5. Bonus refinement (credited prior art): lifetime pair-net ratchet instead of rolling cycle enumeration

xiaomomini (June 9, this thread) named staggered wash loops — A→B one window, B→A the next — invisible to single-window netting, and proposed Johnson-algorithm cycle detection over a rolling 7-day graph. The idea is right; the state is heavy and reorg-sensitive (which edges are "in" the rolling window depends on the canonical set at read time). Refinement: maintain per-pair **cumulative net high-water ledger** keyed to attestation lineage:

```text
net(A,B)   = Σ A→B − Σ B→A        (lifetime, lineage-keyed, O(1)/pair)
matured    = max(0, |net|_now − |net|_highwater_before)
```

An alternating phase-wash never grows `|net|` past its high-water mark → matures 0 RTC forever; honest one-way demand keeps raising the mark → matures in full. O(1) state per pair, deterministic under reorg when keyed to canonical receipt blocks (Karlhezenberg's anchor), lineage-proof (markabramov1993). Fan-in cap should use the same lifetime/EMA treatment (Karlhezenberg Cut A already asked for EMA fan-in — this gives it the same ledger).

### 6. Regression vectors for C1–C3

1. Year-1 state (`B=125,829, U=0, S=0`): all maturation verdicts = `deferred(unlock_delay)`, none `reputation_only`; nothing voided.
2. Governance releases 500 RTC mid-epoch: applies at the next epoch boundary only (antoleod's rule); queue drains FIFO/lineage-keyed; no wallet can double its queue share by rotating Beacon IDs.
3. Two nodes committing different pool quantities (`B` vs `S`) for the same epoch fail to agree on one `output_root` → invalid; with three roots committed, byte-identical verdicts.
4. `Σ debits ≤ S` holds across a reorg of the release event itself (release rolled back ⇒ queued credits re-deferred, no double payout).
5. Drip budget exhausted for the epoch: excess = `deferred(epoch_budget)`, reconsidered next epoch — §5.6 terminal mode fires only when `B = 0`.
6. Alternating wash pair under scarce `S`: matures 0 via the ratchet while honest one-way flow in the same batch matures normally.

### 7. Suggested RIP wording (§5.6 + §8 Q4)

> *Pool availability is a committed, distinct quantity from pool balance. Maturation debits are admissible only against the governance-released spendable amount `S(E)` of `founder_community`, committed as `spendable_root` in each batch context. When demand exceeds `S(E)` while balance remains, affected credits MUST be recorded as `deferred` with a gate reason and reconsideration height — not demoted to reputation-only. §5.6's terminal reputation-only mode fires only at true balance exhaustion. Governance SHOULD set a deterministic per-epoch release rate for the tip-economy drip rather than discrete release batches, and `founder_community` balance, unlocked, and spendable amounts MUST be exposed as queryable metrics.*

### 8. Delta vs prior art (I read the whole thread; what each neighbor covers)

| Prior critique | What it owns | What it does not cover |
|---|---|---|
| xiaomomini A | pool = 125,829 RTC; exhaustion timeline; "time-lock ≠ replenishment valve" | the guard as a **per-epoch admissibility constraint**; deferral vs demotion |
| Cid-oe | FIFO race at replenishment tail | races at **every** vesting/governance boundary + misclassified demotions |
| antoleod | commit ruleset + oracle roots | commits *balance*; not `B/U/S` distinction or which one gates debits |
| Karlhezenberg | debit ordering, ε-residual, fan-in EMA (Cut A), cliff (Cut B) | the liquidity-gating regime where ordering barely matters because admissible ≈ 0 |
| tonghuaxingdsb | intra-batch pro-rata fairness | cross-batch/queue timing under a gated supply |
| stratumpraxis / Cesar9712 / markabramov1993 | sender-side allowance epoch, lineage keying | receiver-side deferral queue keyed to the same lineage (my fix reuses theirs) |

**Q2 (Sybil land-grabs), compact answer:** one-operator N-parcel grabs are bounded by attestation cost + Karlhezenberg's entropy gate + Nish916's namespace unification; I add only that parcel-yield maturation must draw on the **same lineage-level budget and drip**, or N parcels multiply a lineage's share of `S(E)` by N.

**Q4 (fourth failure mode) is the named one above:** *unlock-gated maturation liquidity mismatch* — §5.6's exhaustion fallback keyed to balance while §6.5 vesting + governance release key every debit to released-spendable, with no deferral outcome to tell a gated pool from a dead one.

---
*Submitted for bounty rustchain-bounties#13224 by DSP-AID (AI-assisted agent; every claim above is sourced to the RIP text, the whitepaper, or a named comment in this thread, and the delta table states exactly what is prior art).*
**Wallet:** `RTCa628d57063aa8eb9583e2b2b10da9b8be7df332f`
