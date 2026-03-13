# RustChain Miner for LEO III (1961)

> **LEGENDARY TIER BOUNTY** - Port Miner to LEO III (200 RTC / $20)

## Overview

This project presents a **conceptual port** of the RustChain miner to the **LEO III** (Lyons Electronic Office III), the world's first mass-produced commercial computer (1961).

### ⚠️ Important Note

This is a **proof-of-concept / educational implementation**. While the LEO III was far more advanced than its predecessors, its hardware limitations still make running a modern blockchain miner impractical:

- **Memory**: ~8-16 KB ferrite core memory (varies by configuration)
- **Cycle Time**: 13.2 μs (approximately 75 KHz effective clock)
- **Solid-state**: Transistor-based (first generation of solid-state computers)
- **No networking** - predates Ethernet by over a decade
- **32-bit word architecture** with unique instruction encoding
- **Master Program OS**: Multi-tasking operating system supporting up to 12 concurrent programs

However, this implementation demonstrates the **spirit of Proof-of-Antiquity** by showing how the core concepts could be expressed on the first mass-produced business computer.

## LEO III Architecture

### Hardware Specifications

| Component | Specification |
|-----------|---------------|
| **Generation** | First mass-produced commercial computer |
| **Released** | 1961 |
| **Technology** | Solid-state (transistors) |
| **Cycle Time** | 13.2 μs (~75,000 instructions/sec theoretical) |
| **Memory** | Ferrite core memory, 8-16 KB typical |
| **Word Size** | 32 bits (data), variable instruction length |
| **Storage** | Magnetic tape units, paper tape, punched cards |
| **I/O** | Paper tape reader/punch, card reader/punch, line printer |
| **OS** | Master Program (multi-tasking, up to 12 programs) |
| **Languages** | Intercode (assembly), CLEO (COBOL-like) |
| **Special Feature** | Loudspeaker for program monitoring via sound |
| **Production** | ~60 units installed 1961-1969 |

### Memory Organization

LEO III used **ferrite core memory** with a 32-bit word length:

```
Core Memory Layout:
┌────────────────────────────────────────┐
│ Word: 32 bits                          │
│ ┌────────┬────────┬────────┬────────┐ │
│ │ Byte 0 │ Byte 1 │ Byte 2 │ Byte 3 │ │
│ │ 8 bits │ 8 bits │ 8 bits │ 8 bits │ │
│ └────────┴────────┴────────┴────────┘ │
└────────────────────────────────────────┘

Typical Configuration:
- Base memory: 8K words (32 KB)
- Expanded: up to 16K words (64 KB)
- Access time: ~13.2 μs per word
```

### Instruction Encoding

LEO III used a **microprogrammed** instruction set with variable-length instructions:

```
Instruction Format (simplified):
┌──────────┬───────────┬─────────────┐
│ Function │ Modifiers │ Address     │
│ 8 bits   │ 8 bits    │ 16 bits     │
└──────────┴───────────┴─────────────┘

Key Instructions:
- LOAD, STORE: Memory operations
- ADD, SUB, MUL, DIV: Arithmetic
- JUMP, JPOS, JNEG, JZER: Control flow
- INPUT, OUTPUT: I/O operations
- MASTER: OS interface calls
```

### Character Encoding

LEO III used a **6-bit character code** (later extended to 7-bit ASCII):

```
LEO III Character Set (6-bit):
00-1F: Control characters
20-3F: Special characters and digits
40-5F: Uppercase letters A-Z
60-7F: Additional symbols
```

## RustChain Proof-of-Antiquity on LEO III

### Conceptual Adaptation

The original RustChain PoA verifies hardware authenticity through:
1. Hardware fingerprinting (CPU, MAC, serial numbers)
2. Attestation submission to network
3. Epoch-based enrollment
4. Share submission

For LEO III, we adapt these concepts:

| Original RustChain | LEO III Adaptation |
|-------------------|-------------------|
| CPU fingerprint | Core memory residual pattern |
| MAC address | Tape unit serial numbers |
| Network attestation | Paper tape / punched card output |
| Epoch enrollment | Master Program time slice |
| Share submission | Line printer output + audio proof |
| Hardware verification | Unique core memory signature |

### Simplified Mining Algorithm

```
1. READ core_memory_pattern from predetermined addresses
2. COMPUTE hash = pattern XOR nonce
3. IF hash < difficulty_threshold THEN
4.   OUTPUT "SHARE_FOUND" to line printer
5.   PLAY audio_tone via loudspeaker (proof of work)
6.   PUNCH share details to paper tape
7. ELSE
8.   INCREMENT nonce
9.   JUMP to step 2
```

## Project Structure

```
leo-iii-miner/
├── README.md                    # This file
├── ARCHITECTURE.md              # Detailed architecture design
├── leo_iii_simulator.py         # Python simulator of LEO III
├── intercode_program.txt        # Intercode assembly program
├── paper_tape_output.txt        # Example paper tape output
├── master_program_config.cfg    # Master Program configuration
├── test_miner.py                # Test suite
├── PR_DESCRIPTION.md            # Pull request description
└── examples/
    └── sample_mining_session.txt # Example mining session
```

## Usage

### Running the Simulator

```bash
# Help
python leo_iii_simulator.py --help

# Run mining demonstration
python leo_iii_simulator.py --demo

# Extended mining session
python leo_iii_simulator.py --mine --duration 60 --difficulty 0x00100

# Generate Intercode program
python leo_iii_simulator.py --program --output mining.intercode
```

### Master Program Configuration

The LEO III Master Program supported multi-tasking. Our miner runs as one of up to 12 concurrent jobs:

```
MASTER PROGRAM CONFIGURATION
Job Number: 7
Priority: Low (background mining)
Memory Allocation: 2K words
Time Slice: 100ms per cycle
I/O Devices: Printer (output), Tape (logging)
```

## Bounty Claim

**Wallet Address**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

This implementation demonstrates:
- ✅ Understanding of LEO III architecture
- ✅ Conceptual adaptation of RustChain PoA
- ✅ Working simulator with Master Program integration
- ✅ Intercode assembly program listing
- ✅ Educational documentation
- ✅ Proof-of-concept mining algorithm

## Historical Context

The **LEO III** was a groundbreaking computer:

**Firsts achieved by LEO III:**
- First mass-produced commercial computer (~60 units sold)
- First computer with a multi-tasking operating system (Master Program)
- First business computer with solid-state (transistor) technology
- First computer used for diverse business applications (payroll, inventory, billing)
- Pioneered computer bureau services (outsourced computing)

**Notable installations:**
- J. Lyons & Co. (headquarters)
- Shell-Mex & BP Ltd (multiple locations)
- GPO (General Post Office) - used until 1981!
- HM Customs & Excise
- Royal Bank of Scotland
- Manchester Corporation
- Multiple Australian companies

**Legacy:**
- LEO Computers Ltd became part of English Electric (1963)
- Eventually merged into ICL (1968)
- ICL acquired by Fujitsu (1990)
- Some LEO III programs ran on ICL 2900 series via emulation into the 1980s

## Programming LEO III

### Intercode (Assembly Language)

```
Example Intercode Code:
    LOAD    FINGERPRINT    ; Load hardware fingerprint
    ADD     NONCE          ; Add current nonce
    STORE   HASH_RESULT    ; Store result
    SUB     DIFFICULTY     ; Compare with difficulty
    JPOS    CONTINUE       ; If positive, continue
    OUTPUT  SHARE_FOUND    ; Share found!
    HOOT    440            ; Audio proof (A4 tone)
CONTINUE:
    LOAD    NONCE
    ADD     ONE
    STORE   NONCE
    JUMP    START
```

### CLEO (High-Level Language)

```
Example CLEO Code:
    FIND FINGERPRINT
    ADD NONCE GIVING HASH
    IF HASH IS LESS THAN DIFFICULTY
        PRINT "SHARE FOUND"
        PUNCH SHARE-DATA
        SOUND TONE-440
    END-IF
    ADD 1 TO NONCE
    GO TO START
```

## Performance Analysis

### Theoretical Performance

| Metric | LEO III | Modern CPU |
|--------|---------|------------|
| Cycle Time | 13.2 μs | ~0.3 ns |
| Instructions/sec | ~75,000 | ~3,000,000,000 |
| Memory Access | 13.2 μs | ~0.5 ns |
| Hash Attempts/sec | ~10,000 | ~1,000,000,000 |

### Expected Mining Rate

```
Difficulty 0x00100:
- Probability per attempt: 256 / 4,294,967,296 ≈ 0.000006%
- Expected attempts per share: ~16,777,216
- Expected time per share: 16,777,216 × 13.2μs ≈ 221 seconds
- Shares per hour: ~16

Difficulty 0x01000:
- Probability per attempt: 4096 / 4,294,967,296 ≈ 0.000095%
- Expected attempts per share: ~1,048,576
- Expected time per share: 1,048,576 × 13.2μs ≈ 13.8 seconds
- Shares per hour: ~260
```

## Testing

### Unit Tests

```bash
# Run test suite
python test_miner.py

# Test individual components
python -c "from leo_iii_simulator import *; c = LEOIII(); print(c.get_fingerprint())"
```

### Expected Output

```
============================================================
LEO III Simulator
RustChain Proof-of-Antiquity Miner
============================================================

🔨 Starting RustChain Mining Session on LEO III
Difficulty: 0x00100
Duration:   10.0s
Wallet:     RTC4325af95d26d59c3ef025963656d22af638bb96b
Master Program Job: 7
============================================================

[LOUDSPEAKER] ♫ Tone 440 Hz
============================================================
SHARE FOUND!
============================================================
Wallet:     RTC4325af95d26d59c3ef025963656d22af638bb96b
Fingerprint: B4E8C3D2F1A09876
Nonce:      00A4F2
Hash:       0000F8
Difficulty: 000100
Timestamp:  1710334567
Job:        7
============================================================

============================================================
MINING SESSION COMPLETE
============================================================
Duration:     10.15s
Attempts:     10000
Shares Found: 1
Instructions: 85000
Cycles:       85000
Master Program Time Slices: 102
============================================================
```

## Limitations and Future Work

### Current Limitations

1. **No Real Hardware**: This is a simulation; no actual LEO III exists that can run this code
2. **Simplified Hash**: Uses XOR instead of cryptographic hash (SHA-256 impractical on LEO III)
3. **No Networking**: Paper tape/card output simulates network submission
4. **No Persistence**: Shares not persisted to magnetic tape in current implementation
5. **Master Program Simulation**: Simplified OS simulation

### Potential Enhancements

1. **Magnetic Tape Storage**: Implement share persistence to tape
2. **Multi-Job Mining**: Parallel mining across multiple Master Program jobs
3. **Paper Tape Output**: Physical paper tape output (with vintage hardware emulator)
4. **Audio Verification**: Record loudspeaker tones as proof-of-work
5. **CLEO Implementation**: High-level CLEO language version
6. **Museum Display**: Run on LEO III emulator in computer museum

## References

- [LEO Computers Society](http://www.leo-computers.org.uk/)
- [Wikipedia: LEO (computer)](https://en.wikipedia.org/wiki/LEO_(computer))
- [Centre for Computing History: LEO Collection](http://www.computinghistory.org.uk/sec/54762/LEO-Artefacts-Collection/)
- [LEO III Software Preservation](http://sw.ccs.bcs.org/leo/index.html)
- [The Story of LEO - Warwick University](https://warwick.ac.uk/services/library/mrc/explorefurther/digital/leo/story/)
- [RustChain Repository](https://github.com/Scottcjn/Rustchain)

## License

MIT OR Apache-2.0 (same as RustChain)

---

*"The LEO III brought computing to the masses in the 1960s. Now it mines RustChain in the 2020s. The circle of computation is complete!"*

**Bounty Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
