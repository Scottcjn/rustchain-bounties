# Quick Start Guide - Computer Space (1971) Miner

## Prerequisites

### Software

**Windows**:
```powershell
# Install Python 3.10+
winget install Python.Python.3.11

# Install Git
winget install Git.Git
```

**Linux (Ubuntu/Debian)**:
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip git

# Install FPGA tools (for hardware build)
sudo apt install yosys nextpnr icestorm-tools verilator
```

**macOS**:
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and FPGA tools
brew install python3 yosys nextpnr icestorm-tools verilator
```

### Hardware (Optional - for full implementation)

- **Lattice iCE40 UP5K board** (~$25): e.g., [iCE40HX1K-EVB](https://www.latticesemi.com/Products/DevelopmentBoardsAndKits/iCE40HX1KBreakoutBoard.aspx)
- **ESP32 dev board** (~$12): e.g., [ESP32-WROOM](https://www.espressif.com/en/products/socs/esp32)
- **USB cables** for both boards
- **Jumper wires** for connections

---

## Step 1: Clone the Project

```bash
cd C:\Users\48973\.openclaw-autoclaw\workspace
git clone https://github.com/YOUR_USERNAME/computer-space-miner.git
cd computer-space-miner
```

---

## Step 2: Run the Python Simulator (No Hardware Required!)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the simulator
python computer_space_simulator.py
```

**Expected Output**:
```
======================================================================
  COMPUTER SPACE (1971) - TTL Logic Simulator
  First Commercial Arcade Video Game
======================================================================

[ARCADE] Computer Space Simulator Starting...
   Resolution: 280x220
   Duration: 10.0s @ 60 FPS

[STATS] Frame: 540 | FPS: 10.0 | Score: 0 | Time: 81s

[DONE] Simulation Complete!
   Total frames: 600

[MONEY] Attestation #1
   Reward: 0.0147 RTC
   ...
```

---

## Step 3: Build FPGA Bitstream (Linux/Mac Only)

```bash
# Navigate to project directory
cd computer-space-miner

# Build the bitstream
make build

# Expected output:
# ✅ Synthesis complete
# ✅ Place & Route complete
# ✅ Bitstream packed
# ✅ Build complete!
#    Bitstream: computer_space_miner.bit
#    Size: ~150000 bytes
```

**Windows Users**: Use WSL2 (Windows Subsystem for Linux) or a Linux VM.

---

## Step 4: Flash to FPGA (Requires Hardware)

```bash
# Connect FPGA board via USB
# Flash the bitstream
make flash

# Expected output:
# ⚡ Flashing to FPGA...
# ✅ Flash complete!
```

**LED Indicators**:
- `LED_MINING` should blink slowly
- `LED_NETWORK` should be off (no ESP32 yet)
- `LED_ERROR` should be off

---

## Step 5: Deploy ESP32 Firmware (Requires Hardware)

```bash
# Install MicroPython tool
pip install mpremote

# Connect ESP32 via USB
# Erase flash
mpremote flash erase

# Deploy firmware
mpremote cp esp32/network_bridge.py :main.py

# Edit WiFi credentials in network_bridge.py
# SSID and PASSWORD at the top of the file

# Reset ESP32
mpremote reset
```

**Expected Output** (via serial monitor):
```
============================================================
  COMPUTER SPACE (1971) - ESP32 NETWORK BRIDGE
  RustChain Miner
============================================================
✅ FPGA detected
📶 Connecting to WiFi: YOUR_SSID
✅ WiFi connected!
   IP: 192.168.1.100

💰 Submitting attestation #1...
✅ Attestation successful!
   Reward: 0.0147 RTC
```

---

## Step 6: Connect FPGA to ESP32

**Wiring**:

| FPGA Pin | ESP32 Pin | Signal |
|----------|-----------|--------|
| 46 | GPIO 18 | SPI_CLK |
| 47 | GPIO 23 | SPI_MOSI |
| 28 | GPIO 19 | SPI_MISO |
| 29 | GPIO 5 | SPI_CS |
| GND | GND | Ground |
| 3.3V | 3.3V | Power (optional) |

**Note**: Use level shifters if FPGA runs at 5V (most iCE40 boards are 3.3V).

---

## Step 7: Verify Mining

```bash
# Check active miners on RustChain
curl -sk https://rustchain.org/api/miners | jq .

# Look for your wallet address:
# RTC4325af95d26d59c3ef025963656d22af638bb96b
```

---

## Troubleshooting

### Python Simulator Fails

**Error**: `UnicodeEncodeError`
- **Fix**: Already fixed in latest version. Re-pull if needed.

**Error**: `ModuleNotFoundError: No module named 'requests'`
- **Fix**: `pip install -r requirements.txt`

### FPGA Build Fails

**Error**: `yosys: command not found`
- **Fix**: Install Yosys (see Prerequisites)

**Error**: `nextpnr-ice40: command not found`
- **Fix**: Install nextpnr (see Prerequisites)

**Error**: `PCF file pin out of range`
- **Fix**: Check your FPGA board's pinout. Update `fpga/computer_space.pcf`

### ESP32 Fails to Connect

**Error**: `mpremote: command not found`
- **Fix**: `pip install mpremote`

**Error**: `Device not found`
- **Fix**: 
  - Check USB cable
  - Install ESP32 USB drivers
  - Try different USB port

**Error**: `WiFi connection timeout`
- **Fix**: 
  - Check SSID/PASSWORD in `network_bridge.py`
  - Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
  - Move closer to router

---

## Project Structure

```
computer-space-miner/
├── README.md                    # Full documentation
├── PROJECT_SUMMARY.md           # This summary
├── QUICK_START.md               # This file
├── BOUNTY_ISSUE.md              # GitHub issue template
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── Makefile                     # FPGA build system
├── computer_space_simulator.py  # Python simulator ✓ TESTED
├── fpga/
│   ├── computer_space_miner.v   # FPGA Verilog
│   └── computer_space.pcf       # Pin constraints
└── esp32/
    └── network_bridge.py        # ESP32 firmware
```

---

## Resources

- **RustChain Docs**: https://rustchain.org/docs
- **Lattice iCE40**: https://www.latticesemi.com/iCE40
- **Yosys HQ**: https://yosyshq.net/yosys
- **ESP32 Docs**: https://docs.espressif.com
- **Computer Space Museum**: https://www.arcade-museum.com/machine/computer-space

---

## Support

- **GitHub Issues**: https://github.com/YOUR_USERNAME/computer-space-miner/issues
- **RustChain Discord**: https://discord.gg/VqVVS2CW9Q
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

**Happy Mining! 🚀🕹️**
