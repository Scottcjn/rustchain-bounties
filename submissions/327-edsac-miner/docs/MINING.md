# EDSAC Mining Algorithm

## Conceptual Framework

### Modern Mining vs EDSAC Mining

| Aspect | Modern (SHA-256) | EDSAC (Simplified) |
|--------|------------------|-------------------|
| Hash Function | SHA-256 | Additive checksum |
| Word Size | 32/64 bits | 17 bits |
| Operations | Bitwise (AND, XOR, etc.) | Arithmetic (+, -, ×) |
| Target | 256-bit number | 17-bit number |
| Hash Rate | 10¹² H/s | ~500 H/s |

## Simplified Proof-of-Work

### Algorithm Definition

```
Given:
  - block_header: 17-bit value representing block data
  - target: 17-bit difficulty threshold
  - nonce: 17-bit counter (0 to 16383)

Find nonce such that:
  hash(block_header, nonce) < target

Where:
  hash(h, n) = ((h × 7919) + (n × 104729)) mod 16384
  
(7919 and 104729 are prime numbers for better distribution)
```

### Why This Works

1. **Deterministic:** Same input → same output
2. **Uniform distribution:** Prime multiplication spreads values
3. **Verifiable:** Anyone can check the result
4. **Adjustable difficulty:** Change target threshold

### Difficulty Levels

```
Target = 16384 / difficulty

Difficulty 1:  target = 16384 (any nonce works)
Difficulty 2:  target = 8192  (50% of nonces work)
Difficulty 10: target = 1638  (10% of nonces work)
Difficulty 100: target = 164  (1% of nonces work)
```

## EDSAC Assembly Implementation

### Memory Layout

```
Address  Content
0-19     Program code
20       Block header (input)
21       Target value
22       Current nonce
23       Hash result
24-25    Constants (primes)
26       Temporary storage
```

### Pseudocode

```
START:
  Z           ; Clear accumulator
  T 22        ; nonce = 0
  
LOOP:
  L 20        ; A = block_header
  M 24        ; A = header × 7919
  T 26        ; temp = header × 7919
  
  L 22        ; A = nonce
  M 25        ; A = nonce × 104729
  A 26        ; A = (header×7919) + (nonce×104729)
  
  ; Modulo 16384 (keep lower 14 bits)
  ; EDSAC doesn't have AND, so we use repeated subtraction
  ; For simplicity, we'll use the natural overflow
  
  T 23        ; hash = result
  S 21        ; A = hash - target
  G FOUND     ; If hash < target, jump to FOUND
  
  L 22        ; A = nonce
  A CONST1    ; A = nonce + 1
  T 22        ; nonce = nonce + 1
  
  ; Check for overflow (nonce > 16383)
  S CONST_MAX
  G LOOP      ; If nonce <= max, continue
  
  ; No solution found (shouldn't happen with proper difficulty)
  H           ; Halt with error
  
FOUND:
  O 22        ; Output successful nonce
  H           ; Halt with success
```

### Actual EDSAC Code (miner.e)

See `simulator/miner.e` for the complete assembly listing.

## Python Reference Implementation

### Hash Function

```python
def edsac_hash(header: int, nonce: int) -> int:
    """
    Compute simplified hash for EDSAC miner.
    
    Args:
        header: 17-bit block header value
        nonce: 17-bit nonce value
    
    Returns:
        17-bit hash value
    """
    PRIME1 = 7919
    PRIME2 = 104729
    MODULUS = 16384  # 2^14
    
    result = (header * PRIME1 + nonce * PRIME2) % MODULUS
    return result
```

### Mining Loop

```python
def mine(header: int, target: int) -> tuple[int, int]:
    """
    Find a valid nonce for the given header and target.
    
    Args:
        header: Block header (17-bit)
        target: Difficulty target (17-bit)
    
    Returns:
        Tuple of (nonce, hash) if found, (-1, -1) if not
    """
    for nonce in range(16384):
        h = edsac_hash(header, nonce)
        if h < target:
            return nonce, h
    
    return -1, -1  # No solution
```

## Example Run

### Input

```
Block Header: 1234 (decimal)
Target: 1638 (difficulty 10)
```

### Execution Trace

```
Nonce 0:  hash = (1234×7919 + 0×104729) mod 16384 = 9766 → 9766 ≥ 1638 ❌
Nonce 1:  hash = (1234×7919 + 1×104729) mod 16384 = 1587 → 1587 < 1638 ✅

FOUND! Nonce = 1, Hash = 1587
```

### Output

```
MINING SUCCESSFUL
Block:  1234
Nonce:  1
Hash:   1587
Target: 1638
```

## Verification

### Proof Verification

Anyone can verify the mining result:

```python
def verify(header: int, nonce: int, target: int) -> bool:
    """Verify a mining solution."""
    h = edsac_hash(header, nonce)
    return h < target
```

### Example Verification

```
Header: 1234
Nonce:  1
Target: 1638

hash(1234, 1) = 1587
1587 < 1638 → VALID ✓
```

## Performance Estimates

### Theoretical Maximum

- EDSAC cycle time: ~1.5ms per instruction
- Mining loop: ~20 instructions per nonce
- Time per nonce: ~30ms
- Hash rate: ~33 hashes/second

### Realistic Expectations

- Memory access delays
- Paper tape I/O overhead
- Error checking

**Realistic: ~10-20 hashes/second**

### Time to Find Nonce

| Difficulty | Expected Nonces | Time (at 20 H/s) |
|------------|----------------|------------------|
| 1 | 1 | 0.05s |
| 10 | 10 | 0.5s |
| 100 | 100 | 5s |
| 1000 | 1000 | 50s |
| 10000 | 10000 | 500s (~8 min) |

## Limitations and Notes

1. **Not real cryptocurrency mining** - This is educational
2. **Simplified hash function** - Not cryptographically secure
3. **17-bit security** - Trivially breakable
4. **Historical demonstration** - Shows concept, not practical

## Future Extensions

If we had more time/memory:

1. **Multi-word arithmetic** - Support larger numbers
2. **Better hash function** - More complex mixing
3. **Block validation** - Check previous block hash
4. **Network protocol** - Paper tape message passing!

---

*"This is the world's slowest miner, running on the world's first practical computer."*
