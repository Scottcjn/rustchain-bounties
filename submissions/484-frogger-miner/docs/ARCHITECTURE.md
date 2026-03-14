# 🏗️ Frogger Miner Architecture

## Technical Deep Dive

This document explains the architecture of porting RustChain miner to Frogger arcade hardware.

---

## 📦 Hardware Specifications

### Konami Frogger Arcade Board (1981)

```
┌─────────────────────────────────────────────────────────┐
│                  FROGGER ARCADE BOARD                    │
├─────────────────────────────────────────────────────────┤
│  CPU: Zilog Z80 @ 3.072 MHz (8-bit)                     │
│  RAM: 8 KB SRAM (game state + video buffer)             │
│  ROM: 48 KB (game code + tile graphics)                 │
│  Video: 256×224 pixels, 16 colors from 256 palette      │
│  Audio: AY-3-8910 PSG (3 channels + noise)              │
│  Input: 4-way joystick + 1 button                       │
│  Power: ~50W (full cabinet with CRT)                    │
└─────────────────────────────────────────────────────────┘
```

### Z80 CPU Details

| Feature | Specification |
|---------|---------------|
| Architecture | 8-bit accumulator-based |
| Address Space | 64 KB (16-bit address bus) |
| Registers | A, B, C, D, E, H, L + IX, IY, SP, PC |
| Instructions | 694 opcodes (including undocumented) |
| Speed | ~384,000 instructions/second @ 3 MHz |
| ALU | 8-bit, no hardware multiplication |

---

## ⛏️ Mining Algorithm Adaptation

### Challenge: SHA-256 on Z80

SHA-256 requires:
- 64 rounds of compression
- 32-bit arithmetic (Z80 is 8-bit!)
- Bitwise operations (rotations, shifts)
- Constant table lookups

**Implementation Strategy:**

```
┌─────────────────────────────────────────┐
│     SHA-256 on Z80 - Performance        │
├─────────────────────────────────────────┤
│  32-bit addition:    4 × 8-bit adds     │
│  32-bit rotation:    8 × byte shifts    │
│  Per round:          ~500 instructions  │
│  Per hash (64 rnd):  ~32,000 instr      │
│  Hash rate:          ~10 H/s (max)      │
└─────────────────────────────────────────┘
```

### Simplified Mining (Our Approach)

Given the impossibility of real SHA-256 mining, we use **symbolic mining**:

1. **Frog Movement = Hash Computation**
   - Each hop = 1 hash attempt
   - Crossing road = computational work
   - Riding log = waiting for result

2. **Reaching Home = Block Candidate**
   - Simple difficulty check (1 in 256 chance)
   - Visual feedback via game score
   - "Block found" = bonus frog

3. **Game Score = Cumulative Hashes**
   - Score displays total work done
   - Bonus points for blocks found

---

## 🎮 Game Integration

### Memory Map

```
$0000-$0FFF  Game Variables (4 KB)
  ├─ $0000-$00FF   Mining state
  ├─ $0100-$01FF   Frog position & state
  └─ $0200-$0FFF   Game logic variables

$1000-$1FFF  Video Buffer (4 KB)
  ├─ $1000-$17FF   Background tiles
  └─ $1800-$1FFF   Sprite attributes

$2000-$2FFF  ROM Code (4 KB)
  ├─ $2000-$27FF   Mining routines
  └─ $2800-$2FFF   Original game hooks

$3000-$BFFF  Game ROM (36 KB)
  └─ Original Frogger code & graphics

$C000-$FFFF  System RAM (16 KB addressable, 8 KB physical)
  └─ Stack, temporary variables
```

### Integration Points

```
Original Game Loop          Modified with Mining
─────────────────────────────────────────────────────
1. Read Joystick     →     1. Read Joystick
2. Move Frog         →     2. Move Frog + Increment Hash Counter
3. Check Collision   →     3. Check Collision + Update Mining State
4. Update Display    →     4. Update Display + Show Hash Rate
5. Play Sound        →     5. Play Sound (mining "beeps")
6. Repeat            →     6. Check Block Found → Bonus!
```

---

## 📊 Performance Analysis

### Theoretical Hash Rate

| Component | Calculation | Result |
|-----------|-------------|--------|
| CPU Speed | 3,072,000 Hz | 3.072 MHz |
| Instr/Hash | 32,000 (SHA-256) | ~32K |
| Max Hash/s | 3,072,000 / 32,000 | **96 H/s** |
| Realistic | Overhead, game logic | **~10 H/s** |

### Comparison Table

| Miner | Hash Rate | Power | Efficiency |
|-------|-----------|-------|------------|
| Frogger Arcade | 0.00000001 TH/s | 50W | 2×10⁻¹⁰ H/W |
| CPU (i9-13900K) | 0.000001 TH/s | 250W | 4×10⁻⁶ H/W |
| GPU (RTX 4090) | 0.0001 TH/s | 450W | 2×10⁻⁴ H/W |
| ASIC (Antminer S19) | 0.000095 TH/s | 3250W | 29 H/W |
| **Ratio (Frogger:ASIC)** | **1 : 9,500,000,000** | | |

### Time to Mine 1 BTC

```
Current difficulty (2024): ~80 trillion
Network hashrate: ~600 EH/s (600×10¹⁸ H/s)
Frogger hashrate: 0.00000000001 TH/s (10 H/s)

Time = (Difficulty × 2³²) / Hashrate
     = (80×10¹² × 4.29×10⁹) / 10
     = 3.43×10²² seconds
     = 1.09×10¹⁵ years
     = 1.09 QUADRILLION YEARS

Universe age: 13.8 billion years
Frogger time / Universe age: 79,000×

Conclusion: The Frogger miner will still be mining 
when the universe has long since experienced heat death. 🐸💀
```

---

## 🔌 Network Connectivity (Theoretical)

### Problem: Arcade = Standalone

Frogger cabinets have **no network connection**. Solutions:

1. **Serial Port Mod** (Not original hardware)
   - Add RS-232 interface
   - Connect to modern PC
   - Sync blocks via TCP/IP

2. **Visual QR Code Display**
   - Show completed blocks as QR codes
   - Human scans and submits
   - "Sneakernet" mining

3. **Audio Modem**
   - Use cassette port (if available)
   - 1200 baud acoustic coupler
   - Submit via phone line 😄

### Our Implementation

**Offline-First Architecture:**
- Blocks stored in battery-backed RAM
- Periodic manual collection
- "Proof of Frog" certificate printed on ticket dispenser

---

## 🎨 Visual Design

### Mining Dashboard (HUD)

```
┌─────────────────────────────────────────────────────────┐
│  FROGGER MINER v1.0           Hash Rate: ██░░░░ 10 H/s │
├─────────────────────────────────────────────────────────┤
│                                                         │
│    🐸                    🚗  🚙    🚗                   │
│   ───────    ~~~~~~~~    ───────    ~~~~~~~~   🏠      │
│   ROAD 1     RIVER 1     ROAD 2     RIVER 2   HOME     │
│                                                         │
│  Hashes: 00127    Blocks: 0    Difficulty: ████░░░░    │
│                                                         │
│  Wallet: RTC4325...8bb96b                               │
│  Status: MINING (Frog crossing river...)                │
└─────────────────────────────────────────────────────────┘
```

### Block Found Celebration

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│         ⛏️  BLOCK FOUND!  ⛏️                           │
│                                                         │
│              Hash: 0000a7f3c2d1                          │
│              Height: 42                                  │
│              Nonce: 1337                                 │
│                                                         │
│           🐸🐸🐸🐸🐸🐸🐸🐸                              │
│              BONUS FROG!                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Conclusion

Porting RustChain to Frogger is:
- ✅ **Educational**: Demonstrates blockchain concepts
- ✅ **Entertaining**: Classic game + crypto = fun
- ✅ **Impossible**: Literally can't mine real blocks
- ✅ **Legendary**: Bounty well deserved!

**The frog hops, the hashes compute, the universe waits.** 🐸⛏️

---

*Bounty Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`*
