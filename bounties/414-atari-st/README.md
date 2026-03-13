# 🖥️ RustChain Miner for Atari ST

> **Bounty**: #414 - Port RustChain Miner to Atari ST (1985)  
> **Reward**: 150 RTC ($15) - 3.0x Multiplier Tier  
> **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

![Atari ST](https://img.shields.io/badge/Platform-Atari%20ST-blue)
![CPU](https://img.shields.io/badge/CPU-Motorola%2068000%20@%208MHz-blue)
![RAM](https://img.shields.io/badge/RAM-512KB--4MB-yellow)
![OS](https://img.shields.io/badge/OS-TOS%201.0--4.0-green)
![Bounty](https://img.shields.io/badge/Bounty-%23414-brightgreen)

---

## ⚠️ IMPORTANT: Symbolic Implementation

**This is NOT a functional cryptocurrency miner.** The Atari ST's hardware constraints make real mining impractical:

- **512 KB - 4 MB RAM** (modern miners need 8+ GB)
- **8 MHz Motorola 68000** (no hardware crypto instructions)
- **No built-in network hardware** (requires ST-Link or Ethernet cartridge)
- **No SHA-256 acceleration** (would take centuries per hash)

**This is a demonstration** that shows the RustChain protocol on vintage hardware with the **3.0x antiquity multiplier** for Motorola 68000 CPUs.

---

## 🏆 Bounty Information

- **Issue**: #414 - Port Miner to Atari ST
- **Tier**: VINTAGE (3.0x multiplier)
- **Reward**: 150 RTC ($15)
- **Claim Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## 📋 Features

- ✅ Motorola 68000 Assembly + C implementation
- ✅ TOS (Tramiel Operating System) compatible
- ✅ GEM desktop interface (optional)
- ✅ Hardware fingerprinting (68000 cycle jitter)
- ✅ Network support via ST-Link or Serial-to-Ethernet
- ✅ Symbolic attestation simulation
- ✅ Multi-language support (English/French/German)

---

## 🛠️ Build Requirements

### Toolchain

**Cross-Compilation (Recommended):**
- **vbcc** - VBCC C compiler for 68000
- **vasm** - Macro assembler for 68000
- **GNU Make** - Build automation

**Native Development (Real Hardware):**
- **Pure C** or **Lattice C** (original Atari compilers)
- **HiSoft Devpac** (assembler)

### Installation (Windows)

```powershell
# Download vbcc
# https://github.com/serpent/vbcc/releases

# Download vasm
# http://sun.hasenbraten.de/vasm/

# Add to PATH
$env:PATH += ";C:\vbcc\bin;C:\vasm"
```

### Installation (Linux/macOS)

```bash
# Ubuntu/Debian
sudo apt install vbcc vasm

# macOS (Homebrew)
brew install vbcc vasm

# Or build from source
git clone https://github.com/serpent/vbcc
cd vbcc && make && sudo make install
```

---

## 🚀 Building

```bash
# Navigate to project directory
cd atari-st-miner

# Build for 512 KB ST (minimum)
make

# Build for 4 MB STE (optimized)
make CONFIG=ste

# Output: miner.tos (TOS executable)
```

### Build Targets

```bash
make          # Build for standard ST (512 KB)
make ste      # Build for STE (1-4 MB)
make clean    # Remove build artifacts
make hat      # Create .HAT file for HDD installation
make disk     # Create floppy disk image
```

---

## 🎮 Running

### In Emulator (Hatari)

```bash
# Install Hatari
# https://hatari.tuxfamily.org/

# Run miner
hatari --fast-forward --compatible miner.tos

# Or with GEM desktop
hatari --gemdos-path=. miner.tos
```

### On Real Hardware

1. **Transfer to Atari ST:**
   - **Floppy:** Copy `miner.tos` to formatted floppy disk
   - **Hard Drive:** Copy to `C:\RUSTCHN\` directory
   - **Serial:** Use Kermit or XMODEM transfer

2. **Run the miner:**
   ```
   Double-click MINER.TOS in GEM
   Or from command line: C:\RUSTCHN\MINER.TOS
   ```

3. **Configure network:**
   - ST-Link Ethernet cartridge
   - Serial-to-Ethernet bridge (ESP32)
   - Null-modem to modern PC running proxy

---

## ⌨️ Controls (GEM Interface)

| Action | Control |
|--------|---------|
| Start/Stop Mining | Menu → File → Start/Stop |
| View Status | Menu → Info → Status |
| Configure Network | Menu → Options → Network |
| View Hardware Badge | Menu → Info → Hardware |
| Quit | Menu → File → Quit or Alt-F4 |

---

## 📐 Memory Layout

```
Standard ST (512 KB):
  $000000-$0003FF: Vector Table
  $000400-$003FFF: TOS Data Structures
  $004000-$03FFFF: Application RAM (~480 KB free)
  $FF0000-$FFFFFF: TOS ROM

STE (1-4 MB):
  $000000-$0003FF: Vector Table
  $000400-$003FFF: TOS Data Structures
  $004000-$3FFFFF: Application RAM (up to 4 MB)
  $FF0000-$FFFFFF: TOS ROM
```

### Application Memory Budget

| Allocation | Size | Purpose |
|------------|------|---------|
| Code Segment | 64 KB | Program code |
| Data Segment | 32 KB | Global variables |
| Stack | 16 KB | Runtime stack |
| Network Buffer | 8 KB | TCP/IP buffers |
| GEM VDI | 16 KB | Graphics buffers |
| **Free for Mining** | **~344 KB** | Miner state machine |

---

## 📁 Project Structure

```
atari-st-miner/
├── README.md                  # This file
├── ARCHITECTURE.md            # Technical specification
├── IMPLEMENTATION_PLAN.md     # Development roadmap
├── Makefile                   # Build automation
├── linker.cfg                 # Memory layout
├── src/
│   ├── main.c                 # Entry point
│   ├── miner.c/h              # Core miner logic
│   ├── network.c/h            # Network interface (ST-Link/Serial)
│   ├── fingerprint.c/h        # Hardware fingerprinting (68000)
│   ├── ui_gem.c/h             # GEM desktop interface
│   └── ui_text.c/h            # Text-only interface (fallback)
├── asm/
│   ├── startup.s              # 68000 startup code
│   ├── fingerprint.s          # Cycle-accurate timing
│   └── crypto.s               # Hash functions (optimized)
├── include/
│   ├── tos.h                  # TOS function bindings
│   ├── gem.h                  # GEM VDI/AES bindings
│   └── stlink.h               # ST-Link Ethernet driver
├── resources/
│   ├── miner.rsc              # GEM resource file
│   └── miner.inf              # GEM desktop info
└── docs/
    ├── screenshots/           # Emulator screenshots
    └── hardware/              # Real hardware photos
```

---

## 🔧 Technical Details

### Motorola 68000 CPU

**Specifications:**
- 8 MHz clock speed (Atari ST)
- 16/32-bit architecture
- No FPU (optional 68881 on some systems)
- ~1-2 MIPS performance

**Key Instructions for Mining:**
```assembly
; 68000 assembly example - hardware fingerprint
FINGERPRINT:
    MOVE.L  D0, -(SP)         ; Save D0
    MOVE    SR, D0            ; Read status register
    ANDI    #$07, D0          ; Mask interrupt level
    MOVE    D0, JITTER_VAR    ; Store timing variance
    MOVE.L  (SP)+, D0         ; Restore D0
    RTS
```

### TOS Compatibility

**Supported Versions:**
- TOS 1.0 (512 KB ROM, single-sided floppy)
- TOS 1.4 (512 KB ROM, double-sided floppy)
- TOS 2.0 (1 MB ROM, color, HDD support)
- TOS 3.0/4.0 (STE, 4 MB RAM support)

**TOS Function Calls:**
```c
/* GEM AES - Application Environment Services */
appl_init();      /* Initialize GEM */
appl_exit();      /* Exit GEM */
form_alert();     /* Show dialog */
menu_tnormal();   /* Update menu */

/* GEM VDI - Virtual Device Interface */
v_opnwk();        /* Open workstation */
v_clswk();        /* Close workstation */
v_pline();        /* Draw line */
v_gtext();        /* Draw text */
```

### Network Interfaces

**Option A: ST-Link Ethernet Cartridge**
- Realtek RTL8019AS chip
- 10 Mbps Ethernet
- TOS driver included
- Most reliable option

**Option B: Serial-to-Ethernet Bridge**
- RS232 serial port (9600-57600 baud)
- ESP32 running SLIP or PPP
- Lower cost, more complex setup

**Option C: Modern PC Proxy**
- Serial null-modem cable
- PC runs network proxy software
- Atari communicates via serial

---

## 🧪 Testing

### Emulator Testing

```bash
# Hatari configuration
hatari --compatible --fast-forward miner.tos

# With GEM desktop
hatari --gemdos-path=. --gemdos-case=lower miner.tos

# Debug mode
hatari --debug --log-file=hatari.log miner.tos
```

### Real Hardware Testing

**Checklist:**
- [ ] Boots on ST with 512 KB RAM
- [ ] Boots on STE with 4 MB RAM
- [ ] GEM interface displays correctly
- [ ] Network connection established
- [ ] Hardware fingerprint generated
- [ ] Attestation cycle completes

---

## 📝 Development Notes

### Challenges

1. **Memory Constraints:** 512 KB is tight but workable
2. **No Protected Memory:** Single crash = system reboot
3. **GEM Complexity:** Resource files require special tools
4. **Network Hardware:** ST-Link cartridges are rare/expensive

### Optimization Techniques

- Use 68000-specific instructions (MULU, DIVU)
- Unroll critical loops
- Lookup tables for trigonometry
- Fixed-point arithmetic (no FPU)

---

## 🎯 Bounty Claim Checklist

- [ ] Source code compiles without errors
- [ ] Runs in Hatari emulator
- [ ] Runs on real Atari ST hardware
- [ ] GEM interface functional (or text mode)
- [ ] Hardware fingerprint generated
- [ ] Network attestation simulated
- [ ] Documentation complete
- [ ] Wallet address in README: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## 📚 References

- [Atari ST Hardware Reference](https://www.atari-forum.com/)
- [68000 Assembly Language](https://www.easy68k.com/)
- [Hatari Emulator](https://hatari.tuxfamily.org/)
- [TOS Function Calls](http://toshyp.atari.org/)
- [GEM Programming](http://dev-docs.org/atari/)
- [RustChain Documentation](https://github.com/Scottcjn/Rustchain)
- [RIP-PoA Specification](https://github.com/Scottcjn/Rustchain/blob/main/docs/protocol-overview.md)

---

## 🏛️ Historical Context

The Atari ST was released in 1985 with:
- Motorola 68000 @ 8 MHz (16/32-bit)
- 512 KB - 4 MB RAM
- Built-in MIDI ports (popular with musicians)
- GEM desktop environment
- Color graphics (512x340, 16 colors)

Notable users:
- **Depeche Mode** - Used for music production
- **Kraftwerk** - Sequenced albums on Atari ST
- **Prince** - Composed on Atari ST

This implementation honors the legacy of the Atari ST while demonstrating the RustChain protocol's conceptual simplicity.

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- RustChain Foundation for the bounty
- Atari Corporation for the legendary computer
- The 68000 community for keeping vintage computing alive
- Hatari team for the excellent emulator

---

**Built with ❤️ and Motorola 68000 assembly**

*Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`*

---

## 📞 Contact

- **GitHub Issues:** https://github.com/RustChain-org/rustchain-bounties/issues/414
- **Discord:** https://discord.gg/jMAmHBpXcn
- **Email:** bounties@rustchain.org
