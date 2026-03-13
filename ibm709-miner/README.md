# RustChain IBM 709 Miner (1958)

**"Every vintage computer has historical potential"**

Port of the RustChain Proof-of-Antiquity miner to the IBM 709, IBM's first large-scale scientific computer (announced 1957, first installed August 1958).

![IBM 709 Front Panel](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/IBM_709_front_panel_at_CHM.agr.jpg/640px-IBM_709_front_panel_at_CHM.agr.jpg)

## 🏆 Bounty Tier: LEGENDARY (200 RTC / $20)

This is the **oldest architecture ever to mine RustChain** - predating the IBM 7090/7094 (transistorized versions), Intel 8086, and even integrated circuits!

### Hardware Specifications

| Feature | IBM 709 (1958) |
|---------|----------------|
| **Technology** | Vacuum tubes (later transistorized as 7090) |
| **Word Size** | 36 bits |
| **Memory** | 32,768 words magnetic-core (144 KB equivalent) |
| **Speed** | 42,000 add/subtract per second |
| **Multiply** | 5,000 per second |
| **Power** | 100-250 kW (plus cooling) |
| **Weight** | 2,110 pounds (960 kg) |
| **Instruction Format** | 5 types (A, B, C, D, E) |
| **Registers** | AC (38-bit), MQ (36-bit), 3 Index Registers (15-bit) |
| **Character Encoding** | 6-bit BCD (6 characters per word) |

## 🎯 Antiquity Multiplier: 5.0x

The IBM 709 earns the **highest multiplier in RustChain history** due to:
- Pre-transistor era (vacuum tube technology)
- First commercially available computer with overlapped I/O
- First machine with the FORTRAN Assembly Program (FAP)
- Historical significance: NASA used 709 for Mercury spaceflight calculations

## 📁 Project Structure

```
ibm709-miner/
├── README.md                 # This file
├── ARCHITECTURE.md           # IBM 709 technical details
├── IMPLEMENTATION.md         # Implementation plan and constraints
├── src/
│   ├── miner.fap             # Main miner in FAP assembly
│   ├── entropy.fap           # Entropy collection routines
│   ├── wallet.fap            # Wallet generation/storage
│   └── attestation.fap       # Attestation format generator
├── simh/
│   ├── ibm7090.ini           # SIMH configuration for IBM 7090
│   ├── tape_reader.sim       # Tape output simulation
│   └── submit_host.py        # Modern host attestation submitter
├── build/
│   └── (compiled binaries)
└── docs/
    ├── fap_reference.md      # FAP assembly language reference
    └── ibm709_instruction_set.md
```

## 🔧 Emulation Approach

Since original IBM 709 hardware is extremely rare (only a few preserved in museums), we use **SIMH** to emulate the IBM 7090 (transistorized successor with identical architecture).

### Requirements

1. **SIMH** (Open SIMH fork) - [github.com/open-simh/simh](https://github.com/open-simh/simh)
2. **IBM 7090/7094 Distribution** - Historical software archives
3. **Modern Host** - Python 3.x for attestation submission

### Installation

```bash
# Clone Open SIMH
git clone https://github.com/open-simh/simh.git
cd simh

# Build with IBM 7090 support
make -f makefile all

# Verify IBM 7090 simulator exists
ls bin/ibm7090
```

## 🚀 Quick Start

```bash
# 1. Start the IBM 7090 simulator
cd simh/
./bin/ibm7090 ibm7090.ini

# 2. Load the miner (simulated card reader)
LOAD miner.fap

# 3. Run the miner
RUN miner

# 4. Attestations are written to simulated tape
# 5. Export tape to modern host
# 6. Submit via Python script
python submit_host.py --tape attestation.tap --wallet WALLET.DAT
```

## 💰 Wallet & Payout

**Wallet Address**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

All bounty rewards go to this address. Mining rewards (if any) go to the generated wallet.

## 📊 Mining Architecture

### Challenge: No Networking

The IBM 709 has **no network capabilities** (predates ARPANET by 11 years!). Solution:

1. **Batch Mode Mining**: IBM 709 generates attestations locally
2. **Tape Export**: Attestations written to simulated 7-track tape
3. **Host Submission**: Modern Python script reads tape image and submits to RustChain node

### Entropy Sources

The IBM 709 provides unique entropy from:
- **Core Memory Refresh Timing** - Magnetic core decay patterns
- **Vacuum Tube Warm-up** - Thermal variance in tube banks
- **Instruction Cycle Variance** - Tube switching time variations
- **IBM 733 Drum Memory** - Rotational latency (if attached)
- **Card Reader Timing** - Mechanical variance in punch card reader

### Attestation Format

```json
{
  "miner": "RTC<generated_wallet>",
  "miner_id": "IBM709-<entropy_hash>",
  "nonce": <timestamp>,
  "device": {
    "arch": "ibm_709",
    "family": "vacuum_tube",
    "model": "IBM 709 (1958)",
    "word_size": 36,
    "memory_words": 32768,
    "technology": "vacuum_tube",
    "simulator": "SIMH IBM 7090"
  },
  "entropy": {
    "core_timing": "<hex>",
    "tube_variance": "<hex>",
    "drum_latency": "<hex>"
  },
  "dev_fee": {
    "enabled": true,
    "wallet": "founder_dev_fund",
    "amount": "0.001"
  }
}
```

## 🏛️ Historical Context

The IBM 709 was used for:
- **NASA Mercury Program** - Orbital trajectory calculations
- **NORAD** - Early ballistic missile tracking
- **Weather Prediction** - First numerical weather models
- **Nuclear Research** - Los Alamos scientific computations

By mining RustChain on this architecture, we're connecting 1950s scientific computing with 2020s blockchain technology - a span of nearly 70 years!

## 📝 Development Notes

### FAP Assembly Language

FAP (FORTRAN Assembly Program) was introduced for the IBM 709. Key features:

- **Octal notation** - All addresses and constants in octal
- **Symbolic addresses** - Labels for memory locations
- **Pseudo-operations** - REMOTE, ENTRY, DEC, OCT, BSS
- **Index register support** - XR1, XR2, XR4

Example FAP code:
```
         ENTRY  START
START    CLA    ZERO       / Clear AC
         SXA    SAVE1,1    / Store in index 1
         TZE    LOOP       / Test and jump
ZERO     DEC    0          / Constant zero
LOOP     HTR    LOOP       / Halt
         END    START
```

### Memory Constraints

With only 32K words (144 KB), the miner must be extremely compact:
- **Code**: ~2K words
- **Data/Entropy**: ~1K words  
- **Buffer**: ~1K words
- **Free**: ~28K words for runtime

## 🎓 Educational Value

This project demonstrates:
1. **Computer Architecture Evolution** - From vacuum tubes to modern CPUs
2. **Assembly Programming** - Programming at the metal
3. **Historical Preservation** - Keeping vintage computing alive
4. **Blockchain Universality** - Proof-of-work transcends hardware generations

## 📚 References

- [IBM 709 Reference Manual (1958)](http://bitsavers.org/pdf/ibm/709/A22-6501-0_709_Data_Processing_System_Reference_Manual_Apr58.pdf)
- [Programming the IBM 709-7090-7094](http://bitsavers.org/pdf/ibm/7090/books/Sherman_Programming_and_Coding_the_IBM_709-7090-7094_Computers_1963.pdf)
- [SIMH IBM 7090 Documentation](https://github.com/open-simh/simh/blob/master/IBM7090.md)
- [Computer History Museum - IBM 709](https://computerhistory.org/collections/catalog/102643736)

## 🤝 Contributing

Interested in vintage computing or blockchain history? Contributions welcome:
- FAP assembly optimizations
- Additional entropy sources
- Historical documentation
- SIMH configuration improvements

## 📄 License

Apache 2.0 - Part of the RustChain ecosystem

---

**RustChain - Proof of Antiquity Blockchain**

*Every vintage computer has historical potential.*
