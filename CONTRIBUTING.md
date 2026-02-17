# Contributing to rustchain-bounties

This repo is the bounty board + automation for RustChain. PRs here should be small, clear, and auditable.

## BCOS (Beacon Certified Open Source)

This repo uses BCOS checks to keep PRs auditable and license-clean.

- **Tier label required (non-doc PRs)**: Add `BCOS-L1` or `BCOS-L2` (also accepted: `bcos:l1`, `bcos:l2`).
- **Doc-only exception**: PRs that only touch `docs/**`, `*.md`, or common image/PDF files do not require a tier label.
- **SPDX required (new code files only)**: Newly added code files must include an SPDX header near the top, e.g. `# SPDX-License-Identifier: MIT`.
- **Evidence artifacts**: CI uploads `bcos-artifacts` (SBOM, dependency license report, hashes, and a machine-readable attestation JSON).

When to pick a tier:
- `BCOS-L1`: normal automation/docs/test improvements.
- `BCOS-L2`: anything that touches payout automation, claim verification logic, or secrets handling.

## PR Hygiene

- One issue per PR when possible.
- Include proof for bounty-related automation (sample output or test run).
- Avoid adding vendored blobs; prefer pulling via package managers.

## Fast Claim Checklist (for paid bounties)

Before opening your PR, make sure your submission is payout-ready:

1. Link the bounty issue in the PR body (`Closes #<issue>` or `Refs #<issue>`).
2. Keep the change scoped to one bounty objective.
3. Attach evidence (logs/screenshots/CLI output) when the task is not self-evident from diff alone.
4. Confirm CI is green (or explain any unrelated flaky failures).
5. Add your RustChain wallet/handle exactly as requested in the issue template.

This short checklist helps reviewers verify work quickly and reduces payout delays.

## Maintainer Yes/No Checkpoint (Issue #87)

Before asking for payout or merge review, include this five-line packet:

1. Issue link
2. PR link
3. Last commit link
4. One-sentence scope statement
5. One verification note

Packet template: `docs/ISSUE_87_MINIMAL_ACCEPTANCE_PACKET.md`
