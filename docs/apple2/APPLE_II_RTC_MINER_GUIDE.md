# Apple II RTC Miner — Port Execution Plan

Overview
--------
This document provides a concise, runnable execution plan to port the RustChain miner to the Apple II (MOS 6502 @ ~1 MHz). The goal is a minimal viable miner able to perform the required attestation HTTP requests to a RustChain node and produce evidence for the bounty.

Constraints & Targets
---------------------
- Target hardware: Apple II / II+ / IIe / IIgs (IIe enhanced or IIgs recommended)
- CPU: MOS 6502 (1 MHz typical)
- Usable RAM: ~48 KB (depends on DOS/ProDOS and card configuration)
- Networking: Uthernet II (Wiznet W5100-based) is recommended
- Language/toolchain: CC65 (6502 C) with small assembly stubs where needed

High-level Subtasks (Follow precisely)
--------------------------------------
1) Networking: Get HTTP working on Apple II (50 RTC)
   - Preferred path: Uthernet II (W5100). The W5100 provides socket-level TCP/IP hardware and greatly reduces stack complexity.
   - Approaches (pick one):
     * Use existing Apple II Contiki or IP65 stacks if available for your model.
     * Write a minimal W5100 driver to open a TCP socket and perform HTTP over it.
     * If using Uthernet II and CC65, write a small SPI driver + W5100 register helpers in C/assembly.
   - Deliverable: a minimal program that performs a GET /health or a simple HTTP POST to a configurable node URL and prints the response over serial (Super Serial Card) or writes to disk.

2) Miner client: Minimal attestation client implementation (50 RTC)
   - Language: CC65-compatible C with tiny assembly helpers for timing and hardware access.
   - Memory budget: aim for < 32 KB for the client binary to leave headroom.
   - Requirements:
     * POST to /attest/challenge (or the configured attestation endpoint)
     * Construct JSON body including `miner`, `miner_id`, `nonce`, and a minimal `report` object.
     * Compute a commitment: SHA-256 is desired. If full SHA-256 is too big, produce a server-acceptable placeholder (disclose in submission) or use a compact software SHA-256 implementation (C, ~2–4 KB code) — verify with maintainers.
     * Send the POST and show response code and body.
   - Deliverable: CC65 project that builds an Apple II binary that can send the attestation POST and print server response over serial.

3) Build & Tooling (required)
   - Toolchain: CC65 (https://cc65.github.io/). Version recommendations: latest stable release.
   - Cross-compile on modern machine and provide the .dsk/.po image or raw binary for testing.
   - If using IIgs, ProDOS/ProDOS 16 differences must be documented.
   - Deliverable: build scripts (Makefile) and instructions to produce a runnable image.

4) Testing and Evidence (required)
   - Provide step-by-step instructions to run on real hardware (or how to load images into a real II via CFFA or floppy).
   - Provide serial output logs or photos showing successful HTTP exchange and attestation response (or test node response simulated if required).
   - Provide SHA-256 verification details or explain acceptable fallback if SHA-256 cannot fit into memory.

Minimal Implementation Notes
----------------------------
- Networking with W5100 (Uthernet II):
  1. Initialize Ethernet chip and set MAC/IP (DHCP is advanced; static IP is simpler for a demo).
  2. Open TCP socket to node: default node value: https://50.28.86.131 (note: HTTPS is not feasible on Apple II; use node-side endpoint that accepts HTTP or a reverse proxy. Discuss with maintainers.)
  3. Write a minimal HTTP/1.0 POST with Content-Length header and JSON body.
  4. Read response and forward it to serial.

- JSON construction: manual string building via snprintf-style helpers in C (avoid full JSON libraries).

- SHA-256: there are small public-domain C implementations suitable for 8-bit targets. If code size is an issue, use a staged approach: deliver networking + JSON + attestation POST first, then add SHA-256 as optional follow-up. Document any deviations in the PR.

Suggested Project Layout (in repo)
----------------------------------
miners/apple2/
  |- Makefile            # build with cc65
  |- src/
     |- main.c          # CC65 C entrypoint, builds JSON and calls network
     |- w5100.c         # minimal W5100 helpers
     |- w5100.s         # assembly stubs if needed (SPI timing)
     |- sha256.c        # optional small SHA-256 implementation
  |- images/
     |- rustchain_apple2.dsk  # produced disk image for testing

Minimal CC65 main.c skeleton (concept)
--------------------------------------
// main.c (concept only — include in your PR)
// - Initialize serial for debug
// - Initialize W5100
// - Build JSON body
// - Open TCP socket and POST the body
// - Print response

Next Steps for Contributors (actionable checklist)
--------------------------------------------------
- [ ] Choose Apple II target model (IIe enhanced or IIgs recommended)
- [ ] Obtain or emulate Uthernet II hardware (real card recommended for bounty)
- [ ] Create CC65 project in miners/apple2 following the suggested layout
- [ ] Implement minimal HTTP POST to the attestation endpoint and capture responses
- [ ] Add build instructions and an images/ artifact for maintainers to verify on real hardware
- [ ] Submit PR linking this bounty issue and include logs/photos proving on-hardware operation

Notes & Caveats
---------------
- HTTPS is typically not feasible on Apple II; coordinate with maintainers to accept HTTP attestation or provide a proxy endpoint for proof-of-concept that terminates TLS on a modern host.
- The antiquity multiplier (4.0x) requires real hardware testing — emulation alone may not be accepted for the final payout.
- Keep binaries small; prefer compact C and hand-optimized assembly for tight loops and timing-critical SPI.

Acceptance Criteria (for bounty reviewers)
-----------------------------------------
1. A built Apple II image or binary that runs on real hardware and performs an HTTP POST to the attestation endpoint (or a provided test endpoint) and prints a valid server response.
2. Build instructions, Makefile, and source in miners/apple2/ included in the PR.
3. Evidence of running on a real Apple II (serial logs, photos, or verifier confirmation).
4. Optional: integrated SHA-256 commitment that the node can validate; if omitted, provide a clear explanation and mitigations.

References & Resources
----------------------
- CC65 project: https://cc65.github.io/
- Uthernet II / W5100 docs: https://a2retrosystems.com (reference hardware docs)
- Minimal W5100 programming guides and examples

Support
-------
If you have questions or need a proxy endpoint for non-HTTPS proof-of-concept, open a discussion or tag the maintainers in the bounty issue. For small clarifications, attach logs or a short screencap showing the serial output and HTTP exchange.

Good luck — bringing RustChain mining to a 1977 Apple II will be legendary. Thank you for attempting this bounty.