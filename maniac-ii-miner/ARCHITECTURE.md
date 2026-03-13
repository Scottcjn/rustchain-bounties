# MANIAC II Miner Architecture

Technical specification for the MANIAC II RustChain Proof-of-Antiquity miner implementation.

## Overview

This document describes the architecture of the MANIAC II miner simulation, which emulates the hybrid vacuum tube/transistor computer built at Los Alamos in 1957.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MANIAC II MINER ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐        │
│  │   CPU       │◀──▶│ Core Memory  │    │  Paper Tape │        │
│  │  (Hybrid)   │    │  (4K × 48b)  │◀──▶│  I/O        │        │
│  └─────────────┘    └──────────────┘    └─────────────┘        │
│         │                  │                                     │
│         ▼                  ▼                                     │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐        │
│  │ Arithmetic  │    │ Williams     │    │   CDC Drum  │        │
│  │   Unit      │    │ Tubes (12K)  │    │  Storage    │        │
│  │(48-bit ALU) │    │              │    │  (1MW)      │        │
│  └─────────────┘    └──────────────┘    └─────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Central Processing Unit (CPU)

The MANIAC II CPU was a **hybrid design** using three technologies:

#### Technology Mix
- **Vacuum Tubes**: 5,190 (main logic)
- **Semiconductor Diodes**: 3,050 (signal routing)
- **Transistors**: 1,160 (arithmetic unit)

#### Instruction Set
The CPU implemented an IAS-derived instruction set with 48-bit words:

| Opcode | Mnemonic | Description | Time (early) | Time (solid-state) |
|--------|----------|-------------|--------------|-------------------|
| 0 | LOAD | Load from memory | ~40μs | ~2.5μs |
| 1 | ADD | Add to accumulator | ~40μs | ~2.5μs |
| 2 | STORE | Store accumulator | ~40μs | ~2.5μs |
| 3 | SUB | Subtract | ~40μs | ~2.5μs |
| 4 | MUL | Multiply | 180μs | 8μs |
| 5 | DIV | Divide | 300μs | 25μs |
| 6 | PRINT | Output to paper tape | ~10ms | ~2ms |
| 7 | JUMP | Unconditional jump | ~40μs | ~2.5μs |
| 8 | JZ | Jump if zero | ~40μs | ~2.5μs |
| 9 | JN | Jump if negative | ~40μs | ~2.5μs |

#### 48-Bit ALU

```
┌─────────────────────────────────────────────────────────┐
│              48-BIT ARITHMETIC LOGIC UNIT               │
├─────────────────────────────────────────────────────────┤
│  Input A: 48 bits (from memory or register)             │
│  Input B: 48 bits (from memory or register)             │
│  Output:  48 bits (to accumulator or memory)            │
│                                                         │
│  Operations:                                            │
│  - Addition/Subtraction (two's complement)              │
│  - Multiplication (array multiplier)                    │
│  - Division (restoring division)                        │
│  - Logical AND/OR/NOT                                   │
│  - Shift left/right                                     │
└─────────────────────────────────────────────────────────┘
```

### 2. Memory Hierarchy

MANIAC II featured a sophisticated three-level memory hierarchy:

#### Level 1: Magnetic-Core Memory (Primary)

```
┌─────────────────────────────────────────────────────────┐
│           MAGNETIC-CORE MEMORY BANK                      │
├─────────────────────────────────────────────────────────┤
│  Capacity:     4,096 words × 48 bits                    │
│  Access Time:  2.4 microseconds                         │
│  Cycle Time:   6 microseconds (later upgrade)           │
│  Technology:   Ferrite cores (magnetic)                 │
│  Addressing:   12-bit address (2^12 = 4,096)            │
│  Read:         Non-destructive                          │
│  Write:        Destructive (requires rewrite)           │
└─────────────────────────────────────────────────────────┘
```

**Core Memory Organization:**
```
Word 0 (0x000):  [Sign][Magnitude (47 bits)]
Word 1 (0x001):  [Sign][Magnitude (47 bits)]
...
Word 4095 (0xFFF): [Sign][Magnitude (47 bits)]
```

#### Level 2: Williams Tubes (Supplementary)

```
┌─────────────────────────────────────────────────────────┐
│           WILLIAMS TUBE MEMORY BANK                      │
├─────────────────────────────────────────────────────────┤
│  Capacity:     12,288 words × 48 bits                   │
│  Access Time:  15 microseconds                          │
│  Technology:   Cathode Ray Tubes (CRT)                  │
│  Storage:      Charged spots on phosphor screen         │
│  Refresh:      Continuous beam scanning required        │
│  Volatile:     Yes (power-off = data loss)              │
└─────────────────────────────────────────────────────────┘
```

**Williams Tube Layout:**
```
┌────────────────────────────────────────┐
│  CRT Screen (top view)                 │
│  ┌────┬────┬────┬────┐                │
│  │ 32 │ 32 │ 32 │ 32 │  ← 32 words    │
│  │words│words│words│words│    per tube │
│  ├────┼────┼────┼────┤                │
│  │ ... (32 tubes total) ... │          │
│  └────────────────────────────────────┘│
│  Total: 32 tubes × 32 words × 12 banks │
│        = 12,288 words                  │
└────────────────────────────────────────┘
```

#### Level 3: CDC Drum Storage (Paging)

```
┌─────────────────────────────────────────────────────────┐
│           CDC DRUM STORAGE (PAGING DEVICE)               │
├─────────────────────────────────────────────────────────┤
│  Capacity:     1 megaword (1,048,576 words)             │
│  Access:       Sequential (rotating drum)               │
│  Page Size:    1K words (1,024 words per page)          │
│  Pages:        1,024 pages                              │
│  Lookup:       16-deep associative memory               │
│  Use Case:     Overflow storage, program swapping       │
└─────────────────────────────────────────────────────────┘
```

### 3. Input/Output System

#### Paper Tape Reader/Punch

```
┌─────────────────────────────────────────────────────────┐
│              8-CHANNEL PAPER TAPE FORMAT                 │
├─────────────────────────────────────────────────────────┤
│  Channel 8: Sprocket hole (always punched)              │
│  Channel 7: Data bit 7 (MSB)                            │
│  Channel 6: Data bit 6                                  │
│  Channel 5: Data bit 5                                  │
│  Channel 4: Data bit 4                                  │
│  Channel 3: Data bit 3                                  │
│  Channel 2: Data bit 2                                  │
│  Channel 1: Data bit 1 (LSB)                            │
│                                                         │
│  Read Speed:  ~60 characters/second                     │
│  Punch Speed: ~40 characters/second                     │
│  Width:       1 inch (standard)                         │
└─────────────────────────────────────────────────────────┘
```

**Example Encoding:**
```
Character: 'A' (ASCII 0x41 = 01000001)

Tape representation (● = punched, ○ = not punched):

  87654321  (channel numbers)
  ○●○○○○○●  (physical tape)
   ││    ││
   ││    └└── Bit 0 = 1
   ││
   └└──────── Bit 7 = 1 (MSB)
```

#### IBM Tape Drives

- **2× nine-track** (IBM 360 series)
- **2× seven-track** (1/2" tape)
- Used for bulk data storage and program loading

#### Printer

- **500 lines per minute** (standard character set)
- **1,500 lines per minute** (hexadecimal character set)

## Mining State Machine Implementation

### State Representation

```
┌─────────────────────────────────────────────────────────┐
│              MINING STATE MACHINE                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  State IDLE (0):                                        │
│  ┌─────────────────────────────────────────┐           │
│  │  Core Memory[0x0200] = 0x000000000000  │           │
│  │  Waiting for epoch trigger              │           │
│  │  Output: "IDLE_EPOCH_XXX" on paper tape │           │
│  └─────────────────────────────────────────┘           │
│                    │                                    │
│                    │ [epoch starts]                     │
│                    ▼                                    │
│  State MINING (1):                                      │
│  ┌─────────────────────────────────────────┐           │
│  │  Core Memory[0x0200] = 0x000000000001  │           │
│  │  Computing proof-of-antiquity           │           │
│  │  Output: "MINING_HASH_X" on paper tape  │           │
│  └─────────────────────────────────────────┘           │
│                    │                                    │
│                    │ [computation complete]             │
│                    ▼                                    │
│  State ATTESTING (2):                                   │
│  ┌─────────────────────────────────────────┐           │
│  │  Core Memory[0x0200] = 0x000000000002  │           │
│  │  Generating attestation                 │           │
│  │  Output: "ATTEST_COMPLETE" + wallet     │           │
│  └─────────────────────────────────────────┘           │
│                    │                                    │
│                    │ [attestation complete]             │
│                    └────────────────────────────────────┘
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Memory Layout for Miner

```
Address    Size    Usage
─────────────────────────────────────────────────────────
0x0100     256     Miner program (instructions)
0x0200     1       State register (IDLE/MINING/ATTESTING)
0x0201     1       Epoch counter (low word)
0x0202     1       Epoch counter (high word)
0x0300     10      Wallet address (ASCII encoded)
0x0400     16      Working registers (R0-R15)
0x0500     64      Hash computation buffers
0x0800     12,288  Williams tube overflow area
0x1000+    varies  Drum storage (paged)
```

## Hybrid Logic Simulation

### Vacuum Tube Logic

Vacuum tubes were used as switches and amplifiers:

```
        Plate (+300V)
           │
           │
      ┌────┴────┐
      │         │
Grid ─┤  TUBE   ├─ Output
      │         │
      └────┬────┘
           │
           │
       Cathode (GND)

Grid voltage controls plate current:
- Grid negative: Tube off (output high)
- Grid positive: Tube on (output low)
```

### Transistor Logic (Early Adoption)

MANIAC II was one of the first computers to use transistors:

```
        Collector (+Vcc)
           │
           │
      ┌────┴────┐
      │         │
Base ─┤  NPN    ├─ Output
      │ TRANSIST│
      └────┬────┘
           │
           │
       Emitter (GND)

Base current controls collector current:
- Base low: Transistor off
- Base high: Transistor on (saturated)
```

### Hybrid Gate Implementation

**AND Gate (Diode-Transistor Logic):**
```
    A ──┬───[Diode]──┐
        │            │
    B ──┼───[Diode]──┼───[Resistor]─── Base of Transistor
        │            │
       GND          GND
       
    Output = A AND B
```

## Performance Modeling

### Timing Parameters

| Component | Early (1957) | Solid-State Upgrade | Model Factor |
|-----------|--------------|---------------------|--------------|
| Core Memory Access | 2.4μs | 2.4μs | 1.0× |
| Williams Tube Access | 15μs | 15μs | 1.0× |
| ADD/SUB | ~40μs | ~2.5μs | 16.0× improvement |
| MULTIPLY | 180μs | 8μs | 22.5× improvement |
| DIVIDE | 300μs | 25μs | 12.0× improvement |
| JUMP | ~40μs | ~2.5μs | 16.0× improvement |

### Simulation Accuracy

The Python simulator models:
- ✅ Exact 48-bit word arithmetic
- ✅ Core memory access timing (2.4μs)
- ✅ Williams tube refresh cycles
- ✅ Hybrid logic propagation delays
- ✅ Paper tape I/O timing
- ✅ State machine transitions
- ✅ Memory hierarchy (core → Williams → drum)

## RustChain Protocol Adaptation

### Proof-of-Antiquity for MANIAC II

Since MANIAC II cannot perform SHA-256 hashing, the protocol is adapted:

```
Traditional PoW:          MANIAC II PoA:
┌─────────────────┐      ┌─────────────────┐
│ Block Header    │      │ Epoch Number    │
│ Nonce           │      │ State Machine   │
│ SHA-256 Hash    │      │ Attestation     │
│ Target Compare  │      │ Paper Tape Out  │
└─────────────────┘      └─────────────────┘
```

### Attestation Format

```
┌─────────────────────────────────────────────────────────┐
│           MANIAC II ATTESTATION (Paper Tape)            │
├─────────────────────────────────────────────────────────┤
│  Header: "ATTEST_MANIAC2"                               │
│  Epoch:  [48-bit epoch number]                          │
│  State:  [Final state: 0=IDLE, 1=MINING, 2=ATTESTING]   │
│  Wallet: "RTC4325af95d26d59c3ef025963656d22af638bb96b" │
│  Time:   [Simulated operation count]                    │
│  Check:  [Simple checksum of above fields]              │
└─────────────────────────────────────────────────────────┘
```

## File Structure

```
maniac-ii-miner/
├── README.md                 # User documentation
├── ARCHITECTURE.md           # This file
├── CORE_MEMORY.md            # Magnetic-core memory details
├── HYBRID_LOGIC.md           # Vacuum tube + transistor circuits
├── simulation/
│   ├── maniac2_miner.py      # Main simulator
│   ├── core_memory.py        # Core memory emulation
│   ├── williams_tube.py      # Williams tube emulation
│   ├── maniac2_cpu.py        # CPU simulation
│   ├── hybrid_gates.py       # Logic gate simulation
│   └── test_vectors/         # Test programs
├── paper_tape/
│   ├── miner_program.pt      # Main program
│   └── attestation.pt        # Attestation format
├── diagrams/
│   ├── state_machine.svg     # State diagram
│   ├── memory_hierarchy.svg  # Memory layout
│   └── timing_diagram.svg    # Timing charts
└── docs/
    ├── maniac_ii_history.md  # Historical context
    ├── rustchain_protocol.md # Protocol details
    └── bounty_claim.md       # Claim instructions
```

## Implementation Notes

### Python Simulator Design

```python
class MANIAC2Miner:
    def __init__(self):
        self.core_memory = CoreMemory(size=4096, word_bits=48)
        self.williams_tubes = WilliamsTubes(size=12288, word_bits=48)
        self.cpu = HybridCPU(core_mem=self.core_memory, 
                            williams=self.williams_tubes)
        self.state = MinerState.IDLE
        self.epoch = 0
        
    def run_epoch(self):
        """Simulate one mining epoch"""
        self.state = MinerState.MINING
        # Simulate mining operations
        self.cpu.execute_program(MINING_PROGRAM)
        
        self.state = MinerState.ATTESTING
        # Generate attestation
        attestation = self.generate_attestation()
        
        self.state = MinerState.IDLE
        return attestation
```

### Memory Emulation

```python
class CoreMemory:
    def __init__(self, size=4096, word_bits=48):
        self.words = [0] * size
        self.access_time_us = 2.4
        self.word_bits = word_bits
        
    def read(self, address):
        time.sleep(self.access_time_us / 1_000_000)
        return self.words[address]
        
    def write(self, address, value):
        time.sleep(self.access_time_us / 1_000_000)
        self.words[address] = value & ((1 << self.word_bits) - 1)
```

## Conclusion

This architecture document provides the technical foundation for implementing a MANIAC II miner simulation that honors the historical computer's unique hybrid design while demonstrating the RustChain Proof-of-Antiquity protocol conceptually.

The key innovation is modeling the **transition-era technology** - vacuum tubes working alongside early transistors - which makes MANIAC II one of the most historically significant computers in the evolution of computing.

---

*For more details, see CORE_MEMORY.md and HYBRID_LOGIC.md*
