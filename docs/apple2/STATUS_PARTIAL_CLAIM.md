# Apple II Miner – Partial Claim (Sub-task #1)

SPDX-License-Identifier: MIT

This pull request intentionally **covers ONLY Sub-task #1** of the execution plan for
RustChain bounty **#436 – “Port RustChain Miner to Apple II (6502)”**.

| Acceptance Criterion | Status | Notes |
|----------------------|--------|-------|
| 1. Networking functional (Uthernet II driver) | ❌ Pending | Will be implemented in follow-up PR (#2) |
| 2. Build environment & scaffolding | ✅ Complete | CC65 tool-chain, Makefile, directory layout, draft sources |
| 3. HTTP POST attestation | ❌ Pending | Will rely on W5100 TCP sockets once networking lands |
| 4. Hardware fingerprinting | ❌ Pending | Timing/floating-bus routines planned for PR #3 |
| 5. Miner visible in network API | ❌ Pending | Dependent on #2 & #3 |
| 6. Photo/video evidence on real hardware | ❌ Pending | Will be attached with first on-hardware run |
| 10. Real hardware proof (4.0× multiplier) | ❌ Pending | Same as above |

## What *is* included in this PR
1. Reproducible Apple II cross-compile environment using **CC65 2.19**.
2. `miners/apple2/` directory structure with placeholder source files and SPDX headers.
3. `Makefile` targets:
   * `make host` – build minimal host simulator stub (for compiler sanity).
   * `make apple2` – produce Apple II flat binary (`apple2_miner.bin`).
4. `docs/apple2/PORT_PLAN.md` – technical blueprint and task breakdown (initial draft).

## Not Included (to be delivered in subsequent PRs)
* Uthernet II driver and raw W5100 socket helpers.
* Minimal HTTP client for attestation.
* SHA-256 and JSON construction routines.
* Mining loop, hardware fingerprinting, and anti-emulation logic.
* Real-device evidence & attestation screenshots.

## Quick Test Instructions (Emulator Only – **NOT** qualifying for bounty)
```bash
# Build the placeholder binary
make -C miners/apple2 apple2
# Run in AppleWin or MAME to observe startup banner
openapple apple2_miner.bin      # or your preferred emulator
```
The binary prints:
```
RustChain Apple II Miner – scaffolding build r0.1
```
No networking/mining activity is performed yet.

## Next Steps
1. **PR #2 – Networking & Uthernet II Driver**
2. **PR #3 – HTTP client + Attestation**
3. **PR #4 – Mining core + Fingerprinting**
4. Final evidence capture on real Apple IIe with Uthernet II card.

---
Maintainer checkpoint packet will be added once Sub-task #2 is complete.