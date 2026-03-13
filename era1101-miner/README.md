# ERA 1101 RustChain Miner (1950)

**LEGENDARY Tier Bounty - 200 RTC ($20)**

Port of RustChain miner to the ERA 1101, the first commercially available stored-program computer (1950).

## Overview

This project implements a RustChain cryptocurrency miner on the ERA 1101 computer system, featuring:
- **24-bit parallel binary architecture** with ones' complement arithmetic
- **Magnetic drum memory** (16,384 words × 24 bits = 48 KB)
- **Drum scheduling optimization** for minimal rotational latency
- **Paper tape I/O interface** for network communication
- **5.0× antiquity multiplier** - maximum tier in RustChain

## Architecture Highlights

### ERA 1101 Specifications

| Feature | Specification |
|---------|---------------|
| **Word Size** | 24 bits (parallel binary) |
| **Accumulator** | 48 bits (double-word, subtractive design) |
| **Q-Register** | 24 bits (multiplier/quotient) |
| **Memory** | 16,384 words × 24 bits (48 KB) |
| **Storage** | Magnetic drum, 3500 RPM |
| **Access Time** | 32 μs (min) to 17 ms (max) |
| **Instructions** | 38 instructions |
| **Arithmetic** | Ones' complement |
| **Vacuum Tubes** | ~2,700 |

### Key Challenge: Drum Memory Scheduling

The ERA 1101 uses a rotating magnetic drum with 200 read-write heads. Instructions must be placed at optimal positions to minimize rotational latency. Each instruction includes a **4-bit skip field** that specifies how many memory locations to skip to reach the next instruction.

**Example:** After an ADD instruction (96 μs execution time), the next instruction should be placed ~3-4 positions ahead on the drum to be ready when the CPU needs it.

## Project Structure

```
era1101-miner/
├── README.md                    # This file
├── era1101_simulator.py         # Full CPU and drum simulator
├── era1101_assembler.py         # Cross-assembler with drum optimization
├── sha256_era1101.py            # 24-bit SHA256 implementation
├── miner_core.py                # Core mining logic
├── network_bridge.py            # Paper tape network interface
├── test/
│   ├── test_simulator.py        # Simulator tests
│   ├── test_sha256.py           # SHA256 test vectors
│   └── sample_programs/         # Example ERA 1101 programs
└── docs/
    ├── architecture.md          # Detailed architecture reference
    ├── instruction_set.md       # Complete instruction set
    └── drum_optimization.md     # Scheduling strategies
```

## Implementation Phases

### Phase 1: Simulator Development (50 RTC)
- ✅ ERA 1101 CPU simulator with 24-bit ones' complement arithmetic
- ✅ Magnetic drum memory model with rotational latency
- ✅ Paper tape I/O simulation
- ✅ Cross-assembler with automatic drum optimization
- ✅ Debugging tools (memory dump, single-step, breakpoints)

### Phase 2: SHA256 Implementation (75 RTC)
- ✅ 24-bit arithmetic primitives (add, subtract, rotate, XOR)
- ✅ 64-bit operations using multi-word (3 × 24-bit) representation
- ✅ SHA256 message scheduling with drum-optimized layout
- ✅ Compression function with optimized Σ0, Σ1, Ch, Maj operations
- ✅ NIST test vector validation

### Phase 3: Network Bridge (50 RTC)
- 🔄 Paper tape interface using microcontroller
- 🔄 TCP/IP and HTTPS handling on microcontroller
- 🔄 Request/response protocol via paper tape

### Phase 4: Proof & Documentation (25 RTC)
- 📹 Video demonstration
- 📄 Complete documentation
- 📦 Open source release

## Expected Performance

| Metric | Value |
|--------|-------|
| Single SHA256 hash | ~5-20 seconds (drum-optimized) |
| Hash rate | 0.05-0.2 H/s |
| Paper tape throughput | ~100 characters/second |
| Daily epochs (144) | 86.4 RTC with 5.0× multiplier |

## Memory Layout

| Address Range | Usage |
|---------------|-------|
| 0x0000-0x0FFF | Boot loader and initialization (4K words) |
| 0x1000-0x1FFF | SHA256 constants page 1 (4K words) |
| 0x2000-0x2FFF | SHA256 constants page 2 (4K words) |
| 0x3000-0x3007 | Hash state H0-H7 (8 words) |
| 0x3008-0x30FF | Message schedule buffer |
| 0x3018-0x30FF | Temporary computation buffers |
| 0x3100-0x31FF | Network I/O buffer |
| 0x3200-0x3FFF | Stack and variables |

## Instruction Set Summary

### Arithmetic Instructions
- **INS (00-05)**: Insert various forms into accumulator
- **ADD (06-0B)**: Add to accumulator (various forms)
- **MPY (10)**: Multiply Q × y → A (352 μs)
- **DIV (13)**: Divide A ÷ y, quotient in Q, remainder in A

### Logical/Control
- **STO (15)**: Store right half of A to memory
- **SHL (16)**: Shift accumulator left
- **JMP (1A)**: Unconditional jump
- **JNZ (1C)**: Jump if accumulator not zero

### Key Feature: Skip Field
Each 24-bit instruction includes:
- **6 bits**: Opcode
- **4 bits**: Skip count (0-15)
- **14 bits**: Memory address

## Getting Started

### Running the Simulator

```bash
# Install dependencies (Python 3.8+)
pip install -r requirements.txt

# Run simulator with demo program
python era1101_simulator.py --demo

# Assemble a program
python era1101_assembler.py my_program.asm --output my_program.ptp

# Run SHA256 test vectors
python sha256_era1101.py --test
```

### Example Assembly Program

```assembly
* Simple addition with drum optimization
        ORG 0x1000
START   INS  VALUE1       * Load first value (skip=3)
        ADD  VALUE2       * Add second value (skip=2)
        STO  RESULT       * Store result (skip=0)
        HLT               * Halt

VALUE1  OCT 0001234       * Octal constant
VALUE2  OCT 0005678       * Octal constant
RESULT  OCT 0000000       * Result storage
        END START
```

## Historical Context

The ERA 1101 was designed by Engineering Research Associates (ERA), formed from a team of Navy code-breakers from WWII. The machine was originally called "Atlas" (named after a comic strip character) and was the first stored-program computer to be successfully installed at a distant site (Army Security Agency, December 1950).

The commercial version was named "1101" because 1101 in binary equals 13, the Navy task number for the project.

## Bounty Information

- **Issue**: #1824 on Scottcjn/rustchain-bounties
- **Tier**: LEGENDARY (5.0× multiplier)
- **Reward**: 200 RTC (~$20)
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Engineering Research Associates (ERA) pioneers
- Computer History Museum for documentation
- Bitsavers.org for original manuals
- RustChain community for the bounty program

---

**1950 meets 2026. Magnetic drums mining cryptocurrency.**
