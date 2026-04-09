# RustChain Dockerized Miner 🐳

> One command to start earning RTC (RustChain native token)

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

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WALLET_NAME` | ✅ Yes | - | Your RustChain wallet name |
| `NODE_URL` | No | `https://50.28.86.131` | RustChain node endpoint |

## Directory Structure

```
.
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Docker Compose setup
├── docker-miner-entrypoint.sh   # Entrypoint script
├── requirements.txt             # Python dependencies
└── miners/
    └── linux/
        ├── rustchain_linux_miner.py
        ├── fingerprint_checks.py
        └── color_logs.py
```

## Building from Source

```bash
# Build the image locally
docker build -t rustchain-miner:latest .

# Run
docker run -e WALLET_NAME=your_wallet rustchain-miner:latest
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
