# ZX Spectrum RustChain Miner

Port of the RustChain miner to the ZX Spectrum (1982) - the iconic 8-bit home computer that defined British computing.

![ZX Spectrum](https://upload.wikimedia.org/wikipedia/commons/2/23/Sinclair_ZX_Spectrum_48K.jpg)

## Overview

This project enables real ZX Spectrum hardware to participate in the RustChain network through Proof-of-Antiquity mining. The miner runs natively on the Z80 CPU and uses hardware fingerprinting to prove it's running on authentic 1982 hardware.

**Bounty:** 100 RTC ($10 USD)  
**Antiquity Multiplier:** 3.5×  
**Wallet:** `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
**Issue:** [#420](https://github.com/RustChain/rustchain-bounties/issues/420)

## Hardware Requirements

### Minimum

- ZX Spectrum 48K (or compatible clone)
- Serial interface (ZXpand+, DivMMC, or custom)
- PC with Python 3.x (for network bridge)
- Power supply

### Recommended

- ZX Spectrum 48K (original Sinclair)
- ZXpand+ interface ($60-80)
- Real hardware for final testing (emulators detected!)

## Quick Start

### 1. Build the Miner

**Using z88dk (C):**

```bash
# Install z88dk: https://z88dk.org/site/

zcc +zx -vn -O3 -o miner.tap src/main.c
```

**Using Pasmo (Assembly):**

```bash
# Install Pasmo: http://pasmo.speccy.org/

pasmo src/main.asm miner.tap
```

### 2. Load on Hardware

**Via Cassette Emulation (TAP file):**

1. Connect PC audio output to Spectrum EAR input
2. Use tool like `tap2wav` or load directly in emulator
3. On Spectrum: `LOAD ""`
4. `RUN`

**Via ZXpand+ (SD Card):**

1. Copy `miner.tap` to SD card
2. Insert SD card in ZXpand+
3. On Spectrum: `LOAD ""`
4. `RUN`

### 3. Connect Serial Bridge

```bash
# Install Python dependencies
pip install pyserial requests

# Run PC bridge
python tools/pc_bridge.py
```

### 4. Verify Attestation

Check that your ZX Spectrum appears in the miner list:

```bash
curl https://rustchain.org/api/miners | jq .
```

## Project Structure

```
zx-spectrum-miner/
├── src/
│   ├── main.asm            # Entry point, main loop
│   ├── miner.asm           # Core miner logic
│   ├── network.asm         # Serial communication
│   ├── fingerprint.asm     # Hardware fingerprinting
│   ├── sha256.asm          # SHA-256 implementation
│   └── ui.asm              # User interface
├── include/
│   ├── zx.inc              # ZX Spectrum hardware defines
│   └── serial.inc          # Serial protocol constants
├── tools/
│   ├── pc_bridge.py        # Python network bridge
│   └── build.bat           # Windows build script
├── docs/
│   ├── wiring.md           # Serial interface wiring
│   └── protocol.md         # Communication protocol
├── README.md
├── BOUNTY.md               # Bounty details
├── IMPLEMENTATION_PLAN.md  # Full implementation plan
└── miner.tap               # Output binary
```

## Technical Specifications

### Hardware Target

| Component | Specification |
|-----------|--------------|
| **CPU** | Z80 @ 3.5469 MHz |
| **RAM** | 48 KB |
| **ROM** | 16 KB (Sinclair BASIC) |
| **Display** | 256×192, 15 colors (attribute-based) |
| **I/O** | ULA port ($FE), Serial via expansion |

### Memory Usage

| Component | Allocation |
|-----------|------------|
| Network stack | ~8 KB |
| Miner runtime | ~10 KB |
| SHA-256 workspace | ~4 KB |
| Attestation data | ~2 KB |
| Display/UI | ~6 KB |
| Stack/variables | ~2 KB |
| **Free** | **~16 KB** |

### Performance

| Metric | Value |
|--------|-------|
| SHA-256 time | ~5-10 seconds |
| Serial baud | 9600 |
| Attestation epoch | 10 minutes |
| Power consumption | ~4W |

## Hardware Fingerprinting

The miner collects several hardware-specific values to prove it's running on real ZX Spectrum hardware:

1. **ROM Checksum**: Different ROM versions have unique checksums
2. **ULA Timing**: ULA contention causes CPU slowdowns during display
3. **DRAM Refresh**: Z80 DRAM refresh has analog variance
4. **Crystal Variance**: Actual CPU clock varies (3.5469 MHz ± tolerance)

### Anti-Emulation

The miner detects emulators (Fuse, ZEsarUx, etc.) by:
- Measuring timing variance (emulators have perfect timing)
- Testing undocumented Z80 flags
- Checking ULA contention behavior
- DRAM refresh timing analysis

**Note:** Emulators will be detected and rejected. Real hardware required!

## Serial Protocol

### Message Format

```
ZX Spectrum → PC Bridge:
  ATTEST:{"device_arch":"zx_z80","wallet":"RTC..."}

PC Bridge → ZX Spectrum:
  ACK:OK:0.0042
  ACK:FAIL:error_message

PC Bridge → ZX Spectrum:
  CHALLENGE:abc123...

ZX Spectrum → PC Bridge:
  STATUS:mining
```

### Wiring (Custom Serial)

```
ZX Spectrum Edge Connector    Arduino/ESP32
Pin 1 (+5V)        ─────────► VCC
Pin 2 (GND)        ─────────► GND
Pin 6 (IORQ)       ─────────► Custom logic
Bit-banged TX      ─────────► RX (GPIO)
Bit-banged RX      ─────────► TX (GPIO)
```

See `docs/wiring.md` for detailed diagrams.

## Development

### Toolchain Setup

**Windows:**

```powershell
# z88dk
choco install z88dk

# Pasmo
choco install pasmo

# Fuse emulator
choco install fuse-emulator
```

**Linux:**

```bash
# z88dk
sudo apt install z88dk

# Pasmo
sudo apt install pasmo

# Fuse
sudo apt install fuse-emulator
```

### Build

```bash
# C version
zcc +zx -vn -O3 -o miner.tap src/main.c

# Assembly version
pasmo src/main.asm miner.tap

# Clean
make clean
```

### Test in Emulator

```bash
fuse miner.tap
```

**Note:** Emulators are detected! Use for development only. Final testing requires real hardware.

## Troubleshooting

### Build Fails

- Ensure z88dk or Pasmo is in PATH
- Check for missing include files
- Verify source file encoding (ASCII)

### Serial Communication Fails

- Check baud rate matches (9600)
- Verify wiring (TX↔RX crossover)
- Test with loopback (connect TX to RX)

### Attestation Rejected

- Verify wallet address format
- Check hardware fingerprint collection
- Ensure real hardware (not emulator)

### Out of Memory

- Reduce buffer sizes
- Use 128K Spectrum model
- Optimize SHA-256 workspace

## Proof of Mining

### Required

1. **Photo**: ZX Spectrum running miner with visible timestamp
2. **Video**: 30+ second attestation cycle
3. **Network Proof**: Screenshot from `rustchain.org/api/miners`
4. **Hardware Info**: ROM checksum, ULA fingerprint values

### Example

![Mining Photo](docs/photo-example.jpg)

*ZX Spectrum 48K mining RustChain. Note the "ATTESTING..." status and epoch timer.*

## Bounty Claim

To claim the 100 RTC bounty:

1. Complete implementation on real hardware
2. Collect proof (photo, video, network screenshot)
3. Open PR to `rustchain-bounties` with:
   - Link to this repository
   - Proof files
   - Attestation ID
4. Comment on issue #420 with:
   - PR link
   - Wallet address
   - Implementation notes

**Wallet:** `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Resources

- [z88dk Documentation](https://z88dk.org/site/)
- [Fuse Emulator](https://fuse-emulator.sourceforge.io/)
- [World of Spectrum](https://worldofspectrum.org/)
- [ZXpand+](https://www.zxpand.com/)
- [Z80 Instruction Set](http://www.z80.info/z80code.htm)

## FAQ

**Q: Can I use a ZX Spectrum clone?**

A: Yes! Timex Sinclair, Didaktik, and other Z80-based clones qualify for the same multiplier.

**Q: Do I need ZXpand+?**

A: No. You can build a custom serial interface with Arduino/ESP32 for ~$20.

**Q: How long does SHA-256 take?**

A: Approximately 5-10 seconds on real hardware. This is acceptable for 10-minute epochs.

**Q: Can I test in an emulator?**

A: For development, yes. But emulators are detected and rejected for bounty claims. Real hardware required.

**Q: What if I don't have a ZX Spectrum?**

A: They're available on eBay for $50-150. Consider it an investment in retro computing!

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Sir Clive Sinclair for creating the ZX Spectrum
- The ZX Spectrum homebrew community
- RustChain for the Proof-of-Antiquity concept

---

*The machine that brought computing to the masses in 1980s Britain, now mining cryptocurrency in 2026. From BASIC to blockchain.*

**Happy mining!** 🖥️⛏️
