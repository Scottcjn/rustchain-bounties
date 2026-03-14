# Computer Space (1971) RustChain Miner Port

## 🏆 LEGENDARY Tier Bounty - 200 RTC ($20)

**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Overview

Port the RustChain miner to **Computer Space (1971)** - the first commercial arcade video game ever made!

Computer Space was built by **Nutting Associates** and designed by **Nolan Bushnell** (who later founded Atari). Unlike modern systems, it had:

- **NO CPU** - Pure 7400-series TTL logic chips
- **NO RAM** - Hardwired state machines
- **NO Microprocessor** - Discrete logic gates only
- **~74 TTL chips** - 7400, 7404, 7476, 7493, etc.

This is the **ultimate hardware challenge**: mining cryptocurrency on a machine that predates the microprocessor revolution!

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

### Historical Significance

- **First commercial arcade video game** (predates Pong by 1 year)
- **First video game to use a coin mechanism**
- **Launched the video game industry**
- **Only 1,500 units produced** (extremely rare!)
- **Pure TTL design** - the last of its kind

## The Challenge: Original Hardware vs. Badge Implementation

### Original 1971 Hardware (Extremely Challenging)

The original Computer Space uses:

- **74 TTL logic chips** - Discrete 7400-series ICs
- **Diode matrix** - Game logic programmed via diodes
- **Analog circuits** - For video signal generation
- **Hardwired state machines** - No firmware, pure hardware
- **No digital memory** - Everything is registers and counters

**Conclusion**: The original hardware is theoretically programmable via massive hardware modification, but practically impossible without destroying the machine.

### Badge-Only Solution (Recommended Path)

Create a **modern recreation** that maintains the vintage aesthetic while using programmable hardware:

| Component | Original (1971) | Badge Implementation |
|-----------|-----------------|---------------------|
| **Logic** | 74 TTL chips | FPGA (Lattice iCE40) |
| **Display** | B&W CRT | Original CRT preserved! |
| **Input** | 4 push buttons | Original buttons (preserved) |
| **Memory** | None | FPGA block RAM (64 KB) |
| **Network** | N/A | ESP32 WiFi module |
| **Size** | Full arcade cabinet | Internal PCB replacement |

### Why FPGA?

- **Authentic TTL emulation** - FPGA can replicate 7400-series logic behavior
- **Hardware-level mining** - SHA256 in actual hardware logic
- **Vintage multiplier** - 1971 design = 3.5× antiquity bonus
- **Cultural icon** - First arcade video game ever
- **Technical innovation** - First blockchain miner on pure TTL architecture

## Technical Challenges

### 1. FPGA Development Environment (40 RTC)

**Recommended Toolchain:**

| Tool | Purpose | Link |
|------|---------|------|
| **Yosys** | Open-source FPGA synthesis | https://yosyshq.net/yosys |
| **nextpnr** | Place & route | https://github.com/YosysHQ/nextpnr |
| **icestorm** | Lattice iCE40 toolchain | https://github.com/YosysHQ/icestorm |
| **Verilator** | FPGA simulation | https://www.veripool.org/verilator |
| **RustChain SDK** | clawrtc HTTP API | https://github.com/Scottcjn/clawrtc-rs |

**Setup:**

```bash
# Install FPGA toolchain
sudo apt install yosys nextpnr icestorm-tools verilog

# Install Python dependencies
pip install fusesoc cocotb

# Clone the project
git clone https://github.com/your-username/computer-space-miner.git
cd computer-space-miner/fpga

# Build the bitstream
make build

# Flash to FPGA
make flash
```

**Hardware Required:**

- Lattice iCE40 UP5K FPGA (or iCE40 HX8K)
- ESP32-WROOM module (for WiFi)
- Level shifters (3.3V ↔ 5V)
- Original Computer Space cabinet (preserved!)
- Custom PCB to replace original logic boards
- 3D printed mounting brackets

### 2. TTL Logic Emulation (60 RTC)

**Challenge**: Replicate 74 TTL chips in FPGA fabric.

**Solution**: Create Verilog models of each 7400-series chip used in Computer Space.

```verilog
// 7400 - Quad 2-input NAND gate
module ttl_7400 (
    input [1:0] A, B,
    output [1:0] Y
);
    assign Y = ~(A & B);
endmodule

// 7404 - Hex inverter
module ttl_7404 (
    input [5:0] A,
    output [5:0] Y
);
    assign Y = ~A;
endmodule

// 7476 - Dual JK flip-flop (for state machines)
module ttl_7476 (
    input J, K, CLK, PRE, CLR,
    output Q, QBAR
);
    // JK flip-flop with preset/clear
    // ... (implementation)
endmodule

// 7493 - 4-bit binary counter (for video timing)
module ttl_7493 (
    input CLK, RST,
    output [3:0] Q
);
    // 4-bit ripple counter
    // ... (implementation)
endmodule
```

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

**Challenge**: Generate authentic 1971-era video signal.

**Original Specs:**

- **Resolution**: 280×220 (interlaced)
- **Refresh**: 60 Hz (NTSC)
- **Sync**: Composite sync (3.5V peak-to-peak)
- **Video**: B&W only (1V peak-to-peak)

**FPGA Implementation:**

```verilog
module video_generator (
    input CLK_5MHZ,
    output HSYNC, VSYNC,
    output VIDEO_EN,
    output [1:0] PIXEL
);
    // Computer Space video timing
    // Horizontal: 280 pixels active, 40 blanking
    // Vertical: 220 lines active, 42 blanking
    
    reg [8:0] h_count;
    reg [7:0] v_count;
    
    always @(posedge CLK_5MHZ) begin
        // Horizontal counter
        if (h_count == 319) begin
            h_count <= 0;
            // Generate HSYNC pulse
        end else begin
            h_count <= h_count + 1;
        end
        
        // Vertical counter
        if (h_count == 319 && v_count == 261) begin
            v_count <= 0;
            // Generate VSYNC pulse
        end else if (h_count == 319) begin
            v_count <= v_count + 1;
        end
        
        // Active video region
        VIDEO_EN <= (h_count < 280) && (v_count < 220);
    end
    
    // Pixel output (2-bit grayscale)
    assign PIXEL = (VIDEO_EN) ? game_pixel : 2'b00;
endmodule
```

### 4. Networking Implementation (50 RTC)

**ESP32 WiFi + RustChain HTTP API:**

```python
# network_bridge.py - Runs on ESP32 (MicroPython)
import network
import urequests
import json
import machine
import time

class ComputerSpaceMiner:
    def __init__(self):
        self.wifi_ssid = "YOUR_WIFI"
        self.wifi_pass = "YOUR_PASSWORD"
        self.api_url = "http://rustchain.org/api/attest"
        self.fpga_spi = machine.SPI(1)
        
    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.wifi_ssid, self.wifi_pass)
        while not wlan.isconnected():
            time.sleep(0.5)
        print("WiFi connected!")
        
    def collect_fingerprint(self):
        # Read FPGA fingerprint via SPI
        fingerprint = {
            "device_arch": "computer_space_fpga",
            "device_family": "computer_space_1971",
            "fpga_chip": "lattice_ice40",
            "ttl_chip_count": 74,
            "vintage_year": 1971,
            "hardware_id": self.read_fpga_id(),
            "ttl_emulation_hash": self.get_ttl_hash()
        }
        return fingerprint
    
    def attest_epoch(self):
        self.connect_wifi()
        fp = self.collect_fingerprint()
        
        response = urequests.post(
            self.api_url,
            json=fp,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Attestation successful: {result}")
            return result
        else:
            print(f"Attestation failed: {response.status_code}")
            return None

# Main loop
miner = ComputerSpaceMiner()
while True:
    miner.attest_epoch()
    time.sleep(600)  # 10-minute epoch
```

### 5. Hardware Fingerprinting (50 RTC)

**FPGA-Specific Fingerprint Sources:**

| Check | Description | Emulator Detection |
|-------|-------------|-------------------|
| **FPGA ID** | Lattice unique chip ID | ✗ Emulators fake it |
| **PLL Jitter** | PLL phase noise variance | ✓ Real analog variance |
| **BRAM Timing** | Block RAM access jitter | ✓ Real timing variance |
| **Oscillator Drift** | Crystal frequency drift | ✓ Real crystals drift |
| **Power Signature** | Current consumption pattern | ✓ Analog circuit variance |
| **Temperature** | On-die temp sensor offset | ✓ Manufacturing variance |

**Implementation:**

```python
class FingerprintCollector:
    def __init__(self, fpga):
        self.fpga = fpga
        
    def collect(self):
        fp = {
            "fpga_id": self.read_fpga_efuse(),
            "pll_jitter": self.measure_pll_jitter(),
            "bram_timing": self.measure_bram_timing(),
            "oscillator_drift": self.measure_osc_drift(),
            "power_signature": self.read_power_adc(),
            "temp_offset": self.read_temp_sensor()
        }
        return fp
    
    def detect_emulator(self):
        # Emulators have:
        # - Perfect timing (no jitter)
        # - Deterministic PLL
        # - No power variance
        
        jitter = self.measure_pll_jitter()
        if jitter < 0.001:  # Too perfect
            return True
            
        power_var = self.measure_power_variance()
        if power_var < 0.01:  # Too clean
            return True
            
        return False
```

### 6. SHA256 in FPGA Fabric (60 RTC)

**Challenge**: Implement SHA256 entirely in FPGA logic (no soft CPU).

**Solution**: Hardware SHA256 core in Verilog.

```verilog
module sha256_core (
    input CLK,
    input [511:0] MESSAGE_BLOCK,
    input START,
    output reg [255:0] HASH,
    output DONE
);
    // SHA256 constants
    reg [31:0] K [0:63];
    // ... (initialization)
    
    // Working variables
    reg [31:0] A, B, C, D, E, F, G, H;
    
    // Message schedule
    reg [31:0] W [0:63];
    
    // Compression function (64 rounds)
    integer i;
    always @(posedge CLK) begin
        if (START) begin
            // Initialize working variables
            A <= H0; B <= H1; C <= H2; D <= H3;
            E <= H4; F <= H5; G <= H6; H <= H7;
            
            // 64 rounds
            for (i = 0; i < 64; i = i + 1) begin
                // Σ0, Σ1, Ch, Maj functions
                // ... (SHA256 logic)
            end
            
            // Update hash state
            HASH <= {A+B, C+D, E+F, G+H};
            DONE <= 1;
        end
    end
endmodule
```

**Performance:**

- **Hash rate**: ~100-500 H/s (FPGA parallelism)
- **Power**: ~500 mW (ultra-low!)
- **Logic usage**: ~3,000 LUTs (60% of iCE40 UP5K)

### 7. User Interface (30 RTC)

**Original Control Panel:**

```
+------------------------------------------+
|  COMPUTER SPACE  by Nutting Associates  |
+------------------------------------------+
|                                          |
|    [ROCKET LEFT]    [ROCKET RIGHT]      |
|                                          |
|    [FIRE]           [THRUST]            |
|                                          |
+------------------------------------------+
```

**Button Functions for Mining:**

| Button | Original Function | Mining Function |
|--------|------------------|-----------------|
| **Rocket Left** | Rotate left | Menu navigation ← |
| **Rocket Right** | Rotate right | Menu navigation → |
| **Fire** | Fire missile | Manual attestation |
| **Thrust** | Thrust forward | Start/stop mining |

**Display Overlay:**

```
+------------------------------------------+
| #### RUSTCHAIN MINER v0.1 ####          |
| HARDWARE: COMPUTER SPACE (1971)         |
+------------------------------------------+
|                                          |
| STATUS: [ATTESTING...]                  |
| EPOCH: 00:07:23 REMAINING               |
| EARNED: 0.0042 RTC                      |
|                                          |
| HARDWARE STATS:                         |
| FPGA: LATTICE ICE40 UP5K                |
| TTL CHIPS: 74 (EMULATED)                |
| NET: WiFi (ESP32 BRIDGE)                |
|                                          |
| [F1] PAUSE [F3] MENU [F5] QUIT          |
+------------------------------------------+
```

### 8. Anti-Emulation Checks (40 RTC)

**FPGA Emulator Detection:**

| Check | Real FPGA | Verilator/QEMU |
|-------|-----------|----------------|
| **PLL Jitter** | ✓ Analog variance | ✗ Perfect |
| **BRAM Timing** | ✓ Real variance | ✗ Deterministic |
| **Power Draw** | ✓ Current variance | ✗ Simulated |
| **Oscillator** | ✓ Crystal drift | ✗ Perfect clock |
| **Temperature** | ✓ Thermal noise | ✗ No thermal model |

**Implementation:**

```python
def verify_real_hardware():
    emulator_score = 0
    
    # Check PLL jitter
    jitter = measure_pll_jitter()
    if jitter < 0.001:
        emulator_score += 1
    
    # Check power variance
    power_var = measure_power_variance()
    if power_var < 0.01:
        emulator_score += 1
    
    # Check FPGA ID (should be unique)
    fpga_id = read_fpga_efuse()
    if fpga_id == 0 or fpga_id == 0xDEADBEEF:
        emulator_score += 1
    
    # Check oscillator drift
    drift = measure_osc_drift()
    if drift < 10:  # Too perfect
        emulator_score += 1
    
    return emulator_score < 2  # Allow 1 false positive
```

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

## Multiplier

**Computer Space (1971) FPGA: 3.5× vintage multiplier**

**Justification:**

- 1971 design (55+ years old)
- First commercial arcade video game
- Pure TTL logic (no CPU, no RAM!)
- Extreme rarity (~1,500 units produced)
- Cultural significance (launched video game industry)
- Technical innovation (first hardware-emulated TTL miner)

**Expected Earnings:**

| Metric | Value |
|--------|-------|
| Base reward | 0.12 RTC/epoch |
| With 3.5× multiplier | 0.42 RTC/epoch |
| Per day (144 epochs) | 60.48 RTC |
| Per month | ~1,814 RTC |
| Per year | ~22,075 RTC |

At $0.10/RTC: **~$2,200/year** in mining rewards!

## Skills Required

- **FPGA Development** - Verilog, Yosys, nextpnr, Lattice iCE40
- **Digital Logic Design** - 7400-series TTL, state machines
- **Embedded Systems** - ESP32, MicroPython, WiFi, SPI
- **Hardware Design** - KiCad, PCB design, level shifting
- **3D Modeling** - Fusion 360 for mounting brackets
- **RustChain Protocol** - Attestation API understanding

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

## Getting Started

1. **Comment on the bounty issue**: "I would like to work on this"
2. **Set up development environment**: Yosys + nextpnr + Lattice iCE40
3. **Create a wallet**: `pip install clawrtc && clawrtc wallet create`
4. **Start with Phase 1**: Get LED blinking on FPGA
5. **Post progress updates** in issue comments
6. **Submit PR** when complete with all deliverables

## Payment

- **Milestone payments** available upon request
- **Final payout**: 200 RTC to your wallet address
- **Wallet required**: Include RTC wallet address in PR
- **Verification**: Real hardware proof mandatory before payment

**Bounty Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Notes

- **FPGA implementation** is the only viable path (original TTL is museum-grade)
- **ESP32 chosen** for WiFi + low cost + MicroPython ecosystem
- **Original cabinet** should be preserved (non-destructive installation)
- **Performance** will be excellent (FPGA hardware SHA256)
- **Power consumption**: ~500 mW active, ~10 mW idle

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

## Historical Context: Computer Space (1971)

**Computer Space** was created by **Nolan Bushnell** and **Ted Dabney**, who later founded **Atari** in 1972. Key facts:

- **First video game** to use a coin mechanism
- **First arcade video game** (predates Pong by 1 year)
- **1,500 units produced** by Nutting Associates
- **Based on Spacewar!** (1962, MIT PDP-1)
- **Black and white** vector-style display
- **Two-player** rocket combat game
- **Control panel**: 4 buttons (left, right, fire, thrust)
- **Cabinet design**: Futuristic fiberglass (by Nutting)

**Game Logic:**

- Player controls a rocket ship
- Rotate left/right, thrust forward, fire missiles
- UFO opponent shoots back
- Stars backdrop with parallax scrolling
- First to 10 wins (or highest score after 90 seconds)

**Why it matters:**

Computer Space proved that video games could be a **commercial product**. While not a massive success (too complex for bars), it directly led to Atari's founding and the birth of the video game industry.

---

**"Welcome to the world of Computer Space!"**

*Let's make the first arcade video game earn its keep in 2026!* 🚀🕹️

**Created**: 2026-03-14  
**Bounty Tier**: LEGENDARY (200 RTC / $20 USD)  
**Multiplier**: 3.5× (Vintage Arcade Pioneer)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
