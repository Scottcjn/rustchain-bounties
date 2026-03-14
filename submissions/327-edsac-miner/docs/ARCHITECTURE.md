# EDSAC Architecture Deep Dive

## Historical Context

**EDSAC** (Electronic Delay Storage Automatic Calculator) was designed by **Sir Maurice Wilkes** at Cambridge University Mathematical Laboratory. It ran its first program on **May 6, 1949** - calculating squares and square roots.

### Why EDSAC Matters

- First practical stored-program computer
- Established the von Neumann architecture pattern
- Direct ancestor of modern computers
- Ran real computational work (not just a prototype)

## Technical Specifications

### Word Format

```
Bit:  0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  P
     [S][D0][D1][D2][D3][D4][D5][D6][D7][D8][D9][D10][D11][D12][D13][D14][Parity]
     
S = Sign bit (0 = positive, 1 = negative)
D0-D14 = 15 data bits (magnitude)
P = Parity bit (odd parity)
```

**Effective range:** -16383 to +16383 (15-bit signed magnitude)

### Memory System

#### Mercury Delay Lines

Physical implementation:
- Tanks filled with liquid mercury
- Piezoelectric crystals at each end
- Sound waves propagate through mercury (~1450 m/s)
- Bits recirculated continuously

```
Initial Tank:  512 words (32 "long tanks" × 16 words + 4 "short tanks")
Expanded:      1024 words
Access Time:   ~1.5ms average (serial access)
Refresh:       Automatic (recirculating)
```

#### Memory Map

```
Address 0-31:    Short tanks (faster access, ~200μs)
Address 32-511:  Long tanks (slower, ~1.5ms average)
Address 512-1023: Expanded memory (added later)
```

### Instruction Format

Each instruction = one 17-bit word:

```
[S][Opcode][Address][Length]
  1 bit   5 bits   10 bits    1 bit (for some instructions)
```

**Opcode encoding** (teleprinter characters):
- A (00001) = Add
- S (10011) = Subtract  
- T (10100) = Transfer (store)
- U (10101) = Add and store
- H (01000) = Halt
- E (00101) = Jump if ≥ 0
- G (00111) = Jump if < 0
- I (01001) = Input
- O (01111) = Output
- L (01100) = Load
- M (01101) = Multiply
- N (01110) = Negate
- Z (11010) = Zero accumulator

### Registers

#### Accumulator (A)
- 17-bit register
- Holds results of arithmetic
- Used for comparisons

#### Order Tank
- Holds current instruction
- Automatically incremented to next

#### Multiplier Register (R)
- 17-bit register
- Used for multiplication
- Holds intermediate results

### Instruction Cycle

```
1. Fetch: Load instruction from memory into Order Tank
2. Decode: Interpret opcode
3. Execute: Perform operation
4. Increment: Move to next instruction
5. Repeat
```

**Cycle time:** ~1.5ms per instruction (memory-bound)

## Programming Model

### Assembly Language

EDSAC used **initial letters** of operations:

```
A 45      ; Add contents of address 45 to accumulator
T 100     ; Transfer (store) accumulator to address 100
E 25      ; Jump to 25 if accumulator ≥ 0
H         ; Halt
```

### Constants

Stored in memory using pseudo-instructions:

```
P1024F    ; Constant: 1024 (Fixed point)
P512D     ; Constant: 512 (Double length)
EF        ; Constant: 0 (Empty/F zero)
```

### Input/Output

**Input:**
- 5-hole paper tape
- Read via photoelectric reader
- ~10 characters/second

**Output:**
- Teleprinter (ASCII-like)
- CRT display (for debugging)
- ~10 characters/second

## Limitations for Modern Computing

### What EDSAC Cannot Do

1. **No bitwise operations** - AND, OR, XOR not available
2. **No division** - Only addition, subtraction, multiplication
3. **No indirect addressing** - All addresses must be literal
4. **No subroutines** - No stack, no CALL/RETURN (added later)
5. **Serial memory access** - Cannot random-access quickly
6. **17-bit words only** - Cannot handle larger numbers natively

### Workarounds

- **Bitwise ops:** Simulate via arithmetic (slow)
- **Division:** Repeated subtraction (very slow)
- **Subroutines:** Self-modifying code (dangerous)
- **Large numbers:** Multi-word arithmetic (complex)

## Relevance to Cryptocurrency Mining

### The Challenge

Modern mining requires:
- SHA-256 hashing (bitwise operations, 32-bit words)
- 256-bit state management
- Billions of hashes per second

EDSAC provides:
- 17-bit words
- No bitwise operations
- ~500 operations per second

### The Adaptation

We create a **conceptual proof** that demonstrates:
1. The mathematical structure of PoW
2. Iterative nonce searching
3. Target comparison
4. Block validation

**Not practical, but historically significant!**

---

## References

1. Wilkes, M.V. (1951). "The Best Way to Design an Automatic Calculating Machine"
2. Campbell-Kelly, M. (1989). "The EDSAC: A Case Study in the Management of a Computer Project"
3. Computer Conservation Society - EDSAC Replica Project
4. Cambridge University Computer Laboratory Archives
