# PR Submission Template - C64 Miner Bounty

## Bounty Issue

**Issue**: #1792 - Port RustChain Miner to Commodore 64 — 150 RTC (4.0x Multiplier!)
**URL**: https://github.com/Scottcjn/rustchain-bounties/issues/1792

## Submission Checklist

### Code Requirements

- [x] Complete miner implementation in cc65 C
- [x] Network driver (RR-Net and Userport+ESP32 support)
- [x] Hardware fingerprinting (CIA, VIC-II, SID, ROM)
- [x] Anti-emulation detection
- [x] User interface (40-column text mode)
- [x] JSON builder for attestation payload
- [x] Makefile for building
- [x] Python simulator for testing

### Documentation Requirements

- [x] README.md - Project overview
- [x] QUICKSTART.md - Quick start guide
- [x] docs/BUILD.md - Build instructions
- [x] docs/NETWORK.md - Network setup guide
- [x] docs/FINGERPRINT.md - Fingerprinting details

### Testing Requirements

- [x] Python simulator tests pass
- [x] Attestation payload format correct
- [x] Network simulation works
- [x] Hardware fingerprint generation verified

### Proof Requirements (Real Hardware)

- [ ] **Photo of C64 running miner** (with timestamp)
- [ ] **Video of attestation cycle** (30+ seconds)
- [ ] **Screenshot in /api/miners** showing miner ID
- [ ] **Attestation record** in network database

## Repository

**GitHub**: https://github.com/Scottcjn/Rustchain/tree/c64-miner

**Branch**: `c64-miner`

**Files**:
```
rustchain-c64/
├── src/
│   ├── miner.c           # Main miner logic
│   ├── miner.h
│   ├── network.c         # Network driver
│   ├── network.h
│   ├── fingerprint.c     # Hardware fingerprinting
│   ├── fingerprint.h
│   ├── ui.c              # User interface
│   ├── ui.h
│   ├── json.c            # JSON builder
│   └── json.h
├── simulator/
│   ├── c64_miner_sim.py  # Python simulator
│   └── test_simulator.py # Test suite
├── docs/
│   ├── BUILD.md
│   ├── NETWORK.md
│   └── FINGERPRINT.md
├── Makefile
├── README.md
└── QUICKSTART.md
```

## Technical Specifications

### Hardware Target

- **CPU**: MOS 6510 @ 1.023 MHz (NTSC) / 0.985 MHz (PAL)
- **RAM**: 64 KB
- **Architecture**: 8-bit, no MMU, no FPU
- **Network**: RR-Net cartridge or Userport + ESP32 bridge

### Memory Usage

- **Code size**: ~10 KB
- **Runtime RAM**: ~12 KB
- **Network buffer**: 512 bytes
- **Screen memory**: 1 KB

### Attestation Format

```json
{
  "miner_id": "c64-XXXXXXXX",
  "device": {
    "arch": "6510",
    "family": "commodore_64",
    "cpu_speed": 1023000,
    "total_ram_kb": 64,
    "rom_checksum": 0x77EA
  },
  "signals": {
    "cia_jitter": 42,
    "vic_raster": 64,
    "sid_offset": 137
  },
  "fingerprint": "XXXXXXXXXXXXXXXX",
  "report": {
    "epoch": 0,
    "timestamp": 1710374400
  }
}
```

### Fingerprint Components

1. **CIA Timer Jitter**: 15-85 cycles (real hardware variance)
2. **VIC-II Raster Timing**: 62-66 cycles per line
3. **SID Register Offset**: 1-255 (chip-specific)
4. **Kernal ROM Checksum**: Known values (0x6361, 0x77EA, etc.)

### Anti-Emulation

Detects emulators by:
- Perfect CIA timing (< 10 cycles jitter)
- Exact VIC raster values
- Zero SID readback offset
- Invalid ROM checksums

## Proof of Work

### Simulator Test Results

```
============================================================
RustChain C64 Miner - Test Suite
============================================================

[PASS] Fingerprint test PASSED
[PASS] Miner state test PASSED
[PASS] Attestation payload test PASSED
[PASS] Network simulation test PASSED
[PASS] Full simulation test PASSED

RESULTS: 5 passed, 0 failed

[SUCCESS] All tests PASSED! Ready for deployment.
```

### Real Hardware Proof

**[TO BE COMPLETED]**

- Photo: [Link to photo]
- Video: [Link to video]
- Miner ID: [c64-XXXXXXXX]
- First Attestation: [Timestamp]

## Wallet for Bounty

**RTC Address**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Multiplier Justification

Commodore 64 qualifies for **4.0x multiplier** (maximum tier):

| Criterion | Value | Points |
|-----------|-------|--------|
| Year | 1982 (44 years old) | ✓ |
| RAM | 64 KB (extremely constrained) | ✓ |
| CPU Speed | 1.023 MHz (very slow) | ✓ |
| Networking | No standard solution | ✓ |
| Cultural Impact | Best-selling computer ever | ✓ |
| Market Penetration | 12-17 million units | ✓ |

**Comparison**:
- Ryzen 9 7950X (2022): 1.0x
- PowerPC G4 (2003): 2.5x
- **Commodore 64 (1982): 4.0x** ← Maximum tier
- Apple II (1977): 4.0x

## Build Instructions

### Quick Build

```bash
cd rustchain-c64
make
```

### Test in Simulator

```bash
cd rustchain-c64/simulator
python test_simulator.py
```

### Deploy to Real Hardware

1. Transfer `miner.prg` to C64 (SD2IEC, 1541, or tape)
2. Load: `LOAD "MINER.PRG",8,1`
3. Run: `RUN`
4. Wait for attestation (10 minutes)
5. Verify: https://rustchain.org/api/miners

## Future Enhancements

- [ ] Keyboard input for wallet entry
- [ ] EEPROM storage for wallet
- [ ] Custom charset for nicer UI
- [ ] Datasette motor timing fingerprint
- [ ] Color burst phase detection
- [ ] PAL/NTSC auto-detection

## Acknowledgments

- RustChain team for Proof-of-Antiquity concept
- cc65 team for excellent 6502 compiler
- C64 community for keeping the platform alive
- VICE emulator developers

## License

MIT License - See LICENSE file

---

**Submitted by**: [Your Name/GitHub Username]
**Date**: 2026-03-14
**Contact**: [Your Email/Discord]
