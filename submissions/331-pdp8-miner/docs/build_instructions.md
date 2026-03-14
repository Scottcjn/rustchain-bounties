# Build Instructions for PDP-8 Miner

## Quick Start

The easiest way to run the PDP-8 miner is using the Python simulator:

```bash
cd pdp8-miner
python pdp8_simulator.py
```

## Option 1: Python Simulator (Recommended)

### Requirements

- Python 3.8 or later
- No external dependencies

### Running

```bash
python pdp8_simulator.py
```

### Expected Output

```
============================================================
  PDP-8 Simulator v1.0
  RustChain Miner - Bounty #394
  Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
============================================================

============================================================
RustChain PDP-8 Miner (1965)
============================================================
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
Memory: 4096 words × 12 bits = 6144 bytes
Antiquity Multiplier: 5.0x (LEGENDARY)
============================================================

[Epoch 1/5]
Collecting hardware entropy...
  Timestamp: 2026-03-14T03:25:03.416382
  Hardware FP: D85
  Attestation: 7D7
  Multiplier: 5.0x
  [OK] Attestation submitted

...

[SUCCESS] Bounty #394 submission ready!
```

## Option 2: SIMH PDP-8 Emulator

### Installing SIMH

#### Windows

```powershell
# Download pre-built binaries
# Visit: https://simh-history.com/

# Or build from source:
git clone https://github.com/simh/simh.git
cd simh
# Use Visual Studio or MinGW to build
```

#### Linux/macOS

```bash
git clone https://github.com/simh/simh.git
cd simh
make
```

### Assembling the Miner

The PDP-8 assembly code (`pdp8_miner.pal`) needs to be assembled using PAL-III.

#### Using `pal3` (PAL-III emulator)

```bash
# Download PAL-III from:
# http://www.pdp8.net/pal.shtml

pal3 pdp8_miner.pal
```

This produces:
- `pdp8_miner.bin` - Binary paper tape format
- `pdp8_miner.lst` - Listing file

### Running in SIMH

```bash
# Start PDP-8 emulator
simh> pdp8

# Load the miner program
simh> load pdp8_miner.bin

# Set paper tape reader (if using offline mode)
simh> attach ptp0 attestations.ptp

# Start execution
simh> go

# View memory (optional)
simh> examine 0-100

# Stop execution
simh> quit
```

## Option 3: Real PDP-8 Hardware

### Requirements

- PDP-8 system (any model: Straight-8, 8/S, 8/E, 8/I, etc.)
- Paper tape reader/punch
- Console terminal (ASR-33 or similar)
- Optional: DECtape for storage

### Loading the Program

1. **Assemble on modern system** using PAL-III
2. **Punch to paper tape**:
   ```bash
   # Convert binary to paper tape format
   python create_paper_tape.py pdp8_miner.bin > miner.ptp
   
   # Punch using paper tape punch
   punch < miner.ptp
   ```

3. **Load on PDP-8**:
   - Mount paper tape on reader
   - Set switches to address 0
   - Press LOAD
   - Press START

### Running the Miner

```
READY
RUN MINER

RUSTCHAIN PDP-8 MINER (1965)
WALLET: RTC4325AF95D26D59C3EF025963656D22AF638BB96B
EPOCH: 1
ENTROPY: COLLECTING...
ATTESTATION: SUBMITTED

...
```

## Option 4: Intersil 6100 Development System

For the CMOS PDP-8 implementation:

### Hardware Setup

- Intersil 6801 Development Kit
- IM6100 CPU
- IM6101 PIE (I/O)
- IM6102 MEDIC (memory extension)
- IM6312 ODT Monitor ROM

### Loading Program

1. Use ODT (Octal Debugging Technique) monitor
2. Enter program via front panel switches
3. Or load from cassette tape (if equipped)

```
ODT> R
ODT> 0200/ 7200  (CLA instruction)
ODT> 0201/ ...
ODT> G 200
```

## Testing

### Unit Tests

```bash
cd pdp8-miner
python -m pytest tests/
```

### Manual Testing

1. **Test CPU instructions**:
   ```bash
   python -c "from pdp8_simulator import PDP8CPU; cpu = PDP8CPU(); cpu.run()"
   ```

2. **Test entropy collection**:
   ```bash
   python -c "from pdp8_simulator import *; cpu = PDP8CPU(); miner = RustChainMiner(cpu); miner.collect_entropy()"
   ```

3. **Test wallet generation**:
   ```bash
   python -c "from pdp8_simulator import *; cpu = PDP8CPU(); miner = RustChainMiner(cpu); print(miner.generate_wallet())"
   ```

## Debugging

### PAL-III Assembly

Common issues:

1. **Syntax errors**: Check for missing commas, incorrect octal
2. **Address errors**: Ensure labels don't overlap
3. **Infinite loops**: Check ISZ and skip conditions

Use the listing file (`.lst`) to verify assembly:

```
LOC  CODE   SYMBOL    MNEMONIC
0200 7200   START     CLA
0201 7100             CLL
0202 7001             IAC
```

### Python Simulator

Enable debug output:

```python
# Add to pdp8_simulator.py
DEBUG = True

def execute(self, instruction):
    if DEBUG:
        print(f"PC={self.pc:04o} IR={instruction:04o}")
    ...
```

### SIMH Debugging

```bash
simh> pdp8
simh> load pdp8_miner.bin
simh> deposit pc 200      / Set program counter
simh> break 250           / Set breakpoint
simh> go                  / Run until breakpoint
simh> examine ac          / Check accumulator
simh> examine 0-20        / Check memory
```

## Performance Tuning

### Memory Optimization

- Use page 0 for frequently accessed variables
- Minimize indirect addressing (saves cycles)
- Reuse temporary storage locations

### Speed Optimization

- Unroll loops where possible
- Use ISZ for loop counters
- Minimize memory references

## Troubleshooting

### "Paper tape file not found"

This is normal if you haven't assembled the PAL source. The simulator includes a built-in miner implementation.

### Unicode encoding errors

On Windows with non-UTF8 console:

```bash
# Set UTF-8 encoding
set PYTHONIOENCODING=utf-8
python pdp8_simulator.py
```

### SIMH won't start

Ensure you have the correct PDP-8 emulator:

```bash
# List available emulators
simh> ?

# Should include: pdp8
```

## Next Steps

After successful build:

1. Run miner for multiple epochs
2. Verify attestations are generated
3. Submit to RustChain network
4. Claim bounty with wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

**For RustChain Bounty #394**
Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
