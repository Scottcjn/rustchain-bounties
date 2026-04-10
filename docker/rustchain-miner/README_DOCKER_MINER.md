# RustChain Miner — Docker Deployment

> ⚡ One command to start earning RTC with RustChain's Proof-of-Antiquity mining.

## TL;DR

```bash
# 1. Clone this repo
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain

# 2. Configure your wallet
echo "WALLET_NAME=your_rtc_wallet_id" > .env.miner

# 3. Start mining!
docker-compose -f docker-compose.miner.yml up -d
```

That's it. Your miner will:
- Auto-detect your hardware architecture
- Report honestly to the network for accurate antiquity scoring
- Start earning RTC rewards each epoch

## Quick Start

### Prerequisites

- Docker 20.10+ or Docker Desktop
- docker-compose v2 (or use `docker compose` plugin)
- A RustChain wallet (create one at https://50.28.86.131)

### Setup

**Step 1: Clone the repository**

```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
```

**Step 2: Create `.env.miner`**

```bash
# Required
WALLET_NAME=your_rtc_wallet_id_here

# Optional (defaults shown)
NODE_URL=https://50.28.86.131
BLOCK_TIME=600
LOG_LEVEL=INFO
```

**Step 3: Start the miner**

```bash
docker-compose -f docker-compose.miner.yml up -d
```

**Step 4: Watch the logs**

```bash
docker logs -f rustchain-miner
```

## Architecture Support

| Architecture | Multiplier Range | Example Hardware |
|---|---|---|
| `x86_64` | 0.8-2.5x | Intel/AMD desktop & server |
| `aarch64` (ARM64) | 0.0005x* | SBCs, phones |
| `armv7l` | 0.0005x* | Raspberry Pi (32-bit) |
| `ppc64le` | 1.5-2.5x | IBM POWER8/9 |
| `mips` | 2.3-3.0x | SGI, Loongson |

*Modern ARM (phones/SBCs) gets a low multiplier. Vintage ARM hardware gets much higher.

> Note: The Docker image runs the Linux miner. For Apple Silicon, macOS-native binaries are recommended for best hardware fingerprinting accuracy.

## Docker Hub / GHCR

```bash
# Pull pre-built image
docker pull ghcr.io/scottcjn/rustchain-miner:latest

# Run with environment
docker run -d \
  --name rustchain-miner \
  -e WALLET_NAME=your_wallet \
  -e NODE_URL=https://50.28.86.131 \
  ghcr.io/scottcjn/rustchain-miner:latest
```

## Monitoring

### Prometheus Metrics

The docker-compose includes a Prometheus metrics endpoint:

```bash
# Prometheus is exposed on port 9090
open http://localhost:9090
```

### Health Check

```bash
docker inspect --format='{{.State.Health.Status}}' rustchain-miner
# Expected: healthy
```

### View Logs

```bash
# All logs
docker logs rustchain-miner

# Follow in real-time
docker logs -f rustchain-miner

# Filter by level
docker logs rustchain-miner 2>&1 | grep -i "error\|warn\|info"
```

## Troubleshooting

**"WALLET_NAME is required" error**

Make sure your `.env.miner` file contains:
```
WALLET_NAME=your_wallet_id
```

**Container exits immediately**

Check logs:
```bash
docker logs rustchain-miner
```

**Hardware fingerprinting not working**

The miner requires access to `/proc` for hardware fingerprinting. If running in a restricted environment:
```bash
docker run --privileged \
  -e WALLET_NAME=your_wallet \
  ghcr.io/scottcjn/rustchain-miner:latest
```

## Building from Source

```bash
# Build for current platform
docker build -f Dockerfile.miner -t rustchain-miner:local .

# Build for multiple architectures
docker buildx create --use
docker buildx build -f Dockerfile.miner \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t ghcr.io/scottcjn/rustchain-miner:latest \
  --push .
```

## Files Included

```
.
├── Dockerfile.miner           # Multi-stage build (python:3.11-slim)
├── docker-compose.miner.yml  # docker-compose with Prometheus
├── docker-miner-entrypoint.sh # Auto-detects miner script + env validation
└── README_DOCKER_MINER.md    # This file
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `WALLET_NAME` | ✅ Yes | — | Your RTC wallet name/ID |
| `NODE_URL` | No | `https://50.28.86.131` | RustChain node URL |
| `BLOCK_TIME` | No | `600` | Block time in seconds |
| `LOG_LEVEL` | No | `INFO` | Logging level: DEBUG, INFO, WARN, ERROR |

## License

MIT — See RustChain repository for full license details.

---

For full miner documentation, see [RustChain Miners README](miners/README.md).
