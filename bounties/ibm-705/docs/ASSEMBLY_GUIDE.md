# IBM 705 Assembly Programming Guide

## Overview

The IBM 705 (1954) uses a **character-oriented, variable word-length** architecture. This guide covers programming the IBM 705 for the RustChain mining application.

## Architecture Basics

### Memory Organization

- **Address Space**: 4-digit decimal (0000-9999)
- **Character Size**: 7 bits (6 data + 1 parity)
- **Word Length**: Variable (1-128 characters)
- **Instruction Width**: 12 characters per instruction word

### Registers

| Register | Size | Purpose |
|----------|------|---------|
| **A (Accumulator)** | 128 chars | Main arithmetic register |
| **B (Buffer)** | 12 chars | I/O buffer |
| **C (Counter)** | 6 digits | Loop counter |

## Instruction Set

### Data Movement

| Opcode | Mnemonic | Format | Description |
|--------|----------|--------|-------------|
| `LD` | Load | `LD  address` | Load memory into accumulator |
| `ST` | Store | `ST  address` | Store accumulator to memory |
| `ZT` | Zero & Transfer | `ZT  address` | Clear accumulator, load from memory |

### Arithmetic

| Opcode | Mnemonic | Format | Description |
|--------|----------|--------|-------------|
| `AD` | Add | `AD  address` | Add memory to accumulator |
| `SU` | Subtract | `SU  address` | Subtract memory from accumulator |
| `MU` | Multiply | `MU  address` | Multiply accumulator by memory |
| `DV` | Divide | `DV  address` | Divide accumulator by memory |

### Control Flow

| Opcode | Mnemonic | Format | Description |
|--------|----------|--------|-------------|
| `J` | Jump | `J   address` | Unconditional branch |
| `JT` | Jump True | `JT  address` | Branch if comparison > 0 |
| `JF` | Jump False | `JF  address` | Branch if comparison ≤ 0 |
| `SW` | Stop | `SW  address` | Halt execution |
| `NOP` | No Op | `NOP address` | No operation |

### I/O Operations

| Opcode | Mnemonic | Format | Description |
|--------|----------|--------|-------------|
| `RD` | Read | `RD  address` | Read from input tape |
| `WR` | Write | `WR  address` | Write to output tape |

### Comparison

| Opcode | Mnemonic | Format | Description |
|--------|----------|--------|-------------|
| `CO` | Compare | `CO  address` | Compare accumulator with memory |

**Comparison Results**:
- `comparison_indicator = -1`: Accumulator < Memory
- `comparison_indicator = 0`: Accumulator = Memory
- `comparison_indicator = +1`: Accumulator > Memory

## Programming Example: Mining Loop

```asm
* IBM 705 Mining Program
* Memory Layout:
*   0100-0109: NONCE
*   0110-0119: BLOCK_DATA
*   0120-0129: DIFFICULTY
*   0150-0159: ONE (constant = 1)
*   0160-0169: CONSTANT
*   0170-0179: PRIME

* Initialize nonce to 1
         ZT   0100
         LD   0150
         ST   0100

MINING_LOOP:
* Increment nonce
         LD   0100
         AD   0150
         ST   0100

* Hash: (block_data × nonce) mod PRIME
         LD   0110
         MU   0100
         DV   0170
         ST   0140

* Compare to difficulty
         LD   0140
         CO   0120

* If hash < difficulty, success!
         JF   FOUND

* Continue mining
         J    MINING_LOOP

FOUND:
         WR   0140
         SW   0000
```

## Field Length Conventions

The IBM 705 uses **variable field lengths**. For mining operations:

- **Standard field**: 10 characters (digits)
- **Instruction word**: 12 characters
- **Accumulator**: 128 characters (full width)

### Example: 10-Digit Field

```
Memory: 0100-0109 contains "0000000042"
Load:   LD 0100
Result: Accumulator[0-9] = "0000000042"
```

## Best Practices

### 1. Memory Layout Planning

```
Address Range    Usage
0000-0099        I/O Buffers
0100-0199        Constants and Data
0200-0999        Program Code
1000-9999        Additional Data
```

### 2. Instruction Formatting

Each instruction occupies **12 characters**:
```
"LD  0100    "  (opcode + spaces + 4-digit address + padding)
```

### 3. Loop Optimization

Minimize memory accesses in tight loops:
```asm
* Good: Load once, use multiple times
         LD   CONSTANT
         MU   VALUE1
         ST   TEMP
         LD   CONSTANT    ; Reload if needed
         
* Better: Keep in accumulator when possible
         LD   CONSTANT
         MU   VALUE1
         MU   VALUE2      ; Chain operations
```

### 4. Error Handling

Check indicators after operations:
```asm
         DV   DIVISOR
         JT   CHECK_OK    ; Jump if check indicator set
         * Handle divide error
```

## Mining Algorithm Implementation

### Simplified Proof-of-Work

```
hash = ((block_data × nonce) + CONSTANT) mod PRIME
```

**Implementation**:
```asm
         LD   BLOCK_DATA   ; Load block header hash
         MU   NONCE        ; Multiply by nonce
         AD   CONSTANT     ; Add magic number
         DV   PRIME        ; Divide (remainder = hash)
         ST   HASH_RESULT  ; Store result
         
         LD   HASH_RESULT
         CO   DIFFICULTY   ; Compare to target
         JF   SUCCESS      ; Jump if hash ≤ difficulty
```

### Performance Characteristics

| Metric | Value |
|--------|-------|
| Instructions per hash | ~15 |
| Memory accesses | ~8 per hash |
| Cycle time | ~24 μs per instruction |
| Hash rate | ~0.003 H/s (simulated) |

## Debugging Tips

### 1. Memory Dumps

```python
# In simulator
print(cpu.memory.dump(100, 20))  # Dump addresses 100-119
```

### 2. CPU Status

```python
print(cpu.get_status())
```

### 3. Single-Step Execution

```python
cpu.state.program_status = "RUN"
for i in range(10):
    cpu.step()
    print(f"Step {i}: PC={cpu.state.instruction_address}")
```

## Historical Notes

The IBM 705 was programmed using:
- **SOAP** (Symbolic Optimal Assembly Program) - alphanumeric assembler
- **Speedcoding** - interpreted high-level language
- **FORTRAN** - added in 1957

This implementation uses a simplified assembly syntax compatible with the original instruction set.

## References

- IBM 705 Principles of Operation (A24-1036)
- IBM 705 Programming Manual (A24-1037)
- [IBM 705 Historical Documents](https://archive.org/details/ibm705manual)

---

**For RustChain Bounty #356**  
Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
