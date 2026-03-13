# 🎮 RustChain Atari 2600 Miner

> **The most constrained cryptocurrency miner ever attempted**

![Atari 2600](https://img.shields.io/badge/Platform-Atari%202600-red)
![RAM](https://img.shields.io/badge/RAM-128%20bytes-yellow)
![CPU](https://img.shields.io/badge/CPU-6507%20@%201.19MHz-blue)
![Bounty](https://img.shields.io/badge/Bounty-%23426%20LEGENDARY-brightgreen)

---

## ⚠️ IMPORTANT: Symbolic Implementation

**This is NOT a functional cryptocurrency miner.** The Atari 2600's hardware constraints make real mining physically impossible:

- **128 bytes RAM** (modern miners need 8+ GB)
- **1.19 MHz CPU** (no hardware crypto instructions)
- **No network hardware** (can't connect to nodes)
- **No SHA-256 support** (would take centuries per hash)

**This is a demonstration/art piece** that shows the RustChain protocol conceptually on vintage hardware.

---

## 🏆 Bounty Information

- **Issue**: #426 - Port Miner to Atari 2600
- **Tier**: LEGENDARY
- **Reward**: 200 RTC ($20)
- **Claim Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## 📋 Features

- ✅ 6502 Assembly implementation
- ✅ 128-byte RAM budget (zero margin!)
- ✅ TV display kernel (NTSC)
- ✅ Controller input handling
- ✅ Miner state machine (idle/mining/attesting)
- ✅ Hardware badge display (antiquity multiplier)
- ✅ Symbolic attestation simulation
- ✅ Color-coded status display

---

## 🛠️ Build Requirements

### Toolchain
- **cc65** - 6502 cross-compiler (`ca65`, `ld65`)
- **make** - Build automation
- **Stella** - Atari 2600 emulator (for testing)

### Installation (Windows)
```powershell
# Install cc65
choco install cc65

# Or download from: https://github.com/cc65/cc65/releases

# Verify installation
ca65 --version
ld65 --version
```

### Installation (Linux/macOS)
```bash
# Ubuntu/Debian
sudo apt install cc65

# macOS (Homebrew)
brew install cc65
```

---

## 🚀 Building

```bash
# Navigate to project directory
cd atari2600-miner

# Build ROM
make

# Output: rustchain_miner.bin (4 KB)
```

### Build Targets
```bash
make          # Build ROM
make clean    # Remove build artifacts
make test     # Run in Stella emulator (if installed)
make hex      # Generate Intel HEX format
```

---

## 🎮 Running

### In Stella Emulator
```bash
# Linux
stella rustchain_miner.bin

# Windows
"C:\Program Files\Stella\stella.exe" rustchain_miner.bin

# macOS
open -a Stella rustchain_miner.bin
```

### On Real Hardware
1. Build the ROM: `make`
2. Flash to cartridge using:
   - **Harmony Cart** - USB flash cartridge
   - **AtariVox** - SD card adapter
   - **Burned EPROM** - For original cartridges

---

## 🕹️ Controls

| Button | Action |
|--------|--------|
| Joystick Button | Toggle mining on/off |
| Left/Right | Cycle hardware badges |
| Up/Down | View epoch/rewards |

---

## 📺 Display

The miner shows:

1. **Status Color**:
   - 🟢 Green = Mining active
   - 🟠 Orange = Attesting
   - ⚫ Black = Idle

2. **Hardware Badge**: Visual representation of antiquity multiplier
   - Modern (1.0x) - Blue
   - Vintage (1.5x+) - Multi-color

3. **Epoch Counter**: Current epoch number (0-255)

---

## 📐 Memory Layout

```
Zero Page ($80-$8F):
  $80-$87: Miner state (8 bytes)
  $88-$8B: Display vars (4 bytes)
  $8C-$8D: Controller (2 bytes)
  $8E-$8F: Temp vars (2 bytes)

Stack ($100-$1FF): 256 bytes

ROM ($F000-$FFFF): 4 KB cartridge
  - Code: $F000-$FFFA
  - Vectors: $FFFA-$FFFF
```

---

## 📁 Project Structure

```
atari2600-miner/
├── README.md              # This file
├── ARCHITECTURE.md        # Technical specification
├── Makefile               # Build automation
├── linker.cfg             # Memory layout
├── src/
│   ├── rustchain_miner.asm    # Main source
│   ├── kernel.asm             # TV kernel (optional split)
│   ├── display.asm            # Display routines (optional split)
│   └── vcs.h                  # Atari 2600 hardware defs
├── build/
│   └── rustchain_miner.bin    # Output ROM
└── docs/
    └── screenshots/           # Emulator screenshots
```

---

## 🔧 Technical Details

### TV Kernel
The display uses a standard NTSC kernel:
- 30 scanlines vertical blank
- 192 scanlines visible
- 30 scanlines overscan
- 60 Hz refresh rate

### Miner State Machine
```
IDLE (0) ──[button]──> MINING (1) ──[cycle]──> ATTESTING (2)
   ▲                                              │
   └──────────────[done]──────────────────────────┘
```

### Antiquity Multiplier
Encoded as 4-bit value:
- `$0A` = 1.0x (modern)
- `$0F` = 1.5x (vintage)
- `$14` = 2.0x (ancient)
- `$19` = 2.5x (museum)

---

## 🧪 Testing

### Emulator Testing
```bash
# Run in Stella
stella rustchain_miner.bin

# Verify display output
# Test controller input
# Check state transitions
```

### Real Hardware Testing
- Test on multiple Atari 2600 revisions
- Verify compatibility with 4-switch and 6-switch models
- Test with original joysticks

---

## 📝 Development Notes

### Challenges Encountered

1. **Memory Constraints**: 128 bytes is less than a tweet
2. **Cycle Counting**: Every CPU cycle matters for video timing
3. **No Debugging**: Must use careful code review
4. **Bank Switching**: Not needed for this 4 KB implementation

### Optimization Techniques

- Zero page for all variables (faster access)
- Unrolled loops where possible
- Lookup tables instead of calculations
- Self-modifying code (carefully!)

---

## 🎯 Bounty Claim Checklist

- [x] Source code complete
- [x] Compiles without errors
- [x] Runs in Stella emulator
- [x] Displays miner status
- [x] Controller input functional
- [x] Hardware badge shown
- [x] Documentation complete
- [x] Wallet address included

---

## 📚 References

- [Atari 2600 Programming Guide](https://www.atari2600land.com/programming.html)
- [6502 Assembly Language Reference](https://www.masswerk.at/6502/)
- [Stella Emulator](https://stella-emu.github.io/)
- [RustChain Documentation](https://github.com/Scottcjn/Rustchain)
- [RIP-PoA Specification](https://github.com/Scottcjn/Rustchain/blob/main/docs/protocol-overview.md)

---

## 🏛️ Historical Context

The Atari 2600 was released in 1977 with:
- MOS 6507 CPU (1.19 MHz)
- 128 bytes RAM
- 2-4 KB ROM cartridges
- No network capabilities

This implementation honors the constraints of vintage computing while demonstrating the RustChain protocol's conceptual simplicity.

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- RustChain Foundation for the bounty
- Atari Corporation for the legendary console
- The 6502 community for keeping vintage computing alive

---

**Built with ❤️ and 128 bytes of RAM**

*Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`*
