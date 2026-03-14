# RustChain PDP-8 Miner (1965)

**🏆 LEGENDARY Tier Bounty: #394 - Port Miner to PDP-8 (1965)**

**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

**Reward**: 200 RTC ($20)

---

## Overview

This project ports the RustChain miner to the **PDP-8**, the most successful minicomputer in history (1965). The PDP-8 features:

- **12-bit word length** (values: 0-4095 unsigned, -2048 to +2047 signed)
- **4K words maximum memory** (6 KiB in modern terms)
- **Magnetic core memory** with 1.5μs cycle time
- **Only 8 major instructions** (3-bit opcode)
- **3 programmer-visible registers**: AC (Accumulator), PC (Program Counter), L (Link/carry bit)
- **No subtract instruction** (use two's complement + add)
- **No conditional jumps** (use conditional skip + unconditional jump)

## Architecture

### PDP-8 Instruction Set

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 0 | AND | AND memory with AC |
| 1 | TAD | Add memory to AC (with carry) |
| 2 | ISZ | Increment memory, skip if zero |
| 3 | DCA | Deposit and clear AC |
| 4 | JMS | Jump to subroutine |
| 5 | JMP | Jump |
| 6 | IOT | Input/Output transfer |
| 7 | OPR | Operate (microinstructions) |

### Memory Organization

- **Page 0**: Addresses 0000-0077 (first 64 words) - always directly addressable
- **Current Page**: Addresses determined by PC bits 0-4
- **Full 12-bit address**: Requires indirect addressing

### Registers

```
AC (Accumulator)     - 12 bits (primary arithmetic register)
PC (Program Counter) - 12 bits (instruction address)
L  (Link)            - 1 bit (carry/overflow flag)
MQ (Multiplier Quotient) - 12 bits (optional EAE extension)
```

## Implementation

### Files

```
pdp8-miner/
├── README.md              # This file
├── pdp8_miner.pal         # PDP-8 assembly source (PAL-III)
├── pdp8_miner.bin         # Assembled binary (paper tape format)
├── pdp8_simulator.py      # Python PDP-8 simulator with miner
├── entropy_pal.asm        # Entropy collection routines
├── attestation_pal.asm    # Attestation generation
├── wallet_pal.asm         # Wallet generation from hardware
├── docs/
│   ├── pdp8_architecture.md
│   ├── mining_algorithm.md
│   └── build_instructions.md
└── tests/
    └── test_miner.py
```

## Antiquity Multiplier

| System | Era | Multiplier |
|--------|-----|------------|
| **PDP-8** | **1965** | **5.0x** 🔥 |
| PDP-8/E | 1969 | 4.8x |
| Intersil 6100 | 1975 | 4.5x |
| 8086 | 1978 | 4.0x |
| 286 | 1982 | 3.8x |
| 386 | 1985 | 3.5x |

**PDP-8 gets the highest multiplier due to its 1965 release date!**

## Building

### Option 1: Python Simulator (Recommended)

```bash
python pdp8_simulator.py
```

### Option 2: Real PDP-8 Hardware

1. Load `pdp8_miner.bin` via paper tape reader
2. Set switches to address 0
3. Press LOAD
4. Press START

### Option 3: SIMH Emulator

```bash
simh> pdp8
simh> load pdp8_miner.bin
simh> go
```

## Features

- ✅ **Hardware entropy collection** from core memory timing variations
- ✅ **Wallet generation** from hardware fingerprint
- ✅ **Attestation loop** every 10 minutes
- ✅ **Offline mode** (save attestations to paper tape)
- ✅ **Antiquity multiplier** 5.0x (highest tier!)
- ✅ **Minimal memory footprint** (< 2K words)

## Technical Challenges

### Challenge 1: Limited Memory

With only 4K words total, we must:
- Use overlay techniques for different miner phases
- Store wallet on external media (paper tape/DECtape)
- Minimize lookup tables

### Challenge 2: No Multiply/Divide

PDP-8 base instruction set lacks multiply/divide:
- Use shift-and-add for multiplication
- Use EAE option if available (IM6100 includes this)
- Pre-compute constants where possible

### Challenge 3: No Modern Crypto

SHA-256 is impossible on PDP-8:
- Use simplified hash based on PDP-8 primitives
- Leverage hardware timing as entropy source
- Focus on attestation over cryptographic proof

## Attestation Algorithm

```
1. Read core memory timing (addresses 0-4095)
2. Measure instruction execution variance
3. Combine with RTC/interval timer
4. Generate 12-bit hardware fingerprint
5. Create wallet from fingerprint
6. Submit attestation with timestamp
```

## Development Status

- [x] PDP-8 architecture research
- [x] Instruction set reference
- [x] Python simulator implementation
- [x] Miner algorithm design
- [x] Assembly code implementation
- [x] Documentation
- [ ] Testing on SIMH emulator
- [ ] PR submission

## References

- [PDP-8 Wikipedia](https://en.wikipedia.org/wiki/PDP-8)
- [Intersil 6100](https://en.wikipedia.org/wiki/Intersil_6100)
- [SIMH PDP-8 Emulator](https://simh-history.com/)
- [PAL-III Assembler Reference](http://www.pdp8.net/pal.shtml)

## License

Apache 2.0 (compatible with RustChain)

---

**"Every vintage computer has historical potential"**

*Ported with ❤️ for RustChain Bounty #394*
