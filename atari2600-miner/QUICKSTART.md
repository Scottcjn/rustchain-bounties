# Quick Start Guide - RustChain Atari 2600 Miner

> Get your 1977 miner up and running in 5 minutes!

---

## ⚡ Quick Build (Windows)

### Step 1: Install Toolchain
```powershell
# Using Chocolatey (recommended)
choco install cc65

# Or download from GitHub:
# https://github.com/cc65/cc65/releases
```

### Step 2: Build ROM
```powershell
cd atari2600-miner
make

# Output: build/rustchain_miner.bin (4 KB)
```

### Step 3: Test in Emulator
```powershell
# Install Stella (if not already)
choco install stella

# Run the ROM
stella build/rustchain_miner.bin
```

---

## ⚡ Quick Build (Linux)

### Step 1: Install Toolchain
```bash
sudo apt update
sudo apt install cc65 stella
```

### Step 2: Build ROM
```bash
cd atari2600-miner
make
```

### Step 3: Test
```bash
stella build/rustchain_miner.bin
```

---

## ⚡ Quick Build (macOS)

### Step 1: Install Toolchain
```bash
brew install cc65
```

### Step 2: Build ROM
```bash
cd atari2600-miner
make
```

### Step 3: Test
```bash
# Download Stella from: https://stella-emu.github.io/
open -a Stella build/rustchain_miner.bin
```

---

## 🎮 Controls

| Input | Action |
|-------|--------|
| Joystick Button | Toggle mining ON/OFF |
| Left/Right | (Future) Cycle hardware badges |
| Up/Down | (Future) View details |

---

## 📺 What You'll See

### Idle State (Black)
```
┌─────────────────┐
│                 │
│   RUSTCHAIN     │
│     MINER       │
│                 │
│   [IDLE]        │
│                 │
└─────────────────┘
```

### Mining State (Green)
```
┌─────────────────┐
│                 │
│   RUSTCHAIN     │
│     MINER       │
│                 │
│  [MINING...]    │
│   Epoch: 0      │
│   Reward: 0 RTC │
│                 │
└─────────────────┘
```

### Attesting State (Orange)
```
┌─────────────────┐
│                 │
│   RUSTCHAIN     │
│     MINER       │
│                 │
│  [ATTESTING]    │
│   ✓ Fingerprint │
│   +2.5x Mult    │
│                 │
└─────────────────┘
```

---

## 🛠️ Troubleshooting

### Error: `ca65: command not found`
```bash
# Install cc65
# See installation steps above
```

### Error: `stella: command not found`
```bash
# Install Stella emulator
# Or open ROM manually in Stella GUI
```

### ROM doesn't display
- Verify ROM file exists: `ls build/rustchain_miner.bin`
- Check file size: should be 4096 bytes
- Try different emulator version

### Controller not responding
- Ensure joystick is mapped in emulator
- Try keyboard input (Space = button)
- Check emulator input settings

---

## 📊 Build Output

```
$ make
⚙  Assembling src/rustchain_miner.asm...
🔗 Linking...
✓ Build complete: build/rustchain_miner.bin
  ROM size: 4096 bytes (4 KB)
  Bounty wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
```

---

## 🧪 Verify Build

```bash
# Check file size
ls -l build/rustchain_miner.bin
# Should show: 4096 bytes

# Verify checksum
sha256sum build/rustchain_miner.bin

# Run info
make info
```

---

## 📁 Project Structure

```
atari2600-miner/
├── README.md           ← Start here
├── QUICKSTART.md       ← You are here
├── ARCHITECTURE.md     ← Technical details
├── Makefile            ← Build system
├── linker.cfg          ← Memory layout
├── src/
│   └── rustchain_miner.asm
├── docs/
│   └── MEMORY_MAP.md
└── build/
    └── rustchain_miner.bin
```

---

## 🎯 Next Steps

1. ✅ Build the ROM
2. ✅ Test in emulator
3. 📸 Take screenshots
4. 📝 Submit bounty claim
5. 💰 Receive 200 RTC!

---

## 📚 More Info

- **Full Documentation**: See `README.md`
- **Technical Specs**: See `ARCHITECTURE.md`
- **Memory Details**: See `docs/MEMORY_MAP.md`
- **Bounty Info**: See `PR_DESCRIPTION.md`

---

## 🆘 Need Help?

1. Check `README.md` for detailed instructions
2. Review `ARCHITECTURE.md` for technical details
3. Open an issue on GitHub
4. Join RustChain Discord/Telegram

---

**Happy Mining on Vintage Hardware! 🎮**

*Bounty #426 - LEGENDARY Tier (200 RTC)*  
*Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`*
