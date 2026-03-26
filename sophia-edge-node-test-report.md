# sophia-edge-node Installation Test Report

**Date:** 2026-03-26  
**Bounty Issue:** https://github.com/Scottcjn/rustchain-bounties/issues/2321  
**Payment Address:** eB51DWp1uECrLZRLsE2cnyZUzfRWvzUzaJzkatTpQV9

---

## Environment

- **Architecture:** x86_64 (AMD EPYC-Genoa Processor)  
  - Note: This is NOT an ARM device; the install script is designed for Raspberry Pi 4/5
- **OS:** Linux 5.15.0
- **Python:** 3.10+
- **Install Method:** Cloned from https://github.com/Scottcjn/sophia-edge-node

---

## Test 1: install.sh (Full Installer)

```bash
git clone https://github.com/Scottcjn/sophia-edge-node && cd sophia-edge-node && sudo ./install.sh
```

**Result:** ❌ FAILED

```
[-] Unsupported architecture: x86_64. This installer targets Raspberry Pi 4/5.
```

The install script has a hard architecture check at the beginning (`detect_hardware()`) that rejects x86_64 systems. This is a **design limitation** — the miner components are Python-based and could theoretically run on x86_64, but the installer blocks non-ARM platforms.

**Bug Report Suggestion:** The architecture check is overly restrictive. Consider:
1. Allowing x86_64 to install with a warning instead of an error
2. Creating a separate `install-server.sh` for non-ARM deployments
3. At minimum, allowing the Python dependencies to be installed independently

---

## Test 2: Manual Installation (Python Direct Run)

Since `install.sh` blocks x86_64, I tested running the Python scripts directly:

### Dependencies

```bash
pip install aiohttp
```

All required Python packages are already available or easily installable:
- `aiohttp` ✅ (required)
- Standard library modules: `asyncio`, `json`, `logging`, `hashlib`, `uuid`, `pathlib`, `socket`, `struct`, `time`, `random` ✅

### Miner Execution

```bash
python3 rustchain_miner.py
```

**Output:**
```
[2026-03-26 17:29:23] WARNING Config not found at /opt/rustchain-arcade/config.json, using defaults
[2026-03-26 17:29:23] INFO === Sophia Edge Miner v2.0 ===
[2026-03-26 17:29:23] INFO Node ID   : rustchain-arcade-rpi
[2026-03-26 17:29:23] INFO Miner ID  : acca73a95780d7d6
[2026-03-26 17:29:23] INFO CPU       : AMD EPYC-Genoa Processor (unknown_arm)
[2026-03-26 17:29:23] INFO Arch      : x86_64
[2026-03-26 17:29:23] INFO Node URL  : https://50.28.86.131
[2026-03-26 17:29:23] INFO Running fingerprint checks...
[2026-03-26 17:29:23] INFO   Clock drift: PASS
[2026-03-26 17:29:23] INFO   Thermal drift: PASS
[2026-03-26 17:29:23] INFO   Anti-emulation: FAIL
[2026-03-26 17:29:23] INFO   Overall: FAILED
[2026-03-26 17:29:23] WARNING Attestation rejected (HTTP 401): {"code":"INVALID_NONCE","error":"invalid_or_expired_nonce"}
[2026-03-26 17:29:23] WARNING Will retry in 600s
```

### Issues Found

1. **❌ Anti-emulation check FAILS on non-ARM/x86_64**  
   The `anti-emulation` fingerprint check fails on x86_64, which causes the overall attestation to fail. This is expected behavior on VMs/non-Pi hardware.

2. **❌ Config path hardcoded**  
   Config defaults to `/opt/rustchain-arcade/config.json` — no way to specify a custom path without environment variable `SOPHIA_CONFIG`.

3. **❌ No `--help` or CLI arguments**  
   The miner has no command-line interface (`--help`, `--config`, `--test` flags don't exist).

4. **❌ install.sh blocks x86_64 entirely**  
   Even though the Python code could run on x86_64 with appropriate warnings, the installer hard-rejects.

---

## Files Analyzed

| File | Size | Purpose |
|------|------|---------|
| `rustchain_miner.py` | 16,930 bytes | Main miner |
| `achievement_bridge.py` | 34,786 bytes | RetroAchievements integration |
| `proof_of_play.py` | 20,722 bytes | Session tracking |
| `hud_overlay.py` | 19,878 bytes | Achievement HUD |
| `install.sh` | 17,930 bytes | Raspberry Pi installer |
| `config.json` | 2,312 bytes | Configuration |
| `GAME_SYSTEMS.md` | 6,852 bytes | Supported systems list |

---

## Conclusion

**Confirmed:** The sophia-edge-node software installs and runs (partially) on non-ARM platforms when bypassing the install script.

**Bugs/Issues:**
1. `install.sh` hard-blocks x86_64 — should warn instead of exit
2. `anti-emulation` check fails on non-Pi hardware (expected but unclear)
3. No CLI argument support for testing/config
4. Config path not configurable via CLI

**Recommendation:** To fully test on a Raspberry Pi, a real ARM device is needed. The software appears functionally complete but the installation UX for non-standard environments needs improvement.

---

*Test conducted as part of Bounty #2321 — sophia-edge-node Install & Review*
