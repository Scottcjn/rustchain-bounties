# PDP-1 Architecture Reference

## Overview

The PDP-1 (Programmed Data Processor-1) was DEC's first computer, introduced in 1959. It was revolutionary for its time, being transistor-based rather than vacuum tube-based, making it smaller, faster, and more reliable than its contemporaries.

## Historical Context

- **Developer**: Digital Equipment Corporation (DEC)
- **First Shipped**: 1959
- **Production**: 1959-1966 (53 units built)
- **Original Price**: $120,000 (≈ $1.2M in 2024)
- **Location**: DEC Headquarters, Maynard, Massachusetts

### Notable Achievements

1. **First Minicomputer**: Launched the minicomputer industry
2. **First Interactive Computer**: Users could type and see results immediately
3. **Spacewar! (1962)**: First video game, created by Steve Russell
4. **Hacker Culture**: Birthplace at MIT Tech Model Railroad Club
5. **Text Editing**: First interactive text editor
6. **Computer Graphics**: Ivan Sutherland's Sketchpad (1963)

## Technical Specifications

### Core Architecture

| Component | Specification |
|-----------|---------------|
| **Word Size** | 18 bits |
| **Memory** | 4,096 words (9,216 bytes) magnetic-core |
| **Technology** | Transistors (~500) |
| **Clock Speed** | 5 MHz (200 ns cycle time) |
| **Instruction Time** | 5-10 microseconds |
| **Performance** | 100,000-200,000 instructions/second |
| **Power Consumption** | ~500 watts |

### Registers

The PDP-1 had a minimal register set:

| Register | Size | Purpose |
|----------|------|---------|
| **AC** | 18 bits | Accumulator - primary arithmetic/logic register |
| **IO** | 18 bits | Input-Output register - extends AC for double-precision |
| **PC** | 18 bits | Program Counter - address of next instruction |
| **MB** | 18 bits | Memory Buffer - holds data being transferred |
| **MA** | 18 bits | Memory Address - holds memory address |
| **L** | 1 bit | Link bit - carry/overflow for extended arithmetic |

### Memory Organization

```
PDP-1 Memory: 4,096 words × 18 bits = 73,728 bits (9,216 bytes)

Address Range    Octal Range    Purpose
0x000-0x0FF      0000-0377      System area (boot, constants, I/O)
0x100-0x3FF      0400-1777      Program code and data
0x400-0xFFF      2000-7777      User programs (75% of memory!)
```

### Instruction Format

The PDP-1 used an 18-bit instruction format:

```
Single Address Format:
┌─────┬─────────┬─────┬──────────────┐
│  I  │ OPCODE  │  B  │   ADDRESS    │
│(17) │(16-14)  │(13) │   (12-0)     │
└─────┴─────────┴─────┴──────────────┘

I = Indirect bit (use memory at address as pointer)
B = Index bit (use index register)
ADDRESS = 12-bit memory address (0-4095)
```

### Instruction Set

The PDP-1 had approximately 72 instructions in several classes:

#### Memory Reference Instructions

| Mnemonic | Opcode | Description |
|----------|--------|-------------|
| AND | 0 | Logical AND with memory |
| IOR | 0 | Inclusive OR with memory |
| XOR | 0 | Exclusive OR with memory |
| JMS | 2 | Jump to Subroutine |
| JMP | 3 | Jump |
| ISZ | 4 | Increment and Skip if Zero |
| DCA | 5 | Deposit and Clear Accumulator |
| TAD | 6 | Two's Complement Add |

#### Microinstructions (Operate Class)

| Mnemonic | Code | Description |
|----------|------|-------------|
| HLT | 0000 | Halt |
| CLA | 0001 | Clear Accumulator |
| CLL | 0002 | Clear Link |
| CMA | 0004 | Complement Accumulator |
| CML | 0010 | Complement Link |
| RAR | 0040 | Rotate Accumulator Right |
| RAL | 0100 | Rotate Accumulator Left |
| RTR | 0200 | Rotate Accumulator Right through Link |
| RTL | 0400 | Rotate Accumulator Left through Link |

#### I/O Instructions (IOT)

The PDP-1 used IOT (Input/Output Transfer) instructions to control peripherals:

| Device | Code | Description |
|--------|------|-------------|
| Type 30 | 0 | Precision CRT Display |
| Paper Tape Reader | 1 | High-speed reader |
| Paper Tape Punch | 2 | High-speed punch |
| Typewriter | 3 | Flexowriter console |

### I/O Devices

#### Type 30 Precision CRT Display

- Point-plotting display
- 1024 × 1024 resolution
- Used for graphics and visual output
- Controlled via IOT instructions

#### Paper Tape Reader/Punch

- 8-level paper tape
- 60 characters/second read speed
- 60 characters/second punch speed
- Primary storage medium

#### Flexowriter

- Electric typewriter
- Keyboard input
- Printed output
- Also could read/punch paper tape

## Programming the PDP-1

### Assembly Language Example

```assembly
        / Simple addition program
        / Adds numbers from 1 to 10

START,  CLA             / Clear accumulator
        TAD ONE         / Add 1
        DCA SUM         / Store in SUM
        ISZ COUNT       / Increment COUNT, skip if zero
        JMP START       / Loop back
        HLT             / Halt

ONE,    1               / Constant: 1
COUNT,  -10             / Loop counter (negative)
SUM,    0               / Sum storage
```

### Memory Layout for SHA256

For the RustChain miner, memory is organized as:

```
Address Range   Size    Usage
0x000-0x03F     64      Boot loader and initialization
0x040-0x0BF     128     SHA256 K constants (64 × 2 words each)
0x0C0-0x0DF     32      Hash state H0-H7 (8 × 2 words each)
0x0E0-0x0FF     32      Working variables a-h
0x100-0x13F     64      Message schedule W[0..63]
0x140-0x17F     64      Temporary storage
0x180-0x1FF     128     I/O buffer
0x200-0x3FF     512     Subroutines and utilities
0x400-0xFFF     3,072   Free space (75% available!)
```

## Performance Characteristics

### Instruction Timing

| Operation | Time (μs) |
|-----------|-----------|
| Memory Access | 5 |
| ADD (TAD) | 7.5 |
| Jump (JMP) | 5 |
| Skip (ISZ) | 5-10 |
| I/O Transfer | 10-100 |

### SHA256 Performance Estimates

- Instructions per hash: ~10,000-15,000
- Average instruction time: 7.5 μs
- Time per hash: 0.075-0.11 seconds
- **Estimated hash rate: 9-13 H/s**

This is significantly faster than vacuum tube machines due to:
- Transistor speed (nanoseconds vs microseconds)
- Core memory (no refresh needed)
- Simpler instruction set

## Maintenance and Reliability

### Mean Time Between Failures (MTBF)

- Transistors: Very reliable (years)
- Core memory: Extremely reliable (non-volatile)
- I/O devices: Mechanical wear (paper tape)

### Typical Issues

1. **Core Memory**: Rare failures, individual cores can be replaced
2. **Transistors**: Early transistors could fail, but much better than tubes
3. **Paper Tape**: Tearing, misalignment
4. **CRT Display**: Phosphor burn-in, alignment

## Preservation

### Known Operating PDP-1 Systems

1. **Computer History Museum** (Mountain View, CA)
   - Fully operational
   - Regularly demonstrated
   - Runs Spacewar!

2. **MIT Museum** (Cambridge, MA)
   - Display unit
   - Historical significance

3. **The National Museum of American History** (Washington, DC)
   - Display unit

## References

- DEC PDP-1 Handbook (1963)
- Bitsavers PDP-1 Collection: http://bitsavers.org/pdf/dec/pdp1/
- Computer History Museum: https://computerhistory.org/collections/catalog/102643816
- "DEC's First Computer: The PDP-1" by Edson de Castro

---

**Document Version**: 1.0  
**Created**: 2026-03-13  
**For**: RustChain PDP-1 Miner Project
