# IBM 705 Virtual Tape Mining Protocol

## Overview

This document specifies the **virtual tape protocol** used to communicate between the modern RustChain network and the IBM 705 (1954) miner.

Since the IBM 705 predates computer networks by 15+ years, we use a **simulated 7-track magnetic tape** interface for all communication.

## Architecture

```
┌──────────────────┐         ┌──────────────────┐
│  RustChain       │         │  IBM 705         │
│  Network         │         │  Miner           │
│  (Modern)        │         │  (1954)          │
│                  │         │                  │
│ - HTTP API       │         │ - Assembly Code  │
│ - Block Fetch    │◄───────►│ - Hash Compute   │
│ - Result Submit  │  Tape   │ - Output Write   │
└──────────────────┘         └──────────────────┘
```

## Tape Format

### Input Tape (Network → IBM 705)

**Block Header Record** (80 characters):
```
Offset  Length  Field           Format
00-09   10      Block Hash      Numeric (first 10 digits of SHA256)
10-19   10      Difficulty      Numeric target threshold
20-29   10      Timestamp       Unix timestamp (last 10 digits)
30-39   10      Previous Hash   Numeric (first 10 digits)
40-79   40      Reserved        Spaces
```

**Example Input Record**:
```
1234567890999999999917103456780000000000
```

### Output Tape (IBM 705 → Network)

**Mining Result Record** (20 characters):
```
Offset  Length  Field           Format
00-09   10      Nonce           Found nonce value
10-19   10      Hash Result     Computed hash (simplified)
```

**Example Output Record**:
```
00000012340123456789
```

## Protocol Flow

### 1. Block Fetch Phase

```python
# Modern layer fetches block from RustChain network
block = fetch_block_from_network()

# Extract numeric representation
block_hash = int(block.hash[:10], 16)
difficulty = block.difficulty

# Format input record
input_record = f"{block_hash:010d}{difficulty:010d}{timestamp:010d}{' ' * 40}"

# Load onto virtual tape
io.load_tape([input_record])
```

### 2. Mining Phase

```asm
* IBM 705 reads block data from tape
         RD   0100         * Read input record to memory

* Mining loop
MINING:  LD   0110         * Load nonce
         AD   0120         * Increment
         ST   0110         * Store back
         
         * Compute hash
         LD   0100         * Load block hash
         MU   0110         * Multiply by nonce
         DV   0130         * Modulo prime
         
         * Check difficulty
         CO   0140         * Compare to target
         JF   FOUND        * Success if below target
         J    MINING       * Continue mining

FOUND:   WR   0110         * Write result
         SW   0000         * Halt
```

### 3. Result Submission Phase

```python
# Read result from output tape
output = io.get_output()
if output:
    nonce = int(output[0][:10])
    hash_result = output[0][10:20]
    
    # Verify solution
    if verify_hash(block, nonce, hash_result):
        # Submit to network
        submit_result(block.id, nonce)
```

## Message Types

### Type 1: Block Header (Input)

**Purpose**: Deliver mining work to IBM 705

**Format**:
```
Record 1: Block header data (80 chars)
  [0-9]   : Block hash (numeric)
  [10-19] : Difficulty target
  [20-29] : Timestamp
  [30-39] : Previous block hash
  [40-79] : Reserved (spaces)
```

**Example**:
```
7378799299999999999917103456780000000000
```

### Type 2: Mining Result (Output)

**Purpose**: Submit found solution to network

**Format**:
```
Record 1: Mining result (20 chars)
  [0-9]   : Nonce value
  [10-19] : Hash result
```

**Example**:
```
00000012340123456789
```

### Type 3: Status Report (Optional)

**Purpose**: Report mining statistics

**Format**:
```
Record 1: Status (40 chars)
  [0-9]   : Nonces attempted
  [10-19] : Instructions executed
  [20-29] : Cycles elapsed
  [30-39] : Status code
```

**Status Codes**:
- `0000000000`: Normal operation
- `0000000001`: Solution found
- `0000000002`: Error (check indicator set)
- `0000000003`: Overflow detected

## Error Handling

### Tape Errors

| Error | Code | Recovery |
|-------|------|----------|
| End of tape | EOT | Rewind and retry |
| Read error | RERR | Reload tape |
| Write error | WERR | Clear output, retry |

### CPU Errors

| Error | Indicator | Recovery |
|-------|-----------|----------|
| Divide by zero | Check | Reset and reload |
| Overflow | Overflow | Use smaller fields |
| Memory violation | Check | Check addresses |

### Network Errors

| Error | Recovery |
|-------|----------|
| Fetch timeout | Retry with exponential backoff |
| Submit rejected | Verify hash and retry |
| Connection lost | Queue results locally |

## Timing Considerations

### IBM 705 Performance

| Metric | Value |
|--------|-------|
| Instruction time | 24 μs |
| Memory cycle | 12 μs |
| Tape read | ~10 ms per record |
| Tape write | ~10 ms per record |

### Expected Hash Rate

```
Instructions per hash: ~15
Time per hash: 15 × 24 μs = 360 μs
Hash rate: ~2,777 H/s (theoretical max)

Realistic (with I/O): ~0.001 H/s
```

**Note**: Performance is intentionally limited to match historical accuracy.

## Security Considerations

### Proof Verification

The modern layer **must verify** all IBM 705 submissions:

```python
def verify_solution(block, nonce, hash_result):
    # Recompute hash with found nonce
    expected_hash = compute_hash(block.header, nonce)
    
    # Verify hash matches
    if hash_result != expected_hash:
        return False
    
    # Verify hash meets difficulty
    if int(hash_result) >= block.difficulty:
        return False
    
    return True
```

### Replay Prevention

- Each block header includes unique timestamp
- Nonce must be unique per block
- Results include block hash for binding

## Implementation Example

### Python Bridge

```python
from ibm705_simulator import IBM705CPU

class MiningBridge:
    def __init__(self):
        self.cpu = IBM705CPU()
        self.load_mining_program()
    
    def mine_block(self, block_header):
        # Prepare input
        input_data = self.format_block_header(block_header)
        self.cpu.io.load_tape([input_data])
        
        # Run mining
        self.cpu.run(max_instructions=100000)
        
        # Get result
        output = self.cpu.io.get_output()
        if output:
            return self.parse_result(output[0])
        return None
    
    def format_block_header(self, block):
        hash_num = int(block.hash[:10], 16)
        return f"{hash_num:010d}{block.difficulty:010d}{'0'*60}"
    
    def parse_result(self, record):
        return {
            'nonce': int(record[0:10]),
            'hash': record[10:20]
        }
```

## Testing

### Test Vector 1: Easy Difficulty

**Input**:
```
Block Hash:     1234567890
Difficulty:     9999999999
Timestamp:      1710345678
```

**Expected**:
```
Nonce:          0000000001
Hash Result:    1234567890
```

### Test Vector 2: Medium Difficulty

**Input**:
```
Block Hash:     9876543210
Difficulty:     5000000000
Timestamp:      1710345678
```

**Expected**:
```
Nonce:          0000000005
Hash Result:    <5000000000
```

## Future Extensions

### Planned Enhancements

1. **Multi-block mining**: Queue multiple blocks on tape
2. **Checkpointing**: Save/restore mining state
3. **Statistics reporting**: Track hash rate, power usage
4. **Remote monitoring**: Web interface for mining status

### Compatibility

This protocol is designed for:
- ✅ IBM 705 Simulator (Python)
- ✅ IBM 705 Hardware (if available)
- ⏳ IBM 7080 (successor, minor modifications needed)

---

**For RustChain Bounty #356**  
Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

**Version**: 1.0  
**Date**: March 13, 2026
