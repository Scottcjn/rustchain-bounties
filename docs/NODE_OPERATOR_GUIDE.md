# RustChain Node Operator Guide

Complete guide to running and maintaining a RustChain network node.

**Become a network backbone** by operating a RustChain node and earning rewards while supporting the ecosystem.

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Node Operations](#node-operations)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What is a RustChain Node?

A RustChain node is a full participant in the RIP-200 Proof-of-Attestation network that:

- **Validates transactions** and maintains the blockchain ledger
- **Serves API endpoints** for miners, wallets, and applications
- **Participates in consensus** through attestation verification
- **Stores network state** and provides data to other nodes
- **Earns rewards** for network participation and uptime

### Node Types

| Type | Description | Requirements | Rewards |
|------|-------------|--------------|---------|
| **Full Node** | Complete blockchain validation | 4GB RAM, 100GB storage | Transaction fees |
| **API Node** | Serves public API endpoints | 8GB RAM, 200GB storage | API usage fees |
| **Archive Node** | Full historical data | 16GB RAM, 1TB+ storage | Premium API fees |
| **Validator Node** | Consensus participation | 8GB RAM, 200GB storage | Block rewards |

### Network Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Miner Nodes   │    │  Validator      │    │   API Nodes     │
│                 │    │  Nodes          │    │                 │
│ • Attestations  │◄──►│ • Consensus     │◄──►│ • Public APIs   │
│ • PoA Mining    │    │ • Block Prod.   │    │ • Wallet Svc    │
│ • Hardware ID   │    │ • State Sync    │    │ • Explorer      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Archive Nodes  │
                    │                 │
                    │ • Full History  │
                    │ • Data Backup   │
                    │ • Analytics     │
                    └─────────────────┘
```

---

## System Requirements

### Minimum Requirements (Full Node)

- **CPU**: 4 cores, 2.0GHz+
- **RAM**: 4GB available
- **Storage**: 100GB SSD (NVMe preferred)
- **Network**: 100Mbps up/down, unlimited data
- **OS**: Linux (Ubuntu 20.04+ recommended)

### Recommended Requirements (API Node)

- **CPU**: 8 cores, 3.0GHz+
- **RAM**: 8GB available
- **Storage**: 200GB NVMe SSD
- **Network**: 1Gbps up/down, unlimited data
- **OS**: Ubuntu 22.04 LTS

### Enterprise Requirements (Archive Node)

- **CPU**: 16+ cores, 3.5GHz+
- **RAM**: 16GB+ available
- **Storage**: 1TB+ NVMe SSD (RAID recommended)
- **Network**: 10Gbps up/down, unlimited data
- **OS**: Ubuntu 22.04 LTS with enterprise support

### Supported Platforms

- ✅ **Ubuntu** 20.04, 22.04 LTS (recommended)
- ✅ **Debian** 11, 12
- ✅ **CentOS** 8, 9
- ✅ **RHEL** 8, 9
- ✅ **Arch Linux** (advanced users)
- ⚠️ **macOS** (development only)
- ❌ **Windows** (not supported)

---

## Installation

### Method 1: Quick Install Script (Recommended)

```bash
# Download and run the installer
curl -sSL https://install.rustchain.org | bash

# Or with custom options
curl -sSL https://install.rustchain.org | bash -s -- --node-type=api --wallet-id=my-node
```

### Method 2: Manual Installation

#### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y curl wget git build-essential pkg-config libssl-dev

# Create rustchain user
sudo useradd -m -s /bin/bash rustchain
sudo usermod -aG sudo rustchain
```

#### Step 2: Install Rust

```bash
# Switch to rustchain user
sudo su - rustchain

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install required toolchain
rustup toolchain install stable
rustup default stable
```

#### Step 3: Download and Build Node

```bash
# Clone the repository
git clone https://github.com/rustchain/node.git
cd node

# Build the node (this may take 10-30 minutes)
cargo build --release

# Install binary
sudo cp target/release/rustchain-node /usr/local/bin/
sudo chmod +x /usr/local/bin/rustchain-node
```

#### Step 4: Create Configuration

```bash
# Create config directory
sudo mkdir -p /etc/rustchain
sudo chown rustchain:rustchain /etc/rustchain

# Generate default config
rustchain-node --generate-config > /etc/rustchain/node.toml
```

### Method 3: Docker Installation

```bash
# Pull the official image
docker pull rustchain/node:latest

# Create data directory
mkdir -p ~/rustchain-data

# Run the node
docker run -d \
  --name rustchain-node \
  -p 8080:8080 \
  -p 8443:8443 \
  -v ~/rustchain-data:/data \
  -e RUSTCHAIN_WALLET_ID=my-node-wallet \
  rustchain/node:latest
```

### Method 4: Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  rustchain-node:
    image: rustchain/node:latest
    container_name: rustchain-node
    restart: unless-stopped
    ports:
      - "8080:8080"   # HTTP API
      - "8443:8443"   # HTTPS API
      - "9090:9090"   # P2P Network
    volumes:
      - ./data:/data
      - ./config:/config
    environment:
      - RUSTCHAIN_WALLET_ID=my-node-wallet
      - RUSTCHAIN_NODE_TYPE=full
      - RUSTCHAIN_LOG_LEVEL=info
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Configuration

### Basic Configuration File

```toml
# /etc/rustchain/node.toml

[node]
# Node identification
wallet_id = "my-node-operator"
node_type = "full"  # full, api, archive, validator
network = "mainnet"  # mainnet, testnet

# Network settings
bind_address = "0.0.0.0"
http_port = 8080
https_port = 8443
p2p_port = 9090

# Data storage
data_dir = "/var/lib/rustchain"
log_dir = "/var/log/rustchain"

[consensus]
# RIP-200 Proof-of-Attestation settings
enable_validation = true
attestation_interval = 300  # 5 minutes
max_attestations_per_block = 1000

[api]
# API server settings
enable_http = true
enable_https = true
ssl_cert_path = "/etc/rustchain/ssl/cert.pem"
ssl_key_path = "/etc/rustchain/ssl/key.pem"
cors_origins = ["*"]
rate_limit_per_minute = 1000

[mining]
# Mining pool settings (if applicable)
enable_pool = false
pool_fee_percent = 2.0
min_payout_threshold = 1.0

[database]
# Database configuration
engine = "rocksdb"  # rocksdb, leveldb
cache_size_mb = 1024
max_open_files = 1000

[network]
# P2P network settings
max_peers = 50
bootstrap_nodes = [
    "50.28.86.131:9090",
    "node2.rustchain.org:9090",
    "node3.rustchain.org:9090"
]

[logging]
level = "info"  # trace, debug, info, warn, error
format = "json"  # json, plain
max_file_size_mb = 100
max_files = 10
```

### Advanced Configuration

#### High-Performance API Node

```toml
[node]
wallet_id = "high-perf-api-node"
node_type = "api"
network = "mainnet"

[api]
enable_http = true
enable_https = true
worker_threads = 16
max_connections = 10000
rate_limit_per_minute = 10000
enable_metrics = true
metrics_port = 9091

[database]
engine = "rocksdb"
cache_size_mb = 4096
max_open_files = 10000
compression = "lz4"
bloom_filter_bits = 10

[performance]
# Performance tuning
async_io_threads = 8
network_buffer_size_kb = 256
batch_size = 1000
sync_mode = "fast"
```

#### Archive Node Configuration

```toml
[node]
wallet_id = "archive-node-1"
node_type = "archive"
network = "mainnet"

[storage]
# Archive-specific settings
keep_full_history = true
prune_ancient_blocks = false
snapshot_interval_blocks = 10000
backup_interval_hours = 24

[database]
engine = "rocksdb"
cache_size_mb = 8192
max_open_files = 50000
compression = "zstd"
enable_statistics = true

[backup]
# Automated backup settings
enable_s3_backup = true
s3_bucket = "rustchain-archive-backups"
s3_region = "us-east-1"
backup_retention_days = 365
```

### Environment Variables

```bash
# Core settings
export RUSTCHAIN_WALLET_ID="my-node"
export RUSTCHAIN_NODE_TYPE="full"
export RUSTCHAIN_NETWORK="mainnet"

# Paths
export RUSTCHAIN_DATA_DIR="/var/lib/rustchain"
export RUSTCHAIN_CONFIG_FILE="/etc/rustchain/node.toml"

# Performance
export RUSTCHAIN_WORKER_THREADS="8"
export RUSTCHAIN_CACHE_SIZE_MB="2048"

# Logging
export RUSTCHAIN_LOG_LEVEL="info"
export RUST_LOG="rustchain=info"
```

---

## Node Operations

### Starting the Node

#### Systemd Service (Recommended)

```bash
# Create systemd service file
sudo tee /etc/systemd/system/rustchain-node.service > /dev/null <<EOF
[Unit]
Description=RustChain Node
After=network.target
Wants=network.target

[Service]
Type=simple
User=rustchain
Group=rustchain
WorkingDirectory=/home/rustchain
ExecStart=/usr/local/bin/rustchain-node --config /etc/rustchain/node.toml
Restart=always
RestartSec=10
LimitNOFILE=65536

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/rustchain /var/log/rustchain

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable rustchain-node
sudo systemctl start rustchain-node

# Check status
sudo systemctl status rustchain-node
```

#### Manual Start

```bash
# Start in foreground (for testing)
rustchain-node --config /etc/rustchain/node.toml

# Start in background
nohup rustchain-node --config /etc/rustchain/node.toml > /var/log/rustchain/node.log 2>&1 &
```

#### Docker Start

```bash
# Start with docker run
docker run -d \
  --name rustchain-node \
  --restart unless-stopped \
  -p 8080:8080 \
  -p 8443:8443 \
  -p 9090:9090 \
  -v /var/lib/rustchain:/data \
  rustchain/node:latest

# Or with docker-compose
docker-compose up -d
```

### Node Management Commands

```bash
# Check node status
rustchain-node status

# Get node info
curl -s http://localhost:8080/health | jq

# Check sync status
curl -s http://localhost:8080/sync | jq

# View connected peers
curl -s http://localhost:8080/peers | jq

# Get blockchain info
curl -s http://localhost:8080/chain/info | jq

# Check wallet balance (node operator)
curl -s "http://localhost:8080/wallet/balance?miner_id=my-node" | jq
```

### Updating the Node

```bash
# Stop the node
sudo systemctl stop rustchain-node

# Backup data (recommended)
sudo cp -r /var/lib/rustchain /var/lib/rustchain.backup.$(date +%Y%m%d)

# Update the binary
cd ~/node
git pull origin main
cargo build --release
sudo cp target/release/rustchain-node /usr/local/bin/

# Start the node
sudo systemctl start rustchain-node

# Verify update
rustchain-node --version
```

---

## Monitoring & Maintenance

### Health Monitoring

#### Basic Health Check Script

```bash
#!/bin/bash
# health_check.sh

NODE_URL="http://localhost:8080"
WALLET_ID="my-node"

echo "=== RustChain Node Health Check ==="
echo "Timestamp: $(date)"

# Check if node is responding
if curl -sf "$NODE_URL/health" > /dev/null; then
    echo "✅ Node is responding"
    
    # Get detailed health info
    HEALTH=$(curl -s "$NODE_URL/health")
    echo "Health: $(echo $HEALTH | jq -r '.ok')"
    echo "Uptime: $(echo $HEALTH | jq -r '.uptime_s') seconds"
    echo "Version: $(echo $HEALTH | jq -r '.version')"
    
    # Check sync status
    SYNC=$(curl -s "$NODE_URL/sync")
    echo "Sync Status: $(echo $SYNC | jq -r '.status')"
    echo "Current Block: $(echo $SYNC | jq -r '.current_block')"
    
    # Check peer count
    PEERS=$(curl -s "$NODE_URL/peers" | jq length)
    echo "Connected Peers: $PEERS"
    
    # Check node balance
    BALANCE=$(curl -s "$NODE_URL/wallet/balance?miner_id=$WALLET_ID")
    echo "Node Balance: $(echo $BALANCE | jq -r '.amount_rtc') RTC"
    
else
    echo "❌ Node is not responding"
    exit 1
fi
```

#### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rustchain-node'
    static_configs:
      - targets: ['localhost:9091']
    scrape_interval: 10s
    metrics_path: /metrics
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "RustChain Node Metrics",
    "panels": [
      {
        "title": "Node Uptime",
        "type": "stat",
        "targets": [
          {
            "expr": "rustchain_node_uptime_seconds"
          }
        ]
      },
      {
        "title": "Connected Peers",
        "type": "graph",
        "targets": [
          {
            "expr": "rustchain_node_peers_connected"
          }
        ]
      },
      {
        "title": "API Requests/sec",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(rustchain_api_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Log Management

#### Log Rotation

```bash
# /etc/logrotate.d/rustchain
/var/log/rustchain/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 rustchain rustchain
    postrotate
        systemctl reload rustchain-node
    endscript
}
```

#### Log Analysis

```bash
# View recent logs
sudo journalctl -u rustchain-node -f

# Search for errors
sudo journalctl -u rustchain-node | grep ERROR

# Check for consensus issues
sudo journalctl -u rustchain-node | grep "consensus"

# Monitor API requests
tail -f /var/log/rustchain/api.log | grep "POST\|GET"
```

### Performance Monitoring

#### System Resource Monitoring

```bash
#!/bin/bash
# monitor_resources.sh

echo "=== System Resources ==="

# CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "CPU Usage: ${CPU_USAGE}%"

# Memory usage
MEM_INFO=$(free -m)
MEM_USED=$(echo "$MEM_INFO" | awk 'NR==2{printf "%.1f", $3*100/$2}')
echo "Memory Usage: ${MEM_USED}%"

# Disk usage
DISK_USAGE=$(df -h /var/lib/rustchain | awk 'NR==2{print $5}')
echo "Disk Usage: $DISK_USAGE"

# Network connections
CONNECTIONS=$(netstat -an | grep :8080 | wc -l)
echo "Active Connections: $CONNECTIONS"

# RustChain process info
RUSTCHAIN_PID=$(pgrep rustchain-node)
if [ ! -z "$RUSTCHAIN_PID" ]; then
    RUSTCHAIN_MEM=$(ps -p $RUSTCHAIN_PID -o %mem --no-headers)
    RUSTCHAIN_CPU=$(ps -p $RUSTCHAIN_PID -o %cpu --no-headers)
    echo "RustChain Process - CPU: ${RUSTCHAIN_CPU}%, Memory: ${RUSTCHAIN_MEM}%"
fi
```

### Automated Maintenance

#### Daily Maintenance Script

```bash
#!/bin/bash
# daily_maintenance.sh

LOG_FILE="/var/log/rustchain/maintenance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting daily maintenance" >> $LOG_FILE

# Check disk space
DISK_USAGE=$(df /var/lib/rustchain | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
    # Clean old logs
    find /var/log/rustchain -name "*.log.*" -mtime +7 -delete
fi

# Check node health
if ! curl -sf http://localhost:8080/health > /dev/null; then
    echo "[$DATE] ERROR: Node health check failed" >> $LOG_FILE
    systemctl restart rustchain-node
    sleep 30
fi

# Update peer list
curl -s http://localhost:8080/peers/refresh

# Backup configuration
cp /etc/rustchain/node.toml /etc/rustchain/node.toml.backup.$(date +%Y%m%d)

# Rotate old backups (keep 7 days)
find /etc/rustchain -name "node.toml.backup.*" -mtime +7 -delete

echo "[$DATE] Daily maintenance completed" >> $LOG_FILE
```

#### Cron Job Setup

```bash
# Add to crontab
crontab -e

# Add these lines:
# Daily maintenance at 2 AM
0 2 * * * /home/rustchain/daily_maintenance.sh

# Health check every 5 minutes
*/5 * * * * /home/rustchain/health_check.sh

# Resource monitoring every hour
0 * * * * /home/rustchain/monitor_resources.sh >> /var/log/rustchain/resources.log
```

---

## Security

### Network Security

#### Firewall Configuration

```bash
# UFW (Ubuntu Firewall)
sudo ufw enable

# Allow SSH (adjust port as needed)
sudo ufw allow 22/tcp

# Allow RustChain ports
sudo ufw allow 8080/tcp   # HTTP API
sudo ufw allow 8443/tcp   # HTTPS API
sudo ufw allow 9090/tcp   # P2P Network

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status verbose
```

#### iptables Rules

```bash
# Basic iptables rules
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9090 -j ACCEPT
sudo iptables -A INPUT -j DROP

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

### SSL/TLS Configuration

#### Generate SSL Certificate

```bash
# Self-signed certificate (development)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/rustchain/ssl/key.pem \
  -out /etc/rustchain/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

# Let's Encrypt certificate (production)
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
sudo ln -s /etc/letsencrypt/live/your-domain.com/privkey.pem /etc/rustchain/ssl/key.pem
sudo ln -s /etc/letsencrypt/live/your-domain.com/fullchain.pem /etc/rustchain/ssl/cert.pem
```

### Access Control

#### API Key Authentication

```toml
# In node.toml
[api]
enable_auth = true
auth_method = "api_key"
api_keys = [
    "admin:your-admin-api-key-here",
    "readonly:your-readonly-api-key-here"
]
```

#### Rate Limiting

```toml
[api]
rate_limit_per_minute = 1000
rate_limit_per_hour = 10000
rate_limit_burst = 100

# Per-endpoint limits
[api.endpoints]
"/wallet/balance" = { per_minute = 60, per_hour = 1000 }
"/api/miners" = { per_minute = 10, per_hour = 100 }
```

### System Hardening

#### User Security

```bash
# Disable root login
sudo passwd -l root

# Configure sudo timeout
echo "Defaults timestamp_timeout=5" | sudo tee -a /etc/sudoers

# Set up SSH key authentication
ssh-keygen -t ed25519 -C "rustchain-node-operator"
# Copy public key to ~/.ssh/authorized_keys
# Disable password authentication in /etc/ssh/sshd_config
```

#### File Permissions

```bash
# Secure configuration files
sudo chmod 600 /etc/rustchain/node.toml
sudo chown rustchain:rustchain /etc/rustchain/node.toml

# Secure SSL certificates
sudo chmod 600 /etc/rustchain/ssl/key.pem
sudo chmod 644 /etc/rustchain/ssl/cert.pem
sudo chown rustchain:rustchain /etc/rustchain/ssl/*

# Secure data directory
sudo chmod 750 /var/lib/rustchain
sudo chown -R rustchain:rustchain /var/lib/rustchain
```

---

## Troubleshooting

### Common Issues

#### Node Won't Start

**Symptoms**: Service fails to start, exits immediately

**Diagnosis**:
```bash
# Check service status
sudo systemctl status rustchain-node

# Check logs
sudo journalctl -u rustchain-node -n 50

# Check configuration
rustchain-node --config /etc/rustchain/node.toml --check-config
```

**Solutions**:
```bash
# Fix configuration syntax
rustchain-node --generate-config > /tmp/new-config.toml
diff /etc/rustchain/node.toml /tmp/new-config.toml

# Check file permissions
sudo chown rustchain:rustchain /etc/rustchain/node.toml
sudo chmod 600 /etc/rustchain/node.toml

# Verify data directory
sudo mkdir -p /var/lib/rustchain
sudo chown rustchain:rustchain /var/lib/rustchain
```

#### Sync Issues

**Symptoms**: Node stuck at old block, not syncing

**Diagnosis**:
```bash
# Check sync status
curl -s http://localhost:8080/sync | jq

# Check peer connections
curl -s http://localhost:8080/peers | jq length

# Check network connectivity
telnet 50.28.86.131 9090
```

**Solutions**:
```bash
# Restart sync
curl -X POST http://localhost:8080/sync/restart

# Add more bootstrap peers
# Edit node.toml and add more bootstrap_nodes

# Reset blockchain data (last resort)
sudo systemctl stop rustchain-node
sudo rm -rf /var/lib/rustchain/blockchain
sudo systemctl start rustchain-node
```

#### High Memory Usage

**Symptoms**: Node consuming excessive RAM

**Diagnosis**:
```bash
# Check memory usage
ps aux | grep rustchain-node
free -h

# Check cache settings
grep cache_size_mb /etc/rustchain/node.toml
```

**Solutions**:
```bash
# Reduce cache size in node.toml
[database]
cache_size_mb = 512  # Reduce from default

# Enable swap (temporary fix)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### API Errors

**Symptoms**: API requests failing, timeouts

**Diagnosis**:
```bash
# Test API endpoints
curl -v http://localhost:8080/health
curl -v http://localhost:8080/epoch

# Check API logs
tail -f /var/log/rustchain/api.log

# Check connection limits
netstat -an | grep :8080 | wc -l
```

**Solutions**:
```bash
# Increase connection limits in node.toml
[api]
max_connections = 5000
worker_threads = 8

# Restart API service
sudo systemctl restart rustchain-node

# Check firewall rules
sudo ufw status
```

### Performance Issues

#### Slow API Responses

```bash
# Enable API metrics
[api]
enable_metrics = true
metrics_port = 9091

# Check metrics
curl http://localhost:9091/metrics | grep api_request_duration

# Optimize database
[database]
cache_size_mb = 2048
max_open_files = 5000
compression = "lz4"
```

#### High CPU Usage

```bash
# Check process threads
ps -eLf | grep rustchain-node

# Limit worker threads
[api]
worker_threads = 4  # Reduce if needed

# Enable CPU profiling
RUSTFLAGS="-C target-cpu=native" cargo build --release
```

### Network Issues

#### Peer Connection Problems

```bash
# Check peer status
curl -s http://localhost:8080/peers | jq '.[] | {id, address, status}'

# Test connectivity to bootstrap nodes
for node in 50.28.86.131 node2.rustchain.org node3.rustchain.org; do
    echo "Testing $node..."
    nc -zv $node 9090
done

# Check NAT/firewall
sudo ufw allow 9090/tcp
# Configure port forwarding if behind NAT
```

#### DNS Resolution Issues

```bash
# Test DNS resolution
nslookup node2.rustchain.org
dig node3.rustchain.org

# Use IP addresses in bootstrap_nodes if DNS fails
bootstrap_nodes = [
    "50.28.86.131:9090",
    "192.168.1.100:9090"  # Use IPs instead of hostnames
]
```

### Recovery Procedures

#### Database Corruption

```bash
# Stop node
sudo systemctl stop rustchain-node

# Backup corrupted data
sudo cp -r /var/lib/rustchain /var/lib/rustchain.corrupted

# Try repair
rustchain-node --repair-database --data-dir /var/lib/rustchain

# If repair fails, resync from scratch
sudo rm -rf /var/lib/rustchain/blockchain
sudo systemctl start rustchain-node
```

#### Configuration Recovery

```bash
# Backup current config
sudo cp /etc/rustchain/node.toml /etc/rustchain/node.toml.broken

# Generate fresh config
rustchain-node --generate-config > /tmp/fresh-config.toml

# Merge settings
# Edit /tmp/fresh-config.toml with your custom settings
sudo cp /tmp/fresh-config.toml /etc/rustchain/node.toml
sudo chown rustchain:rustchain /etc/rustchain/node.toml
```

### Monitoring Scripts

#### Automated Problem Detection

```bash
#!/bin/bash
# problem_detector.sh

ALERT_EMAIL="admin@example.com"
NODE_URL="http://localhost:8080"

# Check if node is responding
if ! curl -sf "$NODE_URL/health" > /dev/null; then
    echo "ALERT: Node not responding" | mail -s "RustChain Node Down" $ALERT_EMAIL
    systemctl restart rustchain-node
fi

# Check sync status
SYNC_STATUS=$(curl -s "$NODE_URL/sync" | jq -r '.status')
if [ "$SYNC_STATUS" != "synced" ]; then
    echo "ALERT: Node not synced (status: $SYNC_STATUS)" | mail -s "RustChain Sync Issue" $ALERT_EMAIL
fi

# Check peer count
PEER_COUNT=$(curl -s "$NODE_URL/peers" | jq length)
if [ "$PEER_COUNT" -lt 3 ]; then
    echo "ALERT: Low peer count ($PEER_COUNT)" | mail -s "RustChain Peer Issue" $ALERT_EMAIL
fi

# Check disk space
DISK_USAGE=$(df /var/lib/rustchain | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "ALERT: Disk usage critical (${DISK_USAGE}%)" | mail -s "RustChain Disk Full" $ALERT_EMAIL
fi
```

---

## Support & Resources

### Documentation

- **API Reference**: [API_REFERENCE.md](./API_REFERENCE.md)
- **Miner Setup**: [MINER_SETUP_GUIDE.md](./MINER_SETUP_GUIDE.md)
- **Python SDK**: [PYTHON_SDK_TUTORIAL.md](./PYTHON_SDK_TUTORIAL.md)

### Community

- **GitHub**: [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties)
- **Discord**: [RustChain Community](https://discord.gg/rustchain)
- **Forum**: [forum.rustchain.org](https://forum.rustchain.org)

### Professional Support

- **Enterprise Support**: enterprise@rustchain.org
- **Node Hosting**: hosting@rustchain.org
- **Consulting**: consulting@rustchain.org

---

**Happy Node Operating! 🚀**

*Help secure and decentralize the RustChain network while earning rewards.*

---

*Last updated: February 2026*  
*Guide Version: 1.0*