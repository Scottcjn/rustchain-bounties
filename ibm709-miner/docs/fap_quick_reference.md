# FAP Assembly Quick Reference

## Overview

FAP (FORTRAN Assembly Program) was the assembly language for the IBM 709/7090/7094 series. This quick reference covers the essentials for writing the RustChain miner.

## Basic Syntax

```
LABEL    OP      ADDRESS,INDEX    / COMMENT
```

- **LABEL**: Symbolic name (1-6 characters)
- **OP**: Operation code (mnemonic)
- **ADDRESS**: Memory address or label
- **INDEX**: Index register specification (1, 2, 4, or combinations)
- **COMMENT**: After `/` symbol

## Number Systems

```
DEC     100      / Decimal 100
OCT     144      / Octal 144 (= decimal 100)
BCD     ABC      / BCD characters
```

**Default is OCTAL** for numeric constants!

## Pseudo-Operations

| Pseudo-op | Description | Example |
|-----------|-------------|---------|
| REMOTE | Program name | `REMOTE MINER` |
| ENTRY | Entry point | `ENTRY START` |
| END | End of program | `END START` |
| DEC | Decimal constant | `ZERO DEC 0` |
| OCT | Octal constant | `MASK OCT 777` |
| BSS | Reserve storage | `BUFFER BSS 10` |
| EQU | Equate (define constant) | `MAX EQU 100` |
| ORG | Origin (set location) | `ORG 1000` |

## Register Operations

### Load/Store Accumulator

```
CLA     ADDRESS     / Clear and Add (load to AC)
STO     ADDRESS     / Store AC to memory
LDQ     ADDRESS     / Load MQ register
STQ     ADDRESS     / Store MQ to memory
```

### Index Registers

```
LXA     ADDRESS,1   / Load index register 1
SXA     ADDRESS,1   / Store index register 1
LXA     ADDRESS,2   / Load index register 2
LXA     ADDRESS,4   / Load index register 4
```

Multiple indices (OR'd together):
```
CLA     DATA,1,2    / AC = DATA - (XR1 | XR2)
```

## Arithmetic Operations

```
ADD     ADDRESS     / Add to AC
SUB     ADDRESS     / Subtract from AC
MPY     ADDRESS     / Multiply (AC × ADDRESS → MQ:AC)
DVH     ADDRESS     / Divide (single-length)
DVP     ADDRESS     / Divide (double-length)
```

## Logical Operations

```
ANA     ADDRESS     / Logical AND
ORA     ADDRESS     / Logical OR
ERA     ADDRESS     / Logical XOR (Exclusive OR)
```

## Shift Operations

```
ALS     SHIFT       / Arithmetic Left Shift
ARS     SHIFT       / Arithmetic Right Shift
LLS     SHIFT       / Logical Left Shift
LRS     SHIFT       / Logical Right Shift
```

## Transfer (Branch) Instructions

| Mnemonic | Condition | Description |
|----------|-----------|-------------|
| TZE | AC = 0 | Transfer on Zero |
| TNZ | AC ≠ 0 | Transfer on Non-Zero |
| TPL | AC > 0 | Transfer on Plus |
| TMI | AC < 0 | Transfer on Minus |
| TOV | Overflow | Transfer on Overflow |
| TQI | MQ indicator | Transfer on MQ Indicator |

```
TZE     LABEL       / Jump if AC = 0
TNZ     LABEL       / Jump if AC ≠ 0
TPL     LABEL       / Jump if AC > 0
TMI     LABEL       / Jump if AC < 0
```

## Unconditional Transfer

```
TRA     ADDRESS     / Transfer (jump)
TRA     1,1         / Transfer via index register 1 (return from subroutine)
```

## Subroutine Calls

```
JSUB    ADDRESS     / Jump to Subroutine
        ...
        TRA     1,1 / Return (via index 1)
```

**Calling convention**:
1. Save index register before JSUB
2. Use `TRA 1,1` to return
3. Restore index register after return

Example:
```
         LXA     SAVE1,1     / Save XR1
         JSUB    MYROUTINE
         SXA     SAVE1,1     / Restore XR1
         
MYROUTINE
         ...                 / Do work
         TRA     1,1         / Return
```

## I/O Operations

### Tape Operations

```
LBT     UNIT        / Load Buffer Tape (prepare tape unit)
RDT     UNIT        / Read Tape
WRT     UNIT        / Write Tape
DCT     UNIT        / Disconnect Tape
```

Example:
```
         LBT     0           / Prepare tape unit 0
         CLA     DATA
         WRT     0           / Write to tape
         DCT     0           / Disconnect
```

### Card Operations

```
RCD     UNIT        / Read Card
PCH     UNIT        / Punch Card
```

## Comparison Operations

```
CAS     ADDRESS     / Compare AC with ADDRESS
                      AC > mem: AC positive
                      AC = mem: AC zero
                      AC < mem: AC negative
```

After CAS, use TPL/TZE/TMI to branch.

## Example Program

```
         REMOTE  EXAMPLE
         ENTRY   START
         
* Main program
START    CLA     ZERO
         LXA     SAVE1,1
         TZE     INIT
         
LOOP     JSUB    COLLECT
         JSUB    PROCESS
         TZE     LOOP
         
* Subroutine
COLLECT  SXA     SAVE2,1
         CLA     ENTROPY
         ADD     TIMER
         STO     RESULT
         CLA     SAVE2
         SXA     1,1
         TRA     1,1
         
* Data area
ZERO     DEC     0
ENTROPY  BSS     1
TIMER    DEC     100
RESULT   BSS     1
SAVE1    BSS     1
SAVE2    BSS     1
         
         END     START
```

## Common Patterns

### Loop with Counter

```
         LXA     COUNT,1
LOOP     ...                 / Do work
         LXA     1,1         / Decrement counter
         TZE     LOOP        / Continue if not zero
COUNT    DEC     100
```

### Conditional Execution

```
         CLA     VALUE
         TZE     SKIP        / Skip if zero
         ...                 / Execute if non-zero
SKIP     ...                 / Continue
```

### Save/Restore Index Registers

```
         LXA     SAVE1,1
         LXA     SAVE2,2
         LXA     SAVE4,4
         ...                 / Do work
         SXA     SAVE1,1
         SXA     SAVE2,2
         SXA     SAVE4,4
SAVE1    BSS     1
SAVE2    BSS     1
SAVE4    BSS     1
```

## Memory Layout Convention

```
Address (octal)  Usage
0-777           Zero page / vectors
1000-1777       Code
2000-2777       Data
3000-3777       Constants
4000-7777       Buffers
10000+          Available
```

## Tips for RustChain Miner

1. **Minimize code size** - Only 32K words available
2. **Use index registers efficiently** - Only 3 available
3. **Batch I/O operations** - Tape is slow
4. **Reuse buffers** - Don't allocate unnecessarily
5. **Test in SIMH** - Use STEP and EXAMINE for debugging
6. **Comment heavily** - Octal code is hard to read

## SIMH Debugging Commands

```
sim> STEP              / Single step
sim> EXAMINE AC        / View accumulator
sim> EXAMINE PC        / View program counter
sim> DEPOSIT LOC VAL   / Set memory location
sim> CONTINUE          / Continue execution
sim> BREAK ADDRESS     / Set breakpoint
```

## References

- IBM 709 Reference Manual: http://bitsavers.org/pdf/ibm/709/
- Programming IBM 709-7090-7094: http://bitsavers.org/pdf/ibm/7090/books/
- SIMH Documentation: https://github.com/open-simh/simh
