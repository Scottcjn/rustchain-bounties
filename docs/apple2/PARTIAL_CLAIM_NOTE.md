# Apple II Miner – Partial Claim Notice (Sub-task #1 only)

**Bounty:** https://github.com/Scottcjn/rustchain-bounties/issues/436  
**PR:** _this pull-request_  
**Scope delivered:** **Sub-task #1 – Environment setup & scaffolding**

---

## What is Included
1. Reproducible CC65 tool-chain dockerfile + Makefile
2. Apple II build scaffolding under `miners/apple2/` (no networking yet)
3. Initial README explaining build and flashing to floppy/disk-image

## What is **NOT** Included (future PRs)
- Uthernet II W5100 driver & socket layer (Sub-task #2)
- HTTP client / attestation POST logic (Sub-task #3)
- Mining loop & hardware fingerprinting (Sub-tasks #4-5)
- Real-hardware proof, media evidence, BCOS checkpoint packet (Acceptance criteria #6-10)

## Why This Partial Claim
The bounty explicitly allows incremental submissions (see *Execution Plan § Partial claims accepted*). Providing the tool-chain and project skeleton unblocks subsequent networking and mining work and is therefore submitted for the **50 RTC** allotted to Requirement #1.

Maintainers: please review this PR against the Sub-task #1 acceptance criteria only. All other criteria will be addressed in follow-up PRs.

*SPDX-License-Identifier: CC-BY-4.0*
