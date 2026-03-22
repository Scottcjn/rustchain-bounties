# Ghost in the Machine — Pre-2000 Hardware Resurrection Toolkit

**RustChain Bounty #2314 | 100+ RTC**

A comprehensive toolkit for resurrecting vintage hardware (manufactured before January 1, 2000) and configuring it for RustChain Proof-of-Antiquity mining. Includes hardware detection, compatibility checking, mining configuration generation, performance benchmarking, and step-by-step resurrection guides for 9+ hardware families spanning 6 decades of computing history.

## Features

- **25+ Hardware Profiles** — Pre-loaded database covering Motorola 68K, PowerPC G3, SPARC, MIPS, DEC Alpha, PA-RISC, 6502/65C816, pre-2000 x86, and ARM platforms
- **Compatibility Checker** — Validates hardware for RustChain mining viability with detailed recommendations
- **Mining Config Generator** — Produces ready-to-use JSON configurations with architecture-specific build instructions (cross-compiler flags, target OS, toolchain)
- **Performance Benchmarks** — Simulated benchmarks comparing vintage hardware against modern baselines, with RTC multiplier calculations
- **6 Resurrection Guides** — Step-by-step walkthroughs for SPARC, 68K, MIPS, Alpha, PA-RISC, and 6502 platforms
- **REST API** — 14 endpoints for programmatic access
- **Web Interface** — Interactive wizard with dark vintage-terminal aesthetic, benchmark charts, and config downloads
- **SQLite Database** — Persistent storage for hardware profiles, benchmark results, and resurrection logs

## Quick Start

```bash
# Clone the submission
cd submissions/bounty-2314-ghost-machine

# Start the server (Python 3.6+ required, no external dependencies)
python3 server.py

# Open web interface
# http://localhost:8314/

# Or use the API directly
curl http://localhost:8314/api/health
curl http://localhost:8314/api/profiles
curl http://localhost:8314/api/benchmark?profile=commodore_64
```

The server runs on port 8314 by default. No pip packages required — uses only Python standard library.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GHOST_HOST` | `0.0.0.0` | Server bind address |
| `GHOST_PORT` | `8314` | Server port |
| `GHOST_DB` | `ghost_machine.db` | SQLite database path |
| `RUSTCHAIN_NODE` | `https://50.28.86.131` | RustChain production node |
| `RTC_WALLET` | (empty) | Default wallet name |

## Supported Platforms

### Motorola 68K Family (1990-1994 — 150 RTC, 3.5x multiplier)

| Machine | CPU | Year | Notes |
|---------|-----|------|-------|
| Commodore Amiga 4000 | 68040 @ 25 MHz | 1992 | Zorro III bus, X-Surf 100 Ethernet |
| Commodore Amiga 1200 | 68EC020 @ 14 MHz | 1992 | PCMCIA Ethernet slot |
| Macintosh Quadra 840AV | 68040 @ 40 MHz | 1993 | Fastest 68K Mac, built-in Ethernet |
| NeXTcube | 68040 @ 25 MHz | 1990 | Built-in Ethernet, full UNIX |
| Atari Falcon030 | 68030 @ 16 MHz | 1992 | DSP56001 co-processor |

**Resurrection Guide:** Install NetBSD/m68k or AmigaOS. Cross-compile with `m68k-linux-gnu-gcc`. NeXTcube has built-in Ethernet and UNIX — easiest 68K target.

### PowerPC G3 Family (1995-1999 — 100 RTC, 1.8x multiplier)

| Machine | CPU | Year | Notes |
|---------|-----|------|-------|
| Power Mac G3 (Beige) | PPC 750 @ 233-366 MHz | 1997 | PCI slots, built-in Ethernet |
| Power Mac G3 (Blue & White) | PPC 750 @ 300-450 MHz | 1999 | USB + FireWire, excellent Linux support |
| iMac G3 | PPC 750 @ 233-333 MHz | 1998 | Built-in Ethernet + modem |
| BeBox | Dual PPC 603 @ 66-133 MHz | 1995 | Dual CPU, blinkenlights, GeekPort |

**Resurrection Guide:** Install Yellow Dog Linux or Debian (powerpc). Cross-compile with `powerpc-linux-gnu-gcc` or use Rust's tier 2 PPC target.

### SPARC Family (1994-1998 — 100-150 RTC, 2.0-3.0x multiplier)

| Machine | CPU | Year | Notes |
|---------|-----|------|-------|
| Sun SPARCstation 20 | SuperSPARC II @ 75 MHz | 1994 | Quad-CPU capable, pizza-box form factor |
| Sun SPARCstation 5 | microSPARC II @ 70-110 MHz | 1994 | Budget workstation, solid NetBSD support |
| Sun Ultra 5 | UltraSPARC IIi @ 270-400 MHz | 1998 | PCI + IDE, easiest SPARC to run |

**Resurrection Guide:** Replace dead NVRAM battery. Install NetBSD/sparc or Debian sparc64. Cross-compile with `sparc64-linux-gnu-gcc`. All models have built-in Ethernet.

### MIPS Family / SGI (1991-1996 — 100-150 RTC, 2.5-3.5x multiplier)

| Machine | CPU | Year | Notes |
|---------|-----|------|-------|
| SGI Indy | MIPS R4400 @ 100-200 MHz | 1993 | IndyCam, built-in audio/video |
| SGI O2 | MIPS R5000/R10000 @ 150-300 MHz | 1996 | Unified memory architecture |
| SGI Indigo2 | MIPS R4400 @ 150-250 MHz | 1993 | Impact graphics, purple teal case |
| DECstation 5000/200 | MIPS R3000 @ 25 MHz | 1991 | TURBOchannel bus |

**Resurrection Guide:** Check DALLAS NVRAM chip. Install IRIX 6.5 or NetBSD/sgimips. Native build with MIPSpro on IRIX, or cross-compile with `mips-linux-gnu-gcc`.

### DEC Alpha Family (1995-1996 — 100 RTC, 2.5x multiplier)

| Machine | CPU | Year | Notes |
|---------|-----|------|-------|
| AlphaStation 500 | Alpha 21164 @ 333-500 MHz | 1996 | 64-bit, excellent integer performance |
| AlphaServer 1000A | Alpha 21164 @ 233-400 MHz | 1995 | Server-class reliability |

**Resurrection Guide:** Ensure SRM firmware (not ARC). Install Debian alpha or NetBSD/alpha. Alpha's 64-bit pipeline excels at hashing — surprisingly one of the best vintage miners.

### PA-RISC Family (1993-1994 — 150 RTC, 3.0x multiplier)

| Machine | CPU | Year | Notes |
|---------|-----|------|-------|
| HP 9000/712 | PA-7100LC @ 60-80 MHz | 1994 | Compact workstation, GSC bus |
| HP 9000/735 | PA-7150 @ 125 MHz | 1993 | High-performance workstation |

**Resurrection Guide:** Use serial console (null-modem cable). Install HP-UX 10.20 or Debian hppa. Cross-compile with `hppa-linux-gnu-gcc`. Big-endian — watch byte ordering.

### 6502/65C816 Family (1979-1986 — 200-300 RTC, 4.0-5.0x multiplier)

| Machine | CPU | Year | Bonus | Notes |
|---------|-----|------|-------|-------|
| Apple II Plus | MOS 6502 @ 1 MHz | 1979 | **300 RTC** | Floating bus fingerprint unique per machine |
| Commodore 64 | MOS 6510 @ 1 MHz | 1982 | **300 RTC** | RR-Net cartridge Ethernet, Contiki OS |
| Apple IIGS | WDC 65C816 @ 2.8 MHz | 1986 | 200 RTC | Uthernet II for TCP/IP |

**Resurrection Guide:** Replace C64 PSU (originals are dangerous). Install Uthernet II (Apple) or RR-Net (C64) for Ethernet. Cross-compile with cc65. Binary must fit under 64KB. These machines earn MAXIMUM antiquity bonus — 300 RTC for pre-1985 hardware plus eternal glory.

### Pre-2000 x86 (1987-1997 — 100-200 RTC, 1.5-3.5x multiplier)

| Machine | CPU | Year | Notes |
|---------|-----|------|-------|
| IBM PS/2 Model 80 | Intel 386DX @ 20 MHz | 1987 | MCA bus, can run Linux 2.4 |
| Compaq Deskpro 486/33 | Intel 486DX @ 33 MHz | 1991 | ISA NE2000 Ethernet |
| Generic Pentium MMX | Pentium MMX @ 166-233 MHz | 1997 | PCI bus, plenty of Linux distros |

### Pre-2000 ARM (1994 — 150 RTC, 3.0x multiplier)

| Machine | CPU | Year | Notes |
|---------|-----|------|-------|
| Acorn RiscPC | ARM610 / StrongARM 233 MHz | 1994 | RISC OS, podule Ethernet |

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Service health check with version and PoA signature |
| `/api/profiles` | GET | List all profiles. Filters: `?era=`, `?family=`, `?arch=` |
| `/api/profile?key=` | GET | Detailed profile for a specific hardware |
| `/api/detect` | GET | Detect local machine hardware |
| `/api/compatibility?profile=` | GET | Check mining compatibility |
| `/api/benchmark?profile=` | GET | Run benchmark (omit profile= for all) |
| `/api/config?profile=` | GET | Generate mining configuration JSON |
| `/api/guide?family=` | GET | Resurrection guide for a hardware family |
| `/api/guides` | GET | List all available guides |
| `/api/eras` | GET | Era classification and RTC payouts |
| `/api/benchmarks` | GET | Stored benchmark history (SQLite) |
| `/api/stats` | GET | Database statistics |
| `/api/poa-signature` | GET | Generate Proof-of-Antiquity signature |
| `/api/log-resurrection` | POST | Log a resurrection attempt |

### Example API Usage

```bash
# List all SPARC-family hardware
curl http://localhost:8314/api/profiles?family=sparc

# Check if an SGI Indy is compatible
curl http://localhost:8314/api/compatibility?profile=sgi_indy

# Generate mining config for a Commodore 64
curl http://localhost:8314/api/config?profile=commodore_64

# Run benchmarks for all 25+ platforms
curl http://localhost:8314/api/benchmark

# Get the 68K resurrection guide
curl http://localhost:8314/api/guide?family=68k

# Log a resurrection attempt
curl -X POST http://localhost:8314/api/log-resurrection \
  -H "Content-Type: application/json" \
  -d '{"profile_key":"sparcstation_20","wallet_address":"my-sparc-wallet"}'
```

## Web Interface

The interactive web interface at `http://localhost:8314/` provides:

1. **Resurrection Wizard** — Select hardware, check compatibility, generate config, run benchmarks
2. **Hardware Profiles** — Browse 25+ profiles with filtering by era
3. **Benchmarks** — Visual comparison charts for all platforms
4. **Guides** — Step-by-step resurrection walkthroughs
5. **Config Generator** — Download-ready JSON mining configurations
6. **Hardware Detection** — Auto-detect the current machine
7. **API Reference** — Interactive endpoint documentation

Design uses a dark theme with CRT scanline effect for vintage computer aesthetic.

## Architecture

```
bounty-2314-ghost-machine/
  server.py         # Python web app + REST API (stdlib only, no pip deps)
  resurrect.html    # Interactive frontend (vanilla JS, no frameworks)
  README.md         # This file
  ghost_machine.db  # Auto-created SQLite database (runtime)
```

- **Zero external dependencies** — Uses only Python standard library (`http.server`, `sqlite3`, `json`, `hashlib`, `platform`)
- **Single-file server** — All backend logic in one Python file
- **Self-contained frontend** — Inline CSS/JS, no CDN dependencies
- **SQLite storage** — Auto-initialized database for profiles, benchmarks, and resurrection logs

## Bounty Compliance

Per [Issue #2314](https://github.com/Scottcjn/rustchain-bounties/issues/2314):

- Provides comprehensive tooling for resurrecting pre-2000 hardware
- Covers hardware from 1979 (Apple II Plus) to 1999 (Power Mac G3 B&W)
- Includes 25+ hardware profiles across 9 architecture families
- Generates architecture-specific mining configurations with cross-compiler flags
- 6 detailed resurrection guides with 5 steps each
- Performance benchmarks with RTC multiplier calculations matching the bounty payout scale
- SQLite database for tracking resurrection attempts
- REST API + web interface for complete workflow support

### Payout Scale Coverage

| Era | Bonus | Platforms Covered |
|-----|-------|-------------------|
| Pre-1985 | 300 RTC | Apple II Plus (1979), Commodore 64 (1982) |
| 1985-1989 | 200 RTC | Apple IIGS (1986), IBM PS/2 (1987) |
| 1990-1994 | 150 RTC | Amiga 4000, NeXTcube, Quadra 840AV, SPARCstation 20, SGI Indy, HP 9000, Acorn RiscPC, and more |
| 1995-1999 | 100 RTC | Power Mac G3, iMac G3, BeBox, Sun Ultra 5, SGI O2, AlphaStation 500 |

## RTC Wallet

`ElromEvedElElyon`

## License

Apache-2.0
