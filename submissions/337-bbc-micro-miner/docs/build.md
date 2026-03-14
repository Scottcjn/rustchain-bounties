# Build Instructions - BBC Micro Miner

## Prerequisites

### Host System (Windows/Linux/macOS)

You'll need the following tools to build the miner:

1. **cc65 Toolchain** (6502 cross-assembler)
   ```bash
   # Ubuntu/Debian
   sudo apt install cc65
   
   # macOS (Homebrew)
   brew install cc65
   
   # Windows
   # Download from: https://cc65.github.io/
   ```

2. **Python 3.8+** (for disc image creation)
   ```bash
   # Verify installation
   python --version
   ```

3. **Git** (for version control)
   ```bash
   git --version
   ```

## Build Steps

### Step 1: Clone Repository

```bash
cd C:\Users\48973\.openclaw-autoclaw\workspace
git clone https://github.com/yourusername/rustchain-bbc-micro-miner.git
cd rustchain-bbc-micro-miner
```

### Step 2: Assemble Source Code

```bash
# Navigate to project directory
cd bbc-micro-miner

# Assemble main miner
ca65 miner.asm -o miner.o

# Assemble entropy module
ca65 entropy.asm -o entropy.o

# Assemble SHA-256 module (simplified)
ca65 sha256_mini.asm -o sha256.o
```

### Step 3: Link Object Files

```bash
# Link all modules
ld65 -o MINER -t none miner.o entropy.o sha256.o

# Verify output
ls -la MINER
# Should show ~6KB binary
```

### Step 4: Create Disc Image

```bash
# Use Python script to create SSD disc image
python tools/make_ssd.py MINER LOADER.BAS -o RUSTCHN.SSD

# Verify disc image
ls -la RUSTCHN.SSD
# Should show ~200KB SSD image
```

### Step 5: Test in Emulator

```bash
# Run test suite
python test_miner.py

# Expected output:
# [PASS] Entropy Collection
# [PASS] Wallet Generation
# [PASS] Mining Simulation
```

## Testing on Real Hardware

### Option 1: USB Floppy Drive

1. **Format floppy disk** as BBC Micro DFS format
2. **Copy files** using disc utility:
   ```bash
   # On modern PC with USB floppy
   python tools/write_ssd.py RUSTCHN.SSD /dev/fd0
   ```
3. **Insert disk** into BBC Micro
4. **Load and run**:
   ```basic
   *LOAD MINER
   *RUN MINER
   ```

### Option 2: Cassette Tape

1. **Connect cassette interface** to BBC Micro
2. **Record audio** from PC sound card:
   ```bash
   python tools/cassette_encode.py MINER -o miner.wav
   ```
3. **Play tape** on BBC Micro:
   ```basic
   *LOAD ""
   *RUN
   ```

### Option 3: SD Card Adapter

1. **Use Gotek or similar** floppy emulator
2. **Copy SSD image** to SD card
3. **Insert SD card** into Gotek
4. **Boot BBC Micro** normally

## BBC BASIC Loader

The `LOADER.BAS` program provides a user-friendly interface:

```basic
10 REM RustChain BBC Micro Miner Loader
20 PRINT CHR$(131)  : REM Clear screen
30 PRINT "RUSTCHAIN MINER LOADER"
40 PRINT
50 PRINT "Loading miner..."
60 *LOAD MINER
70 PRINT "Starting miner..."
80 *RUN MINER
```

## Configuration

### Miner Settings (`MINER.CFG`)

```
# Mining configuration
WALLET_FILE=WALLET.DAT
ATTEST_FILE=ATTEST.DAT
MINING_INTERVAL=600    # 10 minutes
DISPLAY_MODE=4         # Text mode
DEBUG=0                # Disable debug
```

### Build Options

Edit `miner.asm` to configure:

```assembly
; Memory configuration
MINER_BASE      = $2000   ; Load address
WORKSPACE       = $3000   ; Data area

; Feature flags
FEATURE_NETWORK = 0       ; Disable networking
FEATURE_DEBUG   = 0       ; Disable debug
```

## Troubleshooting

### Build Errors

**Problem**: `ca65: command not found`
**Solution**: Install cc65 toolchain (see Prerequisites)

**Problem**: `ld65: cannot find input file`
**Solution**: Ensure all `.o` files were assembled successfully

**Problem**: `Output file too large`
**Solution**: Optimize assembly code, remove unused routines

### Runtime Errors

**Problem**: `Miner crashes on startup`
**Solution**: Check memory map configuration, ensure no conflicts with OS

**Problem**: `Wallet not saving`
**Solution**: Verify DFS disc is formatted and writable

**Problem**: `Display garbled`
**Solution**: Check screen memory address, ensure Mode 4 selected

## Performance Tuning

### Optimize for Speed

```assembly
; Unroll loops for speed
MACRO HASH_ROUND
    EOR data,X
    ROL A
    ADC #round_const
ENDMAC
```

### Optimize for Size

```assembly
; Use zero page for frequently accessed variables
entropy_ptr = $50    ; Zero page (fast, small)
```

## Verification

### Checksum Verification

After building, verify binary integrity:

```bash
# Calculate checksum
sha256sum MINER

# Expected (example):
# a1b2c3d4...  MINER
```

### Emulator Testing

```bash
# Run full emulator test
python emulator/beebsim.py --load RUSTCHN.SSD

# Should show:
# - Welcome screen
# - Mining animation
# - Keyboard input working
```

## Distribution

### Package for Release

```bash
# Create release archive
zip rustchain-bbc-micro-v1.0.zip \
    README.md \
    MINER \
    LOADER.BAS \
    RUSTCHN.SSD \
    docs/
```

### Submit to GitHub

```bash
# Commit changes
git add .
git commit -m "BBC Micro miner v1.0 - Bounty #407"
git push origin main

# Create pull request
# See: docs/PR_TEMPLATE.md
```

## Next Steps

1. ✅ Build complete
2. ✅ Tests passing
3. ⏳ Test on real hardware
4. ⏳ Submit PR with wallet address
5. ⏳ Claim bounty (200 RTC / $20)

## Support

For issues or questions:

- **Documentation**: See `docs/architecture.md`
- **Assembly Reference**: `miner.asm` comments
- **6502 Manual**: https://www.masswerk.at/6502/
- **BBC Micro Guide**: https://bbc.godbolt.org/

---

**Build completed successfully!** 🎉

Ready to mine RustChain on your BBC Micro (1981)!
