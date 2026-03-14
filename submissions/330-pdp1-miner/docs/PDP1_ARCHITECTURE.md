# PDP-1 Architecture Documentation

## Historical Overview

The **PDP-1 (Programmed Data Processor-1)** was Digital Equipment Corporation's first computer, introduced in 1959. It is widely considered the first minicomputer and played a pivotal role in computing history.

### Key Historical Facts

- **First shipped**: 1959
- **Last shipped**: 1969
- **Total units**: 53
- **Original price**: $120,000 USD (~$1.3M in 2025)
- **Creator**: Digital Equipment Corporation (DEC)
- **Significance**: Birthed hacker culture at MIT, first video game (Spacewar!, 1962)

## Technical Architecture

### Word Size and Memory

The PDP-1 uses an **18-bit word size**, which was unusual then and is unique today.

```
Word Structure (18 bits):
┌──────────────────────────────────┐
│ 17 │ 16 │ 15 │ 14 │ ... │  1 │ 0 │
│ S  │                            │
└──────────────────────────────────┘
S = Sign bit (bit 17)
Bits 0-16 = Magnitude
```

**Memory Specifications:**
- Standard: 4,096 words (9,216 bytes equivalent)
- Maximum: 65,536 words
- Technology: Magnetic-core memory
- Cycle time: 5.35 microseconds
- Effective clock: ~187 kHz

### Registers

The PDP-1 has several key registers:

| Register | Name | Size | Purpose |
|----------|------|------|---------|
| AC | Accumulator | 18-bit | Main arithmetic register |
| MQ | Multiplier Quotient | 18-bit | Multiply/divide operations |
| PC | Program Counter | 18-bit | Memory address register |
| IR | Instruction Register | 18-bit | Current instruction |

### Number Representation

The PDP-1 uses **one's complement** representation for signed numbers:

```
Positive: 0 00000000000000000 = +0
          0 00000000000000001 = +1
          0 11111111111111111 = +177777 (octal)

Negative: 1 11111111111111111 = -0 (one's complement)
          1 11111111111111110 = -1
          1 00000000000000000 = -177777 (octal)
```

**Note**: One's complement has both +0 and -0, unlike two's complement.

## Instruction Set

### Instruction Format

PDP-1 instructions are 18 bits:

```
┌─────────┬───┬──────────────┐
│ Opcode  │ I │   Address    │
│ 6 bits  │ 1 │   12 bits    │
│ 17..12  │11 │   10..0      │
└─────────┴───┴──────────────┘

I = Indirect bit (bit 11)
```

### Instruction Categories

#### 1. Jump Instructions

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 002 | JMP | Unconditional jump |
| 004 | JSP | Jump to subroutine |
| 006 | JRN | Jump if rightmost bit is 1 |
| 010 | JLT | Jump if less than zero |
| 012 | JLE | Jump if less than or equal |
| 014 | JEQ | Jump if equal to zero |
| 016 | JNE | Jump if not equal |

#### 2. Arithmetic Instructions

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 040 | ADD | Add memory to AC |
| 042 | SUB | Subtract memory from AC |
| 044 | MUL | Multiply AC by memory |
| 046 | DIV | Divide AC by memory |

#### 3. Logic Instructions

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 050 | AND | AND memory with AC |
| 052 | OR  | OR memory with AC |
| 054 | XOR | Exclusive OR with AC |
| 100 | CSW | Complement AC |

#### 4. Data Transfer

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 060 | LDA | Load AC from memory |
| 062 | STA | Store AC to memory |
| 064 | LDI | Load immediate |
| 070 | LMQ | Load MQ from memory |
| 072 | STM | Store MQ to memory |

#### 5. Shift Instructions

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 074 | SHL | Shift left AC |
| 076 | SHR | Shift right AC |

#### 6. I/O Instructions

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 020 | IOA | I/O operation A |
| 022 | IOB | I/O operation B |

#### 7. Control

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 102 | HLT | Halt |

### Example Programs

#### Simple Addition

```
Address  Instruction    Description
000000   LDA 000001     Load from address 1
000001   ADD 000002     Add from address 2
000002   STA 000003     Store to address 3
000003   HLT            Halt
000004   000025         Data: 25 (decimal)
000005   000017         Data: 17 (decimal)
000006   000000         Result storage
```

#### Loop Example

```
Address  Instruction    Description
000000   LDI 000000     Initialize counter = 0
000001   STA 000100     Store counter
000002   LDA 000100     Load counter
000003   ADD 000101     Add 1
000004   STA 000100     Store counter
000005   LDA 000100     Load counter
000006   SUB 000102     Subtract 10
000007   JLT 000002     Jump if < 0 (continue loop)
000010   HLT            Halt
000011   000001         Increment value
000012   000012         Limit (10)
```

## I/O Systems

### Type 30 CRT Display

The PDP-1 featured a revolutionary **Type 30 CRT display**:

- Resolution: 1024 × 1024 points
- Display method: Vector graphics (point plotting)
- Control: X,Y coordinate commands
- Intensity: Multiple levels

**Display Commands:**
```
- Point at (X, Y)
- Set intensity
- Clear display
```

### Punched Tape

The PDP-1 used **punched paper tape** for storage:

- Format: 5-level or 8-level tape
- Speed: ~60 characters/second
- Reader: Photoelectric
- Punch: Mechanical

### Other I/O Devices

- **Teletype**: Model 33 ASR for keyboard/printer
- **Magnetic Tape**: Optional high-speed storage
- **Paper Tape Reader**: High-speed input
- **Display Console**: Control panel with lights

## Memory Technology

### Magnetic-Core Memory

The PDP-1 used **magnetic-core memory**:

```
Core Structure:
    ╔═══════╗
    ║   ⊙   ║  ← Ferrite core
    ╚═══════╝
     ╱ │ ╲
    X  Y  S  ← Wires (X, Y drive, S sense)
```

**Characteristics:**
- Non-volatile (retains data without power)
- Access time: 5.35 μs
- Destructive read (must rewrite after reading)
- Physical size: ~1mm per core

**Memory Organization:**
```
4,096 words × 18 bits = 73,728 cores
Plus sense/inhibit wires
Total: ~100,000+ magnetic cores
```

## Performance

### Instruction Timing

Most instructions take **2 memory cycles** (10.7 μs):
1. Fetch instruction
2. Fetch/store operand

| Operation | Time |
|-----------|------|
| ADD | 10.7 μs |
| SUB | 10.7 μs |
| MUL | 21.4 μs |
| DIV | 42.8 μs |
| JMP | 5.35 μs |

### Performance Metrics

- **Additions**: ~93,000 per second
- **Multiplications**: ~47,000 per second
- **Divisions**: ~23,000 per second

## Programming the PDP-1

### Assembly Language Example

```assembly
        ORG 0           / Start at address 0

START,  LDA VALUE1    / Load first value
        ADD VALUE2    / Add second value
        STA RESULT    / Store result
        HLT           / Halt

VALUE1, 25            / First number
VALUE2, 17            / Second number
RESULT, 0             / Result storage

        END START
```

### Machine Code Representation

```
Octal       Binary              Meaning
0600001     011000 0 000000001  LDA 1
0400002     010000 0 000000010  ADD 2
0620003     011010 0 000000011  STA 3
1020000     100010 0 000000000  HLT
0000025     000000 0 000010101  Data: 25
0000021     000000 0 000010001  Data: 17
```

## SHA-256 on PDP-1

### Challenge

Standard SHA-256 uses **32-bit words**, but PDP-1 has **18-bit words**.

### Solution

Store each 32-bit value as **two 18-bit words**:

```
32-bit value:  0x12345678

High word (14 bits):  0x1234 >> 18 = 0x0048
Low word (18 bits):   0x12345678 & 0x3FFFF = 0x345678

PDP-1 storage:
  Address N:   0x0048 (high)
  Address N+1: 0x345678 (low)
```

### Operations

**Addition:**
```python
def add_32bit(h1, l1, h2, l2):
    v1 = (h1 << 18) | l1
    v2 = (h2 << 18) | l2
    result = (v1 + v2) & 0xFFFFFFFF
    return (result >> 18, result & 0x3FFFF)
```

**Rotation:**
```python
def rot_right(h, l, n):
    value = (h << 18) | l
    value = ((value >> n) | (value << (32 - n))) & 0xFFFFFFFF
    return (value >> 18, value & 0x3FFFF)
```

## RustChain Mining on PDP-1

### Proof-of-Antiquity

The PDP-1 receives the **maximum 5.0x multiplier** as a LEGENDARY tier machine:

| Tier | Year Range | Multiplier |
|------|------------|------------|
| LEGENDARY | 1959-1965 | 5.0x |
| VINTAGE | 1965-1975 | 4.5x |
| CLASSIC | 1975-1985 | 4.0x |
| RETRO | 1985-1995 | 3.0x |

### Mining Process

1. **Hardware Fingerprinting**: Generate unique ID from PDP-1 characteristics
2. **Epoch Creation**: Create mining epoch with timestamp
3. **SHA-256 Computation**: Hash using 18-bit optimized implementation
4. **Difficulty Check**: Compare hash to target
5. **Attestation**: Sign and submit result

### Attestation Format

```json
{
  "version": "1.0.0",
  "type": "proof_of_antiquity",
  "tier": "LEGENDARY",
  "hardware": {
    "architecture": "PDP-1",
    "year": 1959,
    "word_size_bits": 18,
    "hardware_id": "abc123..."
  },
  "mining": {
    "wallet": "RTC...",
    "multiplier": 5.0,
    "epoch": {...},
    "nonce": 12345,
    "hash": "..."
  },
  "signature": {...}
}
```

## References

- **PDP-1 Handbook** (1963): http://bitsavers.org/pdf/dec/pdp1/F-15_PDP-1_Handbook_1963.pdf
- **Computer History Museum**: https://computerhistory.org/collections/catalog/102643816
- **Spacewar! Source**: https://github.com/tannerdolby/spacewar
- **DEC Archives**: http://www.bitsavers.org/pdf/dec/pdp1/

---

*"The PDP-1 started the minicomputer revolution and created hacker culture"*
