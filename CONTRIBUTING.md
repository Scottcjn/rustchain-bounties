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

