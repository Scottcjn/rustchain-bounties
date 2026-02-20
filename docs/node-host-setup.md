# RustChain Node Setup Guide - Issue #359

## Node Host Recruitment

This guide covers setting up RustChain nodes for both **Vintage** (PowerPC) and **Modern** (x86_64/ARM) hardware.

## Quick Start

### Modern Node (x86_64/ARM)

```bash
# Clone and run
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
docker build -t rustchain-node .
docker run -d -p 8080:8080 -p 30303:30303 rustchain-node

# Verify
curl -s http://localhost:8080/health
```

### Vintage Node (PowerPC)

```bash
# PowerPC G4/G5 - use qemu emulation or native
docker build -t rustchain-node:vintage -f Dockerfile.ppc64le .
docker run -d -p 8080:8080 -p 30303:30303 rustchain-node:vintage
```

## Node Identity

After setup, get your node identity:

```bash
curl -s http://localhost:8080/api/identity
```

Output:
```json
{
  "node_id": "node_abc123",
  "hardware_class": "x86_64",
  "region": "us-east",
  "bandwidth": "100Mbps"
}
```

## Health Checks

```bash
# Health endpoint
curl -s http://localhost:8080/health

# Epoch info
curl -s http://localhost:8080/epoch

# Active miners
curl -s http://localhost:8080/api/miners
```

## Cross-Node Reconciliation

Run drift check:

```bash
curl -s http://localhost:8080/api/compare
```

## Hardware Classes

| Class | Hardware | Multiplier |
|-------|----------|------------|
| Vintage | PowerPC G4 | 2.5x |
| Vintage | PowerPC G5 | 2.0x |
| Vintage | 68K | 2.0x |
| Modern | x86_64 | 1.0x |
| Modern | ARM64 | 1.0x |

## Payout

- Vintage node: **120 RTC**
- Modern node: **80 RTC**
- Reliability bonus: **+40 RTC** after 14-day uptime

## Reproducibility

All configs pinned in Dockerfile with SHA256 hashes.
