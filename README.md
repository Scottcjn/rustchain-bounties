# PDP-1 (1959) RustChain Miner

**LEGENDARY Tier Bounty - 200 RTC**

Port of the RustChain miner to the PDP-1, DEC's first computer and the machine that launched the minicomputer revolution (1959).

## Overview

This project implements a RustChain miner on the PDP-1, the computer that made computing accessible to universities and research labs. The PDP-1 was revolutionary for its time - transistor-based, interactive, and affordable (relatively speaking).

### Key Specifications

- **Year**: 1959 (first shipped)
- **Word Size**: 18 bits
- **Memory**: 4,096 words (9,216 bytes) magnetic-core
- **Technology**: Transistors (~500) - no vacuum tubes!
- **Clock Speed**: 5 MHz (200 ns cycle time)
- **Performance**: 100,000-200,000 instructions/second
- **I/O**: Type 30 CRT display, paper tape, typewriter (Flexowriter)
- **Price**: $120,000 (1960) ≈ $1.2M today

## Project Structure

```
pdp1-miner/
├── README.md                 # This file
├── pdp1-sim/                 # PDP-1 CPU simulator
│   ├── pdp1_cpu.py           # CPU emulator
│   ├── core_memory.py        # Magnetic-core memory model
│   └── macro_assembler.py    # MACRO assembly
├── pdp1-miner/               # Miner implementation
│   ├── sha256_pdp1.mac       # SHA256 in PDP-1 assembly
│   └── miner_main.mac        # Main miner program
├── network-bridge/           # Network interface
│   └── paper_tape_interface.py # Paper tape reader/punch interface
└── docs/                     # Documentation
    ├── architecture.md       # PDP-1 architecture reference
    └── implementation.md     # Implementation details
```

## Implementation Status

### Phase 1: Simulator Development (50 RTC)

- [x] PDP-1 CPU simulator created
- [ ] MACRO assembler implementation
- [ ] Debugging tools

### Phase 2: SHA256 Implementation (75 RTC)

- [ ] 18-bit arithmetic primitives
- [ ] SHA256 message scheduling
- [ ] SHA256 compression function
- [ ] Test vector validation

### Phase 3: Network Bridge (50 RTC)

- [ ] Paper tape interface
- [ ] Network protocol implementation
- [ ] Error handling

### Phase 4: Hardware Fingerprint (25 RTC)

- [ ] Core memory timing signature
- [ ] Transistor characteristics
- [ ] Attestation protocol

### Phase 5: Documentation & Verification (25 RTC)

- [ ] Video documentation
- [ ] Technical documentation
- [ ] API verification

## Bounty Information

- **Issue**: #337 (PDP-1 Port)
- **Total Bounty**: 200 RTC
- **Multiplier**: 5.0x (Maximum)
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Quick Start

### Running the Simulator

```bash
cd pdp1-sim
python pdp1_cpu.py
```

### Assembling Programs

```bash
python macro_assembler.py program.mac -o program.ptape
```

## Architecture Highlights

### Registers

- **AC**: 18-bit Accumulator
- **IO**: 18-bit Input-Output register (extends AC for double-precision)
- **PC**: 18-bit Program Counter
- **MB**: 18-bit Memory Buffer
- **MA**: 18-bit Memory Address

### Instruction Format

**Single Address Format (18 bits)**:
```
| 1-bit indirect | 3-bit opcode | 1-bit index | 12-bit address |
| I              | OPCODE       | B          | ADDRESS        |
```

### Memory Layout

```
0x000-0x03F: Boot loader
0x040-0x07F: SHA256 constants
0x080-0x0FF: Hash state and working variables
0x100-0x1FF: I/O buffer
0x200-0x3FF: Stack
0x400-0xFFF: Free space (90% available!)
```

## Historical Context

The PDP-1 was a revolutionary machine:

- **DEC's first computer** - launched the minicomputer industry
- **First interactive computer** - users could type and see results immediately
- **Spacewar! (1962)** - first video game, created on PDP-1
- **Hacker culture birthplace** - MIT Tech Model Railroad Club
- **Text editing pioneer** - first interactive text editor
- **Music synthesis** - early computer music experiments
- **53 units produced** between 1959-1966

### Notable PDP-1 Moments

- **Spacewar!**: Steve Russell created the first video game in 1962
- **Ivan Sutherland's Sketchpad**: Early computer graphics (1963)
- **First word processor**: Expensive Typewriter (1961)
- **Music**: Music Macro Language experiments
- **AI research**: Early artificial intelligence experiments

## License

MIT License - See LICENSE file for details.

## Contact

- GitHub: [Scottcjn/rustchain-bounties #337](https://github.com/Scottcjn/rustchain-bounties/issues/337)
- Discord: RustChain Discord

---

**67 years of computing history. One blockchain. Infinite possibilities.**

*The machine that started it all - DEC's first computer, the grandfather of personal computing.*
