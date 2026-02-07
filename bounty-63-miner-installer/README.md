# Bounty #63: Universal Miner Installer Script

## Description
This submission implements a robust, one-line universal installer script for the RustChain miner. 

### Features
- **One-line installation**: `curl -sSL .../install-miner.sh | bash`
- **--dry-run mode**: Preview changes before applying them.
- **Checksum verification**: SHA256 validation for all downloaded scripts.
- **Multi-platform support**: 
  - Ubuntu 20.04/22.04/24.04
  - Debian 11/12
  - macOS (Intel + Apple Silicon)
  - Raspberry Pi (ARM64)
  - IBM POWER8
- **First Attestation Test**: Runs a health check and attestation challenge after install.
- **Auto-start**: Configures `systemd` user units on Linux and `launchd` agents on macOS.
- **Isolated environment**: Uses Python virtualenv to avoid system package pollution.

## Submission Details
- **Implementation File**: [install-miner.sh](./install-miner.sh)
- **Checksums**: [miners/checksums.sha256](./miners/checksums.sha256)
- **Validation**: See [SUBMISSION_WALKTHROUGH.md](./SUBMISSION_WALKTHROUGH.md) for test results on macOS and Linux (Docker).

## Pull Request Link (Main Repo)
[Link to your PR on Scottcjn/Rustchain will go here]

## RTC Wallet ID
[Your RTC Wallet ID will go here]
