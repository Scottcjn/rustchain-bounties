# Season 1 — Harden the Forge: Claim Requirements

Tracking issue: `Scottcjn/rustchain-bounties#400`
Season window: **Feb 22 – Apr 5, 2026** (6 weeks)
Total pool: **750 RTC** (plus bonus RTC for newly discovered vulnerabilities)
Grand prize: **250 RTC** to the top season contributor at season end.

This document exists because the #400 comment thread has accumulated a large number of
low-signal posts: claim-only comments, "I can do this" intros, and reports that are not
security findings (for example, complaints about emoji rendering in the GitHub API).
Maintainers should not have to re-explain the acceptance bar in every reply.

If a comment does not satisfy this document, it is **not a claim** and carries no
reservation of a bounty slot.

---

## 1. Season bounty table

| Issue | Challenge | Reward | Difficulty |
|-------|-----------|--------|------------|
| #54 | Ledger Integrity Audit | 200 RTC | Hard |
| #56 | Epoch Settlement Testing | 150 RTC | Hard |
| #57 | API Auth Hardening | 100 RTC | Medium |
| #58 | Consensus Attack Vectors | 200 RTC | Hard |
| #59 | Pending Transfer Edge Cases | 150 RTC | Medium |
| #60 | Ergo Anchor Integrity | 100 RTC | Medium |
| #398 | Security Quest Chain | 100 RTC | Progressive |

### Hardening trio (separate, reduced payouts, strict acceptance)

| Issue | Challenge | Reward |
|-------|-----------|--------|
| #474 | Epoch Determinism Simulator + Cross-Node Replay | 113 RTC |
| #475 | Attestation Fuzz Harness + Crash Regression Corpus | 98 RTC |
| #476 | Sybil/Farming Risk Scorer for Bounty Claims | 83 RTC |

Trio total pool: 294 RTC. For the trio, **the first high-quality valid submission per
bounty wins** — an early claim comment does not secure the slot.

> Note: several issue IDs in the original #400 table appear to reference old or closed
> issues. Confirm the currently open issue ID with a maintainer before starting work on a
> specific bounty, and cite the confirmed ID in your claim.

---

## 2. Required fields in a claim comment

Every claim must be posted as a **single comment** containing all of the following. A
claim missing any field is treated as incomplete and is not queued.

```
Bounty: <issue number + title>
GitHub handle: <handle>
Wallet / miner ID: <RTC wallet or miner ID used for payout>

Scope: <which files/endpoints/modules you will touch>
Implementation plan:
  1. <step>
  2. <step>
  3. <step>
Test plan:
  - <exact command or test file that will prove the work>
  - <what a failing run looks like before the fix>
Deliverable form: <PR link target | audit report path | harness + corpus path>
ETA: <YYYY-MM-DD>
```

Minimum bar:

- **Wallet / miner ID** is mandatory. Payout is impossible without it.
- **Scope** must name concrete code paths, not a theme ("security hardening" is not a scope).
- **Test plan** must name a command a maintainer can run, or a test file that will exist in the PR.
- **ETA** must be a date inside the season window or clearly justified.

---

## 3. What counts as a deliverable

Accepted, per bounty type:

- **Audit bounties (#54, #58, #60):** a report committed under `bounties/` with a
  finding list (severity, location, impact, reproduction steps, suggested fix). Findings
  without reproduction steps are not findings.
- **Testing bounties (#56, #59, #475):** runnable tests or a harness, committed with the
  test command documented and passing/failing deterministically.
- **Hardening bounties (#57, #474, #476):** a patch (PR) plus the test that fails before
  the patch and passes after it.
- **#398 Quest Chain:** incremental steps, each step landed separately with its own
  verifiable artifact.

Not accepted:

- Claim-only or intent-only comments with no artifact.
- Reports about GitHub UI/rendering behavior (emoji, markdown, badges) presented as
  security findings.
- Duplicate claims on a bounty already claimed with a merged artifact.
- "I have experience in X" skill listings used in place of a plan.

---

## 4. Claim lifecycle

1. **Claim posted** — must satisfy section 2. Maintainer acknowledges; slot is held for
   the stated ETA.
2. **ETA passes with no artifact** — slot is released; the bounty returns to the open pool
   and may be claimed by someone else.
3. **Artifact submitted** — PR opened or report committed, linked in the original claim
   comment (edit the comment; do not post a new one).
4. **Reviewed and merged** — the artifact is reviewed against the test plan from step 1.
   A passing test plan is the primary acceptance signal.
5. **Payout recorded** — the RTC amount and the contributor handle are added to the season
   leaderboard in #400.

Leaderboard is updated weekly (Saturdays).

---

## 5. Bonus findings

A vulnerability discovered during the season that is **not** covered by an existing bounty
earns bonus RTC on top of the standard bounty. Bonus eligibility requires the same evidence
bar as a standard finding: severity, affected code location, reproduction steps, and a
suggested fix or patch. Unreproducible reports earn nothing.

---

## 6. Payout boundary

This document is a process description only. It is not a maintainer award, payout approval,
wallet transfer, or payment receipt. Being listed here, or posting a compliant claim, does
not by itself entitle a contributor to any RTC. Actual awards are made by the repository
maintainer after review of a merged artifact, and remain subject to the season pool limits
and the general bounty terms of this repository.

---

## 7. Copy-paste claim template

```
Bounty: #57 API Auth Hardening (100 RTC)
GitHub handle: @your-handle
Wallet / miner ID: your-wallet-id

Scope: node/rustchain_sync.py request validation; auth check on write endpoints
Implementation plan:
  1. Reproduce missing-input-validation path with a focused test
  2. Add validation and reject non-conforming payloads
  3. Add regression tests for rejected and accepted payloads
Test plan:
  - python3 -m pytest -q node/tests/test_state_provider_api.py
  - Before fix: new test fails with 200 instead of 400
Deliverable form: PR against Scottcjn/Rustchain
ETA: 2026-03-20
```

Replace every field with real values. A template posted unmodified is treated as a
non-claim.
