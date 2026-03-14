# EDSAC Miner Port (1949) 🖥️

**RustChain Bounty #352** - LEGENDARY Tier (200 RTC / $20)

## Overview

This project ports a cryptocurrency miner to the **EDSAC** (Electronic Delay Storage Automatic Calculator), the world's first practical stored-program computer that ran its first program on May 6, 1949 at Cambridge University.

## EDSAC Architecture

### Key Specifications

| Feature | Specification |
|---------|---------------|
| **Word Length** | 17 bits + 1 parity bit |
| **Memory** | Mercury delay lines (512 words initial, 1024 later) |
| **Memory Type** | Serial access (bits processed sequentially) |
| **Clock Speed** | ~500 kHz |
| **Instructions** | ~18 original instructions |
| **Registers** | Accumulator (A), Order Tank (current instruction) |
| **Input** | 5-hole paper tape |
| **Output** | Teleprinter / CRT display |

### Instruction Set

EDSAC used single-character opcodes:

| Opcode | Mnemonic | Operation |
|--------|----------|-----------|
| `A` | ADD | Add memory to accumulator |
| `S` | SUB | Subtract memory from accumulator |
| `T` | STORE | Transfer accumulator to memory |
| `U` | ADD-STORE | Add then store (non-destructive) |
| `H` | HALT | Stop execution |
| `E` | JUMP-E | Jump if accumulator ≥ 0 |
| `G` | JUMP-G | Jump if accumulator < 0 |
| `I` | INPUT | Read from tape |
| `O` | OUTPUT | Write to teleprinter |
| `L` | LOAD | Load constant |
| `M` | MULTIPLY | Multiply by memory |
| `N` | NEGATE | Negate accumulator |
| `Z` | ZERO | Clear accumulator |

### Memory Organization

- Addresses: 0-511 (initial), 0-1023 (expanded)
- Each word: 17 data bits + 1 parity bit
- Serial access: ~1ms access time average
- Long tank vs short tank organization

## Mining Algorithm Adaptation

### Challenge

EDSAC's extreme limitations require a radically simplified mining approach:

1. **No 256-bit hashes** - EDSAC can only handle 17-bit words
2. **Limited memory** - Cannot store full block headers
3. **Serial processing** - Extremely slow by modern standards
4. **No bitwise ops** - Original EDSAC lacked AND/OR/XOR

### Solution: Proof-of-Work Simplified

We implement a **toy proof-of-work** that demonstrates the concept:

```
Target: Find nonce where f(block_header, nonce) < target
Where: f() = simplified checksum function
```

**Algorithm:**
1. Load block header (simplified to 17-bit value)
2. Iterate nonce from 0
3. Compute: `hash = (header + nonce) mod 2^17`
4. Check if `hash < target`
5. If yes, FOUND! If no, increment nonce and repeat

### Expected Performance

- ~500 operations/second (optimistic)
- For difficulty=1: ~1-10 seconds
- For difficulty=10: ~10-100 seconds
- Not practical for real mining, but demonstrates the concept!

## Project Structure

```
edsac-miner/
├── README.md           # This file
├── docs/
│   ├── ARCHITECTURE.md # Detailed EDSAC specs
│   └── MINING.md       # Mining algorithm explanation
├── simulator/
│   ├── edsac.py        # EDSAC emulator
│   ├── miner.e         # EDSAC assembly miner
│   └── test_miner.py   # Test harness
├── examples/
│   └── sample_run.txt  # Example output
└── PR_SUBMISSION.md    # Bounty claim instructions
```

## Wallet Address

**RTC4325af95d26d59c3ef025963656d22af638bb96b**

## Historical Note

EDSAC predates:
- Transistors (1947, but not widely used until 1950s)
- Integrated circuits (1958)
- The concept of cryptocurrency by ~60 years

This port is a **historical exercise** demonstrating that the mathematical concepts underlying cryptocurrency could theoretically run on the earliest computers, even if practically infeasible.

## Running the Simulator

```bash
cd simulator
python edsac.py miner.e
```

## License

Educational/Historical demonstration
Public Domain

---

*"The first program to run on EDSAC calculated squares and square roots."*
*- Now it mines cryptocurrency (sort of).*
