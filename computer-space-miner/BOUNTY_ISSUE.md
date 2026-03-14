# [BOUNTY] Port RustChain Miner to Computer Space (1971) - 200 RTC (LEGENDARY Tier)

## Status: Open
## Difficulty: Extreme
## Estimated Effort: 3-6 months
## Reward: 200 RTC (LEGENDARY Tier) + 3.5× vintage multiplier

**Wallet for Bounty**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## Overview

Port the RustChain miner to **Computer Space (1971)** - the **first commercial arcade video game** ever made!

Computer Space was designed by **Nolan Bushnell** and **Ted Dabney** (who later founded Atari) and manufactured by **Nutting Associates**. Unlike modern systems, it was built with:

- **NO CPU** - Pure 7400-series TTL logic chips
- **NO RAM** - Hardwired state machines only
- **NO Microprocessor** - Discrete logic gates (74 chips total!)
- **Pure hardware** - Analog video generation, diode matrix programming

This is the **ultimate hardware mining challenge**: running blockchain attestation on a machine that predates the microprocessor revolution!

---

## Why Computer Space (1971)?

| Feature | Specification |
|---------|--------------|
| **Release** | November 1971 (55 years ago!) |
| **Manufacturer** | Nutting Associates |
| **Designer** | Nolan Bushnell & Ted Dabney |
| **Technology** | 7400-series TTL discrete logic |
| **Chips** | ~74 TTL ICs (no CPU!) |
| **Display** | B&W CRT monitor (13" diagonal) |
| **Resolution** | 280×220 (interlaced) |
| **Clock** | ~5 MHz (crystal oscillator) |
| **Memory** | None (hardwired state machines) |
| **Original Price** | $1,995 USD (~$15,000 in 2025) |
| **Units Produced** | ~1,500 (extremely rare!) |

### Historical Significance

- 🎮 **First commercial arcade video game** (predates Pong by 1 year)
- 🪙 **First video game to use a coin mechanism**
- 🚀 **Launched the video game industry**
- 💎 **Pure TTL design** - the last of its kind
- 🏛️ **Museum-grade artifact** - only ~1,500 units made

---

## The Challenge: Original Hardware vs. Badge Implementation

### Original 1971 Hardware (Museum Grade)

The original Computer Space uses:

- **74 TTL logic chips** - Discrete 7400-series ICs
- **Diode matrix** - Game logic "programmed" via diodes
- **Analog circuits** - For video signal generation
- **Hardwired state machines** - No firmware, pure hardware
- **No digital memory** - Everything is registers and counters

**Conclusion**: The original hardware is theoretically modifiable but practically impossible to use without destroying a museum-grade artifact.

### Badge-Only Solution (Recommended Path)

Create a **modern recreation** that maintains the vintage aesthetic while using programmable hardware:

| Component | Original (1971) | Badge Implementation |
|-----------|-----------------|---------------------|
| **Logic** | 74 TTL chips | FPGA (Lattice iCE40 UP5K) |
| **Display** | B&W CRT | Original CRT preserved! |
| **Input** | 4 push buttons | Original buttons (preserved) |
| **Memory** | None | FPGA block RAM (64 KB) |
| **Network** | N/A | ESP32 WiFi module |
| **Installation** | N/A | Internal PCB replacement |

### Why FPGA?

- ✅ **Authentic TTL emulation** - FPGA can replicate 7400-series logic behavior
- ✅ **Hardware-level mining** - SHA256 in actual hardware logic
- ✅ **Vintage multiplier** - 1971 design = 3.5× antiquity bonus
- ✅ **Cultural icon** - First arcade video game ever
- ✅ **Technical innovation** - First blockchain miner on pure TTL architecture

---

## Technical Requirements

### 1. FPGA Development Environment (40 RTC)

**Recommended Toolchain:**

| Tool | Purpose | Link |
|------|---------|------|
| **Yosys** | Open-source FPGA synthesis | https://yosyshq.net/yosys |
| **nextpnr** | Place & route | https://github.com/YosysHQ/nextpnr |
| **icestorm** | Lattice iCE40 toolchain | https://github.com/YosysHQ/icestorm |
| **Verilator** | FPGA simulation | https://www.veripool.org/verilator |

**Hardware Required:**

- Lattice iCE40 UP5K FPGA (or iCE40 HX8K)
- ESP32-WROOM module (for WiFi)
- Level shifters (3.3V ↔ 5V)
- Original Computer Space cabinet (preserved!)
- Custom PCB to replace original logic boards
- 3D printed mounting brackets

### 2. TTL Logic Emulation (60 RTC)

**Challenge**: Replicate 74 TTL chips in FPGA fabric.

**Computer Space TTL Chip Inventory:**

| Chip | Count | Purpose |
|------|-------|---------|
| 7400 | 12 | NAND gates (game logic) |
| 7404 | 6 | Inverters |
| 7410 | 4 | Triple 3-input NAND |
| 7420 | 4 | Dual 4-input NAND |
| 7430 | 2 | 8-input NAND |
| 7442 | 4 | BCD decoder (score display) |
| 7473 | 8 | Dual JK flip-flop (state machines) |
| 7476 | 10 | Dual JK flip-flop (registers) |
| 7486 | 6 | XOR gates (collision detection) |
| 7490 | 4 | Decade counter (video timing) |
| 7493 | 6 | 4-bit counter (position counters) |
| 74107 | 4 | Dual JK flip-flop |
| **Total** | **~74 chips** | |

### 3. Video Signal Generation (40 RTC)

**Original Specs:**

- **Resolution**: 280×220 (interlaced)
- **Refresh**: 60 Hz (NTSC)
- **Sync**: Composite sync (3.5V peak-to-peak)
- **Video**: B&W only (1V peak-to-peak)

**Implementation**: FPGA-based video timing generator that replicates the original analog circuit behavior.

### 4. SHA256 Hardware Core (60 RTC)

**Challenge**: Implement SHA256 entirely in FPGA logic (no soft CPU).

**Performance:**

- **Hash rate**: ~100-500 H/s (FPGA parallelism)
- **Power**: ~500 mW (ultra-low!)
- **Logic usage**: ~3,000 LUTs (60% of iCE40 UP5K)

### 5. Network Bridge (50 RTC)

**ESP32 WiFi + RustChain HTTP API:**

- MicroPython firmware on ESP32
- SPI communication with FPGA
- WiFi connectivity to rustchain.org
- Hardware fingerprinting

### 6. Hardware Fingerprinting (50 RTC)

**FPGA-Specific Fingerprint Sources:**

| Check | Description | Emulator Detection |
|-------|-------------|-------------------|
| **FPGA ID** | Lattice unique chip ID | ✗ Emulators fake it |
| **PLL Jitter** | PLL phase noise variance | ✓ Real analog variance |
| **BRAM Timing** | Block RAM access jitter | ✓ Real timing variance |
| **Oscillator Drift** | Crystal frequency drift | ✓ Real crystals drift |
| **Power Signature** | Current consumption pattern | ✓ Analog circuit variance |

---

## Deliverables

### Phase 1: FPGA Development Environment (40 RTC)

- [ ] Yosys/nextpnr toolchain configured
- [ ] Lattice iCE40 UP5K board setup
- [ ] Basic "Hello World" LED blink
- [ ] SPI communication with ESP32 working

### Phase 2: TTL Logic Emulation (60 RTC)

- [ ] Verilog models for all 74 TTL chips
- [ ] Test benches for each chip model
- [ ] Full Computer Space logic emulation
- [ ] Video signal generation working

### Phase 3: SHA256 Hardware Core (60 RTC)

- [ ] SHA256 module in Verilog
- [ ] NIST test vector validation
- [ ] Performance optimization
- [ ] Integration with network bridge

### Phase 4: Network Bridge (50 RTC)

- [ ] ESP32 MicroPython firmware
- [ ] WiFi connection (WPA2)
- [ ] HTTP POST to RustChain API
- [ ] JSON payload builder
- [ ] Error handling & retry logic

### Phase 5: Fingerprinting (50 RTC)

- [ ] FPGA ID collection
- [ ] PLL jitter measurement
- [ ] Power signature analysis
- [ ] Oscillator drift tracking
- [ ] Emulator detection (must detect Verilator!)

### Phase 6: Integration & Polish (40 RTC)

- [ ] Full system integration
- [ ] Control panel button handling
- [ ] Display overlay (OSD)
- [ ] Low-power modes
- [ ] Configuration menu

### Phase 7: Hardware Build & Documentation (50 RTC)

- [ ] Custom PCB design (KiCad)
- [ ] 3D printed mounting brackets
- [ ] Installation in original cabinet
- [ ] Photo proof with timestamp
- [ ] Video demonstration
- [ ] Complete documentation

**Total**: 400 RTC (capped at 200 RTC for LEGENDARY Tier)

---

## Acceptance Criteria

- [ ] FPGA bitstream compiles for Lattice iCE40
- [ ] TTL emulation passes all test vectors
- [ ] SHA256 core passes NIST test vectors
- [ ] Emulator detection works (Verilator flagged, earns 0 RTC)
- [ ] Networks via WiFi (ESP32 bridge)
- [ ] Successfully attests to rustchain.org
- [ ] Photo proof: Original Computer Space cabinet with miner running
- [ ] Video demonstration: Full attestation cycle + gameplay
- [ ] Source code: Complete, documented, buildable (MIT license)
- [ ] Build instructions: Clear setup guide for others
- [ ] PCB design: KiCad files for reproduction

---

## Multiplier

**Computer Space (1971) FPGA: 3.5× vintage multiplier**

**Justification:**

- ✅ 1971 design (55+ years old)
- ✅ First commercial arcade video game
- ✅ Pure TTL logic (no CPU, no RAM!)
- ✅ Extreme rarity (~1,500 units produced)
- ✅ Cultural significance (launched video game industry)
- ✅ Technical innovation (first hardware-emulated TTL miner)

### Expected Earnings

| Metric | Value |
|--------|-------|
| Base reward | 0.12 RTC/epoch |
| With 3.5× multiplier | 0.42 RTC/epoch |
| Per day (144 epochs) | 60.48 RTC |
| Per month | ~1,814 RTC |
| Per year | ~22,075 RTC |

At $0.10/RTC: **~$2,200/year** in mining rewards!

---

## Skills Required

- **FPGA Development** - Verilog, Yosys, nextpnr, Lattice iCE40
- **Digital Logic Design** - 7400-series TTL, state machines
- **Embedded Systems** - ESP32, MicroPython, WiFi, SPI
- **Hardware Design** - KiCad, PCB design, level shifting
- **3D Modeling** - Fusion 360 for mounting brackets
- **RustChain Protocol** - Attestation API understanding

---

## Resources

| Resource | Link |
|----------|------|
| RustChain Main Repo | https://github.com/Scottcjn/Rustchain |
| Bounties Repo | https://github.com/Scottcjn/rustchain-bounties |
| Node Health | `curl -sk https://rustchain.org/health` |
| Active Miners | `curl -sk https://rustchain.org/api/miners` |
| Lattice iCE40 Docs | https://www.latticesemi.com/iCE40 |
| Yosys HQ | https://yosyshq.net/yosys |
| Computer Space Museum | https://www.arcade-museum.com/machine/computer-space |
| TTL Data Sheets | https://www.ti.com/lit/gpn/sn7400 |
| RustChain Discord | https://discord.gg/VqVVS2CW9Q |

---

## Getting Started

1. **Comment on this issue**: "I would like to work on this"
2. **Set up development environment**: Yosys + nextpnr + Lattice iCE40
3. **Create a wallet**: `pip install clawrtc && clawrtc wallet create`
4. **Start with Phase 1**: Get LED blinking on FPGA
5. **Post progress updates** in issue comments
6. **Submit PR** when complete with all deliverables

---

## Payment

- **Milestone payments** available upon request
- **Final payout**: 200 RTC to your wallet address
- **Wallet required**: Include RTC wallet address in PR
- **Verification**: Real hardware proof mandatory before payment

**Bounty Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## Notes

- **FPGA implementation** is the only viable path (original TTL is museum-grade)
- **ESP32 chosen** for WiFi + low cost + MicroPython ecosystem
- **Original cabinet** should be preserved (non-destructive installation)
- **Performance** will be excellent (FPGA hardware SHA256)
- **Power consumption**: ~500 mW active, ~10 mW idle

---

## FAQ

**Q: Why not use the original 1971 hardware?**

A: The original Computer Space uses 74 discrete TTL chips with hardwired logic. While theoretically possible to modify, it would require destroying the original diode matrix and is practically impossible without ruining a museum-grade artifact. The FPGA approach preserves the original while enabling modern functionality.

**Q: Is FPGA cheating?**

A: No! FPGAs are literal programmable logic - they're the spiritual successor to TTL. An iCE40 UP5K contains 5,280 logic cells, each equivalent to several 7400-series gates. When we emulate 74 TTL chips in FPGA, we're running the actual logic design, just on modern fabric.

**Q: Can I use a different FPGA?**

A: Yes! Xilinx Spartan-7, Lattice ECP5, or even a Raspberry Pi Pico (RP2040) for a softer implementation. iCE40 is recommended for open-source toolchain (no vendor lock-in).

**Q: What if I can't find a Computer Space cabinet?**

A: Options:
- Partner with an arcade museum (many have Computer Space!)
- Build a replica cabinet (plans available online)
- Create a desktop "badge" version with original control panel
- Focus on the FPGA logic emulation (still qualifies for partial bounty)

**Q: How do I connect to the internet?**

A: ESP32 has built-in WiFi. Configure SSID/password in the code. The ESP32 bridges between the FPGA (via SPI) and RustChain API (via HTTP).

**Q: What's the expected mining reward?**

A: Base reward × 3.5× vintage multiplier. Expect ~0.01-0.03 RTC per epoch (10 minutes).

**Q: Can I play Computer Space while it mines?**

A: Yes! The FPGA emulates the full game logic. Mining runs in the background during attract mode or between games.

---

## Historical Context: Computer Space (1971)

**Computer Space** was created by **Nolan Bushnell** and **Ted Dabney**, who later founded **Atari** in 1972. Key facts:

- 🎮 **First video game** to use a coin mechanism
- 🕹️ **First arcade video game** (predates Pong by 1 year)
- 📦 **1,500 units produced** by Nutting Associates
- 🌌 **Based on Spacewar!** (1962, MIT PDP-1)
- ⚫ **Black and white** vector-style display
- 👥 **Two-player** rocket combat game
- 🎛️ **Control panel**: 4 buttons (left, right, fire, thrust)
- 🚀 **Cabinet design**: Futuristic fiberglass (by Nutting)

**Game Logic:**

- Player controls a rocket ship
- Rotate left/right, thrust forward, fire missiles
- UFO opponent shoots back
- Stars backdrop with parallax scrolling
- First to 10 wins (or highest score after 90 seconds)

**Why it matters:**

Computer Space proved that video games could be a **commercial product**. While not a massive success (too complex for bars), it directly led to Atari's founding and the birth of the video game industry.

---

## Project Repository

A reference implementation has been created at:

**https://github.com/[YOUR-USERNAME]/computer-space-miner**

Includes:

- ✅ Python simulator (headless testing)
- ✅ FPGA Verilog implementation
- ✅ ESP32 MicroPython network bridge
- ✅ Build system (Makefile)
- ✅ Documentation

---

**"Welcome to the world of Computer Space!"**

*Let's make the first arcade video game earn its keep in 2026!* 🚀🕹️

---

**Created**: 2026-03-14  
**Bounty Tier**: LEGENDARY (200 RTC / $20 USD)  
**Multiplier**: 3.5× (Vintage Arcade Pioneer)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
