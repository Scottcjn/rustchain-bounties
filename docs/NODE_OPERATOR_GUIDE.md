# RustChain Node Operator Guide

Complete guide for running RustChain attestation nodes.

## Overview

RustChain nodes are essential for network consensus and attestation. This guide covers setting up, configuring, and managing node operations.

## Prerequisites

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 2 GB | 4 GB |
| Storage | 10 GB SSD | 50 GB SSD |
| Network | 10 Mbps | 100 Mbps |
| Uptime | 99% | 99.9% |

### Required Software

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y build-essential git python3 python3-pip curl

# CentOS/RHEL
sudo yum install -y gcc git python3 curl

# macOS
brew install git python3 curl
```

---

## Installation

### Option 1: From Binary

```bash
# Download latest binary
curl -sL https://50.28.86.131/node/latest -o rustchain-node
chmod +x rustchain-node
sudo mv rustchain-node /usr/local/bin/

# Verify installation
rustchain-node --version
```

### Option 2: From Source

```bash
# Clone the repository
git clone https://github.com/Scottcjn/rustchain-node.git
cd rustchain-node

# Build from source
cargo build --release

# Install
sudo cp target/release/rustchain-node /usr/local/bin/
```

### Option 3: Docker

```bash
# Pull image
docker pull scottcjn/rustchain-node:latest

# Run container
docker run -d \
  --name rustchain-node \
  -p 8080:8080 \
  -v /data/rustchain:/data \
  scottcjn/rustchain-node:latest \
  --data-dir /data \
  --rpc-port 8080
```

---

## Configuration

### Create Configuration File

```bash
mkdir -p ~/.rustchain
cat > ~/.rustchain/config.toml << 'EOF'
# RustChain Node Configuration

# Network
node_name = "my-node"
network = "mainnet"

# RPC Settings
[rpc]
enabled = true
host = "0.0.0.0"
port = 8080
max_connections = 100

# P2P Settings
[p2p]
listen_address = "/ip4/0.0.0.0/tcp/0"
bootstrap_nodes = [
    "/dns4/node1.rustchain.io/tcp/4001/p2p/QmNode1...",
    "/dns4/node2.rustchain.io/tcp/4001/p2p/QmNode2..."
]

# Attestation Settings
[attestation]
enabled = true
interval = 60  # seconds
batch_size = 100

# Storage
[storage]
data_dir = "~/.rustchain/data"
max_size_gb = 50

# Logging
[logging]
level = "info"
output = "stdout"
EOF
```

### Environment Variables

```bash
export RUSTCHAIN_NODE_NAME="my-node"
export RUSTCHAIN_RPC_PORT=8080
export RUSTCHAIN_DATA_DIR="/data/rustchain"
export RUSTCHAIN_LOG_LEVEL="info"
```

---

## Running the Node

### Manual Start

```bash
# Start node
rustchain-node --config ~/.rustchain/config.toml

# With custom options
rustchain-node \
  --node-name "my-node" \
  --rpc-port 8080 \
  --data-dir ~/.rustchain/data \
  --log-level info
```

### Background Service

#### Systemd (Linux)

```bash
sudo nano /etc/systemd/system/rustchain-node.service
```

```ini
[Unit]
Description=RustChain Node
After=network.target

[Service]
Type=simple
User=rustchain
Group=rustchain
ExecStart=/usr/local/bin/rustchain-node --config /etc/rustchain/config.toml
WorkingDirectory=/var/lib/rustchain
Restart=always
RestartSec=10
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

```bash
# Setup and start
sudo useradd -r rustchain
sudo mkdir -p /var/lib/rustchain /etc/rustchain
sudo cp ~/.rustchain/config.toml /etc/rustchain/
sudo chown -R rustchain:rustchain /var/lib/rustchain /etc/rustchain

sudo systemctl daemon-reload
sudo systemctl enable rustchain-node
sudo systemctl start rustchain-node

# Check status
sudo systemctl status rustchain-node

# View logs
journalctl -u rustchain-node -f
```

#### LaunchDaemon (macOS)

```xml
~/Library/LaunchAgents/com.rustchain.node.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rustchain.node</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/rustchain-node</string>
        <string>--config</string>
        <string>/Users/username/.rustchain/config.toml</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</string>
    <string>/Users/username/rustchain-node.log</string>
    <key>StandardErrorPath</string>
    <string>/Users/username/rustchain-node.error.log</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.rustchain.node.plist
launchctl start com.rustchain.node
```

---

## Docker Deployment

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  rustchain-node:
    image: scottcjn/rustchain-node:latest
    container_name: rustchain-node
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - ./data:/data
      - ./config.toml:/config.toml:ro
    environment:
      - RUSTCHAIN_LOG_LEVEL=info
    command: ["--config", "/config.toml"]

volumes:
  data:
```

```bash
# Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rustchain-node
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rustchain-node
  template:
    metadata:
      labels:
        app: rustchain-node
    spec:
      containers:
      - name: rustchain-node
        image: scottcjn/rustchain-node:latest
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: data
          mountPath: /data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: rustchain-pvc
```

---

## Monitoring

### Health Checks

```bash
# Check node health
curl -s http://localhost:8080/health | jq .

# Expected response
{
  "ok": true,
  "version": "2.2.1-rip200",
  "uptime_s": 86400,
  "peers": 15,
  "height": 123456
}
```

### Prometheus Metrics

```yaml
# Enable metrics endpoint
[metrics]
enabled = true
port = 9090
path = "/metrics"
```

```bash
# Scrape config for Prometheus
scrape_configs:
  - job_name: 'rustchain-node'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: /metrics
```

### Grafana Dashboard

Import the RustChain dashboard from:
- Dashboard ID: `rustchain-node-1234`
- Source: https://grafana.com/dashboards

### Alert Rules

```yaml
groups:
- name: rustchain-node
  rules:
  - alert: NodeDown
    expr: rustchain_uptime == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "RustChain node is down"
      
  - alert: HighMemory
    expr: rustchain_memory_usage_percent > 90
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on node"
```

---

## Performance Optimization

### Tuning Parameters

```toml
[performance]
# Connection pool
max_connections = 200

# Batch processing
attestation_batch_size = 500

# Cache settings
cache_size_mb = 256
cache_ttl_seconds = 300

# Network
max_peers = 50
dial_timeout_seconds = 30
```

### Hardware Optimization

```bash
# Check CPU
lscpu | grep -E "CPU\(s\)|Model name"

# Check memory
free -h

# Check disk
df -h

# Network speed
speedtest-cli
```

### Recommended Settings

| Component | Setting | Value |
|-----------|---------|-------|
| File descriptors | `ulimit -n` | 65535 |
| TCP settings | `net.ipv4.tcp_fin_timeout` | 15 |
| Swappiness | `vm.swappiness` | 10 |
| Disk I/O | elevator | noop |

---

## Backup & Recovery

### Backup Script

```bash
#!/bin/bash
# backup-node.sh

BACKUP_DIR="/backup/rustchain"
DATE=$(date +%Y%m%d_%H%M%S)

# Stop node
systemctl stop rustchain-node

# Create backup
tar -czf "${BACKUP_DIR}/rustchain_${DATE}.tar.gz" \
  -C /var/lib/rustchain .

# Restart node
systemctl start rustchain-node

# Upload to cloud
aws s3 cp "${BACKUP_DIR}/rustchain_${DATE}.tar.gz" \
  s3://my-backup-bucket/rustchain/

# Cleanup old backups (keep last 7)
find "${BACKUP_DIR}" -name "rustchain_*.tar.gz" -mtime +7 -delete
```

### Restore from Backup

```bash
# Stop node
systemctl stop rustchain-node

# Remove old data
rm -rf /var/lib/rustchain/*

# Extract backup
tar -xzf /backup/rustchain/rustchain_20240212_120000.tar.gz -C /var/lib/rustchain/

# Fix permissions
chown -R rustchain:rustchain /var/lib/rustchain

# Start node
systemctl start rustchain-node
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | Port not open | Check firewall: `sudo ufw allow 8080` |
| Peer count 0 | Bootstrap nodes unreachable | Check network connectivity |
| High memory | Memory leak or insufficient RAM | Restart node, add swap |
| Sync stuck | Database corruption | Re-sync from genesis |

### Diagnostic Commands

```bash
# Check logs
journalctl -u rustchain-node -n 100

# Check connections
netstat -tulpn | grep 8080

# Check disk space
df -h /var/lib/rustchain

# Check memory
free -h

# Test network
curl -sI https://50.28.86.131/health
```

### Debug Mode

```bash
# Enable debug logging
rustchain-node --log-level debug

# Verbose output
rustchain-node -v

# Trace mode (very verbose)
rustchain-node -vvv
```

---

## Security

### Firewall Setup

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow 8080/tcp
sudo ufw enable

# Check status
sudo ufw status
```

### SSL/TLS Setup

```toml
[tls]
enabled = true
cert_path = "/etc/ssl/certs/rustchain.crt"
key_path = "/etc/ssl/private/rustchain.key"
```

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 \
  -keyout /etc/ssl/private/rustchain.key \
  -out /etc/ssl/certs/rustchain.crt \
  -days 365 \
  -nodes \
  -subj "/CN=localhost"
```

### Rate Limiting

```toml
[rate_limit]
enabled = true
requests_per_second = 100
burst_size = 200
```

---

## Upgrades

### Minor Updates

```bash
# Pull latest image
docker pull scottcjn/rustchain-node:latest

# Restart container
docker-compose restart

# Or for binary
curl -sL https://50.28.86.131/node/latest -o /usr/local/bin/rustchain-node
systemctl restart rustchain-node
```

### Major Upgrades

```bash
# Backup first (see Backup section)
./backup-node.sh

# Stop node
systemctl stop rustchain-node

# Update binary
cargo build --release

# Migrate database if needed
rustchain-node --migrate

# Start node
systemctl start rustchain-node

# Verify
curl -s http://localhost:8080/health | jq '.version'
```

---

## API Reference

See [API_REFERENCE.md](./API_REFERENCE.md) for complete node API documentation.

---

## Support

- **Issues:** https://github.com/Scottcjn/rustchain-node/issues
- **Discord:** https://discord.gg/rustchain
- **Docs:** https://docs.rustchain.io/node-operators

---

*Last updated: 2026-02-12*
*Node Version: 2.2.1-rip200*
