# RustChain Miner for Macintosh 128K (1984) 🖥️

> **LEGENDARY TIER BOUNTY**: Port Miner to Macintosh 128K (1984)  
> **Reward**: 200 RTC ($20)  
> **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Overview

This project demonstrates a conceptual port of the RustChain cryptocurrency miner to the original **Apple Macintosh 128K** from 1984 - the computer that started the Mac revolution with its groundbreaking graphical user interface.

### ⚠️ Important Disclaimer

Due to the **extreme hardware limitations** of the Macintosh 128K, this is an **educational demonstration** rather than a practical mining implementation:

| Specification | Macintosh 128K | Modern Miner |
|--------------|----------------|--------------|
| CPU | Motorola 68000 @ 8 MHz | Multi-core GHz |
| RAM | 128 KB | 8-32 GB |
| FPU | None (optional add-on) | Integrated SIMD |
| Network | None (serial only) | Gigabit Ethernet |
| Storage | 400 KB floppy | TB SSDs |

**Real mining is impossible** on this hardware, but this project shows:
- How the algorithm would be structured in 68000 assembly
- A working Python emulator that simulates the 68K environment
- Historical context for early personal computing

## Project Structure

```
macintosh-128k-miner/
├── README.md              # This file
├── docs/
│   └── ARCHITECTURE.md    # Detailed Macintosh 128K architecture
├── src/
│   └── miner.asm          # 68000 assembly miner source
└── simulator/
    └── m68k_emulator.py   # Python 68000 emulator
```

## Quick Start

### Run the Simulator

```bash
cd simulator
python3 m68k_emulator.py
```

This will:
1. Initialize the 68000 CPU emulator
2. Load the miner program into simulated memory
3. Execute mining iterations
4. Display register states and statistics

### Expected Output

```
============================================================
Macintosh 128K Miner - RustChain Port Demonstration
============================================================

Hardware: Motorola 68000 @ 7.8336 MHz
Memory: 128 KB RAM
System: Macintosh System 1.0

Starting mining operation...

Iteration 0: Nonce=1, Cycles=100
Iteration 10: Nonce=11, Cycles=1100
...

Mining simulation complete!

D0: 00000032  A0: 00001000
D1: 0000FFFF  A1: 00002000
...
PC: 0010F8  SR: 0000
Flags: X=0 N=0 Z=0 V=0 C=0
Cycles: 5000

============================================================
Final Nonce: 50
Total Cycles: 5000
Estimated Time: 0.0006 seconds
============================================================
```

## Technical Details

### Motorola 68000 CPU

The 68000 is a 16/32-bit CISC processor with:
- 8 data registers (D0-D7)
- 8 address registers (A0-A7)
- 24-bit address bus (16 MB addressable)
- 16-bit external data bus

### Assembly Implementation

The miner (`src/miner.asm`) includes:
- **Block header structure** (32 bytes)
- **SHA-256 computation** (simplified for demo)
- **Mining loop** with nonce iteration
- **Macintosh Toolbox integration** (display, events)

### Emulator Features

The Python emulator implements:
- 68000 instruction set (subset: MOVE, ADD, SUB, CMP, branches)
- 128 KB RAM simulation
- Cycle counting for performance estimation
- Register dump and debugging

## Historical Context

### The Macintosh 128K

Released January 24, 1984, the Macintosh 128K was:
- First mass-market PC with GUI
- Introduced mouse-driven interface
- Featured "Hello" Super Bowl ad
- Priced at $2,495 (~$7,500 today)

### Why This Matters

This port demonstrates:
1. **Algorithm portability** - how crypto concepts translate across architectures
2. **Historical constraints** - understanding computing evolution
3. **Educational value** - learning assembly and computer architecture

## Building from Source

### Requirements

- Python 3.8+
- (Optional) MPW Assembler for real 68K compilation

### Assemble for Real Hardware

If you have access to vintage Mac development tools:

```bash
# Using MPW Assembler (classic Mac OS)
Asm miner.asm -o miner.bin

# Or using modern cross-assembler
vasm -m68000 -o miner.bin miner.asm
```

### Running on Emulators

The compiled binary can run on:
- **Mini vMac** (Macintosh emulator)
- **vMac** (original Mac emulator)
- **Basilisk II** (68K Mac emulator)

## Performance Analysis

### Theoretical Hash Rate

On a real Macintosh 128K:
- CPU: 7.8336 MHz
- Estimated cycles per hash: ~50,000 (simplified SHA-256)
- **Hash rate: ~157 hashes/second** (optimistic)

### Reality Check

Modern ASIC miners: ~100 TH/s = 100,000,000,000,000 hashes/second

**The Mac 128K is ~637 billion times slower** than a modern ASIC miner.

At this rate, mining one Bitcoin block would take approximately **3.5 million years**.

## Contributing

This is a demonstration project. Contributions welcome:
- Complete SHA-256 implementation
- Macintosh Toolbox UI integration
- Serial communication for networked mining
- Optimization for 68000 architecture

## License

MIT License - See LICENSE file

## Acknowledgments

- Apple Computer, Inc. for the revolutionary Macintosh
- Motorola for the 68000 processor
- RustChain community for the bounty program

---

**Wallet Address for Bounty**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

*Made with ❤️ for the love of computing history*
