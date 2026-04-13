# Submission: install.sh Security Fix (Bounty #2033)

## Bounty Details
- **Bounty**: #2033 - install.sh downloads and executes remote code without verification
- **Severity**: Medium (10 RTC)
- **Reward**: 10 RTC

## What Was Done

### Problem
The `install.sh` script in `Scottcjn/Rustchain` had three security issues:
1. **Wrong URLs**: Used `rustchain_universal_miner.py` which doesn't exist
2. **No hash verification**: Downloaded scripts were executed without verifying integrity
3. **Insecure downloads**: Used `--insecure` flag to skip SSL verification

### Solution
Applied comprehensive security fixes to `install.sh`:

#### 1. Fixed Platform-Specific URLs
Changed from non-existent `rustchain_universal_miner.py` to actual platform-specific files:
- **Linux**: `miners/linux/rustchain_linux_miner.py`
- **macOS**: `miners/macos/rustchain_mac_miner_v2.5.py`

#### 2. Added SHA256 Verification
- Downloads `checksums.sha256` from the repository
- Verifies each downloaded miner file against its expected hash
- **ABORTS** if hash mismatch is detected (prevents tampered downloads)
- Falls back to warning if checksums unavailable

#### 3. Removed --insecure Flag
All downloads now use proper SSL/TLS verification.

#### 4. Updated checksums.sha256
The existing checksums file was stale (files had been updated without regenerating checksums). Updated with current file hashes.

### Files Changed
- `install.sh` - Security fixes (114 lines added, 13 removed)
- `miners/checksums.sha256` - Updated hashes

### Testing
```bash
$ bash install.sh --dry-run
[DRY RUN] Would install to: /home/user/.rustchain
  Miner: https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/rustchain_linux_miner.py
  Fingerprint: https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/fingerprint_checks.py
  Wallet: test-wallet
  Node: https://50.28.86.131
  Silent: 0
```

## Note
The fix was developed against the Rustchain main repository. A PR cannot be submitted directly due to fork restrictions. This submission documents the complete fix for maintainer review and application.

## PR for Main Repo
The actual code changes for `Scottcjn/Rustchain` need to be applied by a maintainer or someone with fork access. Branch: `fix/install-sh-security-hash-verification`

## Wallet
RTC3fcd93a4ec68cfd6b59d1b41c4872c5c239c4ad8
