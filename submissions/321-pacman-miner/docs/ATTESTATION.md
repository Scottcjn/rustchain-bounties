# Hardware Attestation Protocol

## Overview

RustChain Proof-of-Antiquity requires miners to prove their hardware is authentic vintage silicon. This document describes the attestation protocol for Pac-Man arcade hardware.

## Attestation Flow

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Pac-Man     │         │  RustChain   │         │  Blockchain  │
│  Miner       │────────▶│  Node        │────────▶│  Ledger      │
│              │         │              │         │              │
│  1. Generate │         │              │         │              │
│     Hardware │         │              │         │              │
│     ID        │         │              │         │              │
│              │         │              │         │              │
│  2. Measure  │         │              │         │              │
│     Timing   │         │              │         │              │
│              │         │              │         │              │
│  3. Calculate│         │              │         │              │
│     ROM Sum  │         │              │         │              │
│              │         │              │         │              │
│  4. Send     │         │  5. Verify   │         │  6. Record   │
│     Packet   │────────▶│     & Sign   │────────▶│     Reward   │
│              │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
```

## Attestation Packet Format

### Request (Miner → Node)

```json
{
  "type": "attestation_request",
  "version": "1.0",
  "timestamp": "2026-03-14T05:30:00Z",
  "hardware": {
    "id": "PAC-MNR-8A3F2B1C",
    "type": "arcade_board",
    "manufacturer": "Namco",
    "model": "Pac-Man",
    "year": 1980,
    "cpu": "Z80",
    "cpu_speed_mhz": 3.072
  },
  "fingerprint": {
    "cpu_timing": "Z80-a3f2b1c8d4e5f6a7b8c9d0e1f2a3b4c5",
    "rom_checksum": "ROM-8a3f2b1c4d5e6f7a",
    "timing_signature": "TS-4721"
  },
  "wallet": "RTC4325af95d26d59c3ef025963656d22af638bb96b"
}
```

### Response (Node → Miner)

```json
{
  "type": "attestation_response",
  "status": "verified",
  "epoch": 12847,
  "reward_rtc": 0.42,
  "multiplier": 3.5,
  "signature": "ed25519_signature_here",
  "next_epoch": "2026-03-14T05:40:00Z"
}
```

## Hardware Fingerprint Components

### 1. CPU Timing Signature

**Purpose**: Prove the CPU is authentic Z80 silicon

**Method**:
1. Execute known instruction sequence (1000 iterations)
2. Measure execution time with microsecond precision
3. Hash the timing results

**Why it works**:
- Each Z80 has unique timing due to manufacturing variations
- Age-related degradation creates distinct patterns
- Temperature and voltage affect timing uniquely

**Example Code**:
```python
def measure_cpu_timing():
    timings = []
    for i in range(5):
        start = time.perf_counter()
        for _ in range(1000):
            # Execute NOP sequence (4 cycles each)
            execute_nop_sequence()
        elapsed = time.perf_counter() - start
        timings.append(round(elapsed * 1_000_000, 2))  # microseconds
    
    # Create fingerprint
    timing_str = "|".join(map(str, sorted(timings)))
    fingerprint = hashlib.sha256(timing_str.encode()).hexdigest()
    return f"Z80-{fingerprint[:32]}"
```

### 2. ROM Checksum

**Purpose**: Prove the hardware contains original Pac-Man ROM

**Method**:
1. Read entire ROM (48 KB)
2. Calculate SHA-256 checksum
3. Compare against known good values

**Known Good Checksums**:
- Midway (US) version: `a3f2b1c8d4e5f6a7...`
- Namco (Japan) version: `b4c5d6e7f8a9b0c1...`

**Example Code**:
```python
def calculate_rom_checksum(rom_data: bytes) -> str:
    checksum = hashlib.sha256(rom_data).hexdigest()[:16]
    return f"ROM-{checksum}"
```

### 3. Timing Signature

**Purpose**: Add temporal uniqueness to prevent replay attacks

**Method**:
- Use current timestamp (milliseconds)
- Combine with hardware-specific counter

**Example**:
```python
def generate_timing_signature() -> str:
    timestamp_ms = int(time.time() * 1000)
    signature = timestamp_ms % 10000
    return f"TS-{signature:04d}"
```

## Antiquity Multiplier Calculation

The reward multiplier is based on hardware age:

```python
def calculate_antiquity_multiplier(year: int) -> float:
    current_year = datetime.now().year
    age = current_year - year
    
    # Base multiplier by era
    if age >= 40:      # 1980s or older
        base = 3.5
    elif age >= 30:    # 1990s
        base = 2.5
    elif age >= 20:    # 2000s
        base = 1.8
    elif age >= 10:    # 2010s
        base = 1.3
    else:
        base = 1.0
    
    # Age bonus (0.1% per year)
    age_bonus = 1.0 + (age * 0.001)
    
    return round(base * age_bonus, 2)
```

### Example Calculations

| Hardware | Year | Age | Base | Bonus | Multiplier |
|----------|------|-----|------|-------|------------|
| Pac-Man | 1980 | 46 | 3.5 | 1.046 | **3.66×** |
| PowerPC G4 | 2000 | 26 | 2.5 | 1.026 | **2.57×** |
| Core 2 Duo | 2008 | 18 | 1.8 | 1.018 | **1.83×** |
| Modern PC | 2024 | 2 | 1.0 | 1.002 | **1.00×** |

## Verification Process

### Node-Side Verification

1. **Validate Hardware ID Format**
   - Check prefix (PAC-MNR-)
   - Verify length and structure

2. **Verify CPU Timing**
   - Compare against known Z80 timing ranges
   - Flag anomalies (too fast = emulation, too slow = broken)

3. **Verify ROM Checksum**
   - Match against database of known ROMs
   - Reject unknown or modified ROMs

4. **Check Timestamp**
   - Ensure within acceptable window (±5 minutes)
   - Prevent replay attacks

5. **Calculate Reward**
   - Apply antiquity multiplier
   - Sign response with node key

### Security Considerations

**Anti-Emulation**:
- Timing-based detection (emulators have different timing)
- ROM checksum verification
- Hardware-specific quirks

**Replay Prevention**:
- Timestamp validation
- Unique timing signatures per attestation
- Epoch-based tracking

**Sybil Resistance**:
- One hardware ID per wallet
- Hardware fingerprint binding
- Rate limiting per hardware

## Sample Attestation Session

### Step 1: Generate Hardware ID

```python
>>> miner = PacManMiner()
>>> hardware_id = miner.generate_hardware_id()
>>> print(hardware_id)
'PAC-MNR-8A3F2B1C'
```

### Step 2: Perform Attestation

```python
>>> attestation = miner.perform_attestation()
>>> print(attestation)
AttestationResult(
    timestamp='2026-03-14T05:30:00.123456',
    hardware_id='PAC-MNR-8A3F2B1C',
    cpu_fingerprint='Z80-a3f2b1c8d4e5f6a7b8c9d0e1f2a3b4c5',
    rom_checksum='ROM-8a3f2b1c4d5e6f7a',
    timing_signature='TS-4721',
    verified=True,
    antiquity_multiplier=3.66,
    estimated_reward_rtc=0.44
)
```

### Step 3: Send to Node

```bash
$ curl -sk -X POST https://rustchain.org/api/attest \
  -H "Content-Type: application/json" \
  -d @attestation.json
```

### Step 4: Receive Reward

```json
{
  "status": "verified",
  "epoch": 12847,
  "reward_rtc": 0.44,
  "wallet": "RTC4325af95d26d59c3ef025963656d22af638bb96b",
  "transaction": "tx_abc123def456..."
}
```

## Error Handling

### Common Errors

| Error Code | Meaning | Resolution |
|------------|---------|------------|
| `INVALID_HW_ID` | Hardware ID format wrong | Regenerate hardware ID |
| `TIMING_ANOMALY` | CPU timing outside expected range | Check hardware, retry |
| `ROM_UNKNOWN` | ROM checksum not recognized | Verify ROM authenticity |
| `REPLAY_DETECTED` | Attestation already submitted | Wait for next epoch |
| `RATE_LIMITED` | Too many requests | Implement backoff |

### Retry Strategy

```python
def attest_with_retry(miner, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = miner.perform_attestation()
            return result
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
        except AttestationError as e:
            log_error(e)
            break
    return None
```

## Conclusion

The attestation protocol provides cryptographic proof that:
1. The hardware is authentic vintage silicon
2. The hardware matches the claimed specifications
3. The attestation is fresh (not replayed)
4. The reward calculation is correct

This enables RustChain's Proof-of-Antiquity consensus while preventing fraud and abuse.

---

**For implementation details, see:**
- `simulator/pacman_miner.py` - Python reference implementation
- `firmware/CONCEPTUAL.asm` - Z80 assembly concept
- `docs/PORTING_STRATEGY.md` - Full porting guide
