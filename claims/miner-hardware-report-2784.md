# Hardware report for bounty #2784 — miner dry-run / fingerprint test

Issue: https://github.com/Scottcjn/rustchain-bounties/issues/2784

## Environment

| Field | Value |
|-------|-------|
| OS | Linux (Ubuntu 24.04.4 LTS, noble) |
| Kernel | 6.8.0-134-generic |
| Architecture | x86_64 |
| CPU | Intel Xeon E-2334 @ 3.40GHz (2 cores / 4 threads) |
| Hypervisor | Microsoft (full virtualization; DMI vendor Microsoft Corporation) |
| RAM | 7.8 GiB |
| Python | 3.12.3 |
| Miner package | clawrtc 1.9.0 (PyPI) |
| Network status | online (v2.2.1-rip200) |

## What was run

1. `clawrtc install --dry-run` — safe preview, no files written
2. `clawrtc install --wallet hardware-report-2784 --no-service -y` — extract bundled scripts only (no systemd service, no mining loop)
3. `python fingerprint_checks.py` from `~/.clawrtc` — full RIP-PoA fingerprint suite (local only)

No mining loop was started. No attestations were submitted for earning.

## Dry-run install output (excerpt)

```text
[clawrtc] Platform: Linux | Arch: x86_64
...
[clawrtc] DRY RUN — no files extracted, no services created.
```

Install correctly detected platform/arch and listed the six fingerprint data categories that would be collected on a real start.

## Fingerprint check results

| # | Check | Result |
|---|-------|--------|
| 1 | Clock-Skew & Oscillator Drift | PASS |
| 2 | Cache Timing Fingerprint | PASS |
| 3 | SIMD Unit Identity | PASS |
| 4 | Thermal Drift Entropy | PASS |
| 5 | Instruction Path Jitter | PASS |
| 6 | Anti-Emulation Checks | FAIL |

**Overall: FAILED** (anti-emulation only)

### Full fingerprint suite output

```text
Running 6 Hardware Fingerprint Checks...
==================================================

[1/6] Clock-Skew & Oscillator Drift...
  Result: PASS

[2/6] Cache Timing Fingerprint...
  Result: PASS

[3/6] SIMD Unit Identity...
  Result: PASS

[4/6] Thermal Drift Entropy...
  Result: PASS

[5/6] Instruction Path Jitter...
  Result: PASS

[6/6] Anti-Emulation Checks...
  Result: FAIL

==================================================
OVERALL RESULT: FAILED
Failed checks: ['anti_emulation']
```

### Anti-emulation detail (why it failed)

```json
{
  "anti_emulation": {
    "passed": false,
    "data": {
      "vm_indicators": [
        "/sys/class/dmi/id/sys_vendor:microsoft corporation",
        "/sys/class/dmi/id/board_vendor:microsoft corporation",
        "/sys/class/dmi/id/bios_vendor:microsoft corporation",
        "/sys/class/dmi/id/chassis_vendor:microsoft corporation",
        "cpuinfo:hypervisor",
        "systemd_detect_virt:microsoft"
      ],
      "indicator_count": 6,
      "is_likely_vm": true,
      "fail_reason": "vm_detected"
    }
  }
}
```

This matches the install-time VM warning (`sys_vendor` / `board_vendor` Microsoft + `cpuinfo` hypervisor flag). Timing/SIMD/cache checks still pass on this VM; only anti-emulation correctly rejects it.

### SIMD / arch detail (from check 3)

- arch: `x86_64`
- has_sse: true
- has_avx: true
- has_altivec: false
- has_neon: false

## Errors / confusing UX notes

1. **`clawrtc mine --dry-run` is not a valid flag** on clawrtc 1.9.0. The bounty text says “dry-run mode”; the working dry-run path is `clawrtc install --dry-run`. Actual fingerprinting is `python fingerprint_checks.py` after install.
2. **Bundled `miner.py --help` describes a “Windows wallet + miner”** even when installed on Linux. Harmless, but confusing for Linux users.
3. **`miner.py` has no `--dry-run` / `--test-only` flags** (those exist on the native Rust miner). On the Python clawrtc path, fingerprint-only testing is via `fingerprint_checks.py`.
4. **VM failure is valuable signal**: this host is a Microsoft-hypervisor guest. Checks 1–5 pass; check 6 fails with clear indicators. Consistent with “VMs earn ~0x” messaging.

## Bundled file hashes (clawrtc 1.9.0)

```text
miner.py:              eceba6529ab4df35761d6778c6f97032b69a70301b021ff2e217f9b73616f93e
fingerprint_checks.py: bdd982c7bbb53d5d37c0accb2bbc9e7e3b22e12fa9031c8fba11c4ee9c9f7819
```

## Summary

- Ran clawrtc 1.9.0 on **Ubuntu 24.04 / x86_64** (Microsoft Hyper-V guest, Xeon E-2334).
- Dry-run install worked; fingerprint suite ran locally.
- **5/6 checks PASS; anti-emulation FAIL** (VM detected).
- No crashes. Main confusion: bounty “dry-run” maps to `install --dry-run` + `fingerprint_checks.py`, not `mine --dry-run`.
