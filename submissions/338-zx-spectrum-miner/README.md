# ZX Spectrum Miner (1982) 🖥️⛏️

> **Educational Proof-of-Concept**: Porting cryptocurrency mining concepts to the ZX Spectrum

![ZX Spectrum](https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/ZX_Spectrum_48k.jpg/640px-ZX_Spectrum_48k.jpg)

---

## 📋 Overview

This project demonstrates a **conceptual cryptocurrency miner** for the ZX Spectrum, the iconic British home computer from 1982. 

**⚠️ Important**: This is an **educational demonstration**, not a production miner. The ZX Spectrum's hardware limitations (48 KB RAM, 3.5 MHz Z80 CPU, no network) make actual mining impossible. This project shows what mining *logic* would look like on 8-bit hardware.

### 🎯 Project Goals

1. **Educational**: Demonstrate proof-of-work concepts on vintage hardware
2. **Historical**: Show what crypto mining would look like in 1982
3. **Technical**: Create working Z80 assembly code and Python simulator
4. **Community**: Contribute to RustChain's creative porting challenges

---

## 🏆 Bounty Information

- **Challenge**: #406 - Port Miner to ZX Spectrum (1982)
- **Reward**: 200 RTC ($20) - LEGENDARY Tier
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## 📁 Project Structure

```
zx-spectrum-miner/
├── README.md              # This file
├── TECHNICAL_RESEARCH.md  # Architecture research & feasibility analysis
├── miner.asm              # Z80 assembly source code
├── z80_simulator.py       # Python Z80 CPU simulator
├── run_miner.py           # Easy launcher script
└── assets/                # Screenshots and demos (TODO)
```

---

## 🔧 Hardware Specifications

### ZX Spectrum (1982)

| Component | Specification |
|-----------|---------------|
| **CPU** | Zilog Z80A @ 3.5 MHz |
| **Architecture** | 8-bit |
| **RAM** | 16 KB / 48 KB |
| **ROM** | 16 KB (BASIC + OS) |
| **Display** | 256×192, 15 colors |
| **Storage** | Cassette tape (1500 bps) |
| **Network** | None (requires expansion) |

### Why This Is Challenging

| Requirement | Modern Miner | ZX Spectrum | Gap |
|-------------|--------------|-------------|-----|
| RAM | GBs | 48 KB | 20,000× |
| Storage | SSD/NVMe | Cassette | Impossible |
| Network | Ethernet/WiFi | None | Needs expansion |
| Hash Rate | TH/s | ~100 H/s (simulated) | 10¹²× |
| Power | 100s of W | 0.01 W | - |

---

## 🚀 Quick Start

### Option 1: Run Python Simulator (Recommended)

```bash
# Clone or download the project
cd zx-spectrum-miner

# Run the simulator
python z80_simulator.py
```

### Option 2: Assemble Z80 Code

To run on real hardware or emulator:

```bash
# Install Z80 assembler (example: pasmo)
# On Windows: download from https://pasmo.sourceforge.net/

# Assemble
pasmo miner.asm miner.tap

# Load in ZX Spectrum emulator (Fuse, Spectaculator, etc.)
# LOAD "" CODE
# RUN
```

---

## 💻 How It Works

### Mining Algorithm (Simplified)

The miner implements a **simplified proof-of-work**:

1. **Block Header**: 32 bytes of data (simplified from real block headers)
2. **Nonce**: 16-bit counter (0 - 65535)
3. **Hash Function**: XOR-based (not SHA-256, too complex for Z80)
4. **Difficulty**: Hash must be less than target value
5. **Output**: Display nonce on screen when block is found

### Memory Map

```
$8000 - $80FF: Program code
$8100 - $811F: Block header (32 bytes)
$8120 - $8121: Nonce counter (16-bit)
$8122 - $8141: Hash result buffer (32 bytes)
$8142 - $8143: Difficulty target (16-bit)
$8200 - $82FF: Stack and working memory
```

### Z80 Assembly Highlights

```asm
; Main mining loop
MINING_LOOP:
    INC (NONCE)          ; Increment nonce
    CALL COMPUTE_HASH    ; Calculate hash
    CALL CHECK_TARGET    ; Compare with difficulty
    JR NZ, MINING_LOOP   ; Continue if not found
    
    ; Block found!
    CALL DISPLAY_WINNER
    HALT
```

---

## 🎮 Running on Real Hardware

### Requirements

1. **ZX Spectrum 48K** (or emulator)
2. **Interface** to load code (cassette, SD card, or network expansion)
3. **Z80 Assembler** to compile `miner.asm`

### Emulators

- **Fuse** (Free Unix Spectrum Emulator) - Cross-platform
- **Spectaculator** - Windows
- **ZX Spin** - Windows
- **JSMESS** - Browser-based

### Loading Instructions

1. Assemble `miner.asm` to `.tap` or `.tzx` format
2. Load in emulator: `LOAD "" CODE`
3. Run: `RANDOMIZE USR 32768` (0x8000)

---

## 📊 Performance Analysis

### Theoretical Hash Rate

| Platform | Hash Rate | Time to Find Block* |
|----------|-----------|---------------------|
| ZX Spectrum (simulated) | ~100 H/s | ~655 seconds |
| Modern GPU | ~100 MH/s | ~0.0006 seconds |
| ASIC Miner | ~100 TH/s | ~0.0000000006 seconds |

*With 16-bit nonce space (65536 possibilities)

### Power Efficiency

- **ZX Spectrum**: ~0.01 W (extremely efficient!)
- **Modern GPU**: ~200 W
- **ASIC**: ~3000 W

The ZX Spectrum is technically the most power-efficient miner... if you ignore the 10¹²× slower speed! 😄

---

## 🧠 Educational Value

### What You'll Learn

1. **Z80 Assembly**: Classic 8-bit programming
2. **Computer Architecture**: How early PCs worked
3. **Cryptography Basics**: Hash functions and proof-of-work
4. **Optimization**: Making the most of extreme constraints
5. **History**: Understanding computing evolution

### Classroom Use

This project is perfect for:
- Computer history courses
- Assembly language classes
- Cryptocurrency education
- Retro computing workshops

---

## 🤝 Contributing

This is an open educational project. Contributions welcome:

- Improve the Z80 assembly code
- Add more realistic hash functions
- Create visual displays
- Port to other vintage systems (C64, Apple II, etc.)
- Write documentation in other languages

---

## 📝 License

MIT License - Feel free to use, modify, and share!

---

## 🙏 Acknowledgments

- **ZX Spectrum**: Sir Clive Sinclair and the Sinclair team
- **RustChain**: For the creative bounty challenge
- **Z80 Community**: Keeping 8-bit computing alive

---

## 📬 Contact

- **Project**: ZX Spectrum Miner
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
- **Challenge**: #406

---

*"The ZX Spectrum was my first computer. Now it's (theoretically) mining crypto. The future is weird."* 🖥️✨
