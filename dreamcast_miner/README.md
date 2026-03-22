# RustChain Sega Dreamcast (SH4) Miner

Port of the RustChain miner to Sega Dreamcast (1999, SH4 @ 200MHz) via the Broadband Adapter. First console miner on the RustChain network. The SH4 earns a **3.0x antiquity multiplier**.

## Hardware Requirements

| Component | Notes |
|-----------|-------|
| Sega Dreamcast | Any region, any revision |
| Broadband Adapter | HIT-0400 (100Mbps) or HIT-0300 (10Mbps) |
| Boot media | CD-R (MIL-CD) or GDEMU/SD adapter |
| Network | Ethernet to your LAN |

## Prerequisites

### Boot Linux on Dreamcast

1. Download a minimal Dreamcast Linux image
2. Flash to CD-R or use GDEMU/SD adapter
3. Boot via MIL-CD exploit (no modchip needed for CD-R)

### Cross-Compile Toolchain

```bash
# Install SH4 cross-compiler
apt install binutils-sh4-linux-gnu gcc-sh4-linux-gnu
```

## Build

```bash
make

# Output: minerdc (SH4 ELF binary)
```

## Run

```bash
./minerdc --wallet YOUR_WALLET_NAME
```

## SH4-Specific Fingerprinting

The Dreamcast SH4 fingerprint exploits the unique characteristics of the SH7750:

1. **TMU Timer Drift** — The SH4 Timer Unit (TMU) runs at 27MHz / divisor.
   Real Dreamcast hardware has distinctive TMU timing vs. emulators.

2. **16KB Split Cache** — SH4 has 16KB I-cache + 16KB D-cache with unique
   latency profiles. Sequential vs. strided memory access is measured.

3. **FPU Jitter** — The SH4 FPU has a distinctive 4-stage pipeline.
   Floating-point operations on real hardware have a measurable fingerprint
   vs. emulators (NullDC, Flycast, etc.).

4. **Anti-Emulation** — SH4 cache timing, TMU registers, and FPU pipeline
   behavior differ measurably between real hardware and emulators.

## Network

The Broadband Adapter (BBA) uses the 8139too Linux driver.
The attestation uses HTTP POST to port 80 (no TLS needed).

## 3.0x Multiplier

```
sh4 / dreamcast → 3.0x base multiplier (HIGHEST IN NETWORK)
```

The Dreamcast earns 3x the RTC per epoch compared to a modern x86 machine.
More than PowerPC G4 (2.5x), more than PowerPC G5 (2.0x).

## MicroPython Alternative

For a lighter implementation using MicroPython:

```bash
# Build MicroPython for SH4
git clone https://github.com/micropython/micropython.git
cd micropython/ports/unix
make CROSS_COMPILE=sh4-linux-gnu- MICROPY_PY_USSL=0
# Copy micropython binary to Dreamcast
# Then run miner.py on the Dreamcast
```

## License

MIT
