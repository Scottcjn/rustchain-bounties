# Reproducible Run Guide

This guide ensures reviewers can run bounty tooling without unpinned install commands.

## Quick Start (Reproducible)

### Option 1: Docker Container (Recommended)

```bash
# Build the pinned container
docker build -t rustchain-bounty .

# Run tests inside container
docker run --rm -it rustchain-bounty pytest -v

# Run specific script
docker run --rm -it rustchain-bounty python -m beacon_dashboard.dashboard
```

### Option 2: Local with Pinned Dependencies

```bash
# Install pinned dependencies
pip install -r requirements.txt

# Run tests
pytest -v

# Run specific tool
python -m beacon_dashboard.dashboard
```

## Verifying Checksums

Before running any downloaded artifacts, verify integrity:

```bash
# Generate checksums
python3 scripts/generate_checksums.py --generate

# Verify existing checksums
python3 scripts/generate_checksums.py --verify
```

Expected output:
```
OK: beacon_dashboard/dashboard.py
OK: scripts/generate_checksums.py
...
✓ All checksums verified!
```

## For Reviewers

### Running Tests

```bash
# Using Docker (fully reproducible)
docker build -t rustchain-bounty .
docker run --rm -it rustchain-bounty pytest -v

# Using local (ensure pinned deps)
pip install -r requirements.txt
pytest -v
```

### Verifying Artifacts

```bash
# Verify checksums before running
python3 scripts/generate_checksums.py --verify
```

## Why This Matters

### Supply Chain Risk Reduction

Using pinned dependencies and containers prevents:

1. **Dependency Confusion Attacks** - Malicious packages with same name on PyPI
2. **Typosquatting** - Packages with similar names to popular libs
3. **Malicious Maintainers** - Compromised package maintainer accounts
4. **Dependency Version Drift** - Latest version changed after your testing

### Example Attack Vector

Without pinned versions:
```bash
pip install requests  # Could install malicious version
```

With pinned versions:
```bash
pip install requests==2.31.0  # Always this exact version
```

## Threat Note

**This approach reduces supply-chain risk by:**

1. **Immutable Artifacts** - Checksums verify files haven't been tampered with
2. **Pinned Dependencies** - Exact versions prevent automatic updates to compromised packages
3. **Reproducible Builds** - Same input = same output, verifiable by anyone
4. **No Unpinned Install Paths** - Reviewers never need to run `pip install package` (without version)

## References

- [Python Dependency Security Guide](https://docs.python-guide.org/writing/structure/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [SLSA Supply Chain Security](https://slsa.dev/)
