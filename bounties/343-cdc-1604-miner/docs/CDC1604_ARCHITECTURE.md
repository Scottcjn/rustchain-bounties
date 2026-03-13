# CDC 1604 Architecture Reference

## Overview

The CDC 1604 is a 48-bit transistorized computer designed by Seymour Cray at Control Data Corporation, first delivered in January 1960.

## Memory Organization

### Core Memory

- **Capacity**: 32,768 words × 48 bits (192 KB)
- **Technology**: Magnetic core memory
- **Cycle Time**: 6.4 microseconds
- **Organization**: Two interleaved banks of 16K words
  - Bank A: Odd addresses
  - Bank B: Even addresses
- **Bank Skew**: 3.2 microseconds apart
- **Effective Access Time**: 4.8 microseconds average

### Memory Layout

```
Word Address Range: 0 - 32767 (octal: 00000 - 77777)

Bank A (Odd):   00001, 00003, 00005, ..., 77777
Bank B (Even):  00000, 00002, 00004, ..., 77776
```

## CPU Registers

### Operand Registers (48-bit)

| Register | Name | Purpose |
|----------|------|---------|
| A | Accumulator | Primary arithmetic and logic operations |
| Q | Auxiliary Arithmetic | Double-length operations, temporary storage |

### Control Registers

| Register | Width | Purpose |
|----------|-------|---------|
| P | 15-bit | Program Counter |
| 1-6 | 15-bit each | Index Registers |

### Register Bit Layout

```
Accumulator (A) - 48 bits
┌─────────────────────────────────────────────────────────────┐
│ 47                                                        0 │
│                        48-bit Word                          │
└─────────────────────────────────────────────────────────────┘

Program Counter (P) - 15 bits
┌──────────────┬──────────────────────────────────────────────┐
│ (unused)     │ 14                                        0 │
│ 33 bits      │              15-bit Address                  │
└──────────────┴──────────────────────────────────────────────┘

Index Registers (1-6) - 15 bits each
┌──────────────┬──────────────────────────────────────────────┐
│ (unused)     │ 14                                        0 │
│ 33 bits      │              15-bit Index Value              │
└──────────────┴──────────────────────────────────────────────┘
```

## Instruction Format

### Single Instruction (24 bits)

```
┌──────────┬─────────┬────────────────────────────────────────┐
│  Opcode  │Designat │              Address                   │
│   6 bits │ 3 bits  │              15 bits                   │
│  23-18   │  17-15  │              14-0                      │
└──────────┴─────────┴────────────────────────────────────────┘
```

### Two Instructions per Word (48 bits)

```
┌─────────────────────────────────────────────────────────────┐
│  Left Instruction (24 bits)  │  Right Instruction (24 bits) │
│     47-24                    │     23-0                      │
└─────────────────────────────────────────────────────────────┘
```

### Opcode Categories

| Opcode Range | Category | Examples |
|--------------|----------|----------|
| 00-07 | Arithmetic | ADD, SUB, MUL, DIV |
| 10-17 | Logical | ANA, ORA, ERA |
| 20-27 | Shift | LLS, LRS, ALS, ARS |
| 30-37 | Control | JMP, JBS, JBN |
| 40-47 | Index | LXA, AXJ, TXJ |
| 50-57 | I/O | INP, OUT |
| 60-67 | Special | HLT, NOP |

### Designator Field Usage

For memory access instructions:
- 000: No index
- 001-110: Index register 1-6
- 111: Indirect addressing

For jump instructions:
- Condition code for branch

## Arithmetic

### Integer Representation

- **Format**: Ones' complement
- **Range**: ±(2^47 - 1)
- **Sign Bit**: Bit 47 (MSB)
  - 0 = Positive
  - 1 = Negative

### Ones' Complement Rules

```
Positive: Standard binary representation
Negative: Bitwise complement of absolute value

Example:
+5 = 000...000101
-5 = 111...111010 (complement of +5)

Note: Two representations of zero
+0 = 000...000
-0 = 111...111
```

### Floating Point Format

```
┌─────┬───────────┬────────────────────────────────────────────┐
│ Sign│ Exponent  │            Significand                     │
│ 1 bit│ 11 bits  │              36 bits                       │
│  47 │  46-36    │              35-0                          │
└─────┴───────────┴────────────────────────────────────────────┘
```

- **Exponent**: Offset binary (bias = 2^10 = 1024)
- **Significand**: Fractional, normalized
- **Range**: Approximately 10^-308 to 10^308

## Console Audio Output

The CDC 1604 has a unique feature: the 3 most significant bits of the accumulator are connected to a DAC and audio amplifier.

```
Accumulator Bits 47, 46, 45 → 3-bit DAC → Audio Amplifier → Speaker
```

This was used for:
- Debugging (musical patterns indicated program state)
- Operator alerts
- Early computer music

### Audio Sampling for Entropy

The audio output provides entropy through:
- Transistor switching variations
- Power supply noise
- Thermal drift effects

## I/O System

### CDC 160 I/O Processor

The CDC 1604 typically used a CDC 160 minicomputer as an I/O processor:

- **Architecture**: 12-bit
- **Memory**: 4K words
- **Function**: Handled all I/O operations
- **Channels**: 6 independent I/O channels

### I/O Instructions

```
INP  - Input from device
OUT  - Output to device

Device selection via designator field:
- 001: Card Reader
- 010: Card Punch
- 011: Line Printer
- 100: Magnetic Tape
- 101: CDC 160 I/O Processor
- 110: Paper Tape Reader
- 111: Paper Tape Punch
```

## Programming Model

### JOVIAL Example

```jovial
BEGIN ENTROPY_COLLECTOR
  DECLARE timing: ARRAY(32) OF WORD;
  DECLARE i: INTEGER;
  
  FOR i = 0 TO 31 DO BEGIN
    CALL TIMER_READ(timing(i));
  END;
  
  CALL PROCESS_ENTROPY(timing);
END ENTROPY_COLLECTOR
```

### Assembly Example

```assembly
         LXA     1,0          / Load index 1 with 0
         LXA     2,32         / Load index 2 with 32 (loop count)
LOOP     TD      TIMER        / Test timer device
         JO      LOOP         / Jump if timer not ready
         INP     1,1          / Input from timer to index 1
         AXJ     LOOP,1,2     / Add index, jump if count > 0
         HRS     0            / Halt
```

## Performance Characteristics

### Instruction Timing

| Instruction Type | Cycles | Time (μs) |
|------------------|--------|-----------|
| Register ops | 2-3 | 9.6-14.4 |
| Memory access | 4-6 | 19.2-28.8 |
| Multiply | 13-15 | 62.4-72.0 |
| Divide | 15-18 | 72.0-86.4 |
| I/O | Variable | Variable |

### Overall Performance

- **Instructions per Second**: ~100,000
- **MIPS**: 0.1
- **Clock Frequency**: 208 kHz

## Physical Characteristics

| Property | Value |
|----------|-------|
| Height | 176 cm (69 in) |
| Length | 227 cm (89 in) |
| Width | 68 cm (27 in) |
| Weight | 2,200 lbs (1,000 kg) |
| Power | 5.5 kW @ 208V 60Hz |
| Transistors | ~2,500 |
| Diodes | ~10,000 |

## Historical Significance

- **Designer**: Seymour Cray (later founded Cray Research)
- **First Delivery**: January 1960, U.S. Navy Postgraduate School
- **Total Built**: 50+ systems
- **Original Price**: $1,030,000 (1960 dollars)
- **Notable Uses**:
  - Fleet weather prediction
  - Minuteman ICBM guidance
  - PLATO educational system
  - Early text mining (Masquerade)

## Emulation vs. Real Hardware

### SIMH Simulator

The SIMH project provides a CDC 1604 simulator:

```bash
sim> cdc1604
sim> load entropy_collector.bin
sim> go
```

### Real Hardware Entropy

Real CDC 1604 hardware provides unique entropy sources:

1. **Core Memory Variations**: Each core has unique magnetic properties
2. **Transistor Aging**: 60+ year old transistors have unique characteristics
3. **Power Supply Noise**: Analog power supplies create unique signatures
4. **Console CRT**: Unique phosphor persistence and electron beam behavior
5. **Thermal Patterns**: Heat distribution across chassis is unique

### Anti-Emulation Validation

The RustChain node validates:

- Timing patterns match 208 kHz clock with analog drift
- Audio DAC patterns show transistor-level variations
- Memory access times show core memory decay characteristics
- No digital clock signatures (emulators use clean digital timing)

---

## References

1. CDC 1604 Computer Reference Manual, Control Data Corporation, 1963
2. Hassitt, A. & Ralston, A. "Computer Programming and Computer Systems", Academic Press, 2014
3. Fleming, G. "CDC 1604 Format Description", NASA NSSDC, 2017
4. Oral History with CDC Engineers, Charles Babbage Institute, 1975
