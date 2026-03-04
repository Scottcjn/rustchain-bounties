# SPDX-License-Identifier: MIT

# Apple II Miner Port Plan (Scaffold)

This document tracks the step-by-step work for bounty **#436**.

## ✅ 1. Environment & Skeleton (this PR)
* CC65 build tool-chain verified
* `miners/apple2/` directory created
* Minimal `main.c` that boots and prints banner on Apple II
* `Makefile` builds DOS 3.3 disk image (`*.dsk`) ready for flashing or emulator testing

## ⏳ 2. Uthernet II Driver (next)
* Low-level W5100 register access in 6502 assembly
* TCP socket open / send / recv helpers

## ⏳ 3. Minimal HTTP POST Client
* Manual request string construction
* Response code parse (3-digit only)

## ⏳ 4. Miner Core Loop
* Proof-of-Age compatible workload (integer-only)
* JSON payload assembly for `/attest/submit`

## ⏳ 5. Hardware Fingerprinting Routines
* Clock-drift, floating-bus, memory refresh timing, etc.

## Build Instructions (host)
```bash
cd miners/apple2
make          # produces rustchain_apple2_miner.dsk
```

Flash or load `rustchain_apple2_miner.dsk` on real Apple II hardware (or emulator for development only). A banner should appear; further functionality will be added in subsequent PRs.
