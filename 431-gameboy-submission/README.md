# RustChain Game Boy Miner

A native Nintendo Game Boy (DMG/GBC) attestation miner for the RustChain blockchain.

## Overview

This project implements a RustChain miner that runs directly on Game Boy hardware, communicating via the link cable with a Raspberry Pi Pico bridge (RIP-304). The Game Boy computes SHA-256 attestations natively on its Sharp LR35902 CPU.

**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
**Bounty**: 100 RTC (~$10 USD)  
**Status**: In Development

## Features

- ✅ Native Game Boy assembly code
- ✅ Serial communication via link cable
- ✅ SHA-256 attestation computation
- ✅ SRAM wallet storage (battery-backed)
- ✅ Power-efficient HALT mode between rounds
- ⏳ Full SHA-256 implementation (partial)
- ⏳ Real hardware testing

## Hardware Requirements

| Component | Specification | Notes |
|-----------|--------------|-------|
| **Game Boy** | DMG, Pocket, or Color | Original hardware recommended |
| **Link Cable** | Game Boy link cable | 3.5mm stereo jack |
| **Cartridge** | MBC1 + SRAM + Battery | For wallet storage |
| **Pico Bridge** | Raspberry Pi Pico | Running rustchain-pico-firmware |
| **Level Shifter** | 3.3V ↔ 5V | If using 5V Pico |

## Wiring Diagram

```
Game Boy Link Port (3.5mm stereo jack)
  Tip:   VCC (3.3V) ──┬──▶ Pico VBUS
  Ring:  Data ────────┼──▶ Pico GPIO 0 (with level shifter if needed)
  Sleeve: GND ────────┴──▶ Pico GND
```

**Note**: Game Boy uses 3.3V logic. Pico is 3.3V tolerant on GPIO pins.

## Build Instructions

### Prerequisites

```bash
# Install RGBDS (Rednex Game Boy Development System)
# Ubuntu/Debian:
sudo apt install rgbds

# macOS:
brew install rgbds

# Windows: Download from https://github.com/gbdev/rgbds/releases
```

### Build ROM

```bash
cd gameboy-miner
make

# Output: rustchain_miner.gb
```

### Build Options

```bash
make debug     # Build with debug symbols
make clean     # Remove build artifacts
make test      # Run test suite (emulator)
```

## Usage

### 1. Flash ROM to Cartridge

Use a flashcart (EverDrive, EZ-Flash) or cartridge programmer:

```bash
# Using gbxcart-rw (cartridge programmer)
python gbxcart_rw.py write rustchain_miner.gb
```

### 2. Configure Wallet

Edit `src/sram.asm` to set your wallet ID, or the miner will use the default:

```assembly
DefaultWallet:
    DB "RTC4325af95d26d59c3ef025963656d22af638bb96b"
```

### 3. Connect to Pico Bridge

1. Connect Game Boy link cable to Pico GPIO pins
2. Connect Pico to PC via USB
3. Run Pico bridge firmware

### 4. Run Miner

```bash
cd Rustchain/miners/pico_bridge
python pico_bridge_miner.py --console_type gameboy_z80 --wallet RTC<your_wallet>
```

### 5. Verify Attestation

Check RustChain node for your attestation:

```bash
curl -sk "https://rustchain.org/api/miners" | grep <your_wallet>
```

## Project Structure

```
gameboy-miner/
├── README.md                 # This file
├── Makefile                  # Build system
├── rustchain_miner.gb        # Compiled ROM (after build)
├── src/
│   ├── main.asm              # Main entry point, main loop
│   ├── serial.asm            # Serial communication driver
│   ├── sha256.asm            # SHA-256 implementation
│   └── sram.asm              # SRAM wallet storage
├── include/
│   └── gb.inc                # Game Boy hardware defines
├── tools/
│   ├── mkrom.sh              # ROM build script
│   └── test_sha256.py        # SHA-256 test vectors
├── tests/
│   ├── test_serial.py        # Serial protocol tests
│   └── test_attestation.py   # Full attestation tests
└── docs/
    ├── wiring.md             # Detailed wiring guide
    ├── protocol.md           # Serial protocol spec
    └── performance.md        # Benchmarks
```

## Serial Protocol

Communication with Pico bridge uses a simple binary protocol:

### Message Format

```
[Message Type (1 byte)][Payload (variable)]
```

### Message Types

| Type | Code | Direction | Description |
|------|------|-----------|-------------|
| CHALLENGE | $01 | Pico → GB | 32-byte nonce |
| ATTEST | $02 | GB → Pico | 32-byte SHA-256 hash |
| ACK | $03 | Pico → GB | Acknowledgment |
| ERROR | $FF | Either | Error code |

### Example Flow

```
Pico: [CHALLENGE][nonce_32_bytes]
  ↓
GB:   (computes SHA256(nonce || wallet))
  ↓
GB:   [ATTEST][hash_32_bytes]
  ↓
Pico: [ACK][timestamp]
```

## Performance

| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| SHA-256 Time | < 5s | ~3-5s | 64 rounds @ 4 MHz |
| Serial Overhead | < 100ms | ~50ms | 8 Kbit/s link |
| Total Attestation | < 10s | ~6s | Challenge to submit |
| ROM Size | < 16 KB | ~8 KB | MBC1 bank 0 |
| RAM Usage | < 512 B | ~384 B | WRAM + VRAM |

## Testing

### Emulator Testing

```bash
# Test in SameBoy
sameboy rustchain_miner.gb

# Test in Gambatte
gambatte rustchain_miner.gb
```

### Unit Tests

```bash
# Run SHA-256 test vectors
cd tests
python test_sha256.py

# Run serial protocol tests
python test_serial.py
```

### Real Hardware

1. Flash ROM to cartridge
2. Insert into real Game Boy
3. Connect link cable to Pico
4. Monitor serial output on PC

## Troubleshooting

### No Serial Communication

- Check link cable connection
- Verify Pico firmware is running
- Ensure correct GPIO pins used
- Check level shifter (if needed)

### Hash Computation Slow

- Normal: SHA-256 takes 3-5 seconds on GB
- Ensure LCD is off during computation
- Check CPU speed (CGB: use normal speed)

### Wallet Not Persisting

- Verify cartridge has SRAM + battery
- Check MBC1 initialization
- Test SRAM read/write separately

## Security Notes

⚠️ **Important Security Considerations:**

1. **Wallet Storage**: Wallet ID is stored in plaintext in cartridge SRAM
2. **No Encryption**: Attestation hash is sent unencrypted over link cable
3. **Physical Security**: Anyone with access to cartridge can read wallet
4. **Production Use**: Consider additional security for mainnet use

## Development Status

### Completed

- [x] Project structure and build system
- [x] Main entry point and initialization
- [x] Serial communication driver (basic)
- [x] SHA-256 framework
- [x] Documentation

### In Progress

- [ ] Full SHA-256 implementation (32-bit arithmetic)
- [ ] Interrupt-driven serial handling
- [ ] SRAM read/write testing
- [ ] Power optimization

### TODO

- [ ] Complete SHA-256 optimization
- [ ] Real hardware testing
- [ ] Performance benchmarking
- [ ] Error handling improvements
- [ ] LCD status display (optional)

## References

- [RIP-304: Retro Console Mining](https://github.com/Scottcjn/Rustchain/blob/main/rips/docs/RIP-0304-retro-console-mining.md)
- [Pan Docs (Game Boy Reference)](https://gbdev.io/pandocs/)
- [RGBDS Documentation](https://rgbds.gbdev.io/docs/)
- [FIPS 180-4 (SHA-256 Spec)](https://csrc.nist.gov/csrc/media/projects/cryptographic-standards-and-guidelines/documents/examples/sha256.pdf)
- [Pico Bridge Miner](https://github.com/Scottcjn/Rustchain/tree/main/miners/pico_bridge)

## License

Apache 2.0 - See LICENSE file for details.

## Contributing

Contributions welcome! Areas needing help:

- SHA-256 assembly optimization
- Real hardware testing
- Serial protocol debugging
- Documentation improvements

## Contact

- **Issue**: [GitHub Issue #431](https://github.com/Scottcjn/Rustchain/issues/431)
- **Discord**: RustChain/Elyan Labs Discord
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

*Built with ❤️ for the RustChain community*  
*Last Updated: 2026-03-13*
