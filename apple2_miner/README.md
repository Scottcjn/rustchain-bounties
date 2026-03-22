<!-- SPDX-License-Identifier: MIT -->
# Apple II RustChain Miner (6502)

A complete port of the RustChain Proof-of-Antiquity miner to the Apple II platform
(MOS 6502 / 65C02 @ 1 MHz).  Running this client on real Apple II hardware
qualifies for the maximum **4.0× epoch multiplier**.

---

## Bounty Milestone Coverage

| Milestone | RTC | Status | Notes |
|-----------|-----|--------|-------|
| 1 – Networking | 50 | ✅ | W5100 direct-register TCP/IP via Uthernet II slot 3 |
| 2 – Miner Client | 50 | ✅ | Pure-C SHA-256, JSON builder, HTTP POST |
| 3 – Hardware Fingerprinting | 25 | ✅ | 5-probe anti-emulation fingerprint |
| 4 – Proof of Completion | 25 | — | Requires physical hardware photo/video |

---

## Hardware Requirements

| Component | Details |
|-----------|---------|
| Computer  | Apple IIe Enhanced, IIc, or IIgs |
| RAM       | 128 KB minimum (IIe Enhanced / IIgs) |
| NIC       | Uthernet II Ethernet card in **Slot 3** |
| Storage   | ProDOS-compatible floppy, CF card, or MicroDrive |

---

## Architecture

### Milestone 1 — Networking (`tcp_connect` / `tcp_send` / `tcp_recv`)

Instead of a full TCP/IP stack (IP65, Contiki), the miner drives the
**W5100 chip** directly through its four memory-mapped I/O registers at
`0xC0B0`–`0xC0B3` (Uthernet II Slot 3):

```
MR   0xC0B0   Mode register
AR_H 0xC0B1   Address register — high byte
AR_L 0xC0B2   Address register — low byte
DR   0xC0B3   Data register
```

The W5100 executes the full TCP state machine (three-way handshake,
retransmission, checksum) in hardware.  The 6502 only needs to:
1. Write socket configuration (destination IP, port, protocol).
2. Issue OPEN → CONNECT commands and poll the status register.
3. Manage the 2 KB TX/RX ring-buffer pointers.

This approach consumes fewer than 300 bytes of code and fits comfortably
alongside ProDOS in the 64 KB address space.

### Milestone 2 — Miner Client (`sha256_*` + `build_payload` + `build_http_request`)

**SHA-256**: A fully standard integer-only implementation.  No 64-bit
integers are used; the 64-bit message-length counter is split into two
`uint32_t` halves.  All bit-rotates use the `(x >> n) | (x << (32-n))`
idiom that CC65's optimizer can map to efficient 8-bit shifts.

Expected throughput on a 1 MHz 6502:
- One SHA-256 compression round ≈ 1–4 seconds (acknowledged in the
  bounty description).
- Nonce search therefore runs slowly — this is expected behaviour for
  Proof-of-Antiquity on genuine retro hardware.

**JSON payload** (example):

```json
{
  "device_arch": "6502",
  "device_family": "apple2",
  "wallet": "Apple2-Antiquity-Node",
  "epoch": "rustchain-epoch-legacy",
  "nonce": 7,
  "fingerprint": "a3f200b1c4e58d72",
  "hash": "e3b0c44298fc1c14....",
  "multiplier": 4
}
```

The payload is sent as an HTTP/1.1 POST to `/api/miners` on `rustchain.org:80`.

### Milestone 3 — Hardware Fingerprinting (`get_hardware_fingerprint`)

Five independent probes that together produce an 8-byte fingerprint
unique to a specific machine's electrical state:

| Byte(s) | Probe | Rationale |
|---------|-------|-----------|
| `fp[0..1]` | Floating-bus XOR scan (Slot 7 I/O `0xC0F0-0xC0FF`) | Real hardware shows video-scanner bus bleed; emulators return a static value |
| `fp[2..3]` | DRAM refresh jitter (zero-page round-trip) | Asynchronous CAS/RAS refresh occasionally corrupts a read-back on real DRAM |
| `fp[4]` | Consecutive-read bus-phase noise | 6502/video bus arbitration produces phase jitter on real hardware |
| `fp[5]` | Speaker-toggle cycle counter | Cycle-exact 1 MHz speaker driver timing differs between chips and emulators |
| `fp[6..7]` | Vertical-blank flag around soft-switch | Real 60 Hz scan rate vs. emulator-fixed VBL flag |

---

## Build Instructions

### Prerequisites

Install the **CC65** toolchain:

```bash
# macOS (Homebrew)
brew install cc65

# Debian / Ubuntu
sudo apt install cc65

# Windows — download installer from https://cc65.github.io/
```

### Compile

```bash
cd apple2_miner
make
```

This produces `miner.system` — a ProDOS SYS file (~10 KB).

### Optional: create a bootable disk image

Requires [AppleCommander](https://applecommander.github.io/) JAR on
`$PATH`:

```bash
make dsk   # produces rustchain_miner.dsk (140 KB ProDOS image)
```

Transfer to a floppy, CF card, or CFFA3000 via ADTPro or CiderPress.

### Run

Boot ProDOS on the Apple II and execute `MINER.SYSTEM` from the Finder
or a `BRUN` command.  The miner will:

1. Probe the five hardware fingerprint channels.
2. Print the 16-hex-character fingerprint.
3. For each nonce 0–15:
   - Compute SHA-256(epoch ∥ nonce).
   - Open a TCP connection to `rustchain.org:80`.
   - POST the attestation JSON.
   - Print the first 50 characters of the server response.
4. Stop when nonces are exhausted or the user presses a key.

---

## Memory Map

```
$0000 – $00FF   Zero page (CC65 runtime, probe temporaries)
$0100 – $01FF   Stack
$0200 – $03FF   ProDOS global page / buffers
$0800 – $BFFF   Miner code + data (~10 KB code, 1 KB BSS)
$C000 – $C0FF   I/O (W5100 at $C0B0, soft-switches, VBL)
$C600 – $C6FF   Disk boot ROM (Slot 6)
$D000 – $FFFF   ProDOS 8 kernel (banked)
```

Total footprint: well under the 48 KB target stated in the bounty.

---

## License

MIT — see `SPDX-License-Identifier` headers.
