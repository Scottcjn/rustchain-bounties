# IBM 704 (1954) RustChain Miner

**LEGENDARY Tier Bounty - 200 RTC**

Port of the RustChain miner to the IBM 704, IBM's first mass-produced computer with hardware floating-point arithmetic (1954).

## Overview

This project implements a RustChain miner on the IBM 704, the machine that gave birth to FORTRAN and LISP. The IBM 704 was designed by John Backus and Gene Amdahl and was the first computer with hardware floating-point support.

### Key Specifications

- **Year**: 1954
- **Word Size**: 36 bits
- **Memory**: 4,096 words (18,432 bytes) magnetic-core
- **Technology**: Vacuum tubes (~2,000)
- **Floating-Point**: Hardware support (8-bit excess-128 exponent, 27-bit fraction)
- **Performance**: 12,000 floating-point additions/second
- **I/O**: Punched cards (IBM 711/721), Magnetic tape (IBM 727)

## Project Structure

```
ibm704-miner/
├── README.md                 # This file
├── ibm704-sim/              # IBM 704 CPU simulator
│   ├── ibm704_cpu.py        # CPU emulator
│   ├── core_memory.py       # Magnetic-core memory model
│   └── sap_assembler.py     # Symbolic Assembly Program
├── ibm704-miner/            # Miner implementation
│   ├── sha256_ibm704.s      # SHA256 in IBM 704 assembly
│   └── miner_main.s         # Main miner program
├── network-bridge/          # Network interface
│   └── card_interface.py    # Card reader/punch interface
└── docs/                    # Documentation
    ├── architecture.md      # IBM 704 architecture reference
    └── implementation.md    # Implementation details
```

## Implementation Status

### Phase 1: Simulator Development (50 RTC)

- [x] IBM 704 CPU simulator created
- [ ] SAP assembler implementation
- [ ] Debugging tools

### Phase 2: SHA256 Implementation (75 RTC)

- [ ] 36-bit arithmetic primitives
- [ ] SHA256 message scheduling
- [ ] SHA256 compression function
- [ ] Test vector validation

### Phase 3: Network Bridge (50 RTC)

- [ ] Card reader/punch interface
- [ ] Network protocol implementation
- [ ] Error handling

### Phase 4: Hardware Fingerprint (25 RTC)

- [ ] Core memory timing signature
- [ ] Vacuum tube characteristics
- [ ] Attestation protocol

### Phase 5: Documentation & Verification (25 RTC)

- [ ] Video documentation
- [ ] Technical documentation
- [ ] API verification

## Bounty Information

- **Issue**: [#1834](https://github.com/Scottcjn/rustchain-bounties/issues/1834)
- **Total Bounty**: 200 RTC
- **Multiplier**: 5.0x (Maximum)
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Quick Start

### Running the Simulator

```bash
cd ibm704-sim
python ibm704_cpu.py
```

### Assembling Programs

```bash
python sap_assembler.py program.s -o program.cards
```

## Architecture Highlights

### Registers

- **AC**: 38-bit Accumulator (2 bits for overflow)
- **MQ**: 36-bit Multiplier-Quotient register
- **XR1, XR2, XR4**: 15-bit Index registers
- **IC**: 15-bit Instruction Counter

### Instruction Formats

**Type A** (Index operations):
```
| 3-bit prefix | 15-bit decrement | 3-bit tag | 15-bit address |
```

**Type B** (Most instructions):
```
| 12-bit opcode | 2-bit flag | 4-bit unused | 3-bit tag | 15-bit address |
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

The IBM 704 was a revolutionary machine:

- First mass-produced computer with floating-point hardware
- Birthplace of FORTRAN (1957) and LISP (1958)
- Used for Operation Moonwatch satellite tracking
- Frank Rosenblatt implemented the Perceptron on IBM 704
- Edward Thorp used it for blackjack probability research
- 123 units produced between 1955-1960

## License

MIT License - See LICENSE file for details.

## Contact

- GitHub: [Scottcjn/rustchain-bounties #1834](https://github.com/Scottcjn/rustchain-bounties/issues/1834)
- Discord: RustChain Discord

---

**72 years of computing history. One blockchain. Infinite possibilities.**
