#!/usr/bin/env python3
"""
Ghost in the Machine — Pre-2000 Hardware Resurrection Toolkit for RustChain Mining

A comprehensive web application and REST API that helps users resurrect vintage
hardware (manufactured before January 1, 2000) and configure it for RustChain
Proof-of-Antiquity mining.

Supported architectures:
  - Motorola 68K (Amiga, Macintosh, NeXT, Atari ST)
  - PowerPC G3 (Power Mac G3, iMac G3, BeBox)
  - SPARC (Sun SPARCstation, Ultra 5/10)
  - MIPS (SGI Indy, Indigo2, O2, DECstation)
  - DEC Alpha (AlphaStation, AlphaServer)
  - PA-RISC (HP 9000 series)
  - 6502 / 65C816 (Apple II, Commodore 64, SNES)
  - x86 (i386/i486/Pentium era PCs)
  - ARM (Acorn, RiscPC, StrongARM)

Author: ElromEvedElElyon
Bounty: #2314 — Ghost in the Machine (100+ RTC)
License: Apache-2.0
"""

import hashlib
import json
import os
import platform
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RUSTCHAIN_NODE = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")
WALLET_ADDRESS = os.environ.get("RTC_WALLET", "")
DB_PATH = os.environ.get("GHOST_DB", "ghost_machine.db")
HOST = os.environ.get("GHOST_HOST", "0.0.0.0")
PORT = int(os.environ.get("GHOST_PORT", "8314"))
VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Hardware Database — Pre-2000 Platforms
# ---------------------------------------------------------------------------

HARDWARE_PROFILES = {
    # ── Motorola 68K Family ──────────────────────────────────────────────
    "amiga_4000": {
        "name": "Commodore Amiga 4000",
        "manufacturer": "Commodore",
        "year": 1992,
        "cpu": "Motorola 68040 @ 25 MHz",
        "arch": "m68k",
        "family": "68k",
        "ram_typical_mb": 6,
        "era": "1990-1994",
        "rtc_multiplier": 3.5,
        "rtc_bonus": 150,
        "os_options": ["AmigaOS 3.1", "AmigaOS 3.9", "NetBSD/amiga"],
        "network_options": ["X-Surf 100 (Zorro III)", "A2065 Ethernet", "PCMCIA NIC"],
        "mining_viable": True,
        "notes": "Zorro III bus provides decent I/O. 68040 FPU useful for fingerprint hashing."
    },
    "amiga_1200": {
        "name": "Commodore Amiga 1200",
        "manufacturer": "Commodore",
        "year": 1992,
        "cpu": "Motorola 68EC020 @ 14 MHz",
        "arch": "m68k",
        "family": "68k",
        "ram_typical_mb": 2,
        "era": "1990-1994",
        "rtc_multiplier": 3.5,
        "rtc_bonus": 150,
        "os_options": ["AmigaOS 3.1", "AmigaOS 3.9"],
        "network_options": ["PCMCIA Ethernet", "Plipbox (parallel port)"],
        "mining_viable": True,
        "notes": "PCMCIA slot is the easiest network path. Consider 68030 accelerator card."
    },
    "mac_quadra_840av": {
        "name": "Macintosh Quadra 840AV",
        "manufacturer": "Apple",
        "year": 1993,
        "cpu": "Motorola 68040 @ 40 MHz",
        "arch": "m68k",
        "family": "68k",
        "ram_typical_mb": 8,
        "era": "1990-1994",
        "rtc_multiplier": 3.5,
        "rtc_bonus": 150,
        "os_options": ["Mac OS 8.1", "NetBSD/mac68k", "A/UX 3.1"],
        "network_options": ["Built-in Ethernet (AAUI-15)", "AAUI transceiver to 10Base-T"],
        "mining_viable": True,
        "notes": "Fastest 68K Mac ever made. Built-in Ethernet simplifies network setup."
    },
    "next_cube": {
        "name": "NeXTcube",
        "manufacturer": "NeXT",
        "year": 1990,
        "cpu": "Motorola 68040 @ 25 MHz",
        "arch": "m68k",
        "family": "68k",
        "ram_typical_mb": 16,
        "era": "1990-1994",
        "rtc_multiplier": 3.5,
        "rtc_bonus": 150,
        "os_options": ["NeXTSTEP 3.3", "OPENSTEP 4.2", "NetBSD/next68k"],
        "network_options": ["Built-in 10Base-T Ethernet"],
        "mining_viable": True,
        "notes": "Built-in Ethernet and full UNIX make this ideal. Tim Berners-Lee wrote the first web server on one."
    },
    "atari_falcon030": {
        "name": "Atari Falcon030",
        "manufacturer": "Atari",
        "year": 1992,
        "cpu": "Motorola 68030 @ 16 MHz",
        "arch": "m68k",
        "family": "68k",
        "ram_typical_mb": 4,
        "era": "1990-1994",
        "rtc_multiplier": 3.5,
        "rtc_bonus": 150,
        "os_options": ["TOS 4.04", "MiNT/FreeMiNT", "NetBSD/atari"],
        "network_options": ["NetUSBee (USB-Ethernet)", "EtherNEC (cartridge port)"],
        "mining_viable": True,
        "notes": "DSP56001 co-processor could theoretically accelerate hashing."
    },

    # ── PowerPC Family ───────────────────────────────────────────────────
    "power_mac_g3_beige": {
        "name": "Power Macintosh G3 (Beige)",
        "manufacturer": "Apple",
        "year": 1997,
        "cpu": "PowerPC 750 @ 233-366 MHz",
        "arch": "powerpc",
        "family": "g3",
        "ram_typical_mb": 128,
        "era": "1995-1999",
        "rtc_multiplier": 1.8,
        "rtc_bonus": 100,
        "os_options": ["Mac OS 9.1", "Yellow Dog Linux 3.0", "Debian (powerpc)"],
        "network_options": ["Built-in 10/100 Ethernet", "PCI NIC"],
        "mining_viable": True,
        "notes": "Run Yellow Dog Linux or Debian for full POSIX support. GCC cross-compile from modern host."
    },
    "power_mac_g3_bw": {
        "name": "Power Macintosh G3 (Blue & White)",
        "manufacturer": "Apple",
        "year": 1999,
        "cpu": "PowerPC 750 @ 300-450 MHz",
        "arch": "powerpc",
        "family": "g3",
        "ram_typical_mb": 256,
        "era": "1995-1999",
        "rtc_multiplier": 1.8,
        "rtc_bonus": 100,
        "os_options": ["Mac OS 9.2.2", "Yellow Dog Linux 3.0", "Debian (powerpc)", "MorphOS"],
        "network_options": ["Built-in 10/100 Ethernet"],
        "mining_viable": True,
        "notes": "Excellent Linux support. USB + FireWire available. Good first vintage Mac to try."
    },
    "imac_g3": {
        "name": "iMac G3 (Rev A-D)",
        "manufacturer": "Apple",
        "year": 1998,
        "cpu": "PowerPC 750 @ 233-333 MHz",
        "arch": "powerpc",
        "family": "g3",
        "ram_typical_mb": 128,
        "era": "1995-1999",
        "rtc_multiplier": 1.8,
        "rtc_bonus": 100,
        "os_options": ["Mac OS 9.2.2", "Yellow Dog Linux", "Debian (powerpc)"],
        "network_options": ["Built-in 10/100 Ethernet"],
        "mining_viable": True,
        "notes": "Built-in modem and Ethernet. IR port for retro authenticity."
    },
    "bebox": {
        "name": "BeBox",
        "manufacturer": "Be Inc.",
        "year": 1995,
        "cpu": "Dual PowerPC 603 @ 66-133 MHz",
        "arch": "powerpc",
        "family": "g3",
        "ram_typical_mb": 64,
        "era": "1995-1999",
        "rtc_multiplier": 2.2,
        "rtc_bonus": 100,
        "os_options": ["BeOS R5", "Haiku"],
        "network_options": ["Built-in Ethernet", "GeekPort (custom I/O)"],
        "mining_viable": True,
        "notes": "Dual CPUs! The blinkenlights show CPU load. GeekPort could drive custom attestation hardware."
    },

    # ── SPARC Family ─────────────────────────────────────────────────────
    "sparcstation_20": {
        "name": "Sun SPARCstation 20",
        "manufacturer": "Sun Microsystems",
        "year": 1994,
        "cpu": "SuperSPARC II @ 75 MHz (up to quad CPU)",
        "arch": "sparc",
        "family": "sparc",
        "ram_typical_mb": 256,
        "era": "1990-1994",
        "rtc_multiplier": 3.0,
        "rtc_bonus": 150,
        "os_options": ["Solaris 9", "NetBSD/sparc", "Linux (sparc32)"],
        "network_options": ["Built-in 10Base-T Ethernet", "SBus NIC"],
        "mining_viable": True,
        "notes": "Quad-CPU capable. Run NetBSD for modern toolchain. Pizza-box form factor."
    },
    "sun_ultra_5": {
        "name": "Sun Ultra 5",
        "manufacturer": "Sun Microsystems",
        "year": 1998,
        "cpu": "UltraSPARC IIi @ 270-400 MHz",
        "arch": "sparc64",
        "family": "sparc",
        "ram_typical_mb": 512,
        "era": "1995-1999",
        "rtc_multiplier": 2.0,
        "rtc_bonus": 100,
        "os_options": ["Solaris 10", "NetBSD/sparc64", "Debian (sparc64)", "Aurora Linux"],
        "network_options": ["Built-in 10/100 Ethernet", "PCI NIC"],
        "mining_viable": True,
        "notes": "PCI slots + IDE make this the easiest SPARC to get running. Excellent Debian support."
    },
    "sparcstation_5": {
        "name": "Sun SPARCstation 5",
        "manufacturer": "Sun Microsystems",
        "year": 1994,
        "cpu": "microSPARC II @ 70-110 MHz",
        "arch": "sparc",
        "family": "sparc",
        "ram_typical_mb": 128,
        "era": "1990-1994",
        "rtc_multiplier": 3.0,
        "rtc_bonus": 150,
        "os_options": ["Solaris 8", "NetBSD/sparc", "OpenBSD/sparc"],
        "network_options": ["Built-in 10Base-T Ethernet", "AUI transceiver"],
        "mining_viable": True,
        "notes": "Turbo model recommended. On-board audio is a bonus."
    },

    # ── MIPS Family ──────────────────────────────────────────────────────
    "sgi_indy": {
        "name": "SGI Indy",
        "manufacturer": "Silicon Graphics",
        "year": 1993,
        "cpu": "MIPS R4400 @ 100-200 MHz",
        "arch": "mips",
        "family": "mips",
        "ram_typical_mb": 256,
        "era": "1990-1994",
        "rtc_multiplier": 3.0,
        "rtc_bonus": 150,
        "os_options": ["IRIX 6.5", "NetBSD/sgimips", "Linux (mips)"],
        "network_options": ["Built-in 10/100 Ethernet", "AUI port"],
        "mining_viable": True,
        "notes": "IndyCam and built-in audio for attestation proof. IRIX still boots from SCSI."
    },
    "sgi_o2": {
        "name": "SGI O2",
        "manufacturer": "Silicon Graphics",
        "year": 1996,
        "cpu": "MIPS R5000 @ 150-300 MHz / R10000 @ 175-250 MHz",
        "arch": "mips64",
        "family": "mips",
        "ram_typical_mb": 512,
        "era": "1995-1999",
        "rtc_multiplier": 2.5,
        "rtc_bonus": 100,
        "os_options": ["IRIX 6.5.22", "NetBSD/sgimips", "Gentoo (mips)"],
        "network_options": ["Built-in 10/100 Ethernet"],
        "mining_viable": True,
        "notes": "Unified Memory Architecture is unique. R10000 version is significantly faster."
    },
    "sgi_indigo2": {
        "name": "SGI Indigo2",
        "manufacturer": "Silicon Graphics",
        "year": 1993,
        "cpu": "MIPS R4400 @ 150-250 MHz",
        "arch": "mips",
        "family": "mips",
        "ram_typical_mb": 384,
        "era": "1990-1994",
        "rtc_multiplier": 3.0,
        "rtc_bonus": 150,
        "os_options": ["IRIX 6.5", "NetBSD/sgimips"],
        "network_options": ["Built-in 10/100 Ethernet", "GIO64 NIC"],
        "mining_viable": True,
        "notes": "Impact/MaxIMPACT graphics are legendary. Purple teal case is iconic."
    },
    "decstation_5000": {
        "name": "DECstation 5000/200",
        "manufacturer": "Digital Equipment Corporation",
        "year": 1991,
        "cpu": "MIPS R3000 @ 25 MHz",
        "arch": "mips",
        "family": "mips",
        "ram_typical_mb": 40,
        "era": "1990-1994",
        "rtc_multiplier": 3.5,
        "rtc_bonus": 150,
        "os_options": ["Ultrix 4.5", "NetBSD/pmax"],
        "network_options": ["Built-in 10Base-T Ethernet (LANCE)"],
        "mining_viable": True,
        "notes": "TURBOchannel bus. NetBSD/pmax is the best modern option."
    },

    # ── DEC Alpha Family ─────────────────────────────────────────────────
    "alphastation_500": {
        "name": "AlphaStation 500",
        "manufacturer": "Digital Equipment Corporation",
        "year": 1996,
        "cpu": "DEC Alpha 21164 @ 333-500 MHz",
        "arch": "alpha",
        "family": "alpha",
        "ram_typical_mb": 512,
        "era": "1995-1999",
        "rtc_multiplier": 2.5,
        "rtc_bonus": 100,
        "os_options": ["Tru64 UNIX 5.1B", "NetBSD/alpha", "Debian (alpha)", "Gentoo (alpha)"],
        "network_options": ["Built-in 10/100 Ethernet", "PCI NIC"],
        "mining_viable": True,
        "notes": "64-bit architecture was ahead of its time. Excellent integer performance for hashing."
    },
    "alphaserver_1000a": {
        "name": "AlphaServer 1000A",
        "manufacturer": "Digital Equipment Corporation",
        "year": 1995,
        "cpu": "DEC Alpha 21164 @ 233-400 MHz",
        "arch": "alpha",
        "family": "alpha",
        "ram_typical_mb": 1024,
        "era": "1995-1999",
        "rtc_multiplier": 2.5,
        "rtc_bonus": 100,
        "os_options": ["Tru64 UNIX 5.1B", "OpenVMS 8.4", "NetBSD/alpha", "Debian (alpha)"],
        "network_options": ["Built-in 10/100 Ethernet", "EISA/PCI NIC"],
        "mining_viable": True,
        "notes": "Server-class reliability. SRM console firmware for Linux boot."
    },

    # ── PA-RISC Family ───────────────────────────────────────────────────
    "hp_9000_712": {
        "name": "HP 9000/712",
        "manufacturer": "Hewlett-Packard",
        "year": 1994,
        "cpu": "PA-7100LC @ 60-80 MHz",
        "arch": "hppa",
        "family": "parisc",
        "ram_typical_mb": 128,
        "era": "1990-1994",
        "rtc_multiplier": 3.0,
        "rtc_bonus": 150,
        "os_options": ["HP-UX 10.20", "HP-UX 11.0", "NetBSD/hp700", "Debian (hppa)"],
        "network_options": ["Built-in 10Base-T Ethernet (LASI)"],
        "mining_viable": True,
        "notes": "Compact workstation. GSC bus. Debian hppa port works but is experimental."
    },
    "hp_9000_735": {
        "name": "HP 9000/735",
        "manufacturer": "Hewlett-Packard",
        "year": 1993,
        "cpu": "PA-7150 @ 125 MHz",
        "arch": "hppa",
        "family": "parisc",
        "ram_typical_mb": 256,
        "era": "1990-1994",
        "rtc_multiplier": 3.0,
        "rtc_bonus": 150,
        "os_options": ["HP-UX 10.20", "HP-UX 11.0", "NetBSD/hp700"],
        "network_options": ["Built-in 10Base-T Ethernet", "EISA NIC"],
        "mining_viable": True,
        "notes": "One of the fastest PA-RISC workstations of its era. CRX graphics."
    },

    # ── 6502 / 65C816 Family ─────────────────────────────────────────────
    "apple_iigs": {
        "name": "Apple IIGS",
        "manufacturer": "Apple",
        "year": 1986,
        "cpu": "WDC 65C816 @ 2.8 MHz",
        "arch": "65c816",
        "family": "6502",
        "ram_typical_mb": 1,
        "era": "1985-1989",
        "rtc_multiplier": 4.0,
        "rtc_bonus": 200,
        "os_options": ["GS/OS 6.0.1", "ProDOS 8"],
        "network_options": ["Uthernet II (Slot 3/7)", "LANceGS"],
        "mining_viable": True,
        "notes": "Uthernet II provides TCP/IP stack. Use cc65 cross-compiler."
    },
    "commodore_64": {
        "name": "Commodore 64",
        "manufacturer": "Commodore",
        "year": 1982,
        "cpu": "MOS 6510 @ 1 MHz",
        "arch": "6502",
        "family": "6502",
        "ram_typical_mb": 0.064,
        "era": "pre-1985",
        "rtc_multiplier": 5.0,
        "rtc_bonus": 300,
        "os_options": ["KERNAL ROM", "Contiki OS"],
        "network_options": ["RR-Net (cartridge Ethernet)", "ETH64 (user port)", "Comet64"],
        "mining_viable": True,
        "notes": "The ultimate retro flex. RR-Net + Contiki provides TCP/IP. Use cc65 cross-compiler. 300 RTC bonus!"
    },
    "apple_ii_plus": {
        "name": "Apple II Plus",
        "manufacturer": "Apple",
        "year": 1979,
        "cpu": "MOS 6502 @ 1 MHz",
        "arch": "6502",
        "family": "6502",
        "ram_typical_mb": 0.048,
        "era": "pre-1985",
        "rtc_multiplier": 5.0,
        "rtc_bonus": 300,
        "os_options": ["Apple DOS 3.3", "ProDOS"],
        "network_options": ["Uthernet II (Slot 3)", "Serial SLIP"],
        "mining_viable": True,
        "notes": "Floating bus fingerprint is unique per machine. 300 RTC bonus for pre-1985!"
    },

    # ── x86 (pre-2000) ──────────────────────────────────────────────────
    "ibm_ps2_model_80": {
        "name": "IBM PS/2 Model 80",
        "manufacturer": "IBM",
        "year": 1987,
        "cpu": "Intel 386DX @ 20 MHz",
        "arch": "i386",
        "family": "x86",
        "ram_typical_mb": 4,
        "era": "1985-1989",
        "rtc_multiplier": 3.5,
        "rtc_bonus": 200,
        "os_options": ["FreeBSD 4.11", "NetBSD/i386", "Slackware 7.1"],
        "network_options": ["MCA Token Ring -> Bridge", "MCA Ethernet"],
        "mining_viable": True,
        "notes": "MCA bus is proprietary but some Ethernet cards exist. 386 can run Linux 2.4."
    },
    "compaq_deskpro_486": {
        "name": "Compaq Deskpro 486/33",
        "manufacturer": "Compaq",
        "year": 1991,
        "cpu": "Intel 486DX @ 33 MHz",
        "arch": "i486",
        "family": "x86",
        "ram_typical_mb": 16,
        "era": "1990-1994",
        "rtc_multiplier": 3.0,
        "rtc_bonus": 150,
        "os_options": ["FreeBSD 4.11", "NetBSD/i386", "Slackware 8.0", "Linux 2.4"],
        "network_options": ["ISA NE2000 clone", "EISA NIC"],
        "mining_viable": True,
        "notes": "ISA NE2000 compatibles are cheap and well-supported. EISA bus for performance."
    },
    "pentium_mmx_pc": {
        "name": "Generic Pentium MMX PC",
        "manufacturer": "Various",
        "year": 1997,
        "cpu": "Intel Pentium MMX @ 166-233 MHz",
        "arch": "i586",
        "family": "x86",
        "ram_typical_mb": 64,
        "era": "1995-1999",
        "rtc_multiplier": 1.5,
        "rtc_bonus": 100,
        "os_options": ["Debian 3.1 (Sarge)", "Slackware 10", "FreeBSD 6.0", "OpenBSD 4.0"],
        "network_options": ["PCI NE2000", "3Com 3C905B", "Intel EtherExpress Pro"],
        "mining_viable": True,
        "notes": "PCI bus makes NIC installation trivial. Plenty of Linux distro options."
    },

    # ── ARM (pre-2000) ───────────────────────────────────────────────────
    "acorn_riscpc": {
        "name": "Acorn RiscPC",
        "manufacturer": "Acorn Computers",
        "year": 1994,
        "cpu": "ARM610 @ 30 MHz / StrongARM 233 MHz",
        "arch": "arm",
        "family": "arm",
        "ram_typical_mb": 64,
        "era": "1990-1994",
        "rtc_multiplier": 3.0,
        "rtc_bonus": 150,
        "os_options": ["RISC OS 4.39", "NetBSD/acorn32"],
        "network_options": ["Podule Ethernet (EtherH)", "10Base-T NIC"],
        "mining_viable": True,
        "notes": "StrongARM upgrade dramatically improves performance. RISC OS is unique."
    },
}

# Era classification for payout scale
ERA_PAYOUTS = {
    "pre-1985": {"rtc": 300, "label": "Pre-1985 — Eternal Glory"},
    "1985-1989": {"rtc": 200, "label": "1985-1989 — Legendary"},
    "1990-1994": {"rtc": 150, "label": "1990-1994 — Veteran"},
    "1995-1999": {"rtc": 100, "label": "1995-1999 — Classic"},
}

# ---------------------------------------------------------------------------
# Database Setup
# ---------------------------------------------------------------------------

def init_db():
    """Initialize SQLite database for hardware profiles and benchmark results."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS hardware_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_key TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            manufacturer TEXT,
            year INTEGER,
            cpu TEXT,
            arch TEXT,
            family TEXT,
            ram_mb REAL,
            era TEXT,
            rtc_multiplier REAL,
            rtc_bonus INTEGER,
            mining_viable INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS benchmark_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_key TEXT NOT NULL,
            hash_rate REAL,
            attestation_time_ms REAL,
            memory_usage_mb REAL,
            network_latency_ms REAL,
            fingerprint_hash TEXT,
            modern_baseline_ratio REAL,
            score REAL,
            notes TEXT,
            tested_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (profile_key) REFERENCES hardware_profiles(profile_key)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS resurrection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_key TEXT NOT NULL,
            wallet_address TEXT,
            status TEXT DEFAULT 'pending',
            attestation_hash TEXT,
            os_installed TEXT,
            network_method TEXT,
            steps_completed TEXT,
            proof_photo_path TEXT,
            proof_screenshot_path TEXT,
            submitted_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (profile_key) REFERENCES hardware_profiles(profile_key)
        )
    """)

    # Seed hardware profiles
    for key, profile in HARDWARE_PROFILES.items():
        c.execute("""
            INSERT OR IGNORE INTO hardware_profiles
            (profile_key, name, manufacturer, year, cpu, arch, family, ram_mb, era,
             rtc_multiplier, rtc_bonus, mining_viable)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            key, profile["name"], profile["manufacturer"], profile["year"],
            profile["cpu"], profile["arch"], profile["family"],
            profile["ram_typical_mb"], profile["era"],
            profile["rtc_multiplier"], profile["rtc_bonus"],
            1 if profile["mining_viable"] else 0
        ))

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Hardware Detection
# ---------------------------------------------------------------------------

def detect_local_hardware():
    """Detect the current machine's hardware for compatibility assessment."""
    info = {
        "hostname": platform.node(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "python_version": platform.python_version(),
        "is_vintage": False,
        "detected_arch": "unknown",
        "detected_family": "unknown",
    }

    machine = platform.machine().lower()
    processor = (platform.processor() or "").lower()

    # Architecture detection
    arch_map = {
        "ppc": ("powerpc", "g3"),
        "powerpc": ("powerpc", "g3"),
        "ppc64": ("powerpc", "g5"),
        "sparc": ("sparc", "sparc"),
        "sparc64": ("sparc64", "sparc"),
        "mips": ("mips", "mips"),
        "mips64": ("mips64", "mips"),
        "alpha": ("alpha", "alpha"),
        "parisc": ("hppa", "parisc"),
        "hppa": ("hppa", "parisc"),
        "m68k": ("m68k", "68k"),
        "armv": ("arm", "arm"),
        "aarch64": ("aarch64", "arm"),
        "i386": ("i386", "x86"),
        "i486": ("i486", "x86"),
        "i586": ("i586", "x86"),
        "i686": ("i686", "x86"),
        "x86_64": ("x86_64", "x86"),
    }

    for pattern, (arch, family) in arch_map.items():
        if pattern in machine or pattern in processor:
            info["detected_arch"] = arch
            info["detected_family"] = family
            break

    # Check if vintage
    vintage_arches = {"m68k", "powerpc", "sparc", "sparc64", "mips", "mips64",
                      "alpha", "hppa", "6502", "65c816", "i386", "i486", "i586"}
    if info["detected_arch"] in vintage_arches:
        info["is_vintage"] = True

    # Try to get CPU info on Linux
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
            for line in cpuinfo.split("\n"):
                if "model name" in line.lower() or "cpu" in line.lower():
                    info["cpu_detail"] = line.split(":")[-1].strip()
                    break
        except (IOError, OSError):
            pass

    return info


def check_compatibility(profile_key):
    """Check compatibility of a specific hardware profile for RustChain mining."""
    if profile_key not in HARDWARE_PROFILES:
        return {"error": f"Unknown hardware profile: {profile_key}"}

    profile = HARDWARE_PROFILES[profile_key]
    result = {
        "profile": profile_key,
        "name": profile["name"],
        "compatible": True,
        "issues": [],
        "recommendations": [],
        "mining_config": None,
        "estimated_performance": {},
    }

    # Check RAM
    if profile["ram_typical_mb"] < 0.5:
        result["issues"].append("Extremely limited RAM. Miner must be hand-optimized for this platform.")
        result["recommendations"].append("Use the stripped-down C miner with cc65 cross-compiler.")
    elif profile["ram_typical_mb"] < 4:
        result["issues"].append("Limited RAM. Use lightweight miner build.")
        result["recommendations"].append("Compile with -Os optimization. Disable debug symbols.")
    elif profile["ram_typical_mb"] < 32:
        result["recommendations"].append("Standard miner should work. Consider swap space.")

    # Check network options
    if not profile.get("network_options"):
        result["compatible"] = False
        result["issues"].append("No known network options. Cannot submit attestations.")
    else:
        result["recommendations"].append(
            f"Recommended network: {profile['network_options'][0]}"
        )

    # OS recommendations
    if profile.get("os_options"):
        unix_options = [o for o in profile["os_options"]
                       if any(u in o.lower() for u in ["linux", "bsd", "unix", "debian", "gentoo"])]
        if unix_options:
            result["recommendations"].append(
                f"Recommended OS for mining: {unix_options[0]} (POSIX support for Rust/C toolchain)"
            )
        else:
            result["recommendations"].append(
                f"Available OS: {profile['os_options'][0]}. May need custom miner port."
            )

    # Architecture-specific notes
    arch_notes = {
        "m68k": "Cross-compile with m68k-linux-gnu-gcc or use NetBSD pkgsrc.",
        "powerpc": "Use powerpc-linux-gnu-gcc cross-compiler. Rust has tier 2 PPC support.",
        "sparc": "Cross-compile with sparc-linux-gnu-gcc. NetBSD has best support.",
        "sparc64": "Rust has tier 2 sparc64 support. Debian sparc64 port available.",
        "mips": "Cross-compile with mips-linux-gnu-gcc. IRIX native build possible with MIPSpro.",
        "mips64": "Use mips64-linux-gnu-gcc. SGI O2 has decent Gentoo support.",
        "alpha": "Debian alpha port available. GCC 4.x cross-compiler works.",
        "hppa": "Cross-compile with hppa-linux-gnu-gcc. Debian hppa is experimental.",
        "6502": "Use cc65 cross-compiler. Miner must be pure C, under 64KB.",
        "65c816": "Use cc65 with --target apple2enh. 16-bit addressing available.",
        "arm": "ARM cross-compile is well-supported. NetBSD/acorn32 recommended.",
        "i386": "Standard GCC targeting i386. Linux 2.4/2.6 kernels work.",
        "i486": "GCC with -march=i486. Most Linux distros dropped i486 support.",
        "i586": "GCC with -march=pentium. Slackware and Debian old-stable work.",
    }
    if profile["arch"] in arch_notes:
        result["recommendations"].append(arch_notes[profile["arch"]])

    # Estimated performance
    modern_hash_rate = 50000  # hashes/sec on modern x86_64
    era_factor = {"pre-1985": 0.001, "1985-1989": 0.01, "1990-1994": 0.05, "1995-1999": 0.15}
    raw_rate = modern_hash_rate * era_factor.get(profile["era"], 0.1)
    effective_rate = raw_rate * profile["rtc_multiplier"]

    result["estimated_performance"] = {
        "raw_hash_rate": round(raw_rate, 2),
        "effective_hash_rate": round(effective_rate, 2),
        "rtc_multiplier": profile["rtc_multiplier"],
        "rtc_per_epoch_estimate": round(effective_rate / modern_hash_rate * 10, 4),
        "attestation_time_estimate_sec": round(1.0 / max(raw_rate, 1) * 1000, 2),
    }

    # Generate mining config
    result["mining_config"] = generate_mining_config(profile_key)

    return result


# ---------------------------------------------------------------------------
# Mining Configuration Generator
# ---------------------------------------------------------------------------

def generate_mining_config(profile_key):
    """Generate a mining configuration for a specific vintage hardware profile."""
    if profile_key not in HARDWARE_PROFILES:
        return None

    profile = HARDWARE_PROFILES[profile_key]
    config = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hardware": {
            "profile": profile_key,
            "name": profile["name"],
            "cpu": profile["cpu"],
            "arch": profile["arch"],
            "family": profile["family"],
        },
        "rustchain": {
            "node": RUSTCHAIN_NODE,
            "wallet": WALLET_ADDRESS or "YOUR_WALLET_NAME",
            "device_arch": profile["arch"],
            "device_family": profile["family"],
        },
        "mining": {
            "threads": 1,
            "hash_buffer_kb": min(profile["ram_typical_mb"] * 128, 4096),
            "attestation_interval_sec": 30,
            "retry_on_failure": True,
            "retry_delay_sec": 10,
            "max_retries": 5,
        },
        "network": {
            "timeout_sec": 30,
            "tls_verify": False,  # Self-signed cert on production node
            "preferred_method": profile["network_options"][0] if profile.get("network_options") else "unknown",
        },
        "fingerprint": {
            "clock_drift_samples": 100,
            "cache_sweep_sizes": [1024, 4096, 16384, 65536],
            "thermal_samples": 50,
            "jitter_iterations": 200,
        },
        "build": {},
    }

    # Architecture-specific build configuration
    arch = profile["arch"]
    if arch in ("6502", "65c816"):
        config["build"] = {
            "toolchain": "cc65",
            "target": "apple2" if "apple" in profile_key else "c64",
            "compiler": "cl65",
            "flags": "-Oi -Os --static-locals",
            "linker": "ld65",
            "max_binary_size_kb": 48,
            "note": "Cross-compile on modern host, transfer via serial/SD card"
        }
        config["mining"]["threads"] = 1
        config["mining"]["hash_buffer_kb"] = 8
        config["mining"]["attestation_interval_sec"] = 120
        config["fingerprint"]["clock_drift_samples"] = 20
        config["fingerprint"]["cache_sweep_sizes"] = [256, 1024]
        config["fingerprint"]["thermal_samples"] = 10
        config["fingerprint"]["jitter_iterations"] = 50
    elif arch == "m68k":
        config["build"] = {
            "toolchain": "gcc-m68k",
            "cross_compiler": "m68k-linux-gnu-gcc",
            "flags": "-O2 -m68040 -mhard-float",
            "target_os": "NetBSD/m68k or AmigaOS",
            "note": "Use -m68040 for Quadra/Amiga 4000, -m68030 for Falcon/A1200"
        }
        config["mining"]["threads"] = 1
        config["mining"]["hash_buffer_kb"] = 64
    elif arch == "powerpc":
        config["build"] = {
            "toolchain": "gcc-powerpc or rustc",
            "cross_compiler": "powerpc-linux-gnu-gcc",
            "rust_target": "powerpc-unknown-linux-gnu",
            "flags": "-O2 -mcpu=750",
            "note": "Rust tier 2 support. Use 'cross' for easier builds."
        }
        config["mining"]["threads"] = 1
        config["mining"]["hash_buffer_kb"] = 512
    elif arch in ("sparc", "sparc64"):
        config["build"] = {
            "toolchain": "gcc-sparc",
            "cross_compiler": f"{'sparc64' if arch == 'sparc64' else 'sparc'}-linux-gnu-gcc",
            "flags": "-O2 -mcpu=v8" if arch == "sparc" else "-O2 -mcpu=ultrasparc",
            "target_os": "NetBSD/sparc or Solaris",
            "note": "NetBSD provides best modern toolchain on SPARC hardware."
        }
        config["mining"]["hash_buffer_kb"] = 256
    elif arch in ("mips", "mips64"):
        config["build"] = {
            "toolchain": "gcc-mips",
            "cross_compiler": f"{'mips64' if arch == 'mips64' else 'mips'}-linux-gnu-gcc",
            "flags": "-O2 -mips3" if arch == "mips" else "-O2 -mips4",
            "target_os": "IRIX 6.5 or NetBSD/sgimips",
            "irix_compiler": "MIPSpro cc -O2 -mips4 -n32",
            "note": "IRIX native build possible with MIPSpro compiler."
        }
        config["mining"]["hash_buffer_kb"] = 256
    elif arch == "alpha":
        config["build"] = {
            "toolchain": "gcc-alpha",
            "cross_compiler": "alpha-linux-gnu-gcc",
            "flags": "-O2 -mcpu=ev56",
            "target_os": "Tru64 UNIX or Debian alpha",
            "note": "Alpha's 64-bit integer ops are excellent for hashing."
        }
        config["mining"]["hash_buffer_kb"] = 512
    elif arch == "hppa":
        config["build"] = {
            "toolchain": "gcc-hppa",
            "cross_compiler": "hppa-linux-gnu-gcc",
            "flags": "-O2",
            "target_os": "HP-UX 10.20 or Debian hppa",
            "note": "PA-RISC is big-endian. Watch byte ordering in network code."
        }
        config["mining"]["hash_buffer_kb"] = 256
    elif arch == "arm":
        config["build"] = {
            "toolchain": "gcc-arm",
            "cross_compiler": "arm-linux-gnueabi-gcc",
            "flags": "-O2 -march=armv3",
            "target_os": "NetBSD/acorn32 or RISC OS",
            "note": "StrongARM upgrade recommended for reasonable hash rates."
        }
        config["mining"]["hash_buffer_kb"] = 128
    else:
        # x86 variants
        march = {"i386": "i386", "i486": "i486", "i586": "pentium"}.get(arch, "i686")
        config["build"] = {
            "toolchain": "gcc",
            "cross_compiler": f"gcc -march={march}",
            "flags": f"-O2 -march={march} -static",
            "target_os": "Slackware or FreeBSD",
            "note": f"Static linking recommended for {arch} targets."
        }
        config["mining"]["hash_buffer_kb"] = min(profile["ram_typical_mb"] * 256, 2048)

    return config


# ---------------------------------------------------------------------------
# Performance Benchmarking
# ---------------------------------------------------------------------------

def run_benchmark(profile_key):
    """Run simulated benchmark for a hardware profile against modern baseline."""
    if profile_key not in HARDWARE_PROFILES:
        return {"error": f"Unknown profile: {profile_key}"}

    profile = HARDWARE_PROFILES[profile_key]

    # Modern baseline (x86_64 @ 3.5 GHz)
    modern_baseline = {
        "hash_rate": 50000,           # hashes/sec
        "attestation_time_ms": 2.5,   # ms per attestation
        "memory_bandwidth_mbps": 25000,
        "network_latency_ms": 5,
    }

    # Era-based performance scaling
    era_scale = {
        "pre-1985": {"cpu": 0.0005, "mem": 0.001, "net": 0.1},
        "1985-1989": {"cpu": 0.005, "mem": 0.01, "net": 0.3},
        "1990-1994": {"cpu": 0.03, "mem": 0.05, "net": 0.5},
        "1995-1999": {"cpu": 0.12, "mem": 0.15, "net": 0.8},
    }
    scale = era_scale.get(profile["era"], {"cpu": 0.1, "mem": 0.1, "net": 0.5})

    # Calculate simulated metrics
    raw_hash_rate = modern_baseline["hash_rate"] * scale["cpu"]
    attestation_time = modern_baseline["attestation_time_ms"] / scale["cpu"]
    mem_bandwidth = modern_baseline["memory_bandwidth_mbps"] * scale["mem"]
    net_latency = modern_baseline["network_latency_ms"] / scale["net"]

    # Apply multiplier for effective mining rate
    effective_rate = raw_hash_rate * profile["rtc_multiplier"]

    # Generate fingerprint hash for this profile
    fp_data = f"{profile['name']}-{profile['cpu']}-{profile['arch']}-{time.time()}"
    fingerprint = hashlib.sha256(fp_data.encode()).hexdigest()[:16]

    # Score: balance of raw performance and antiquity bonus
    score = (effective_rate / modern_baseline["hash_rate"]) * 100

    result = {
        "profile": profile_key,
        "name": profile["name"],
        "era": profile["era"],
        "benchmark": {
            "raw_hash_rate": round(raw_hash_rate, 2),
            "effective_hash_rate": round(effective_rate, 2),
            "attestation_time_ms": round(attestation_time, 2),
            "memory_bandwidth_mbps": round(mem_bandwidth, 2),
            "network_latency_ms": round(net_latency, 2),
            "fingerprint_hash": fingerprint,
        },
        "comparison": {
            "vs_modern_raw": f"{scale['cpu'] * 100:.2f}%",
            "vs_modern_effective": f"{effective_rate / modern_baseline['hash_rate'] * 100:.2f}%",
            "rtc_multiplier": profile["rtc_multiplier"],
            "rtc_bonus": profile["rtc_bonus"],
        },
        "score": round(score, 2),
        "verdict": _get_verdict(score, profile["era"]),
    }

    # Store in database
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO benchmark_results
        (profile_key, hash_rate, attestation_time_ms, memory_usage_mb,
         network_latency_ms, fingerprint_hash, modern_baseline_ratio, score, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        profile_key, effective_rate, attestation_time,
        profile["ram_typical_mb"], net_latency, fingerprint,
        effective_rate / modern_baseline["hash_rate"], score,
        result["verdict"]
    ))
    conn.commit()
    conn.close()

    return result


def _get_verdict(score, era):
    """Generate a human-readable verdict for a benchmark score."""
    if era == "pre-1985":
        return f"Score {score:.1f} — LEGENDARY. This machine predates the Macintosh. The antiquity bonus alone makes it worthwhile. Eternal glory awaits."
    elif era == "1985-1989":
        return f"Score {score:.1f} — HEROIC. Cold War era hardware mining cryptocurrency. The 200 RTC bonus is well-deserved."
    elif era == "1990-1994":
        return f"Score {score:.1f} — VETERAN. Early 90s workstation class. The multiplier makes this surprisingly viable."
    elif era == "1995-1999":
        return f"Score {score:.1f} — CLASSIC. Late 90s hardware with decent performance. Solid mining candidate."
    else:
        return f"Score {score:.1f} — Standard hardware. No antiquity bonus."


# ---------------------------------------------------------------------------
# Resurrection Guides
# ---------------------------------------------------------------------------

RESURRECTION_GUIDES = {
    "sparc": {
        "title": "Resurrecting a Sun SPARCstation for RustChain Mining",
        "platforms": ["Sun SPARCstation 5", "Sun SPARCstation 20", "Sun Ultra 5"],
        "difficulty": "Medium",
        "time_estimate": "4-8 hours",
        "steps": [
            {
                "step": 1,
                "title": "Acquire and Inspect Hardware",
                "details": [
                    "Check for corroded NVRAM battery (common failure point on Sun hardware).",
                    "Replace the NVRAM chip or re-program with hostid/MAC using mkp command.",
                    "Verify SCSI drives spin up (listen for the whine).",
                    "Check for bulging capacitors on the motherboard.",
                    "Ensure you have the correct monitor cable (13W3 for older models, VGA for Ultra 5).",
                ]
            },
            {
                "step": 2,
                "title": "Install Operating System",
                "details": [
                    "For SPARCstation 5/20: Install NetBSD/sparc from CD or network boot.",
                    "For Ultra 5: Install Debian sparc64 or NetBSD/sparc64.",
                    "Network boot: Set up a RARP/TFTP/NFS server on a modern machine.",
                    "Boot into OBP (OpenBoot PROM) with Stop+A, then: boot net",
                    "Alternative: Write install image to SCSI disk from another machine.",
                ]
            },
            {
                "step": 3,
                "title": "Configure Network",
                "details": [
                    "Built-in Ethernet should be auto-detected (le0 or hme0).",
                    "For SPARCstation 5: AUI port needs a transceiver for 10Base-T.",
                    "For Ultra 5: Standard 10/100 RJ-45 port.",
                    "Configure static IP or DHCP in /etc/rc.conf (NetBSD) or /etc/network/interfaces (Debian).",
                    "Test connectivity: ping the RustChain node at 50.28.86.131.",
                ]
            },
            {
                "step": 4,
                "title": "Cross-Compile the Miner",
                "details": [
                    "On a modern host: apt install gcc-sparc64-linux-gnu",
                    "Clone rustchain-miner and modify Cargo.toml for sparc target.",
                    "For C miner: sparc64-linux-gnu-gcc -O2 -o rtc-miner miner.c -lssl -lcrypto",
                    "For minimal build without TLS: sparc64-linux-gnu-gcc -O2 -DNOTLS -o rtc-miner miner.c",
                    "Transfer binary via SCP or NFS mount.",
                ]
            },
            {
                "step": 5,
                "title": "Run the Miner and Submit Attestation",
                "details": [
                    "Set environment: export RUSTCHAIN_NODE=https://50.28.86.131",
                    "Set wallet: export RTC_WALLET=your_wallet_name",
                    "Run: ./rtc-miner --wallet $RTC_WALLET --node $RUSTCHAIN_NODE",
                    "First run performs hardware fingerprinting (clock drift, cache timing, etc.).",
                    "Wait for 'Attestation submitted successfully' message.",
                    "Take a photo of the running machine with timestamp visible.",
                    "Screenshot the miner output showing successful attestation.",
                ]
            },
        ]
    },

    "68k": {
        "title": "Resurrecting Motorola 68K Hardware for RustChain Mining",
        "platforms": ["Amiga 4000", "Amiga 1200", "Macintosh Quadra 840AV", "NeXTcube", "Atari Falcon030"],
        "difficulty": "Hard",
        "time_estimate": "8-16 hours",
        "steps": [
            {
                "step": 1,
                "title": "Hardware Assessment",
                "details": [
                    "Check for battery leakage (very common on 68K Macs and Amigas).",
                    "Clean any corrosion with isopropyl alcohol and a soft brush.",
                    "For Amigas: Check Kickstart ROM version (3.1 recommended).",
                    "For NeXT: Verify magneto-optical or SCSI HDD is functional.",
                    "Test all RAM modules — 68K machines are sensitive to bad RAM.",
                ]
            },
            {
                "step": 2,
                "title": "Install Operating System",
                "details": [
                    "NeXTcube: NeXTSTEP 3.3 or OPENSTEP 4.2 from optical media.",
                    "Amiga: AmigaOS 3.1 from Cloanto Amiga Forever or original disks.",
                    "Mac Quadra: NetBSD/mac68k from network boot or SCSI disk.",
                    "Falcon: FreeMiNT with network stack.",
                    "For all: NetBSD provides the most consistent cross-platform experience.",
                ]
            },
            {
                "step": 3,
                "title": "Network Setup",
                "details": [
                    "NeXTcube: Built-in Ethernet — just plug in and configure.",
                    "Amiga 4000: Install X-Surf 100 in Zorro III slot, or use A2065.",
                    "Amiga 1200: PCMCIA Ethernet card (e.g., Netgear FA411) with device driver.",
                    "Mac Quadra: Built-in Ethernet via AAUI-15 with 10Base-T transceiver.",
                    "Falcon: NetUSBee adapter or EtherNEC on cartridge port.",
                    "Install Miami or AmiTCP for AmigaOS TCP/IP stack.",
                ]
            },
            {
                "step": 4,
                "title": "Cross-Compile the Miner",
                "details": [
                    "On modern host: apt install gcc-m68k-linux-gnu binutils-m68k-linux-gnu",
                    "Compile: m68k-linux-gnu-gcc -O2 -m68040 -o rtc-miner miner.c",
                    "For 68030 targets (Falcon, A1200): use -m68030 flag.",
                    "For AmigaOS native: use VBCC cross-compiler with amiga target.",
                    "For NeXTSTEP native: use GCC on the NeXT itself (ships with dev tools).",
                    "Transfer via FTP, serial (Zmodem), or physical media.",
                ]
            },
            {
                "step": 5,
                "title": "Mine and Document",
                "details": [
                    "Run the miner with: ./rtc-miner --wallet YOUR_WALLET",
                    "68040 machines should achieve attestation within 2-5 minutes.",
                    "68030 machines may take 5-15 minutes per attestation.",
                    "Photograph the machine running — show the screen and a clock/newspaper.",
                    "Screenshot or photograph the terminal showing attestation success.",
                    "Note: 68K machines get a 3.5x multiplier for the 1990-1994 era.",
                ]
            },
        ]
    },

    "mips": {
        "title": "Resurrecting SGI/MIPS Hardware for RustChain Mining",
        "platforms": ["SGI Indy", "SGI O2", "SGI Indigo2", "DECstation 5000"],
        "difficulty": "Medium-Hard",
        "time_estimate": "6-12 hours",
        "steps": [
            {
                "step": 1,
                "title": "Hardware Preparation",
                "details": [
                    "SGI machines: Check for dead DALLAS NVRAM (similar to Sun — contains MAC/serial).",
                    "Indy/Indigo2: Need 13W3 to VGA adapter for modern monitor.",
                    "O2: Standard VGA output — easiest SGI to connect to modern display.",
                    "Check SCSI drives — SGI used 50-pin narrow SCSI (Indy) or 68-pin wide SCSI.",
                    "DECstation: Requires special serial console cable (MMJ to DB9).",
                ]
            },
            {
                "step": 2,
                "title": "Install Operating System",
                "details": [
                    "SGI with IRIX: Install from original CDs. IRIX 6.5.22 is the final version.",
                    "SGI with Linux: Gentoo/MIPS or NetBSD/sgimips via network boot.",
                    "Network boot SGI: bootp() command from PROM, set up DHCP + TFTP server.",
                    "DECstation: NetBSD/pmax from network boot (BOOTP/MOP protocol).",
                    "For mining, Linux/NetBSD is preferred — modern TLS libraries available.",
                ]
            },
            {
                "step": 3,
                "title": "Network Configuration",
                "details": [
                    "All SGI machines have built-in Ethernet — usually ec0 or ef0.",
                    "IRIX: Use 'chkconfig network on' and edit /etc/hosts + /etc/config/netif.options.",
                    "Linux/NetBSD: Standard ifconfig or ip commands.",
                    "DECstation: Built-in LANCE Ethernet (le0 in NetBSD).",
                    "Test: ping 50.28.86.131 (RustChain production node).",
                ]
            },
            {
                "step": 4,
                "title": "Build the Miner",
                "details": [
                    "IRIX native build: cc -O2 -mips4 -n32 -o rtc-miner miner.c -lssl -lcrypto",
                    "Cross-compile on modern host: mips-linux-gnu-gcc -O2 -o rtc-miner miner.c",
                    "For O2 (R10000/R5000): mips64-linux-gnu-gcc -O2 -mips4 -o rtc-miner miner.c",
                    "NetBSD/sgimips: Install pkgsrc, build with system GCC.",
                    "Transfer binary via rcp, scp, or NFS.",
                ]
            },
            {
                "step": 5,
                "title": "Mining and Attestation",
                "details": [
                    "Start the miner: ./rtc-miner --wallet YOUR_WALLET --node https://50.28.86.131",
                    "R4400 (Indy) should complete fingerprint in 1-3 minutes.",
                    "R10000 (O2) is significantly faster — under 1 minute.",
                    "R3000 (DECstation) will be slow — 5-10 minutes per attestation.",
                    "Use IndyCam for timestamped video proof if available.",
                    "MIPS machines get 3.0x multiplier (1990-1994 era).",
                ]
            },
        ]
    },

    "alpha": {
        "title": "Resurrecting DEC Alpha Hardware for RustChain Mining",
        "platforms": ["AlphaStation 500", "AlphaServer 1000A"],
        "difficulty": "Medium",
        "time_estimate": "4-8 hours",
        "steps": [
            {
                "step": 1,
                "title": "Hardware Check",
                "details": [
                    "Verify SRM console firmware is installed (not ARC — ARC is for Windows NT only).",
                    "Toggle between SRM and ARC: set os_type unix in SRM, or flash firmware.",
                    "Check PCI slots and SCSI chain.",
                    "Alpha machines are loud — server-grade fans. Consider earplugs.",
                    "Ensure adequate power — AlphaServer 1000A can draw 500W+.",
                ]
            },
            {
                "step": 2,
                "title": "Install Operating System",
                "details": [
                    "Recommended: Debian alpha (archive.debian.org has old ISOs).",
                    "Alternative: NetBSD/alpha — excellent hardware support.",
                    "Tru64 UNIX: Works but limited modern software availability.",
                    "SRM boot command: boot dka0 (SCSI) or boot ewa0 (network).",
                    "aboot is the Linux bootloader for Alpha — install to MBR.",
                ]
            },
            {
                "step": 3,
                "title": "Network Configuration",
                "details": [
                    "Built-in Tulip (DEC 21x4x) Ethernet — excellent driver support.",
                    "PCI slots accept standard x86 NICs (Intel, 3Com).",
                    "Configure in /etc/network/interfaces (Debian) or /etc/rc.conf (NetBSD).",
                    "Alpha has 64-bit addressing — no network driver compatibility issues.",
                ]
            },
            {
                "step": 4,
                "title": "Build the Miner",
                "details": [
                    "Cross-compile: alpha-linux-gnu-gcc -O2 -mcpu=ev56 -o rtc-miner miner.c",
                    "Or build natively on Debian alpha with gcc and libssl-dev.",
                    "Alpha excels at 64-bit integer arithmetic — hash performance is surprisingly good.",
                    "Native Tru64 build: cc -O2 -arch ev56 -o rtc-miner miner.c -lssl -lcrypto",
                ]
            },
            {
                "step": 5,
                "title": "Mining Attestation",
                "details": [
                    "Run: ./rtc-miner --wallet YOUR_WALLET --node https://50.28.86.131",
                    "21164 (EV56) at 500 MHz should complete attestation in under 30 seconds.",
                    "Alpha's 64-bit pipeline makes it one of the best vintage miners.",
                    "2.5x multiplier for 1995-1999 era hardware.",
                    "Take photos of the distinctive DEC tower case with miner running.",
                ]
            },
        ]
    },

    "parisc": {
        "title": "Resurrecting HP PA-RISC Hardware for RustChain Mining",
        "platforms": ["HP 9000/712", "HP 9000/735"],
        "difficulty": "Hard",
        "time_estimate": "8-16 hours",
        "steps": [
            {
                "step": 1,
                "title": "Hardware Inspection",
                "details": [
                    "HP 9000 workstations use proprietary HIL keyboard/mouse by default.",
                    "Later models (712) support PS/2 — use a PS/2 keyboard.",
                    "Serial console is the most reliable interface — use a null-modem cable.",
                    "Check SCSI drives — HP used Fast/Wide SCSI-2.",
                    "Verify graphics: CRX (712) or Visualize (later models).",
                ]
            },
            {
                "step": 2,
                "title": "Install Operating System",
                "details": [
                    "HP-UX 10.20 or 11.0: Install from DDS tape or CD.",
                    "Debian hppa: Experimental port — use daily builds from debian-ports.org.",
                    "NetBSD/hp700: Most stable open-source option.",
                    "Boot from network: Use 'boot lan' at PDC (Processor Dependent Code) prompt.",
                    "ISL (Initial System Loader) handles the boot chain.",
                ]
            },
            {
                "step": 3,
                "title": "Network Setup",
                "details": [
                    "Built-in LASI Ethernet (le0) on most models.",
                    "EISA models can use standard EISA NICs.",
                    "HP-UX: Use SAM tool for network configuration.",
                    "Debian/NetBSD: Standard configuration files.",
                    "PA-RISC is big-endian — ensure miner handles byte ordering correctly.",
                ]
            },
            {
                "step": 4,
                "title": "Cross-Compile the Miner",
                "details": [
                    "On modern host: apt install gcc-hppa-linux-gnu",
                    "Compile: hppa-linux-gnu-gcc -O2 -o rtc-miner miner.c -lssl -lcrypto",
                    "HP-UX native: Use aCC (HP C compiler) or GCC from HP Porting Centre.",
                    "Watch for PA-RISC calling convention differences in assembly code.",
                    "Static linking recommended: -static flag.",
                ]
            },
            {
                "step": 5,
                "title": "Mine and Prove",
                "details": [
                    "Run miner with appropriate wallet and node settings.",
                    "PA-7100LC at 80 MHz: expect 3-8 minutes per attestation.",
                    "PA-7150 at 125 MHz: expect 2-4 minutes per attestation.",
                    "3.0x multiplier for 1990-1994 era.",
                    "HP 9000 machines are distinctively designed — great for proof photos.",
                ]
            },
        ]
    },

    "6502": {
        "title": "Resurrecting 6502/65C816 Hardware for RustChain Mining",
        "platforms": ["Commodore 64", "Apple II Plus", "Apple IIGS"],
        "difficulty": "Extreme",
        "time_estimate": "16-40 hours",
        "steps": [
            {
                "step": 1,
                "title": "Hardware Revival",
                "details": [
                    "C64: Check the power supply — original PSU can fry the machine. Use a modern replacement.",
                    "Apple II: Check for corroded chip sockets. Re-seat all socketed ICs.",
                    "IIGS: Replace the PRAM battery (3.6V lithium). Check for leakage damage.",
                    "Test with a known-good display (composite for C64/Apple II, RGB for IIGS).",
                    "Clean all edge connectors with isopropyl alcohol.",
                ]
            },
            {
                "step": 2,
                "title": "Add Network Hardware",
                "details": [
                    "C64: Install RR-Net MK3 (cartridge-port Ethernet with CS8900A chip).",
                    "Apple II/IIGS: Install Uthernet II card in Slot 3 (W5100-based).",
                    "Alternative for C64: Comet64 WiFi cartridge, or ETH64 (user port).",
                    "Alternative for Apple II: Serial port + SLIP/PPP to a bridge machine.",
                    "The Uthernet II / RR-Net provide raw TCP/IP socket access.",
                ]
            },
            {
                "step": 3,
                "title": "Set Up Development Environment",
                "details": [
                    "Install cc65 cross-compiler on a modern host (apt install cc65).",
                    "C64 target: cl65 -t c64 -O -o rtc-miner.prg miner.c",
                    "Apple II target: cl65 -t apple2 -O -o rtc-miner miner.c",
                    "IIGS target: cl65 -t apple2enh -O -o rtc-miner miner.c",
                    "Binary must fit in available RAM: ~38KB on C64, ~48KB on Apple II.",
                    "Use the existing apple2_miner/miner.c as a reference implementation.",
                ]
            },
            {
                "step": 4,
                "title": "Transfer and Run",
                "details": [
                    "C64: Transfer .prg via SD2IEC, 1541 Ultimate, or serial link.",
                    "Apple II: Transfer via CFFA3000, Floppy Emu, or serial with ADTPro.",
                    "IIGS: Use CFFA3000 CompactFlash adapter or FloppyEmu.",
                    "C64: LOAD\"RTC-MINER\",8,1 then RUN",
                    "Apple II: BRUN RTC-MINER or ProDOS launcher.",
                    "The miner will use floating bus / VIC-II timing for hardware fingerprint.",
                ]
            },
            {
                "step": 5,
                "title": "Submit Attestation",
                "details": [
                    "The miner connects directly to 50.28.86.131:80 via W5100/CS8900A.",
                    "Attestation payload is sent as HTTP POST with JSON body.",
                    "At 1 MHz, expect 15-60 minutes per attestation cycle.",
                    "C64/Apple II Plus get the MAXIMUM 5.0x multiplier and 300 RTC bonus.",
                    "IIGS gets 4.0x multiplier and 200 RTC bonus.",
                    "This is the ultimate retro flex. Document everything with photos and video.",
                    "ETERNAL GLORY awaits for pre-1985 machines.",
                ]
            },
        ]
    },
}


def get_resurrection_guide(family):
    """Get the resurrection guide for a hardware family."""
    if family in RESURRECTION_GUIDES:
        return RESURRECTION_GUIDES[family]
    return {"error": f"No guide available for family: {family}. Available: {list(RESURRECTION_GUIDES.keys())}"}


# ---------------------------------------------------------------------------
# PoA Signature Generation
# ---------------------------------------------------------------------------

def generate_poa_signature():
    """Generate a Proof-of-Antiquity signature for this submission."""
    data = f"ghost2314-{VERSION}-{datetime.now(timezone.utc).isoformat()}-ElromEvedElElyon"
    return "poa_ghost2314_" + hashlib.sha256(data.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# REST API Request Handler
# ---------------------------------------------------------------------------

class GhostMachineHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Ghost in the Machine toolkit."""

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        routes = {
            "/": self._serve_html,
            "/api/health": self._api_health,
            "/api/profiles": self._api_profiles,
            "/api/profile": self._api_profile_detail,
            "/api/detect": self._api_detect,
            "/api/compatibility": self._api_compatibility,
            "/api/benchmark": self._api_benchmark,
            "/api/config": self._api_config,
            "/api/guide": self._api_guide,
            "/api/guides": self._api_guides_list,
            "/api/eras": self._api_eras,
            "/api/benchmarks": self._api_benchmark_history,
            "/api/stats": self._api_stats,
            "/api/poa-signature": self._api_poa_signature,
        }

        handler = routes.get(path)
        if handler:
            handler(params)
        else:
            self._json_response(404, {"error": "Not found", "available_endpoints": list(routes.keys())})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            data = json.loads(body) if body.strip() else {}
        except json.JSONDecodeError:
            self._json_response(400, {"error": "Invalid JSON"})
            return

        if path == "/api/log-resurrection":
            self._api_log_resurrection(data)
        elif path == "/api/benchmark":
            profile = data.get("profile", "")
            self._api_benchmark({"profile": [profile]})
        else:
            self._json_response(404, {"error": "Not found"})

    def _json_response(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode("utf-8"))

    def _serve_html(self, params):
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resurrect.html")
        if os.path.exists(html_path):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(html_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self._json_response(404, {"error": "resurrect.html not found. Place it next to server.py."})

    def _api_health(self, params):
        self._json_response(200, {
            "status": "alive",
            "service": "Ghost in the Machine — Pre-2000 Hardware Resurrection Toolkit",
            "version": VERSION,
            "profiles_loaded": len(HARDWARE_PROFILES),
            "guides_available": len(RESURRECTION_GUIDES),
            "bounty": "#2314",
            "poa_signature": generate_poa_signature(),
        })

    def _api_profiles(self, params):
        era_filter = params.get("era", [None])[0]
        family_filter = params.get("family", [None])[0]
        arch_filter = params.get("arch", [None])[0]

        profiles = []
        for key, p in HARDWARE_PROFILES.items():
            if era_filter and p["era"] != era_filter:
                continue
            if family_filter and p["family"] != family_filter:
                continue
            if arch_filter and p["arch"] != arch_filter:
                continue
            profiles.append({
                "key": key,
                "name": p["name"],
                "manufacturer": p["manufacturer"],
                "year": p["year"],
                "cpu": p["cpu"],
                "arch": p["arch"],
                "family": p["family"],
                "era": p["era"],
                "rtc_multiplier": p["rtc_multiplier"],
                "rtc_bonus": p["rtc_bonus"],
            })

        profiles.sort(key=lambda x: x["year"])
        self._json_response(200, {
            "count": len(profiles),
            "profiles": profiles,
            "filters": {"era": era_filter, "family": family_filter, "arch": arch_filter},
        })

    def _api_profile_detail(self, params):
        key = params.get("key", [None])[0]
        if not key or key not in HARDWARE_PROFILES:
            self._json_response(400, {
                "error": "Missing or invalid 'key' parameter",
                "available": sorted(HARDWARE_PROFILES.keys()),
            })
            return
        self._json_response(200, {"key": key, **HARDWARE_PROFILES[key]})

    def _api_detect(self, params):
        info = detect_local_hardware()
        self._json_response(200, info)

    def _api_compatibility(self, params):
        key = params.get("profile", [None])[0]
        if not key:
            self._json_response(400, {"error": "Missing 'profile' query parameter"})
            return
        result = check_compatibility(key)
        if "error" in result:
            self._json_response(404, result)
        else:
            self._json_response(200, result)

    def _api_benchmark(self, params):
        key = params.get("profile", [None])[0]
        if not key:
            # Benchmark all profiles
            results = []
            for k in HARDWARE_PROFILES:
                results.append(run_benchmark(k))
            results.sort(key=lambda x: x["score"], reverse=True)
            self._json_response(200, {"count": len(results), "benchmarks": results})
            return
        result = run_benchmark(key)
        if "error" in result:
            self._json_response(404, result)
        else:
            self._json_response(200, result)

    def _api_config(self, params):
        key = params.get("profile", [None])[0]
        if not key:
            self._json_response(400, {"error": "Missing 'profile' query parameter"})
            return
        config = generate_mining_config(key)
        if not config:
            self._json_response(404, {"error": f"Unknown profile: {key}"})
        else:
            self._json_response(200, config)

    def _api_guide(self, params):
        family = params.get("family", [None])[0]
        if not family:
            self._json_response(400, {
                "error": "Missing 'family' query parameter",
                "available": list(RESURRECTION_GUIDES.keys()),
            })
            return
        guide = get_resurrection_guide(family)
        self._json_response(200, guide)

    def _api_guides_list(self, params):
        guides = []
        for key, g in RESURRECTION_GUIDES.items():
            guides.append({
                "family": key,
                "title": g["title"],
                "platforms": g["platforms"],
                "difficulty": g["difficulty"],
                "time_estimate": g["time_estimate"],
                "steps_count": len(g["steps"]),
            })
        self._json_response(200, {"count": len(guides), "guides": guides})

    def _api_eras(self, params):
        self._json_response(200, ERA_PAYOUTS)

    def _api_benchmark_history(self, params):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM benchmark_results ORDER BY tested_at DESC LIMIT 100"
        ).fetchall()
        conn.close()
        self._json_response(200, {
            "count": len(rows),
            "results": [dict(r) for r in rows],
        })

    def _api_stats(self, params):
        conn = sqlite3.connect(DB_PATH)
        stats = {
            "total_profiles": conn.execute("SELECT COUNT(*) FROM hardware_profiles").fetchone()[0],
            "total_benchmarks": conn.execute("SELECT COUNT(*) FROM benchmark_results").fetchone()[0],
            "total_resurrections": conn.execute("SELECT COUNT(*) FROM resurrection_logs").fetchone()[0],
            "avg_score": conn.execute("SELECT AVG(score) FROM benchmark_results").fetchone()[0],
            "top_scorer": None,
            "eras": {},
        }

        top = conn.execute(
            "SELECT profile_key, MAX(score) as max_score FROM benchmark_results"
        ).fetchone()
        if top and top[0]:
            stats["top_scorer"] = {"profile": top[0], "score": top[1]}

        for era in ERA_PAYOUTS:
            count = conn.execute(
                "SELECT COUNT(*) FROM hardware_profiles WHERE era = ?", (era,)
            ).fetchone()[0]
            stats["eras"][era] = count

        conn.close()
        self._json_response(200, stats)

    def _api_poa_signature(self, params):
        self._json_response(200, {
            "signature": generate_poa_signature(),
            "bounty": "#2314",
            "author": "ElromEvedElElyon",
        })

    def _api_log_resurrection(self, data):
        required = ["profile_key", "wallet_address"]
        for field in required:
            if field not in data:
                self._json_response(400, {"error": f"Missing required field: {field}"})
                return

        if data["profile_key"] not in HARDWARE_PROFILES:
            self._json_response(400, {"error": f"Unknown profile: {data['profile_key']}"})
            return

        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO resurrection_logs
            (profile_key, wallet_address, os_installed, network_method, steps_completed)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["profile_key"],
            data["wallet_address"],
            data.get("os_installed", ""),
            data.get("network_method", ""),
            json.dumps(data.get("steps_completed", [])),
        ))
        conn.commit()
        conn.close()

        self._json_response(201, {
            "status": "logged",
            "message": f"Resurrection attempt for {data['profile_key']} logged successfully.",
        })

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sys.stderr.write(f"[{timestamp}] {args[0]}\n")


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main():
    """Start the Ghost in the Machine server."""
    print(r"""
   ____  _               _     _         _   _
  / ___|| |__   ___  ___| |_  (_)_ __   | |_| |__   ___
 | |  _ | '_ \ / _ \/ __| __| | | '_ \  | __| '_ \ / _ \
 | |_| || | | | (_) \__ \ |_  | | | | | | |_| | | |  __/
  \____||_| |_|\___/|___/\__| |_|_| |_|  \__|_| |_|\___|
  __  __            _     _
 |  \/  | __ _  ___| |__ (_)_ __   ___
 | |\/| |/ _` |/ __| '_ \| | '_ \ / _ \
 | |  | | (_| | (__| | | | | | | |  __/
 |_|  |_|\__,_|\___|_| |_|_|_| |_|\___|

  Pre-2000 Hardware Resurrection Toolkit for RustChain
  Bounty #2314 — Ghost in the Machine (100+ RTC)
  Version {version}
    """.format(version=VERSION))

    init_db()
    print(f"[*] Database initialized: {DB_PATH}")
    print(f"[*] Loaded {len(HARDWARE_PROFILES)} hardware profiles")
    print(f"[*] Loaded {len(RESURRECTION_GUIDES)} resurrection guides")
    print(f"[*] PoA Signature: {generate_poa_signature()}")
    print(f"[*] Starting server on {HOST}:{PORT}")
    print(f"[*] Web interface: http://localhost:{PORT}/")
    print(f"[*] API docs:      http://localhost:{PORT}/api/health")
    print()

    server = HTTPServer((HOST, PORT), GhostMachineHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Ghost in the Machine server.")
        server.server_close()


if __name__ == "__main__":
    main()
