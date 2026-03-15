<!-- SPDX-License-Identifier: MIT -->
# Apple II RustChain Miner (6502)

This implements the RustChain Proof-of-Antiquity miner for the Apple II platform (MOS 6502 @ 1MHz).
By running this client, you qualify for the maximum **4.0x epoch multiplier**.

## Hardware Requirements
- Apple IIe or IIgs (128KB RAM minimum recommended)
- Uthernet II Ethernet Card (installed in Slot 3)
- ProDOS storage medium

## Architecture Details

### 1. Zero-Overhead Networking (W5100 Raw Sockets)
To fit within the 64KB address space alongside ProDOS, this miner bypasses traditional TCP/IP stacks (like IP65/Contiki). Instead, it communicates directly with the Uthernet II's W5100 networking chip via memory-mapped IO registers at `0xC0B0`. The W5100 handles the TCP handshake and packet construction in hardware.

### 2. Hardware Fingerprinting (Anti-Emulation)
We sample the Apple II's floating bus behavior at `0xC0F0` (Slot 7 IO space). Real Apple II hardware exhibits video scanner memory bleed on floating pins when not actively driven by an expansion card. Emulators rarely synchronize video analog states to the floating bus accurately, making this an excellent cryptographic signature for antiquity verification.

### 3. Hash Implementation
A lightweight 8-bit iterative hashing routine derives the nonce to secure the block within the constraints of the 1MHz clock speed.

## Build Instructions
Requires the [CC65 compiler suite](https://cc65.github.io/):

```bash
cd apple2_miner
make
```

Transfer `miner.system` to your CFFA3000, MicroDrive, or Floppy, and execute it from ProDOS.
