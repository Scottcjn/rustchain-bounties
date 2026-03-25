# RustChain Miner Handbook

**Version:** RIP-200 PoA (Protocol v2.2.1)  
**Last Updated:** January 2025  
**Bounty Reference:** This document supports the RustChain miner ecosystem

---

## Table of Contents

1. [Overview](#overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Operating System Setup](#operating-system-setup)
4. [Miner Installation](#miner-installation)
5. [Configuration](#configuration)
6. [Your First Attestation](#your-first-attestation)
7. [Hardware Fingerprinting](#hardware-fingerprinting)
8. [Multiplier Tiers](#multiplier-tiers)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Configuration](#advanced-configuration)

---

## Overview

RustChain uses **RIP-200 Proof of Attestation (PoA)** — a novel consensus mechanism where miners prove two things simultaneously:

1. **Physical hardware existence** — via hardware fingerprinting using cache timing, clock drift, SIMD feature detection, and thermal profiling
2. **Honest participation** — via attestation challenges that require the hardware to perform real computations

Unlike proof-of-work (PoW) which rewards energy consumption, or proof-of-stake (PoS) which rewards token ownership, RIP-200 rewards **real, diverse hardware diversity**. Older and rarer hardware earns higher multipliers, creating economic incentive to keep vintage hardware running.

The network operates in **epochs** of 144 blocks each. Miners must successfully attest once per epoch to maintain enrollment and qualify for the epoch lottery.

---

## Hardware Requirements

### Minimum Requirements

| Component | Minimum | Recommended |
|---|---|---|
| CPU | Any x86_64, ARM64, or PowerPC (G4+) | x86_64 with AES-NI, ≥ 4 cores |
| RAM | 2 GB | 4 GB or more |
| Disk | 100 MB for miner software | SSD with 1 GB+ free |
| Network | Broadband internet (stable) | Wired Ethernet, ≥ 10 Mbps upload |
| OS | Linux, macOS, Windows with Python 3.8+ | Linux (Ubuntu 22.04 LTS or Debian 12) |

### Hardware Requirements by Category

**x86_64 CPUs (Intel/AMD)**
- Works on any x86_64 CPU from 2010+
- Modern CPUs (Zen 3, Ice Lake, Tiger Lake) get 1.0× multiplier
- Older architectures (Haswell, Skylake) may get slight bumps
- AES-NI support is checked but not required
- CPU must support at least one of: RDTSC, RDTSCP,_cpuid

**ARM64 CPUs (Apple Silicon, ARM servers)**
- Apple Silicon (M1/M2/M3) → 1.2× multiplier (dedicated hardware bonus)
- ARM server chips (Graviton, Ampere Altra) → 1.0–1.1× depending on age
- ARM32 is **not supported** for RIP-200 attestation

**PowerPC (Vintage Hardware)**
- PowerPC G4 (7450/7447 family) → 2.5× multiplier
- PowerPC G5 (970/POWER4 family) → 2.0× multiplier
- POWER8 → 1.5× multiplier
- POWER9/POWER10 → 1.0–1.2× (closer to commodity server hardware)
- **Note:** PowerPC miners require `ppc64` Linux and may need cross-compilation

**RISC-V**
- Experimental support; multiplier depends on implementation
- Generally 1.0× unless the hardware is certified vintage

### Real Hardware Requirement

> ⚠️ **Critical:** Virtual machines, containers, and cloud instances **will** attest, but rewards can be **penalized or withheld** if the hardware fingerprint shows VM signatures. The node operators review attestation data weekly and may exclude suspicious miners from the lottery.

If you're running in a cloud VM for testing, use `--dry-run` mode (see [Testing Mode](#testing-mode)) and move to bare-metal hardware for production.

---

## Operating System Setup

### Linux (Ubuntu 22.04 / Debian 12)

1. **Update system packages:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python and dependencies:**
   ```bash
   sudo apt install -y python3 python3-pip python3-venv git curl
   ```

3. **Check Python version (requires 3.8+):**
   ```bash
   python3 --version
   # Should show Python 3.8.0 or higher
   ```

4. **Configure firewall (optional but recommended):**
   ```bash
   sudo ufw allow 443/tcp   # For HTTPS to node
   sudo ufw allow 80/tcp    # For HTTP (health checks)
   ```

### macOS (Ventura or later)

1. **Install Homebrew (if not present):**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python:**
   ```bash
   brew install python@3.11
   ```

3. **Verify Python:**
   ```bash
   python3 --version
   ```

### Windows (10/11)

1. **Install Python 3.11+** from [python.org](https://python.org/downloads)
   - During install, check **"Add Python to PATH"**

2. **Open PowerShell as Administrator** and verify:
   ```powershell
   python --version
   ```

3. **Install Git:**
   ```powershell
   winget install Git.Git
   ```

---

## Miner Installation

### Option A: Clone the Repository (Recommended)

```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
```

Platform-specific miners are in the `miners/` directory:

| Platform | Path | Notes |
|---|---|---|
| Linux x86_64 | `miners/linux/rustchain_linux_miner.py` | Main miner script |
| macOS Intel/Apple Silicon | `miners/macos/rustchain_mac_miner_v2.4.py` | Universal binary |
| Windows | `miners/windows/rustchain_windows_miner.py` | GUI miner with Tkinter |

### Option B: Direct Download (No Git)

```bash
# Linux
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/rustchain_linux_miner.py \
  -o rustchain_linux_miner.py

# macOS
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/macos/rustchain_mac_miner_v2.4.py \
  -o rustchain_mac_miner_v2.4.py

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/windows/rustchain_windows_miner.py" \
  -OutFile "rustchain_windows_miner.py"
```

### Option C: Build from Source (Advanced)

If you want to build a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build Linux executable
pyinstaller --onefile --name rustchain-miner \
  miners/linux/rustchain_linux_miner.py

# Output: dist/rustchain-miner
```

---

## Configuration

### Configuration File

The miner reads configuration from `~/.rustchain/miner.cfg` (Linux/macOS) or `%USERPROFILE%\.rustchain\miner.cfg` (Windows). Create it if it doesn't exist:

```ini
[miner]
wallet = YOUR_MINER_ID
node_url = https://50.28.86.131
log_level = INFO

[attestation]
interval_seconds = 300
timeout_seconds = 30
retry_attempts = 3

[fingerprint]
enable_thermal = true
enable_simd = true
enable_cache_timing = true
```

### Command-Line Arguments

Most options can be passed as CLI arguments (these override the config file):

| Argument | Description | Default |
|---|---|---|
| `--wallet` | Miner/wallet ID | _(required)_ |
| `--node` | RustChain node URL | `https://50.28.86.131` |
| `--log-level` | DEBUG, INFO, WARNING, ERROR | `INFO` |
| `--dry-run` | Run without attesting | `false` |
| `--fingerprint-only` | Only run fingerprinting, don't attest | `false` |

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `RUSTCHAIN_NODE_URL` | Primary node URL | `https://50.28.86.131` |
| `RUSTCHAIN_BACKUP_URLS` | Comma-separated backup URLs | _(none)_ |
| `RUSTCHAIN_LOG_LEVEL` | Logging verbosity | `INFO` |

---

## Your First Attestation

Follow these steps to complete your first attestation challenge:

### Step 1: Verify Node Connectivity

```bash
curl -sk https://50.28.86.131/health | python3 -m json.tool
```

Expected output includes `"ok": true`. If you see SSL errors, use `-k` flag (self-signed cert) or add `verify=False` in Python.

### Step 2: Get an Attestation Challenge

```bash
curl -sk -X POST https://50.28.86.131/attest/challenge \
  -H 'Content-Type: application/json' \
  -d '{}' | python3 -m json.tool
```

Response:
```json
{
  "nonce": "a3f8c2d1e9b4...",
  "server_time": 1771038696,
  "expires_at": 1771038996
}
```

The nonce expires in 300 seconds. You must complete the attestation before `expires_at`.

### Step 3: Submit Attestation

The miner script handles the fingerprinting and computation automatically:

```bash
# Linux
python3 miners/linux/rustchain_linux_miner.py \
  --wallet YOUR_MINER_ID \
  --node https://50.28.86.131
```

The miner will:
1. Collect hardware fingerprints (cache timing, clock drift, SIMD detection)
2. Build the attestation payload
3. Submit to `POST /attest/submit`

### Step 4: Enroll for the Epoch

After a successful attestation, you must enroll in the current epoch:

```bash
curl -sk -X POST https://50.28.86.131/epoch/enroll \
  -H 'Content-Type: application/json' \
  -d '{"miner_id": "YOUR_MINER_ID"}'
```

If you get `{"error": "no_recent_attestation", "ttl_s": 600}`, wait a few minutes and retry after the attestation has propagated.

### Step 5: Verify Enrollment

```bash
curl -sk https://50.28.86.131/api/miners | python3 -c "
import json, sys
miners = json.load(sys.stdin)
for m in miners:
    if m.get('miner') == 'YOUR_MINER_ID':
        print('ENROLLED:', json.dumps(m, indent=2))
        break
else:
    print('NOT FOUND — wait a few minutes and retry')
"
```

---

## Hardware Fingerprinting

RIP-200 attestation is unique because it identifies your physical hardware through multiple independent signals — not just a MAC address or IP address which are trivially spoofable. Each signal measures a physical property of your hardware:

### 1. Cache Timing Analysis

The memory cache timing fingerprint measures how long it takes to access memory at different offsets. Because cache behavior is determined by the physical CPU's cache geometry (cache size, associativity, line size), this creates a **unique, non-spoofable signature** tied to your specific CPU model and stepping.

**How it works:**
- The probe performs repeated memory accesses with carefully chosen offsets
- Timing variations reveal cache hit/miss patterns unique to your CPU
- Multiple probe rounds are averaged to reduce noise

**What it detects:**
- CPU model and microarchitecture family
- Cache hierarchy (L1/L2/L3 size and associativity)
- Whether running in a VM (VMs have distorted cache geometry)

**Tolerance:** ±5% variance is acceptable for matching.

### 2. Clock Drift Measurement

All hardware oscillators have slight frequency imperfections. The rate at which your CPU's TSC (Time Stamp Counter) drifts relative to a network NTP source is a **biometric of your specific hardware board**, stable over months.

**How it works:**
- Compare local RDTSC ticks against NTP-synchronized wall clock
- Measure drift over a 30-second window
- Report drift in PPM (parts per million) and direction

**What it detects:**
- Unique oscillator characteristics of the motherboard/CPU
- Changes in hardware (replacement of CPU/motherboard invalidates fingerprint)
- VM detection: VMs typically show zero or unnatural drift

**Tolerance:** ±50 PPM variance is acceptable.

### 3. SIMD Feature Detection

SIMD (Single Instruction Multiple Data) instructions — SSE, AVX, NEON, AltiVec — are hardware-specific. The exact set of SIMD extensions available, combined with measured throughput, provides a fingerprint of the CPU's silicon implementation.

**How it works:**
- Probe CPUID for available SIMD extensions
- Measure throughput of SIMD operations (e.g., 256-bit AVX2 add throughput)
- Compare against known signatures for CPU families

**What it detects:**
- CPU vendor (Intel vs AMD vs Apple vs IBM)
- CPU family and generation
- Die-to-die variations within the same model (rare but measurable)

### 4. Thermal Profiling

The thermal fingerprint measures how the CPU's temperature changes under a standardized load, then how fast it cools. Different CPU architectures have distinct thermal curves — heat capacity, thermal resistance, fan characteristics.

**How it works:**
- Apply a fixed computational load for 30 seconds
- Sample temperature every second via `os.cpu_freq()` or `psutil`
- Measure cool-down curve after load stops
- Fit to a thermal model to extract thermal constants

**What it detects:**
- Heatsink/cooling solution presence (or absence)
- CPU architecture (different architectures have different heat densities)
- Thermal throttling behavior

**Tolerance:** ±2°C variance is acceptable. Cooling solutions affect this significantly.

### 5. Combined Entropy Score

Each signal contributes to a combined **entropy score** (0.0–1.0) stored on-chain with every attestation. Higher entropy = harder to spoof = more trusted attestation.

The entropy score is published in `/api/miners` as `"entropy_score"` and factors into the lottery eligibility weighting.

---

## Multiplier Tiers

Miners earn reward multipliers based on hardware rarity and attestation entropy. Higher multipliers = more RTC per epoch lottery win.

### Current Multiplier Table

| Hardware | Multiplier | Notes |
|---|---|---|
| PowerPC G4 (7450/7447) | **4.0×** | Rarest; highest reward |
| PowerPC G5 (970 family) | **3.5×** | Vintage Apple hardware |
| POWER8 | **3.0×** | IBM server hardware |
| POWER9 | **2.0×** | Still relatively common |
| Apple Silicon (M-series) | **1.5×** | Dedicated ASIC-like efficiency |
| ARM64 Graviton/Ampere | **1.3×** | Cloud-native ARM servers |
| x86_64 (Haswell/Skylake) | **1.2×** | Older commodity server |
| x86_64 (Zen 3/ Ice Lake+) | **1.0×** | Modern commodity |

### Entropy Bonus

In addition to hardware type, attestation entropy provides a bonus:

| Entropy Score | Bonus Multiplier |
|---|---|
| 0.95–1.00 | +0.25× |
| 0.85–0.94 | +0.15× |
| 0.70–0.84 | +0.05× |
| 0.00–0.69 | no bonus |

### Effective Multiplier Example

A PowerPC G4 with an entropy score of 0.91 gets:
- Hardware base: 4.0×
- Entropy bonus: +0.15×
- **Effective multiplier: 4.15×**

---

## Monitoring

### Check Attestation Status

```bash
# Fetch miner list and filter for your miner
curl -sk https://50.28.86.131/api/miners | python3 -c "
import json, sys, datetime
data = json.load(sys.stdin)
for m in data:
    if m.get('miner') == 'YOUR_MINER_ID':
        last = m.get('last_attest', 0)
        print(f'Last attestation: {datetime.datetime.fromtimestamp(last)}')
        print(f'Entropy score: {m.get(\"entropy_score\")}')
        print(f'Multiplier: {m.get(\"antiquity_multiplier\")}')
        print(f'Hardware: {m.get(\"hardware_type\")} / {m.get(\"device_arch\")}')
"
```

### Check Lottery Eligibility

```bash
curl -sk "https://50.28.86.131/lottery/eligibility?miner_id=YOUR_MINER_ID"
```

### Check Balance

```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_MINER_ID"
```

### Prometheus Metrics (Advanced)

If the node exposes Prometheus metrics at `/metrics`:

```bash
curl -sk https://50.28.86.131/metrics | grep rustchain
```

Available metrics include:
- `rustchain_attestation_total` — total attestations by status
- `rustchain_epoch_current` — current epoch number
- `rustchain_miners_online` — number of online miners
- `rustchain_attestation_duration_seconds` — attestation round-trip time

---

## Troubleshooting

### Problem: Miner not showing in `/api/miners`

**Symptoms:** `rustchain_miners` tool doesn't return your miner ID.

**Causes:**
1. Attestation not yet completed successfully
2. Running on a VM (hardware fingerprint rejected)
3. Network connectivity issue to the node
4. Wrong `miner_id` in configuration

**Solutions:**
```bash
# 1. Check node health
curl -sk https://50.28.86.131/health

# 2. Re-run attestation challenge manually
curl -sk -X POST https://50.28.86.131/attest/challenge

# 3. Re-enroll
curl -sk -X POST https://50.28.86.131/epoch/enroll \
  -H 'Content-Type: application/json' \
  -d '{"miner_id": "YOUR_MINER_ID"}'

# 4. If VM suspected, move to bare-metal hardware
```

---

### Problem: SSL Certificate Errors

**Symptoms:** `SSL: CERTIFICATE_VERIFY_FAILED` or `requests.exceptions.SSLError`.

**Cause:** The RustChain node uses a self-signed certificate.

**Solutions:**
- For the Python miner: already handled in the miner script (`verify=False`)
- For direct curl: use `-k` / `--insecure` flag:
  ```bash
  curl -sk https://50.28.86.131/health
  ```

---

### Problem: Attestation Fails with "Signature Mismatch"

**Symptoms:** Attestation submit returns error about signature.

**Cause:** Clock drift is too large (> 60 seconds from node time).

**Solution:**
```bash
# Sync your system clock
sudo ntpdate -s time.google.com   # Linux
# or on macOS:
sudo sntp -s time.apple.com
```

---

### Problem: Enrollment Fails with "no_recent_attestation"

**Symptoms:** `POST /epoch/enroll` returns `{"error": "no_recent_attestation", "ttl_s": 600}`.

**Cause:** Your most recent attestation is older than the enrollment window. The attestation was either not submitted or was submitted after the enrollment window closed.

**Solution:**
```bash
# Wait for next epoch (up to 10 minutes) and re-attest
sleep 120
curl -sk -X POST https://50.28.86.131/attest/challenge
# Then re-submit via miner script
python3 rustchain_linux_miner.py --wallet YOUR_MINER_ID
```

---

### Problem: Permission Denied on Linux

**Symptoms:** `PermissionError: [Errno 13] Permission denied` when running the miner.

**Solution:**
```bash
# Ensure Python script is executable
chmod +x rustchain_linux_miner.py

# If using a system Python, consider a virtual environment
python3 -m venv ~/.rustchain/venv
source ~/.rustchain/venv/bin/activate
pip install requests httpx
python3 rustchain_linux_miner.py --wallet YOUR_MINER_ID
```

---

## Advanced Configuration

### Custom Fingerprint Parameters

For fine-tuning attestation fingerprinting, pass these to the miner script:

```bash
python3 rustchain_linux_miner.py \
  --wallet YOUR_MINER_ID \
  --fingerprint-cache-timing=strict \
  --fingerprint-simd=full \
  --fingerprint-thermal=false \
  --entropy-target=0.95
```

| Parameter | Options | Effect |
|---|---|---|
| `--fingerprint-cache-timing` | `loose`, `normal`, `strict` | Cache timing variance tolerance |
| `--fingerprint-simd` | `basic`, `full` | Basic = CPUID only; Full = throughput testing |
| `--fingerprint-thermal` | `true`, `false` | Enable/disable thermal profiling |
| `--entropy-target` | `0.0`–`1.0` | Minimum entropy score to accept attestation |

### Dry Run / Testing Mode

For testing without affecting on-chain state:

```bash
python3 rustchain_linux_miner.py \
  --wallet YOUR_MINER_ID \
  --dry-run
```

In dry-run mode:
- Fingerprinting runs but is not submitted
- No on-chain record is created
- Balance is not affected
- Useful for testing connectivity and verifying hardware detection

### Autostart with systemd (Linux)

For production miners, use systemd to ensure the miner restarts after reboots:

```ini
[Unit]
Description=RustChain PoA Miner
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Rustchain
ExecStart=/home/YOUR_USERNAME/.rustchain/venv/bin/python \
    /home/YOUR_USERNAME/Rustchain/miners/linux/rustchain_linux_miner.py \
    --wallet YOUR_MINER_ID \
    --node https://50.28.86.131
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo tee /etc/systemd/system/rustchain-miner.service >/dev/null <<'SERVICE'
[Unit]
Description=RustChain PoA Miner
After=network-online.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Rustchain
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/Rustchain/miners/linux/rustchain_linux_miner.py --wallet YOUR_MINER_ID
Restart=always
RestartSec=30
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable --now rustchain-miner
sudo systemctl status rustchain-miner
```

### Multi-Miner on Same Machine

You can run multiple miners on the same physical machine if each has a distinct `miner_id`. They will share hardware fingerprints but the node tracks each miner separately. This is useful for managing multiple wallet addresses from one machine.

```bash
# Miner 1
python3 rustchain_linux_miner.py --wallet miner-alpha --port 8001

# Miner 2
python3 rustchain_linux_miner.py --wallet miner-beta --port 8002
```

Each miner instance should have a distinct `--port` to avoid port conflicts if running simultaneously.
