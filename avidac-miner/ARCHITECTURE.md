# AVIDAC Miner Architecture

This document describes the architecture of the AVIDAC RustChain miner implementation.

## Overview

The AVIDAC miner consists of four main components:

1. **AVIDAC Simulator** - Python implementation of the AVIDAC computer
2. **SHA256 Implementation** - Hash function optimized for 40-bit architecture
3. **Network Bridge** - Microcontroller firmware for internet connectivity
4. **Hardware Fingerprint** - Attestation system for unique hardware identification

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AVIDAC Computer (1953)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   CPU       │  │   Memory     │  │   Paper      │           │
│  │  (IAS Arch) │  │ (Williams    │  │   Tape I/O   │           │
│  │             │  │   Tubes)     │  │              │           │
│  │ - 40-bit AC │  │ - 1024 words │  │ - Input      │           │
│  │ - 40-bit MQ │  │ - 40 bits    │  │ - Output     │           │
│  │ - PC (10b)  │  │ - 5 KB total │  │ - Protocol   │           │
│  └─────────────┘  └──────────────┘  └──────────────┘           │
│         │                │                  │                    │
│         └────────────────┴──────────────────┘                    │
│                          │                                        │
│                   SHA256 Miner Code                              │
│                   (Assembly Language)                            │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                    Paper Tape Interface
                    (Optical Sensor / Punch)
                           │
┌──────────────────────────┴───────────────────────────────────────┐
│                    Microcontroller Bridge                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   ESP32/    │  │   Paper      │  │   Network    │           │
│  │   Arduino   │  │   Tape       │  │   Stack      │           │
│  │   Due       │  │   Protocol   │  │   (WiFi/ETH) │           │
│  │             │  │              │  │              │           │
│  │ - UART I/O  │  │ - STX/ETX    │  │ - HTTPS      │           │
│  │ - GPIO      │  │ - 8-byte     │  │ - TCP/IP     │           │
│  │             │  │   messages   │  │              │           │
│  └─────────────┘  └──────────────┘  └──────────────┘           │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           │ HTTPS
                           │
┌──────────────────────────┴───────────────────────────────────────┐
│                      RustChain Network                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Mining    │  │   Attest-    │  │   Reward     │           │
│  │   Pool      │  │   ation API  │  │   System     │           │
│  └─────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. AVIDAC Simulator

**Purpose**: Emulate AVIDAC hardware for development and testing.

**Key Files**:
- `simulator/cpu.py` - CPU implementation
- `simulator/williams_tube.py` - Memory simulation
- `simulator/paper_tape.py` - I/O simulation
- `simulator/assembler.py` - Cross-assembler
- `simulator/arithmetic.py` - 40-bit math primitives

**Features**:
- Accurate IAS architecture emulation
- Two 20-bit instructions per 40-bit word
- Asynchronous timing model
- Williams tube drift simulation
- Paper tape protocol emulation

**Usage**:
```python
from simulator import AVIDACCPU, WilliamsTubeMemory

# Create CPU with custom memory
memory = WilliamsTubeMemory(enable_drift=True)
cpu = AVIDACCPU(memory=memory)

# Load program
program = [0x0000000000, ...]  # 40-bit words
cpu.load_program(program)

# Run
cpu.run(max_instructions=1000)

# Get results
print(cpu.dump_state())
```

### 2. SHA256 Implementation

**Purpose**: Compute SHA256 hashes on AVIDAC architecture.

**Key Files**:
- `simulator/sha256.py` - SHA256 implementation
- `assembly/sha256_*.asm` - Assembly implementations

**Memory Layout** (160 words total):
```
Address   Component              Size
0x000-0x03F K constants (K0-K63)  64 words
0x040-0x047 Hash state (H0-H7)    8 words
0x048-0x087 Message schedule      64 words
0x088-0x08F Working variables     8 words
0x090-0x09F Input block buffer    16 words
```

**Performance**:
- ~7,100 instructions per hash
- ~100 μs average instruction time
- **~0.71 seconds per hash** (theoretical)
- **~1.4 H/s** hash rate

**Optimization Strategies**:
1. Lookup tables for constants
2. Unrolled loops where possible
3. Minimize memory accesses
4. Use 40-bit words efficiently (32-bit SHA256 + 8 bits spare)

### 3. Network Bridge

**Purpose**: Connect AVIDAC to internet via paper tape interface.

**Hardware**:
- ESP32 or Arduino Due microcontroller
- Optical paper tape reader sensor
- Paper tape punch control circuit
- WiFi or Ethernet connectivity

**Protocol**:
```
Request (Bridge → AVIDAC):
  [STX][NONCE_7][NONCE_6]...[NONCE_0][ETX]
  - STX: 0x02
  - NONCE: 8 bytes (64-bit, big-endian)
  - ETX: 0x03

Response (AVIDAC → Bridge):
  [STX][RESULT_7][RESULT_6]...[RESULT_0][ETX]
  - RESULT: 8 bytes (hash fragment or status)
```

**Firmware Features**:
- HTTPS client for mining pool
- Paper tape protocol handler
- Error handling and retry logic
- Offline mode with share queuing

### 4. Hardware Fingerprint

**Purpose**: Prove unique AVIDAC hardware is running the miner.

**Fingerprint Components**:

1. **Williams Tube Drift Pattern**
   - Each CRT tube has unique phosphor aging
   - Charge leakage patterns vary by location
   - Temperature-dependent behavior

2. **Vacuum Tube Power Signature**
   - ~1,700 tubes create unique power draw
   - Voltage ripple patterns
   - Warm-up curve characteristics

3. **Thermal Profile**
   - Temperature gradients across cabinet
   - Heat dissipation patterns
   - Cooling characteristics

4. **Timing Signature**
   - Asynchronous instruction timing variations
   - Memory access timing variance
   - I/O latency patterns

**Attestation Flow**:
```
1. Extract fingerprint data
2. Sign with hardware signature
3. POST to RustChain attestation API
4. Receive verification token
5. Include token in mining submissions
```

## Data Flow

### Mining Operation

```
1. Bridge fetches work from mining pool
   - Receives: target, nonce_range, block_header_template

2. Bridge sends nonce to AVIDAC via paper tape
   - Format: [STX][nonce_bytes][ETX]

3. AVIDAC computes SHA256(block_header || nonce)
   - Uses assembly implementation
   - ~1-2 seconds per hash

4. AVIDAC sends result to Bridge
   - Format: [STX][hash_bytes][ETX]

5. Bridge checks if hash < target
   - If yes: submit share to pool
   - If no: increment nonce, repeat

6. Bridge submits valid shares
   - Includes hardware fingerprint
   - Receives reward credit
```

### Attestation Flow

```
1. On startup, extract hardware fingerprint
   - Williams tube drift pattern
   - Power signature
   - Thermal profile

2. Generate attestation report
   {
     "hardware_type": "avidac",
     "year": 1953,
     "location": "argonne_national_laboratory",
     "fingerprint": {...},
     "timestamp": "2026-03-13T19:00:00Z"
   }

3. Submit to RustChain API
   POST /api/miners/attest

4. Receive verification token
   {
     "verified": true,
     "multiplier": 5.0,
     "token": "abc123..."
   }

5. Include token in mining submissions
```

## Memory Map

### AVIDAC Memory (1024 words × 40 bits)

```
Address Range   Usage                    Size
0x000-0x0FF     Boot loader              256 words
0x100-0x1FF     SHA256 code              256 words
0x200-0x23F     K constants              64 words
0x240-0x247     Hash state H0-H7         8 words
0x248-0x287     Message schedule W0-W63  64 words
0x288-0x28F     Working variables a-h    8 words
0x290-0x29F     Input block buffer       16 words
0x2A0-0x2FF     Nonce space              96 words
0x300-0x3FF     Stack & temporaries      256 words
```

**Total**: 1024 words (100% utilized)

## Performance Analysis

### Instruction Count per SHA256 Hash

| Operation | Instructions | Notes |
|-----------|-------------|-------|
| Message schedule (W0-W63) | ~1,000 | 48 extensions × ~20 instr |
| Round function (64 rounds) | ~5,760 | 64 × ~90 instr/round |
| Initialization | ~100 | Load constants |
| Finalization | ~100 | Add working vars to state |
| I/O overhead | ~140 | Paper tape read/write |
| **Total** | **~7,100** | |

### Timing Analysis

| Instruction Type | Cycles | Time (μs) | Frequency |
|-----------------|--------|-----------|-----------|
| ADD/SUB | 5 | 62 | 40% |
| LD/ST | 3 | 40 | 30% |
| JMP/JZ/JN | 2 | 25 | 15% |
| MUL | 50 | 713 | 5% |
| AND/OR | 3 | 40 | 7% |
| IN/OUT | 100 | 1500 | 3% |
| **Weighted Average** | **~8.4** | **~100** | |

**Total time per hash**: 7,100 × 100 μs = 710,000 μs = **0.71 seconds**

**Hash rate**: 1 / 0.71 = **1.4 H/s**

**Realistic (with errors, refresh)**: **0.5-1.0 H/s**

## Error Handling

### Williams Tube Errors

- **Detection**: Parity or checksum validation
- **Recovery**: Retry operation, use error correction
- **Prevention**: Frequent refresh (~100 Hz)

### Paper Tape Errors

- **Detection**: STX/ETX framing, checksums
- **Recovery**: Retry read, request resend
- **Prevention**: Error-correcting codes

### Network Errors

- **Detection**: HTTPS timeout, connection refused
- **Recovery**: Exponential backoff, offline mode
- **Prevention**: Connection pooling, keep-alive

## Security Considerations

### Hardware Fingerprint Security

- Fingerprint must be:
  - Unique to specific AVIDAC hardware
  - Difficult to spoof
  - Stable over time
  - Verifiable by network

### Attestation Security

- Signed attestations prevent replay attacks
- Timestamps prevent old fingerprint reuse
- Network verification ensures authenticity

### Mining Security

- Nonce must be unique per hash attempt
- Results must be verifiable
- Share submission must be authenticated

## Development Workflow

### Simulator Development

1. Implement arithmetic primitives
2. Build CPU simulator
3. Add memory simulation
4. Implement I/O
5. Create assembler
6. Write test suite
7. Validate against specifications

### SHA256 Development

1. Implement in Python for reference
2. Validate against NIST test vectors
3. Translate to AVIDAC assembly
4. Test in simulator
5. Optimize for performance
6. Validate on hardware (if available)

### Bridge Development

1. Design paper tape protocol
2. Implement firmware
3. Test with simulator
4. Build hardware interface
5. Test with real AVIDAC (if available)

## Testing Strategy

### Unit Tests

- Arithmetic operations
- Individual CPU instructions
- Memory read/write
- Paper tape encoding/decoding
- SHA256 test vectors

### Integration Tests

- Full SHA256 computation
- Paper tape protocol end-to-end
- Network bridge communication
- Attestation flow

### Performance Tests

- Hash rate measurement
- Memory access patterns
- Instruction timing
- Error rate under stress

## Future Enhancements

### Performance Optimizations

- Hand-tuned assembly for critical paths
- Lookup tables for expensive operations
- Pipeline optimization (if hardware allows)

### Hardware Improvements

- Faster paper tape reader
- Solid-state memory interface (hybrid mode)
- Multiple AVIDAC machines (distributed mining)

### Feature Additions

- SHA256d (double SHA256) support
- Stratum protocol support
- Pool failover
- Statistics reporting

## References

- [IAS Architecture Paper (von Neumann, 1946)](https://www.cs.princeton.edu/courses/archive/spr06/cos423/papers/vonNeumann_1946.pdf)
- [NIST FIPS 180-4: Secure Hash Standard](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)
- [Williams Tube Memory Technical Details](https://www.computerhistory.org/collections/catalog/102643906)
- [Argonne National Laboratory History](https://www.anl.gov/about/history)
