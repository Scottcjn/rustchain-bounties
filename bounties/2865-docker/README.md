# SPDX-License-Identifier: MIT

# RustChain Miner - Docker Container

One-command deployment for RustChain mining. Start earning RTC immediately with Docker.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- A RTC wallet address (optional - auto-generated if not provided)

### Run Miner

**Option 1: Using docker-compose (Recommended)**

```bash
# Clone this repository
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties/bounties/2865-docker

# Start the miner with your wallet
export WALLET="your-rtc-wallet-address"
docker-compose up -d

# View logs
docker-compose logs -f rustchain-miner

# Stop the miner
docker-compose down
```

**Option 2: Using Docker directly**

```bash
# Build the image
docker build -t rustchain-miner .

# Run the container
docker run -d \
  --name rustchain-miner \
  -e WALLET="your-rtc-wallet-address" \
  -e NODE_URL="https://50.28.86.131" \
  rustchain-miner

# View logs
docker logs -f rustchain-miner

# Stop the container
docker stop rustchain-miner
```

## Features

✅ **Lightweight** - python:3.11-slim base (~150MB)
✅ **Auto-detection** - Detects your hardware architecture automatically
✅ **Configurable** - Environment variables for wallet and node URL
✅ **Health Check** - Built-in health monitoring
✅ **Multi-platform** - Works on amd64, arm64, and other architectures
✅ **Low Resource** - Optimized for Raspberry Pi and vintage hardware
✅ **Zero Setup** - One command to start mining

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WALLET` | (auto-generated) | Your RTC wallet address to receive mining rewards |
| `NODE_URL` | `https://50.28.86.131` | RustChain node endpoint |

### Example with Custom Node

```bash
docker-compose -e NODE_URL="https://your-node.example.com" up
```

## Hardware Support

The miner auto-detects and optimizes for:
- **x86_64**: Modern Intel/AMD processors
- **ARM64**: Apple Silicon (M1/M2/M3), Raspberry Pi 4/5
- **PowerPC**: G3/G4/G5 architecture (vintage bonus multiplier)
- **ARM32**: 32-bit ARM boards

## Proof of Antiquity (PoA) Bonus

RustChain rewards mining on vintage and retro hardware with higher weights:
- **PowerPC G3**: 3.0x weight
- **PowerPC G4**: 2.5x weight
- **PowerPC G5**: 2.0x weight
- **Apple Silicon M1/M2**: 1.2x weight
- **Intel Core 2**: 1.5x weight
- **Modern x86**: 0.8x weight (penalty)

## Monitoring

### Health Check
```bash
# Check miner health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Example output:
# NAME              STATUS
# rustchain-miner   Up 2 minutes (healthy)
```

### View Mining Status
```bash
docker logs rustchain-miner | tail -20
```

### Full Logs
```bash
docker logs rustchain-miner
```

## Troubleshooting

### Connection Issues
- Verify the node is reachable: `curl -k https://50.28.86.131/health`
- Check your firewall settings
- Ensure the container has network access

### Miner Not Starting
```bash
# Check logs for errors
docker logs rustchain-miner

# Rebuild the image (clear cache)
docker-compose build --no-cache
```

### SSL Certificate Warnings
These are expected - RustChain uses self-signed certificates. The miner handles this automatically.

## Development

### Build Locally
```bash
docker build -t rustchain-miner:local .
docker run -it rustchain-miner:local python /app/miners/rustchain_universal_miner.py --help
```

### Custom Miner Script
To use a different miner version, modify the `Dockerfile`:
```dockerfile
RUN curl -s -o /app/miners/rustchain_universal_miner.py \
    "https://raw.githubusercontent.com/YOUR_FORK/Rustchain/main/miners/YOUR_MINER.py"
```

## Performance Notes

- Mining works on all CPU architectures
- Vintage hardware (PowerPC, Core 2 Duo) receives higher weights
- RustChain uses Proof of Antiquity - older hardware is more profitable
- No GPU required

## License

SPDX-License-Identifier: MIT

## Support

For issues with the Docker container, see: https://github.com/Scottcjn/rustchain-bounties

For RustChain questions, see: https://github.com/Scottcjn/Rustchain
