# RustChain SPARCstation (SPARC V7) Miner

Port of the RustChain miner to Sun SPARCstation IPX (1991, SPARC V7 @ 40MHz). First Sun workstation miner on the RustChain network. The SPARCstation IPX earns a **2.5x antiquity multiplier** (1990-1994 era).

## Hardware Requirements

| Component | Notes |
|-----------|-------|
| SPARCstation | IPX, IPXC, SLC, ELC (any variant) |
| Memory | Minimum 8MB RAM, 16MB recommended |
| Storage | 200MB+ SCSI disk |
| Network | 10Mbps AUI/UTP via on-board Ethernet (hme0) |
| Display | CG6 (color) or CG3 (grayscale) framebuffer |

## Prerequisites

### Boot SunOS or Solaris

1. **SunOS 4.1.x** (recommended for IPX):
   - Download SunOS 4.1.4 media
   - Boot from CD or network (tip: use QEMU-sparc for testing)
   
2. **Solaris 2.x** (alternative):
   - Solaris 2.5.1 or later for SPARCstation

### Install Development Tools

```bash
# On the SPARCstation itself:
# Install gcc and networking libraries
pkgadd -d https://get.spack.org/sparc/sunlib SUNWgcc
# Or from media:
mount /dev/cdrom /mnt
pkgadd -d /mnt/Solaris_2.x/Tools/setup_install SUNWgcc SUNWtoo
```

### Cross-Compile Toolchain

```bash
# Install SPARC cross-compiler (for building on x86)
apt install binutils-sparc-linux-gnu gcc-sparc-linux-gnu

# Build:
make CC=sparc-linux-gnu-gcc
```

## Build

```bash
# Native build (on SPARCstation):
make native

# Cross-compile (on x86):
make cross
```

## Run

```bash
./minersparc --wallet YOUR_WALLET_NAME
```

## SPARC-Specific Fingerprinting

The SPARCstation fingerprint exploits the unique characteristics of the SPARC V7 architecture:

1. **Split I/D Cache** — SPARC has separate instruction and data caches.
   Real hardware has distinctive cache hit/miss timing vs. emulators.

2. **FPU Pipeline** — The SPARC FPU (often a separate chip like the Cypress C68881)
   has unique floating-point timing on real hardware.

3. **Memory Bus Timing** — SPARCstation IPX uses page-mode DRAM with
   distinctive access patterns. Sequential vs. strided reads are measurable.

4. **Tick Register** — The SPARC %tick register (cycle counter) provides
   hardware-grade nonces that prove real-time execution.

5. **Platform String** — SI_PLATFORM sysinfo returns "SUNW,SPARCstation-IPX"
   or similar, hashed into the fingerprint.

## Network

The SPARCstation IPX uses the `hme` (Happy Meal Ethernet) driver for 10/100Mbps.
The attestation uses HTTP POST to port 80 (no TLS for maximum compatibility).

## 2.5x Multiplier

```
SPARCstation IPX (1991) → 2.5x base multiplier (1990-1994 tier)
```

The SPARCstation earns 2.5x the RTC per epoch compared to a modern x86 machine.
Competes with Dreamcast (3.0x), exceeds x86 PC era machines.

## Why SPARCstation?

The SPARCstation IPX represents the 1990-1994 workstation era:
- **40MHz SPARC V7** CPU — pure RISC architecture
- **SunOS 4.1.x** — classic Unix workstation environment  
- **Classic Unix networking** — pre-POSIX threads, pre-IPv6
- **Distinctive hardware** — no x86 heritage whatsoever

This is the Ghost in the Machine: a legendary Sun workstation, resurrected for
the RustChain network.

## Testing Without Hardware

For development/testing without physical SPARC hardware:

```bash
# Use QEMU SPARC emulation:
qemu-system-sparc -M SS-5 -m 256 -hda disk.img -net user,hostfwd=tcp::8022-:22

# Or SPARC64 (SparcStation 10 or later):
qemu-system-sparc64 -M prep -m 512 -hda disk.img
```

## License

MIT
