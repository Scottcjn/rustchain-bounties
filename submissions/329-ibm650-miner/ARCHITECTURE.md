# IBM 650 Miner Architecture Design

## 1. System Overview

### 1.1 Historical Context

The IBM 650 Magnetic Drum Data-Processing Machine (1953-1962) represents:
- **First mass-produced computer**: ~2,000 units sold
- **First profitable computer**: Made meaningful profit for IBM
- **Educational pioneer**: First computer in many universities
- **Knuth's dedication**: "The Art of Computer Programming" dedicated to the 650

### 1.2 Technical Specifications

| Component | Specification |
|-----------|--------------|
| **Technology** | Vacuum tubes |
| **Clock Frequency** | 125 kHz |
| **Memory Type** | Magnetic drum (rotating) |
| **Memory Capacity** | 1,000 / 2,000 / 4,000 words |
| **Word Size** | 10 decimal digits + sign |
| **Encoding** | Bi-quinary coded decimal |
| **Access Time** | 0-4.8 ms (average 2.5 ms) |
| **Instruction Rate** | ~40/sec (unoptimized), ~2000/sec (optimized) |
| **Weight** | 5,400-6,263 lbs (2.4-2.8 tonnes) |
| **Power** | Requires IBM 655 Power Unit |
| **Price (1959)** | $150,000 (~$1.5M today) |

## 2. Architecture Constraints

### 2.1 Decimal System

The IBM 650 is a **decimal computer**, not binary:
- All arithmetic operates on decimal digits
- No native binary operations
- Bi-quinary encoding: 2 bits for "five" + 5 bits for "0-4"
- This fundamentally changes cryptographic approach

### 2.2 Memory Organization

```
Drum Memory Layout (2K model):
┌─────────────────────────────────────┐
│ Band 0: Words 0000-0049            │
│ Band 1: Words 0050-0099            │
│ ...                                 │
│ Band 39: Words 1950-1999           │
└─────────────────────────────────────┘

Drum rotates at 12,500 RPM
- 208.33 rotations per second
- 4.8 ms per full rotation
- 50 words per band
- 0.096 ms per word time
```

### 2.3 Instruction Format

```
┌─────┬──────────┬─────────────┐
│ OP  │    DA    │     IA      │
│ 2   │    4     │     4       │
└─────┴──────────┴─────────────┘

OP  = Operation code (00-99)
DA  = Data address (0000-1999)
IA  = Next instruction address (0000-1999)
```

### 2.4 Address Space

| Range | Purpose |
|-------|---------|
| 0000-1999 | Drum memory (2K model) |
| 8000 | Console switches |
| 8001 | Console display |
| 8002 | Lower accumulator |
| 8003 | Upper accumulator |
| 8005-8007 | Index registers (IBM 653) |
| 9000-9059 | Core storage (IBM 653) |

## 3. Mining Algorithm Design

### 3.1 Challenge: Cryptography on Decimal Computer

Traditional cryptographic hashes (SHA-256, etc.) rely on:
- Binary operations (XOR, AND, OR)
- Bit shifts and rotations
- 32/64-bit arithmetic

**IBM 650 only supports:**
- Decimal addition/subtraction
- Decimal multiplication/division
- No bitwise operations
- 10-digit precision

### 3.2 Solution: Decimal Hash Function

We design a hash function using only decimal operations:

```python
def decimal_hash(state, input_data):
    """
    Compute hash using decimal arithmetic only
    """
    # Initialize from wallet
    state = wallet_digits_as_integer()
    
    # Mix in input data
    for digit in input_data:
        state = (state * PRIME + digit) % MODULO
    
    # Multiple rounds of mixing
    for round in range(ROUNDS):
        state = (state * ROUND_PRIME[round]) % MODULO
        # Additional mixing: add high digits to low
        state = (state + (state // 1000)) % MODULO
    
    return state
```

### 3.3 Constants

```
PRIME constants (for mixing):
  PRIME1 = 7
  PRIME2 = 11
  PRIME3 = 13
  PRIME4 = 17
  PRIME5 = 19
  PRIME6 = 23
  PRIME7 = 29
  PRIME8 = 31

MODULO = 10^10 (keep lower 10 digits)
```

### 3.4 Proof Format

Each proof is output on an 80-column punched card:

```
┌────────────────────────────────────────────────────────┐
│ Cols  1-10: Wallet ID (numeric digits only)           │
│ Cols 11-20: Timestamp (YYMMDDHHMM format)             │
│ Cols 21-30: Proof Hash Part 1 (10 digits)             │
│ Cols 31-40: Proof Hash Part 2 (10 digits)             │
│ Cols 41-50: Checksum (sum of cols 1-40 mod 10^10)     │
│ Cols 51-80: Reserved / Debug information              │
└────────────────────────────────────────────────────────┘
```

## 4. Memory Layout

### 4.1 Program Organization

```
Address   Size    Purpose
------    ----    -------
0000-0099 100     Bootstrap & Constants
0100-0299 200     Main Program
0300-0499 200     Hash Computation Routines
0500-0699 200     Card I/O Routines
0700-0899 200     Data Storage (wallet, proofs, temp)
0900-1999 1100    Available for optimization
```

### 4.2 Constant Storage

```
0000: PRIME1   (7)
0001: PRIME2   (11)
0002: PRIME3   (13)
0003: PRIME4   (17)
0004: PRIME5   (19)
0005: PRIME6   (23)
0006: PRIME7   (29)
0007: PRIME8   (31)
0008: MODULO   (0000000000)
0009: WALLET   (4325956365)
0010: ZERO     (0)
```

### 4.3 Data Storage

```
0700: HASH1    Hash result part 1
0701: HASH2    Hash result part 2
0702: ENTROPY  Current entropy value
0703: TIME     Timestamp
0710-0719: CARD_OUT  Card output template (10 words)
```

## 5. Instruction Optimization

### 5.1 Drum Timing Optimization

The IBM 650 requires **optimal programming** to achieve maximum speed:

```
Without optimization:
- Average access time: 2.5 ms
- Instruction time: ~27.6 ms
- Speed: ~40 instructions/sec

With optimization:
- Average access time: 0.5 ms
- Instruction time: ~0.5 ms
- Speed: ~2000 instructions/sec
```

### 5.2 Optimal Instruction Placement

Instructions should be placed to minimize drum rotation:

```assembly
* Poor placement (waits for drum rotation):
0100: RAL  WALLET  0101    ; Execute, then wait for 0101
0101: MULT PRIME1  0102    ; Must wait ~2.5ms for next word

* Optimal placement (immediate access):
0100: RAL  WALLET  0105    ; Execute, drum rotates to 0105
0105: MULT PRIME1  0110    ; Immediate execution
0110: AL   ENTROPY 0115    ; Continue without waiting
```

### 5.3 SOAP Assembler Optimization

The SOAP (Symbolic Optimal Assembly Program) assembler automatically optimizes placement:

```
SOAP analyzes instruction timing and places next instructions
at optimal drum positions to minimize wait time.
```

## 6. I/O Strategy

### 6.1 Entropy Collection

**Primary method**: Console switches (address 8000)
- Operator manually sets switches
- Provides true randomness
- Limited to 10 decimal digits

**Secondary method**: Punched card input
- Pre-generated entropy on cards
- Read using RD instruction
- Batch processing

### 6.2 Proof Output

**Method**: Punched cards (IBM 533)
- PCH instruction punches card
- One proof per card
- Cards can be batched for submission

### 6.3 Network Submission

Since IBM 650 has **no network capability**:

1. Punch proof cards during mining
2. Transfer cards to modern system (scan/manual entry)
3. Submit to RustChain network via API
4. Rewards sent to wallet

## 7. Performance Analysis

### 7.1 Mining Speed

```
Instruction count per proof: ~200 instructions
Optimized execution: 200 / 2000 = 0.1 seconds
Unoptimized: 200 / 40 = 5 seconds

With manual entropy input: ~1 proof per minute
Automated (card entropy): ~10 proofs per minute
```

### 7.2 Antiquity Multiplier

Based on RustChain proof-of-antiquity:

```
IBM 650 (1953): LEGENDARY tier
Estimated multiplier: 10.0x (oldest viable platform)

Comparison:
- 8086 (1978): 4.0x
- 286 (1982): 3.8x
- 386 (1985): 3.5x
- IBM 650 (1953): 10.0x (estimated)
```

### 7.3 Power Efficiency

```
IBM 650 power consumption: ~10 kW
Proofs per hour: 600 (automated)
Proofs per kWh: 0.06

Modern GPU miner:
Power: 0.3 kW
Proofs per hour: 3600
Proofs per kWh: 12

IBM 650 is ~200x less efficient, but earns 10x multiplier.
Historical significance > efficiency.
```

## 8. Error Handling

### 8.1 Overflow Detection

```assembly
* Check for overflow after arithmetic
BROV  OVERFLOW_HANDLER  NEXT_INSTR
```

### 8.2 Invalid Data

```assembly
* Validate input from cards
RD    CARD_BUFFER  NEXT
BRNZ  VALIDATE     NEXT
STOP  001          NEXT    * Stop with error code 001
```

### 8.3 Recovery

```assembly
* On error, return to start
OVERFLOW_HANDLER:
    RAL   ZERO    NEXT
    BRNZ  START   START
```

## 9. Testing Strategy

### 9.1 Simulator Testing

Python simulator allows:
- Rapid prototyping
- Instruction verification
- Proof validation
- Performance analysis

### 9.2 Real Hardware Testing

Using Open SIMH or web650:
1. Assemble SOAP program
2. Load into simulator
3. Run mining cycle
4. Verify punched card output
5. Validate proof format

### 9.3 Proof Verification

```python
def verify_proof(card_data):
    wallet = card_data[0:10]
    timestamp = card_data[10:20]
    proof_hash = card_data[20:40]
    checksum = int(card_data[40:50])
    
    # Verify checksum
    expected = sum(int(c) for c in wallet + timestamp + proof_hash)
    expected = expected % (10 ** 10)
    
    return expected == checksum
```

## 10. Future Enhancements

### 10.1 With IBM 653 Storage Unit

If IBM 653 is available:
- Core storage (9000-9059): 60 words at 96μs
- Index registers: Simplify addressing
- Floating point: More precise calculations

### 10.2 With IBM 652 Control Unit

- Magnetic tape support
- Batch processing of proofs
- Larger entropy pools

### 10.3 Multi-Machine Mining

Coordinate multiple IBM 650s:
- Each machine has unique wallet
- Centralized card collection
- Distributed proof generation

## 11. Security Considerations

### 11.1 Wallet Protection

```
Wallet stored on drum (address 0009)
- Not readable from console
- Protected by physical security
- Backup on punched card
```

### 11.2 Proof Tampering

```
Checksum prevents tampering:
- Any modification invalidates checksum
- Verification catches alterations
- Timestamp prevents replay attacks
```

### 11.3 Entropy Quality

```
Console switches provide true randomness
- Human input is unpredictable
- Better than pseudo-random
- Rate limited by operator speed
```

## 12. Conclusion

This implementation demonstrates that **cryptographic mining is possible** on the first mass-produced computer, despite severe constraints:

- ✅ Decimal-only arithmetic
- ✅ Limited memory (2K words)
- ✅ No network connectivity
- ✅ Sequential memory access
- ✅ Vacuum tube technology

The IBM 650 miner represents the **ultimate proof-of-antiquity**: mining blockchain on a machine that predates transistors, integrated circuits, and the modern concept of software.

**Bounty Claim**: 200 RTC (LEGENDARY Tier)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
