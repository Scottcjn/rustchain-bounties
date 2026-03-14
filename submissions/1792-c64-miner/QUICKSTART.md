# Quick Start Guide - RustChain C64 Miner

Get started mining RustChain on your Commodore 64 in 5 minutes!

## Prerequisites

- **For testing**: Python 3.x (any OS)
- **For building**: cc65 compiler
- **For real mining**: Commodore 64 + RR-Net cartridge

## Option 1: Test with Simulator (Recommended First)

### Step 1: Run the Simulator

```bash
cd rustchain-c64/simulator

# Run test suite
python test_simulator.py

# Run interactive simulator
python c64_miner_sim.py
```

### Step 2: Verify Output

You should see:
```
[PASS] Fingerprint test PASSED
[PASS] Miner state test PASSED
[PASS] Attestation payload test PASSED
[PASS] Network simulation test PASSED
[PASS] Full simulation test PASSED

[SUCCESS] All tests PASSED! Ready for deployment.
```

### Step 3: Understand the Output

The simulator shows:
- Hardware fingerprint generation
- Attestation payload structure
- Network communication
- Mining rewards calculation

## Option 2: Build for Real Hardware

### Step 1: Install cc65

```bash
# Windows
choco install cc65

# Linux
sudo apt install cc65

# macOS
brew install cc65
```

### Step 2: Build the Miner

```bash
cd rustchain-c64

# Build
make

# Output: miner.prg
```

### Step 3: Test in VICE (Emulator)

```bash
# Run in emulator
make run

# Or manually
x64 miner.prg
```

**Note**: The miner will detect emulation and won't submit attestations.

### Step 4: Deploy to Real C64

#### Using SD2IEC:

1. Copy `miner.prg` to SD card
2. Insert SD card into SD2IEC
3. On C64: `LOAD "MINER.PRG",8,1` then `RUN`

#### Using RR-Net:

1. Insert RR-Net cartridge
2. Connect Ethernet cable
3. Load and run miner

### Step 5: Verify Attestation

1. Wait for first attestation cycle (10 minutes)
2. Check https://rustchain.org/api/miners
3. Look for your miner ID: `c64-XXXXXXXX`
4. Verify 4.0x multiplier

## Wallet Setup

### Using Default Wallet (for testing)

The default wallet is: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

**Note**: This is the bounty wallet. For real mining, use your own!

### Create Your Own Wallet

```bash
# Install clawrtc
pip install clawrtc

# Create wallet
clawrtc wallet create

# Save the address
```

### Update Wallet in Code

Edit `src/miner.c`:

```c
strcpy(g_miner.wallet, "YOUR_WALLET_ADDRESS");
```

Or enter via keyboard (future feature).

## Troubleshooting

### Simulator Won't Run

```bash
# Check Python version
python --version  # Should be 3.x

# Install dependencies (none required)
pip install -r requirements.txt
```

### Build Fails

```bash
# Check cc65 installation
cl65 --version

# Clean and rebuild
make clean
make
```

### Network Issues (Real Hardware)

- Check Ethernet cable connection
- Verify DHCP is enabled on router
- Try static IP configuration (see NETWORK.md)

### Attestation Fails

- Check network connectivity
- Verify rustchain.org is reachable
- Check firewall settings

## Expected Rewards

| Hardware | Multiplier | Reward/Epoch | Reward/Day |
|----------|------------|--------------|------------|
| C64 (1982) | 4.0x | 0.0042 RTC | 0.60 RTC |
| Modern PC | 1.0x | 0.00105 RTC | 0.15 RTC |

**C64 earns 4x more than modern hardware!**

## Next Steps

After successful setup:

1. **Run for 24 hours** - Verify stable operation
2. **Take photos/video** - Document your setup
3. **Check rewards** - Verify in block explorer
4. **Submit PR** - Claim your bounty!

## Bounty Claim Process

1. Complete all requirements:
   - [ ] Code working on real C64
   - [ ] Photo of C64 running miner
   - [ ] Video of attestation cycle
   - [ ] Screenshot in /api/miners
   - [ ] All source code on GitHub

2. Open PR to rustchain-bounties:
   - Link to your repository
   - Include proof images/videos
   - Add wallet address for payout

3. Wait for verification (24-48 hours)

4. Receive 150 RTC bounty!

## Resources

- **Full Documentation**: See docs/ folder
- **Build Guide**: docs/BUILD.md
- **Network Setup**: docs/NETWORK.md
- **Fingerprinting**: docs/FINGERPRINT.md
- **Bounty Issue**: https://github.com/Scottcjn/rustchain-bounties/issues/1792

## Support

- **Discord**: https://discord.gg/VqVVS2CW9Q
- **GitHub Issues**: Open an issue on this repo
- **C64 Community**: https://www.lemon64.com/forum

## FAQ

**Q: Do I need real hardware to test?**
A: No! Use the Python simulator for development and testing.

**Q: Can I use an emulator?**
A: For testing, yes. For real mining and bounty, NO - it will be detected.

**Q: How long does mining take?**
A: Attestation cycle is 10 minutes. Rewards accumulate continuously.

**Q: What if I don't have RR-Net?**
A: Use Userport + ESP32 bridge (cheaper, ~$20). See NETWORK.md.

**Q: Is this profitable?**
A: At 4.0x multiplier: ~0.60 RTC/day = $0.06/day. Bounty is 150 RTC = $15. Main value is the bounty!

---

**Happy Mining! 🖥️⛏️**

The computer that defined a generation is now earning cryptocurrency.
