# Reproducible Client Pack

This directory contains a reproducible Docker-based environment for bounty tooling and client workflows.

## What's Included

- `Dockerfile` - Pinned container recipe for bounty tooling
- `checksum.sh` - SHA256 checksum generation for artifacts
- `verify.sh` - Artifact verification script
- `README.md` - Reproducible run guide

## Quick Start

### Build the Container

```bash
cd /path/to/rustchain-bounties
docker build -t rustchain-bounty-tools -f reproducible/Dockerfile .
```

### Generate Checksums

```bash
./reproducible/checksum.sh
```

This generates `checksums.sha256` with SHA256 hashes of all release artifacts.

### Verify Artifacts

```bash
# Verify all artifacts
./reproducible/verify.sh

# Verify specific file
./reproducible/verify.sh path/to/file
```

## Reproducible Run for Reviewers

```bash
# 1. Clone the repo
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties

# 2. Build pinned container
docker build -t rustchain-bounty-tools -f reproducible/Dockerfile .

# 3. Run tests in container
docker run --rm rustchain-bounty-tools pytest tests/ -v

# 4. Verify checksums
docker run --rm -v $(pwd)/reproducible:/app rustchain-bounty-tools sh -c "cd /app && ./verify.sh"
```

## Why This Reduces Supply-Chain Risk

1. **Pinned Dependencies** - Base image and pip packages are version-locked
2. **Checksums** - SHA256 hashes detect tampering
3. **Deterministic Build** - Same Dockerfile produces identical output
4. **No Unpinned Commands** - Eliminates `curl | bash` patterns

## Files

```
reproducible/
├── Dockerfile      # Pinned container recipe
├── checksum.sh     # Generate SHA256 checksums
├── verify.sh       # Verify artifact checksums
└── README.md       # This file
```
