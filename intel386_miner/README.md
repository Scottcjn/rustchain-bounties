# RustChain Intel 386 Miner

Port of the RustChain miner to Intel i386 (1985). The 386 earns a **4.0x antiquity multiplier** — the maximum tier in the RustChain network.

## Hardware Requirements

| Component | Notes |
|-----------|-------|
| 386 system | 386DX or 386SX, any speed (16-40MHz) |
| RAM | 4MB minimum (8MB+ preferred) |
| Network card | NE2000 compatible ISA (0x300 default I/O) |
| Boot media | Floppy, CF-to-IDE, or HDD |
| Storage | 10MB+ for DOS + mTCP |

## Supported Modes

- **DOS + mTCP** (easiest): DJGPP C compiler, DOS packet driver for NE2000
- **Linux on 386**: ELKS or old Slackware, i386-elf-gcc toolchain

## Build — DOS / DJGPP

```bash
# Install DJGPP (http://www.delorie.com/djgpp/)
# Set DJGPP environment:
#   set DJGPP=C:\DJGPP\DJGPP.ENV
#   set PATH=C:\DJGPP\BIN;%PATH%

gcc -o miner386.exe miner.c -lsocket

# Run
miner386 --wallet YOUR_WALLET_NAME
```

## Build — Linux / i386-elf-gcc

```bash
# Install i386 cross-compiler
apt install binutils-i386-elf gcc-i386-elf

# Build
i386-elf-gcc -o miner386 miner.c -static -no-pie -march=i386

# Run (as root, for raw network access)
./miner386 --wallet YOUR_WALLET_NAME
```

## Build — Native 386 Linux (no cross-compile)

```bash
# On a 386 with Linux (ELKS or Slackware 3.x):
# Install the DJGPP-like compiler:
#   apt install gcc-386

gcc -o miner386 miner.c -march=i386 -static
./miner386 --wallet YOUR_WALLET_NAME
```

## Usage

```bash
miner386 --wallet YourWalletName           # Default node (50.28.86.131)
miner386 --wallet YourWalletName --node custom.node.com:8080
```

## 386-Specific Fingerprinting

The 386 fingerprint exploits unique characteristics of the 1985 architecture:

1. **No L1/L2 Cache** — Early 386s had zero cache (or at most 16-64KB).
   Strided memory access is dramatically slower than sequential.
   The `get_386_fingerprint()` function measures this.

2. **Clock Drift** — The 386 crystal oscillator has massive drift
   compared to modern CPUs. Measured via TSC (Time Stamp Counter).

3. **No FPU** — 386SX/DX without 387 coprocessor does software float only.
   Presence/absence of 387 is itself a hardware fingerprint.

4. **ISA Bus Timing** — Unique bus arbitration on real 386 hardware.

## Network

The NE2000 ISA Ethernet card (0x300 I/O base) is used for TCP/IP.
- **DOS**: mTCP packet driver (http://www.brutman.com/mTCP/)
- **Linux**: kernel socket layer (standard TCP/IP)

The attestation uses HTTP POST to port 80 (no TLS — the 386 can't do modern TLS).

## Attestation Payload

```json
{
  "device_arch": "i386",
  "device_family": "i386",
  "wallet": "YourWalletName",
  "fingerprint": "DEADBEEF",
  "nonce": "12345678",
  "hash": "CAFEBABE",
  "has_fpu": 0,
  "miner_id": "YourWalletName"
}
```

## The 4.0x Multiplier

```
i386 / 386 → 4.0x base multiplier (MAXIMUM TIER)
```

Nothing earns more per epoch than a 386. You need ~4 modern x86_64 machines to match what one 386 earns.

## License

MIT
