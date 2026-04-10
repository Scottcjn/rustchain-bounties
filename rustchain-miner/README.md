# RustChain Docker Miner

Start mining RTC with a single command.

## Quick Start

```bash
# Pull and run
docker run -d \
  --name rtc-miner \
  -e WALLET=your-wallet-name \
  -p 8080:8080 \
  ghcr.io/scottcjn/rustchain-miner

# Check logs
docker logs -f rtc-miner

# Check health
curl http://localhost:8080/health
```

## Docker Compose

```bash
# Clone and start
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties/rustchain-miner

# Edit .env with your wallet
echo "WALLET=my-wallet" > .env

docker compose up -d
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WALLET` | (required) | Your RTC wallet name |
| `NODE_URL` | `https://50.28.86.131` | RustChain node URL |
| `MINER_THREADS` | `1` | Number of mining threads |
| `LOG_LEVEL` | `INFO` | Logging level |

## Multi-Architecture (amd64 + arm64)

```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t rustchain-miner .
```

Works on **Raspberry Pi** (arm64) and regular servers (amd64).

## Health Check

The miner exposes a health endpoint at `http://localhost:8080/health`:

```json
{"status": "ok", "wallet": "my-wallet", "mining": true, "uptime_seconds": 3600}
```

## Monitoring (Grafana)

Import `grafana-dashboard.json` into Grafana for mining metrics:
- Hashrate over time
- Shares submitted
- Balance changes
- Uptime

## License

MIT
