# PDP-8 Architecture Reference

## Overview

The PDP-8, introduced in 1965 by Digital Equipment Corporation (DEC), was the first minicomputer to sell for under $20,000. Over 50,000 units were sold, making it the best-selling computer of its era.

## Key Specifications

| Feature | Specification |
|---------|--------------|
| **Word Size** | 12 bits |
| **Memory** | 4K words (6 KiB) maximum |
| **Memory Type** | Magnetic core (1.5μs cycle) |
| **Registers** | AC (12-bit), PC (12-bit), L (1-bit) |
| **Instructions** | 8 major opcodes |
| **Clock** | ~0.667 MHz |
| **Performance** | ~0.333 MIPS |

## Memory Organization

```
Address Range    Size        Description
0000-0077 (oct)  64 words    Page 0 (always directly addressable)
0100-0177        64 words    Page 1
...
7600-7777        64 words    Page 63
```

### Addressing Modes

1. **Direct Page 0**: Addresses 0000-0077 always accessible
2. **Direct Current Page**: Addresses within current 128-word page
3. **Indirect**: Full 12-bit address via memory indirection

## Instruction Set

### Basic Instructions (3-bit opcode)

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| 0 | AND | AND memory with AC | 2 |
| 1 | TAD | Add memory to AC (with carry) | 2 |
| 2 | ISZ | Increment memory, skip if zero | 2 |
| 3 | DCA | Deposit AC and clear | 2 |
| 4 | JMS | Jump to subroutine | 2 |
| 5 | JMP | Jump unconditionally | 1 |
| 6 | IOT | Input/Output transfer | 2 |
| 7 | OPR | Operate (microinstructions) | 1 |

### OPR Microinstructions

#### Group 1 (AC/L operations)

| Code | Mnemonic | Operation |
|------|----------|-----------|
| 7001 | IAC | Increment AC |
| 7010 | RAR | Rotate AC right (through L) |
| 7011 | RAL | Rotate AC left (through L) |
| 7012 | RTR | Rotate AC right twice |
| 7013 | RTL | Rotate AC left twice |
| 7040 | CMA | Complement AC (one's complement) |
| 7100 | CML | Complement L |
| 7200 | CLA | Clear AC |
| 7200 | CLE | Clear L |

#### Group 2 (MQ operations - EAE)

| Code | Mnemonic | Operation |
|------|----------|-----------|
| 7300 | CAM | Clear AC and MQ |
| 7340 | CMQ | Clear MQ |

### IOT Device Codes

| Device | Code | Function |
|--------|------|----------|
| Paper Tape Reader | 6000 | Read character |
| Paper Tape Punch | 6001 | Write character |
| Console Keyboard | 6010 | Read key |
| Console Display | 6011 | Write character |
| RTC/Timer | 6020 | Read time/entropy |

## Programming Techniques

### Two's Complement Negation

PDP-8 has no subtract instruction. To compute A - B:

```assembly
    CLA         / Clear AC
    CMA         / Complement B (one's complement)
    TAD     B   / Add B
    TAD     ONE / Add 1 (complete two's complement)
    TAD     A   / Add A
                / Result: A - B in AC
```

### Conditional Branches

No conditional jump instructions exist. Use skip + jump:

```assembly
    / If AC == 0, jump to LABEL
    SZA         / Skip if AC zero
    JMP     NEXT
    JMP     LABEL
NEXT, ...
```

### Subroutine Calls

JMS stores return address at subroutine entry:

```assembly
    JMS     SUBR    / Jump to subroutine
    ...             / Continue here after return
    
SUBR,   0           / Return address stored here
        ...         / Subroutine code
        JMP     I SUBR  / Return to caller
```

**Warning**: This doesn't support recursion! The return address overwrites the first word.

## Multiplication (Shift and Add)

Without hardware multiply (EAE option):

```assembly
/ Multiply AC by value at MULT
/ Result in AC (may overflow)

MULTIPLY,
    0
    DCA     TEMP        / Save multiplier
    CLA                 / Clear result
    TAD     MULT        / Load multiplicand
    DCA     MULT_TEMP
    
MULT_LOOP,
    TAD     TEMP
    SZA                 / Skip if multiplier bit zero
    TAD     MULT_TEMP   / Add multiplicand
    
    RAL                 / Rotate for next bit
    ...
    JMP     I MULTIPLY
```

## Hardware Entropy Collection

For RustChain mining, entropy is collected from:

1. **Core Memory Timing**: Slight variations in access times
2. **Interval Timer**: Hardware clock drift
3. **RTC**: Real-time clock low bits
4. **Instruction Timing**: Thermal variations

Example entropy collection:

```assembly
ENTROPY_LOOP,
    IOT     6020        / Read RTC
    DCA     I ENTROPY_PTR
    ISZ     COUNTER
    JMP     ENTROPY_LOOP
```

## Memory Limitations

With only 4K words:

- Use **overlay techniques** for large programs
- Store persistent data on **paper tape** or **DECtape**
- Minimize lookup tables
- Reuse memory locations for different purposes

## Emulation

### SIMH PDP-8 Emulator

```bash
# Install SIMH
git clone https://github.com/simh/simh.git
cd simh
make

# Run PDP-8 emulator
simh> pdp8
simh> load pdp8_miner.bin
simh> go
simh> quit
```

### Python Simulator

```bash
python pdp8_simulator.py
```

## References

- DEC PDP-8 Handbook (1972)
- "The PDP-8: A Case Study in Minimalism"
- SIMH PDP-8 Documentation
- Intersil 6100 Datasheet

---

**For RustChain Bounty #394**
Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
