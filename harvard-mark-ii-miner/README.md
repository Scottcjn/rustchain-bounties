# Harvard Mark II Miner - RustChain Proof-of-Antiquity

[![Platform-Harvard Mark II (1947)](https://img.shields.io/badge/Platform-Harvard%20Mark%20II%20(1947)-red)](https://en.wikipedia.org/wiki/Harvard_Mark_II)
[![Technology-Electromechanical Relays](https://img.shields.io/badge/Technology-Electromechanical%20Relays-orange)]()
[![Input-Paper Tape](https://img.shields.io/badge/Input-Paper%20Tape-yellow)]()
[![Speed-0.3s Addition](https://img.shields.io/badge/Speed-0.3s%20Addition-blue)]()
[![Bounty-#393 LEGENDARY](https://img.shields.io/badge/Bounty-%23393%20LEGENDARY-brightgreen)]()

**The most constrained cryptocurrency miner ever attempted - on an electromechanical relay computer from 1947!**

## ⚠️ Important Notice

This is **NOT** a functional cryptocurrency miner. The Harvard Mark II's hardware constraints make real mining physically impossible:

- **Electromechanical relays** (not transistors or integrated circuits)
- **Decimal arithmetic** (not binary)
- **Paper tape I/O** (no electronic memory storage)
- **~0.3 seconds per addition** (modern miners do billions of ops/sec)
- **No network capabilities** (obviously - predates Ethernet by 25+ years)
- **No SHA-256 support** (would take longer than the age of the universe per hash)

This is a **demonstration/art piece** that shows the RustChain protocol conceptually on one of history's most significant vintage computers.

---

## 📋 Bounty Information

- **Issue**: #393 - Port Miner to ASCC Harvard Mark II
- **Tier**: LEGENDARY
- **Reward**: 200 RTC ($20)
- **Claim Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## 🏛️ Harvard Mark II (ASCC) Background

The **Harvard Mark II** (also known as the **Automatic Sequence Controlled Calculator** or **ASCC**) was an early electromechanical computer built at Harvard University in 1947.

### Key Specifications

| Component | Specification |
|-----------|--------------|
| **Technology** | Electromechanical relays |
| **Relay Count** | ~3,300 relays |
| **Wire Length** | ~5000 miles of wire |
| **Arithmetic** | Decimal (base-10), not binary |
| **Addition Time** | ~0.3 seconds |
| **Multiplication Time** | ~5 seconds |
| **Input** | Paper tape (8-channel) |
| **Output** | Paper tape / Electric typewriter |
| **Memory** | Relay-based registers (no RAM) |
| **Clock Speed** | ~3 Hz (relay switching speed) |
| **Power Consumption** | ~10 kW |
| **Physical Size** | 51 feet long, 8 feet high |

### Historical Significance

- Designed by **Howard H. Aiken**
- Funded by the **U.S. Navy**
- One of the last great electromechanical computers before electronic computers took over
- Featured in early computer science literature
- **Grace Hopper** found the first actual "computer bug" (a moth) in the Mark II in 1947

---

## 🎯 Implementation Overview

This implementation demonstrates the RustChain Proof-of-Antiquity protocol through:

1. **Paper Tape Program**: A complete program encoded in 8-channel paper tape format
2. **Relay Logic Diagrams**: Schematic showing how relay circuits would implement mining state machine
3. **Decimal Arithmetic**: All calculations in BCD (Binary-Coded Decimal) to match Mark II's native format
4. **State Machine**: Conceptual mining states (IDLE → MINING → ATTESTING)
5. **Visual Display**: Paper tape output showing miner status and epoch progress
6. **Hardware Badge**: Representation of the "museum tier" antiquity multiplier (1947 = maximum!)

---

## 📦 Repository Structure

```
harvard-mark-ii-miner/
├── README.md                    # This file
├── ARCHITECTURE.md              # Technical specification
├── PAPER_TAPE_FORMAT.md         # Paper tape encoding specification
├── RELAY_LOGIC.md               # Relay circuit diagrams
├── simulation/
│   ├── mark2_miner.py           # Python simulator
│   ├── paper_tape_encoder.py    # Encode programs to paper tape format
│   ├── paper_tape_decoder.py    # Decode paper tape images
│   └── test_vectors/            # Test paper tape patterns
├── paper_tape/
│   ├── miner_program.pt         # Main miner program (paper tape format)
│   ├── attestation.pt           # Attestation output format
│   └── epoch_counter.pt         # Epoch tracking program
├── diagrams/
│   ├── state_machine.svg        # Mining state machine
│   ├── relay_layout.svg         # Relay bank organization
│   └── timing_diagram.svg       # Operation timing
├── docs/
│   ├── harvard_mark_ii_history.md    # Historical background
│   ├── rustchain_protocol.md         # Protocol adaptation
│   └── bounty_claim.md               # Bounty claim documentation
└── LICENSE
```

---

## 🔧 Paper Tape Format

The Harvard Mark II used **8-channel paper tape** for program input:

```
Channel 8: Sprocket hole (always punched)
Channel 7: Data bit 7
Channel 6: Data bit 6
Channel 5: Data bit 5
Channel 4: Data bit 4
Channel 3: Data bit 3
Channel 2: Data bit 2
Channel 1: Data bit 1
```

### Example Encoding

```
Character: 'A' (0x41)
Tape:  ○●○○○○○●  (● = punched, ○ = not punched)
       87654321   (channel numbers)
```

See `PAPER_TAPE_FORMAT.md` for complete encoding specification.

---

## ⚙️ Mining State Machine

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌──────┐     ┌─────────┐     ┌──────────┐            │
│  │ IDLE │────▶│ MINING  │────▶│ATTESTING │            │
│  │ (0)  │     │   (1)   │     │   (2)    │            │
│  └──────┘     └─────────┘     └──────────┘            │
│      ▲                             │                   │
│      └─────────────────────────────┘                   │
│              [attestation complete]                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### State Descriptions

| State | Code | Description | Paper Tape Output |
|-------|------|-------------|-------------------|
| **IDLE** | 0 | Waiting for operator input | `IDLE_EPOCH_XXX` |
| **MINING** | 1 | Computing proof-of-antiquity | `MINING_HASH_X` |
| **ATTESTING** | 2 | Generating attestation | `ATTEST_COMPLETE` |

---

## 🎨 Hardware Badge - Museum Tier

The Harvard Mark II (1947) represents the **ultimate antiquity**:

| Era | Multiplier | Example |
|-----|------------|---------|
| Modern (2020+) | 1.0× | Apple Silicon |
| Vintage (2000-2010) | 1.5× | Core 2 Duo |
| Ancient (1980-1999) | 2.0× | PowerPC G3 |
| **Museum (pre-1980)** | **2.5×** | **Harvard Mark II** |

**Theoretical Multiplier for Harvard Mark II**: **2.5×** (maximum tier)

---

## 🧪 Simulation

Since we can't physically run code on the actual Harvard Mark II (it's in a museum!), we provide a Python simulator:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the simulator
python simulation/mark2_miner.py

# Generate paper tape output
python simulation/paper_tape_encoder.py miner_program.asm output.pt

# View paper tape as text
python simulation/paper_tape_decoder.py output.pt
```

### Simulator Features

- ✅ Emulates Harvard Mark II decimal arithmetic
- ✅ Simulates relay switching delays (~0.3s per operation)
- ✅ Generates authentic paper tape output
- ✅ Models state machine transitions
- ✅ Produces attestation reports

---

## 📊 Performance Characteristics

| Operation | Harvard Mark II | Modern CPU | Ratio |
|-----------|-----------------|------------|-------|
| Addition | 0.3s | ~1ns | 300,000,000:1 |
| Multiplication | 5s | ~3ns | 1,666,666,667:1 |
| Memory Access | 0.01s (relay) | ~100ns | 100,000:1 |
| SHA-256 Hash | ∞ (not possible) | ~10ns | ∞ |

**Conclusion**: Real mining is physically impossible. This is a conceptual demonstration.

---

## 🔬 Technical Challenges

### 1. Decimal vs Binary

The Mark II used **decimal arithmetic**, not binary. All values must be encoded in **BCD (Binary-Coded Decimal)**:

```
Decimal 42 → BCD: 0100 0010
             (4)  (2)
```

### 2. Paper Tape Limitations

- **Sequential access only** (no random access memory)
- **Read speed**: ~10 characters/second
- **No write capability** during operation (output to separate tape)

### 3. Relay Timing

- Each relay takes ~10ms to switch
- Complex operations require multiple relay stages
- Timing diagrams must account for relay bounce

### 4. No Cryptographic Primitives

- No SHA-256 hardware (obviously)
- No random number generation beyond mechanical switches
- Solution: Use epoch number as "proof" (symbolic only)

---

## 📝 Program Listing

The main miner program is encoded in paper tape format. Here's a simplified assembly-like representation:

```asm
; Harvard Mark II Miner - Main Program
; Encoded for 8-channel paper tape

START:  LOAD    EPOCH_COUNT     ; Load current epoch
        ADD     ONE             ; Increment epoch
        STORE   EPOCH_COUNT     ; Store back
        
        LOAD    STATE           ; Load miner state
        COMPARE MINING_STATE    ; Check if mining
        JUMP    ATTEST          ; If mining, go attest
        
        ; Display status on paper tape
        PRINT   STATUS_IDLE
        JUMP    START

ATTEST: PRINT   STATUS_ATTEST
        PRINT   EPOCH_COUNT
        PRINT   WALLET_ADDR     ; Output wallet for bounty
        
        ; Reset state
        LOAD    ZERO
        STORE   STATE
        JUMP    START

; Data section
EPOCH_COUNT:  DEC 0
STATE:        DEC 0
WALLET_ADDR:  ASCII "RTC4325af95d26d59c3ef025963656d22af638bb96b"
ONE:          DEC 1
ZERO:         DEC 0
STATUS_IDLE:  ASCII "IDLE"
STATUS_ATTEST: ASCII "ATTEST"
```

---

## 🏆 Bounty Claim

**Wallet Address**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

### Completion Checklist

- [x] Repository created
- [x] README.md with full documentation
- [x] ARCHITECTURE.md technical specification
- [x] Paper tape format specification
- [x] Relay logic diagrams
- [x] Python simulator
- [x] Sample paper tape programs
- [x] Historical documentation
- [x] Wallet address included
- [ ] PR submitted to rustchain-bounties
- [ ] Bounty claimed

---

## 📚 References

- [Harvard Mark II - Wikipedia](https://en.wikipedia.org/wiki/Harvard_Mark_II)
- [IEEE History Center: Harvard Mark II](https://ethw.org/Harvard_Computers)
- [Computer History Museum: ASCC](https://computerhistory.org/collections/harvard-mark-ii/)
- [Grace Hopper and the First Computer Bug](https://www.navy.mil/submit/display.asp?story_id=70394)
- [RustChain Documentation](https://github.com/Scottcjn/Rustchain)
- [RIP-PoA Specification](https://github.com/Scottcjn/Rustchain/blob/main/docs/protocol-overview.md)

---

## 🙏 Acknowledgments

- **Harvard University** for preserving computing history
- **Grace Hopper** for debugging the Mark II (literally!)
- **Howard Aiken** for visionary computer design
- **RustChain Foundation** for the LEGENDARY tier bounty
- **The electromechanical computing community** for keeping history alive

---

## 📄 License

MIT License - See LICENSE file

---

## 🎯 Conclusion

The Harvard Mark II represents a pivotal moment in computing history - the transition from purely mechanical calculators to programmable computers. While it cannot mine cryptocurrency in any practical sense, this implementation honors its legacy by demonstrating that the **concept** of Proof-of-Antiquity applies even to the most ancient computing hardware.

**Built with ❤️ and 3,300 relays**

*Your vintage hardware earns rewards. Make mining meaningful again.*

---

**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
