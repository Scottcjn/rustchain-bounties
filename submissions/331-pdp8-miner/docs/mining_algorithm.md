# RustChain Mining Algorithm for PDP-8

## Overview

The RustChain mining algorithm for PDP-8 is designed around the severe constraints of 1965 hardware while maintaining the core principles of hardware attestation and proof-of-antiquity.

## Design Goals

1. **Minimal Memory**: < 2K words for code + data
2. **No Complex Math**: Avoid SHA-256, use PDP-8 native operations
3. **Hardware-Dependent**: Leverage unique PDP-8 characteristics
4. **Offline Capable**: Store attestations on paper tape

## Attestation Flow

```
┌─────────────────┐
│  Start Epoch    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Collect Entropy │───► Core memory timing
│ from Hardware   │    Interval timer
└────────┬────────┘    RTC low bits
         │
         ▼
┌─────────────────┐
│  Generate       │───► XOR all entropy
│  Fingerprint    │    Rotate and mix
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create         │───► Epoch number
│  Attestation    │    Fingerprint
│  Record         │    Timestamp (simplified)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Submit or      │───► Network (if available)
│  Store Locally  │    Paper tape (offline)
└─────────────────┘
```

## Entropy Sources

### 1. Core Memory Timing

Magnetic core memory has slight timing variations:

```
Access Time: 1.5μs nominal
Variance: ±20ns due to:
  - Temperature variations
  - Core magnetization history
  - Power supply ripple
  - Address decode delays
```

**Collection Method**:
```assembly
ENTROPY_LOOP,
    IOT     6020        / Read timer
    DCA     TEMP
    / Access memory at varying addresses
    TAD     I ADDR_PTR
    DCA     DUMMY
    / Measure timing (simulated)
    IOT     6020
    DCA     I ENTROPY_PTR
    ...
```

### 2. Interval Timer

PDP-8 interval timer drift provides entropy:

```
Timer Frequency: ~60 Hz
Drift: ±0.1% due to temperature
Low bits: Unpredictable
```

### 3. Hardware Fingerprint

Each PDP-8 has unique characteristics:

- Core memory timing pattern
- Instruction timing variations
- Power-on state of flip-flops
- I/O device response times

## Fingerprint Algorithm

```python
def generate_fingerprint(entropy_pool):
    fingerprint = 0
    
    # XOR all entropy values
    for entropy in entropy_pool:
        fingerprint ^= entropy
    
    # Mix with rotations
    for i in range(8):
        fingerprint = ((fingerprint << 3) | 
                      (fingerprint >> 9)) & 0xFFF
    
    return fingerprint
```

**Assembly Implementation**:
```assembly
GEN_FINGERPRINT,
    0
    CLA
    CLL
    
    / Initialize with first entropy
    TAD     ENTROPY
    DCA     FINGERPRINT
    
    / XOR and rotate loop
    TAD     I TWO_FOUR
    DCA     COUNTER
    
MIX_LOOP,
    TAD     I ENTROPY_PTR
    XOR     FINGERPRINT
    DCA     FINGERPRINT
    
    RAL
    RAL
    RAL         / Rotate left 3
    
    ISZ     COUNTER
    JMP     MIX_LOOP
    
    JMP     I GEN_FINGERPRINT
```

## Attestation Record Format

```
Word  Offset  Description
----- ------  -----------
ATTEST+0   0   Epoch number (12 bits)
ATTEST+1   1   Fingerprint (12 bits)
ATTEST+2   2   Hash low (12 bits)
ATTEST+3   3   Hash high (12 bits)
ATTEST+4   4   Timestamp hour (8 bits) + minute (4 bits)
ATTEST+5   5   Timestamp second (12 bits)
ATTEST+6   6   Multiplier (encoded, 12 bits)
ATTEST+7   7   Checksum (12 bits)
```

### Hash Generation

Simplified hash for PDP-8 constraints:

```python
def generate_hash(fingerprint, entropy_pool, epoch):
    hash_val = fingerprint ^ epoch
    
    for i, entropy in enumerate(entropy_pool):
        # Rotate and XOR
        hash_val = ((hash_val << 5) | (hash_val >> 7)) & 0xFFF
        hash_val ^= entropy
        hash_val ^= (i * 123) & 0xFFF
    
    return hash_val
```

## Antiquity Multiplier

The PDP-8 receives the **highest multiplier** due to its 1965 release date:

| System | Year | Multiplier | Tier |
|--------|------|------------|------|
| **PDP-8** | **1965** | **5.0x** | **LEGENDARY** 🔥 |
| PDP-8/E | 1969 | 4.8x | LEGENDARY |
| Intersil 6100 | 1975 | 4.5x | LEGENDARY |
| 8086 | 1978 | 4.0x | EPIC |
| 286 | 1982 | 3.8x | EPIC |
| 386 | 1985 | 3.5x | RARE |
| 486 | 1989 | 3.0x | RARE |
| Pentium | 1993 | 2.5x | UNCOMMON |

**Calculation**:
```
Base Reward × Antiquity Multiplier = Final Reward

Example:
10 RTC × 5.0x = 50 RTC per epoch
```

## Epoch Timing

Standard epoch: **10 minutes**

On PDP-8, this is measured using:
- Interval timer interrupts
- Real-time clock (if equipped)
- Software delay loops (calibrated)

**Delay Loop Example**:
```assembly
/ Approximate 10-minute delay
/ Calibrated for 1.5μs memory cycle

DELAY_10MIN,
    TAD     I DELAY_COUNT
    DCA     TEMP
    
OUTER_LOOP,
    TAD     I INNER_COUNT
    DCA     TEMP2
    
INNER_LOOP,
    ISZ     TEMP2
    JMP     INNER_LOOP
    
    ISZ     TEMP
    JMP     OUTER_LOOP
    
    JMP     I DELAY_10MIN
```

## Offline Mode

For PDP-8 systems without networking:

1. **Generate attestation** normally
2. **Punch to paper tape** in binary format
3. **Transfer** to modern system via:
   - Paper tape reader
   - Manual transcription (octal dump)
   - Photograph and OCR

**Paper Tape Format**:
```
Leader: 80 nulls (0x00)
Header: "RUSTCHAIN ATTESTATION"
Data: Binary attestation record
Checksum: 12-bit XOR checksum
Trailer: 80 nulls
```

## Security Considerations

### Limitations

1. **No Cryptographic Security**: PDP-8 cannot run SHA-256
2. **Deterministic**: Same hardware produces same fingerprint
3. **Limited Entropy**: Only 12 bits per sample

### Mitigations

1. **Hardware Dependency**: Requires physical PDP-8
2. **Time-Bound**: Attestations include timestamp
3. **Network Verification**: Cross-check with other miners
4. **Antiquity Bonus**: High multiplier justifies relaxed security

## Performance

**Memory Usage**:
- Code: ~500 words
- Data: ~100 words
- Entropy Pool: 24 words
- Attestation Buffer: 24 words
- **Total**: ~650 words (16% of memory)

**Execution Time**:
- Entropy Collection: ~1 second
- Fingerprint Generation: ~100ms
- Attestation Creation: ~200ms
- **Total per Epoch**: ~1.3 seconds (excluding 10-min wait)

## Example Output

```
============================================================
RustChain PDP-8 Miner (1965)
============================================================
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
Memory: 4096 words × 12 bits = 6144 bytes
Antiquity Multiplier: 5.0x (LEGENDARY)
============================================================

[Epoch 1/10]
Collecting hardware entropy...
  Timestamp: 2026-03-14T03:22:00
  Hardware FP: 3A7
  Attestation: F2C
  Multiplier: 5.0x
  ✓ Attestation submitted

[Epoch 2/10]
...

============================================================
Mining complete! 10 epochs submitted.
Total attestations: 10
============================================================
```

## Future Enhancements

1. **EAE Support**: Use hardware multiply if available
2. **DECtape Storage**: Persistent wallet/attestation storage
3. **Network Stack**: Watt-32 port for direct submission
4. **Multi-System**: Distributed mining across multiple PDP-8s

---

**For RustChain Bounty #394**
Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
