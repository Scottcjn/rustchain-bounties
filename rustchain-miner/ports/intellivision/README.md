# Intellivision (1979) Port

**LEGENDARY Tier Bounty #455** - 200 RTC ($20)

## Quick Start

```bash
# Test the CP1610 simulator
python intellivision_simulator.py

# Run the miner (simulated mode)
python intellivision_miner.py

# Run with custom wallet
python intellivision_miner.py RTC4325af95d26d59c3ef025963656d22af638bb96b

# Test fingerprint only
python intellivision_miner.py --test-only

# Mine multiple epochs
python intellivision_miner.py --epochs 5

# Live mode (submit to node)
python intellivision_miner.py --live
```

## Wallet

`RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Files

- `intellivision_simulator.py` - CP1610 CPU instruction set simulator
- `intellivision_miner.py` - RustChain miner adapted for Intellivision
- `INT1610_PORT.md` - Detailed port documentation
- `assembly/miner.asm` - CP1610 assembly source code

## Architecture

| Feature | Specification |
|---------|---------------|
| **Console** | Mattel Intellivision |
| **Year** | 1979 |
| **CPU** | General Instrument CP1610 |
| **Clock** | 894.889 kHz |
| **Architecture** | 16-bit CISC |
| **RAM** | 1 KB |
| **ROM** | 6 KB |
| **Registers** | 8 × 16-bit (R0-R7) |

## Bounty

| Field | Value |
|-------|-------|
| **Bounty #** | 455 |
| **Tier** | LEGENDARY |
| **Reward** | 200 RTC ($20) |

🎮 **GAME ON!** 🎮
