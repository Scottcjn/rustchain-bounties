# ERA 1101 Architecture Reference

Detailed technical reference for the ERA 1101 computer system.

## Overview

The ERA 1101 (Engineering Research Associates 1101), later renamed UNIVAC 1101, was introduced in 1950 as the first commercially available stored-program computer.

## Physical Specifications

| Property | Value |
|----------|-------|
| Dimensions | 38 ft × 20 ft (12m × 6.1m) |
| Weight | 8.4 short tons (7.6 t) |
| Power | ~25 kW |
| Vacuum Tubes | ~2,700 |
| Cooling | Industrial HVAC required |

## Memory System

### Magnetic Drum

| Property | Value |
|----------|-------|
| Diameter | 8.5 inches (22 cm) |
| Rotation Speed | 3,500 RPM |
| Rotation Period | ~17,143 μs |
| Read-Write Heads | 200 |
| Total Capacity | 16,384 words × 24 bits = 48 KB |
| Words per Track | 82 |
| Word Access Time | ~209 μs |

### Access Timing

- **Minimum Access Time**: 32 μs (when word is already under head)
- **Maximum Access Time**: 17 ms (full rotation)
- **Average Access Time**: ~8.5 ms (half rotation)

### Drum Optimization

The key to ERA 1101 programming is **instruction scheduling**. Each instruction includes a 4-bit **skip field** that specifies how many memory locations to skip before fetching the next instruction.

**Calculation:**
```
skip = (execution_time_us / word_time_us) - 1
```

Example:
- ADD instruction: 96 μs execution
- Word time: 209 μs
- Optimal skip: (96 / 209) - 1 ≈ 0 (no skip needed)
- MPY instruction: 352 μs execution
- Optimal skip: (352 / 209) - 1 ≈ 1

## CPU Architecture

### Registers

| Register | Size | Purpose |
|----------|------|---------|
| A (Accumulator) | 48 bits | Primary arithmetic (double-word) |
| Q | 24 bits | Multiplier/quotient register |
| X | 24 bits | Index register |
| PC | 14 bits | Program counter |

### Word Format

```
Bits 0-5:   Opcode (6 bits)
Bits 6-9:   Skip count (4 bits)
Bits 10-23: Address (14 bits)
```

### Number Representation

- **Format**: Ones' complement binary
- **Word Size**: 24 bits
- **Sign Bit**: Bit 23 (MSB)
- **Range**: -8,388,607 to +8,388,607
- **Negative Zero**: Exists in ones' complement (0xFFFFFF)

## Instruction Set

### Arithmetic Instructions

| Opcode | Mnemonic | Description | Time (μs) |
|--------|----------|-------------|-----------|
| 00-05 | INS | Insert various forms into A | 96 |
| 06-0B | ADD | Add to A (various forms) | 96 |
| 0C | INSQ | Insert Q in A | 96 |
| 0D | CLR | Clear right half of A | 96 |
| 0E | ADDQ | Add Q to A | 96 |
| 0F | TRA | Transfer A to Q | 96 |

### Multiply/Divide

| Opcode | Mnemonic | Description | Time (μs) |
|--------|----------|-------------|-----------|
| 10 | MPY | Q × y → A | 352 |
| 11 | LGR | Logical product add | 192 |
| 12 | AND | Logical product Q × y | 96 |
| 13 | DIV | A ÷ y, Q=quotient, A=remainder | 1000 |
| 14 | MLA | Multiply and add | 352 |

### Logical/Control

| Opcode | Mnemonic | Description | Time (μs) |
|--------|----------|-------------|-----------|
| 15 | STO | Store right half of A | 96 |
| 16 | SHL | Shift A left | 96 |
| 17 | STQ | Store Q | 96 |
| 18 | SHQ | Shift Q left | 96 |
| 19 | RPL | Replace using Q as operator | 96 |
| 1A | JMP | Unconditional jump | 96 |
| 1B | STA | Store address portion | 96 |
| 1C | JNZ | Jump if A ≠ 0 | 96 |
| 1D | INSX | Insert into X | 96 |
| 1E | JN | Jump if A < 0 | 96 |
| 1F | JQ | Jump if Q < 0 | 96 |

### I/O Instructions

| Opcode | Mnemonic | Description | Time (μs) |
|--------|----------|-------------|-----------|
| 20 | HLT | Halt | 0 |
| 21 | NOP | No operation | 96 |
| 22 | PRT | Print | 5000 |
| 23 | PCH | Punch | 10000 |
| 24 | STP | Stop | 0 |

## Ones' Complement Arithmetic

### Addition

```
result = a + b
if result >= 2^24:
    result = (result & 0xFFFFFF) + 1  # End-around carry
```

### Negation

```
negate(x) = (~x) & 0xFFFFFF
```

### Subtraction

```
a - b = a + (~b)  # Add ones' complement
```

## Programming Example

### Simple Addition with Drum Optimization

```assembly
* Add two numbers with optimal drum scheduling
        ORG 0x1000

START   INS  VALUE1       * Load first value
        ADD  VALUE2       * Add second value  
        STO  RESULT       * Store result
        HLT               * Halt

* Data section
        ORG 0x2000
VALUE1  OCT 000123        * Octal: 0123
VALUE2  OCT 000456        * Octal: 0456
RESULT  OCT 000000        * Will hold sum

        END START
```

### Assembled Output

```
Address  Word     Instruction
0x1000   006000   INS  skip=6, addr=0x2000
0x1001   066001   ADD  skip=6, addr=0x2001
0x1002   156002   STO  skip=6, addr=0x2002
0x1003   200000   HLT  skip=0, addr=0x0000
```

## Performance Characteristics

### Instruction Execution Times

| Operation | Time (μs) | Equivalent Clock Cycles |
|-----------|-----------|------------------------|
| ADD/SUB | 96 | ~12 cycles @ 8 MHz equivalent |
| MPY | 352 | ~44 cycles |
| DIV | 1000 | ~125 cycles |
| Memory Access | 32-17000 | Variable (rotational) |

### Estimated SHA256 Performance

| Metric | Value |
|--------|-------|
| Hashes per second | 0.05-0.2 H/s |
| Time per hash | 5-20 seconds |
| Memory usage | ~12 KB |
| Instructions per hash | ~50,000 |

## Historical Notes

- **Original Name**: Atlas (named after Barnaby comic strip character)
- **Commercial Name**: 1101 (binary for 13, the Navy task number)
- **Designer**: Engineering Research Associates (ERA)
- **ERA Founders**: Former Navy code-breakers from WWII
- **First Installation**: Army Security Agency, December 1950
- **Successor**: UNIVAC 1103

## References

- [Bitsavers ERA 1101 Documentation](http://www.bitsavers.org/pdf/era/1101/)
- [Computer History Museum](https://www.computerhistory.org/)
- [UNIVAC 1101 Wikipedia](https://en.wikipedia.org/wiki/UNIVAC_1101)

---

*This document is part of the RustChain Bounty #1824 submission.*
*ERA 1101 Miner - 1950 meets 2026.*
