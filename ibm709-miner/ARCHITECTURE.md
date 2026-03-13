# IBM 709 Architecture Reference

## Overview

The IBM 709 (1958) is a 36-bit vacuum tube computer, the third in IBM's 700/7000 series of scientific computers. It was succeeded by the transistorized IBM 7090 (1959), which maintained binary compatibility.

## Physical Characteristics

| Property | Value |
|----------|-------|
| Technology | Vacuum tubes (later 7090: transistors) |
| Memory | 32,768 × 36-bit magnetic-core |
| Cycle Time | 2.18 microseconds |
| Add/Subtract | 42,000 per second |
| Multiply | 5,000 per second |
| Divide | 2,500 per second |
| Power Consumption | 100-250 kW |
| Weight | 2,110 lbs (960 kg) |
| Dimensions | Multiple cabinets |

## Memory Organization

### Core Memory
- **Word Size**: 36 bits
- **Address Space**: 15 bits (0-32767 octal: 0-16383 decimal)
- **Word Format**: 
  ```
  Bit:  0    1-8   9-35
        S    Exp   Fraction  (floating-point)
        
  Bit:  0    1-35
        S    Magnitude         (fixed-point)
  ```

### Memory Protection
- No hardware memory protection
- Single-user operation typical
- Self-modifying code common

## Registers

### Accumulator (AC) - 38 bits
```
Bit 0:     Sign (S)
Bit 1-2:   Unused (Q, P)
Bit 3-38:  Data (bits 01-35 + sign extension)
```

### Multiplier-Quotient (MQ) - 36 bits
```
Bit 0:     Sign
Bit 1-35:  Data
```

### Index Registers - 15 bits each
- **XR1 (XRA)**: Index Register 1
- **XR2 (XRB)**: Index Register 2  
- **XR4 (XRC)**: Index Register 4

Index registers are **subtracted** from effective address (not added).
Multiple indices can be combined via logical OR.

### Instruction Counter (IC) - 15 bits
Holds address of next instruction.

## Instruction Formats

### Type A (Conditional Jump)
```
Bits:  0-2   3-17    18-20   21-35
       Code  Decr    Tag     Address
```
- Code: 3 bits (must have bits 1-2 non-zero)
- Decrement: 15-bit value
- Tag: 3-bit index register select
- Address: 15-bit memory address

### Type B (Most Instructions)
```
Bits:  0-11   12-13   14-17   18-20   21-35
       Op      Flag    Unused  Tag     Address
```
- Op: 12-bit opcode (bits 1-2 must be 0)
- Flag: 2-bit modification
- Tag: 3-bit index register select
- Address: 15-bit memory address

### Type C, D, E
Specialized formats for shift, convert, and I/O instructions.

## Instruction Set Summary

### Load/Store
| Mnemonic | Op | Description |
|----------|-----|-------------|
| CLA | 0100 | Clear and Add (load) |
| LDQ | 0101 | Load MQ |
| STO | 0110 | Store AC |
| STQ | 0111 | Store MQ |
| LXA | 0460 | Load Index |
| SXA | 0461 | Store Index |

### Arithmetic
| Mnemonic | Op | Description |
|----------|-----|-------------|
| ADD | 0001 | Add |
| SUB | 0010 | Subtract |
| MPY | 0011 | Multiply |
| DVH | 0014 | Divide (single-length) |
| DVP | 0015 | Divide (double-length) |

### Logical
| Mnemonic | Op | Description |
|----------|-----|-------------|
| ANA | 0104 | Logical AND |
| ORA | 0105 | Logical OR |
| ERA | 0106 | Logical XOR |

### Shift
| Mnemonic | Op | Description |
|----------|-----|-------------|
| ALS | 0720 | Arithmetic Left Shift |
| ARS | 0721 | Arithmetic Right Shift |
| LLS | 0740 | Logical Left Shift |
| LRS | 0741 | Logical Right Shift |

### Transfer (Branch)
| Mnemonic | Op | Description |
|----------|-----|-------------|
| TZE | 0300 | Transfer on Zero |
| TNZ | 0301 | Transfer on Non-Zero |
| TPL | 0302 | Transfer on Plus |
| TMI | 0303 | Transfer on Minus |
| TOV | 0304 | Transfer on Overflow |
| TQI | 0320 | Transfer on MQ Indicator |

### I/O
| Mnemonic | Op | Description |
|----------|-----|-------------|
| RDT | 0500 | Read Tape |
| WRT | 0501 | Write Tape |
| RCD | 0502 | Read Card |
| PCH | 0503 | Punch Card |
| DCT | 0520 | Disconnect Tape |

### Other
| Mnemonic | Op | Description |
|----------|-----|-------------|
| HTR | 0000 | Halt and Transfer |
| NOP | 0444 | No Operation |
| PAU | 0445 | Pause |
| LBT | 0540 | Load Buffer Tape |

## I/O Channels

The IBM 709 introduced **independent I/O channels** (IBM 766 Data Synchronizer):
- Up to 3 Data Synchronizers
- Each controls up to 20 IBM 729 tape drives
- Also supports: IBM 716 printer, IBM 711 card reader, IBM 721 card punch
- I/O operates in parallel with CPU execution

## Data Formats

### Fixed-Point
- Sign/Magnitude format
- 35-bit magnitude + 1 sign bit

### Floating-Point (Single Precision)
- 1-bit sign
- 8-bit excess-128 exponent
- 27-bit fraction (no hidden bit)

### Characters (BCD)
- 6-bit BCD code
- 6 characters per 36-bit word
- Format: `C1 C2 C3 C4 C5 C6`

## Programming Model

### FAP Assembly Example

```
         REMOTE  MINER
         ENTRY   START
         
* Main entry point
START    CLA     ZERO          / Clear accumulator
         LXA     SAVE1,1       / Load index 1
         TZE     INIT          / If zero, initialize
         
* Mining loop
LOOP     CLA     ENTROPY       / Load entropy source
         ADD     TIMER         / Add timer value
         STO     ACCUM         / Store result
         TZE     CHECK         / Check for attestation
         
CHECK    CLA     COUNTER       / Load counter
         SUB     THRESHOLD     / Compare to threshold
         TMI     LOOP          / If negative, continue
         
* Generate attestation
GEN      CLA     WALLET        / Load wallet ID
         WRT     TAPE          / Write to tape
         CLA     ZERO
         STO     COUNTER       / Reset counter
         TZE     LOOP          / Continue mining
         
* Data area
ZERO     DEC     0
ENTROPY  BSS     1
TIMER    BSS     1
ACCUM    BSS     1
COUNTER  DEC     0
THRESHOLD DEC    600
WALLET   OCT     1234567654321 / Wallet ID
SAVE1    BSS     1

         END     START
```

### Octal Notation

All numeric constants in FAP are octal by default:
```
DEC     100      / Decimal 100
OCT     144      / Octal 144 (= decimal 100)
```

### Index Register Usage

```
         LXA     VALUE,1       / Load VALUE into XR1
         CLA     DATA,1        / Load DATA - XR1
         SXA     SAVE,1        / Store XR1 to SAVE
```

Multiple indices (OR'd together):
```
         CLA     DATA,1,2,4    / DATA - (XR1 | XR2 | XR4)
```

## SIMH Emulation

### Starting IBM 7090 Simulator

```bash
sim> ibm7090
```

### Basic Commands

```
sim> LOAD program.bin      / Load binary program
sim> RUN                   / Start execution
sim> STEP                  / Single step
sim> DEPOSIT PC 1000       / Set program counter
sim> EXAMINE AC            / Examine accumulator
sim> ATTACH card reader deck.pun  / Attach card deck
sim> ATTACH tape0n tape.tap       / Attach tape
```

### Configuration File (ibm7090.ini)

```
set cpu 32k
set cpu idle
attach card reader cards.pun
attach punch punch.out
attach tape0n tape0.tap
attach tape1n tape1.tap
load miner.bin
run
```

## Mining Implementation Considerations

### Memory Layout

```
Address (octal)  Usage
0-777           Interrupt vectors / zero page
1000-1777       Code (miner logic)
2000-2777       Data (entropy, counters)
3000-3777       Wallet storage
4000-7777       Buffer space
10000-37777     Unused / available
```

### Timing Considerations

- Instruction cycle: 2.18 μs
- Memory access: 2.18 μs (core memory)
- Tape operation: milliseconds (async)
- Card reader: ~100 cards/minute

### Entropy Generation Strategy

1. **Timer-based**: Use instruction timing variance
2. **Core decay**: Read memory timing variations
3. **I/O timing**: Card reader mechanical variance
4. **Tube noise**: Vacuum tube thermal variations (simulated)

## References

1. IBM 709 Reference Manual, Form A22-6501-0, 1958
2. Sherman, P.M. "Programming and Coding the IBM 709-7090-7094 Computers", 1963
3. SIMH IBM 7090 Documentation: https://github.com/open-simh/simh
4. bitsavers.org IBM 709 archive: http://bitsavers.org/pdf/ibm/709/
