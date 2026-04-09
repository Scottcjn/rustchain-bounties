# RustChain Dockerized Miner 🐳

> One command to start earning RTC (RustChain native token)

## Features

- ✅ **Multi-arch support**: amd64 + arm64 (Raspberry Pi compatible)
- ✅ **Health check**: Built-in Docker health check
- ✅ **Grafana dashboard**: Monitoring template included
- ✅ **One-command deployment**: `docker-compose up -d`
- ✅ **Wallet validation**: Entry point validates WALLET_NAME

## Quick Start

```bash
# 1. Set your wallet
export WALLET_NAME=your_rustchain_wallet_name

# 2. Run with Docker
docker run -d \
  --name rustchain-miner \
  -e WALLET_NAME="$WALLET_NAME" \
  -e NODE_URL="https://50.28.86.131" \
  --restart unless-stopped \
  ghcr.io/scottcjn/rustchain-miner:latest
```

Or with Docker Compose:

```bash
# Edit docker-compose.yml with your WALLET_NAME
export WALLET_NAME=your_wallet_name
docker-compose up -d
```

## Multi-Arch Build (Raspberry Pi)

Build for multiple architectures:

```bash
# Build multi-arch image
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/scottcjn/rustchain-miner:latest \
  --push .
```

Or run locally:

```bash
# Build for current platform
docker build -t rustchain-miner:latest .

# Run on Raspberry Pi
docker run -e WALLET_NAME=your_wallet rustchain-miner:latest
```

## Grafana Dashboard

Import `grafana/rustchain-dashboard.json` into Grafana for monitoring:

1. Open Grafana → Dashboards → Import
2. Upload the JSON file
3. Select Prometheus datasource
4. Dashboard includes:
   - Wallet Balance
   - Miner Status
   - Mining Rate (epochs/min)

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WALLET_NAME` | ✅ Yes | - | Your RustChain wallet name |
| `NODE_URL` | No | `https://50.28.86.131` | RustChain node endpoint |

## Bonus Features (5 extra RTC)

- ✅ Multi-arch build (amd64 + arm64)
- ✅ Runs on Raspberry Pi
- ✅ Includes Grafana dashboard template

## Directory Structure

```
.
├── Dockerfile                    # Multi-arch container definition
├── docker-compose.yml           # Docker Compose setup
├── docker-miner-entrypoint.sh   # Entrypoint script
├── requirements.txt             # Python dependencies
├── grafana/
│   └── rustchain-dashboard.json # Grafana monitoring template
└── miners/
    └── linux/
        ├── rustchain_linux_miner.py
        ├── fingerprint_checks.py
        └── color_logs.py
```

## Building from Source

```bash
# Clone repo
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties/dockerized-miner

# Build for current platform
docker build -t rustchain-miner:latest .

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/scottcjn/rustchain-miner:latest \
  --push .
```

## Monitoring

```bash
# View logs
docker logs -f rustchain-miner

# Check health
docker inspect --format='{{.State.Health.Status}}' rustchain-miner

# Check balance
curl -s "https://50.28.86.131/wallet/balance?wallet=your_wallet_name"
```

## Important Notes

⚠️ **Docker miners earn reduced rewards** due to RustChain's anti-VM detection. For maximum rewards, run the miner directly on physical hardware.

🔒 The container runs as non-root user (`rustchain`, UID 1000) for security.

## License

Same as RustChain project.
