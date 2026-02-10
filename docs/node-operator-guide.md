# RustChain Node Operator Guide

Guide for running a RustChain attestation node.

## Overview

RustChain attestation nodes validate hardware fingerprints, distribute mining rewards, and maintain the ledger. Running a node helps decentralize the network.

## Requirements

### Hardware
- 4+ CPU cores
- 8GB+ RAM
- 100GB+ SSD storage
- Stable internet connection (100+ Mbps recommended)
- Static IP address or dynamic DNS

### Software
- Ubuntu 22.04 LTS or newer (recommended)
- Python 3.9+
- PostgreSQL 14+ or SQLite
- Nginx or Apache (for reverse proxy)
- SSL certificate (Let's Encrypt recommended)

## Installation

### System Preparation

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx postgresql postgresql-contrib
```

### Clone Repository

```bash
git clone https://github.com/rustchain/node.git
cd node
```

### Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Setup

**PostgreSQL (recommended for production):**

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE rustchain;
CREATE USER rustchain_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE rustchain TO rustchain_user;
\q
```

**SQLite (for testing):**

No setup required - database file created automatically.

## Configuration

### Node Configuration

Create `config.yaml`:

```yaml
node:
  bind_address: "0.0.0.0"
  port: 8443
  ssl_cert: "/etc/letsencrypt/live/your-domain.com/fullchain.pem"
  ssl_key: "/etc/letsencrypt/live/your-domain.com/privkey.pem"
  
database:
  type: "postgresql"  # or "sqlite"
  host: "localhost"
  port: 5432
  name: "rustchain"
  user: "rustchain_user"
  password: "secure_password"

network:
  chain_id: "rustchain-mainnet-1"
  epoch_duration: 3600  # seconds
  reward_per_epoch: 1.5
  
validation:
  require_hardware_attestation: true
  vm_detection_enabled: true
  min_uptime_for_rewards: 1800  # seconds
  
multipliers:
  PowerPC_G4: 2.5
  PowerPC_G5: 2.0
  PowerPC_G3: 1.8
  Pentium_4: 1.5
  retro_x86: 1.4
  Apple_Silicon: 1.2
  x86_64: 1.0
```

### SSL Certificate

**Let's Encrypt (recommended):**

```bash
sudo certbot certonly --nginx -d your-domain.com
```

**Self-signed (testing only):**

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/rustchain.key \
  -out /etc/ssl/certs/rustchain.crt
```

### Firewall Configuration

```bash
sudo ufw allow 8443/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## Running the Node

### Development Mode

```bash
source venv/bin/activate
python3 rustchain_node.py --config config.yaml
```

### Production (systemd)

Create `/etc/systemd/system/rustchain-node.service`:

```ini
[Unit]
Description=RustChain Attestation Node
After=network.target postgresql.service

[Service]
Type=simple
User=rustchain
Group=rustchain
WorkingDirectory=/opt/rustchain/node
Environment="PATH=/opt/rustchain/node/venv/bin"
ExecStart=/opt/rustchain/node/venv/bin/python3 /opt/rustchain/node/rustchain_node.py --config /opt/rustchain/node/config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable rustchain-node
sudo systemctl start rustchain-node
sudo systemctl status rustchain-node
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/rustchain`:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass https://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws {
        proxy_pass https://127.0.0.1:8443/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/rustchain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Maintenance

### Monitor Logs

```bash
sudo journalctl -u rustchain-node -f
```

### Database Backup

**PostgreSQL:**

```bash
pg_dump rustchain > backup_$(date +%Y%m%d).sql
```

**SQLite:**

```bash
cp rustchain.db backup_$(date +%Y%m%d).db
```

### Update Node Software

```bash
cd /opt/rustchain/node
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart rustchain-node
```

### Health Checks

```bash
curl -sk https://your-domain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1704067200,
  "version": "1.0.0",
  "uptime": 86400
}
```

## Monitoring

### Prometheus Integration

Add to `config.yaml`:

```yaml
monitoring:
  prometheus_enabled: true
  metrics_port: 9090
```

Scrape metrics:

```bash
curl http://localhost:9090/metrics
```

### Key Metrics

- `rustchain_active_miners` - Number of active miners
- `rustchain_epoch_number` - Current epoch
- `rustchain_total_rewards_distributed` - Total RTC distributed
- `rustchain_attestations_per_second` - Attestation throughput
- `rustchain_database_connections` - Active DB connections

### Grafana Dashboard

Import dashboard template from `grafana/rustchain-node-dashboard.json`.

## Troubleshooting

### Node Won't Start

**Check logs:**
```bash
sudo journalctl -u rustchain-node -n 50
```

**Common issues:**
- Port 8443 already in use: Change port in config.yaml
- SSL certificate not found: Verify paths in config.yaml
- Database connection failed: Check PostgreSQL service status

### High Memory Usage

**Check process:**
```bash
ps aux | grep rustchain_node
```

**Adjust connection pool in config.yaml:**
```yaml
database:
  max_connections: 20  # Reduce if memory constrained
```

### Slow Attestation Processing

**Increase worker threads:**
```yaml
node:
  worker_threads: 8  # Match CPU core count
```

**Enable database query caching:**
```yaml
database:
  query_cache_enabled: true
  cache_size_mb: 512
```

## Security

### Hardening Checklist

- [ ] Use strong database passwords
- [ ] Enable firewall (ufw)
- [ ] Use SSL certificates (Let's Encrypt)
- [ ] Run node as non-root user
- [ ] Keep software updated
- [ ] Enable fail2ban for SSH
- [ ] Restrict API access by IP if needed
- [ ] Regular database backups
- [ ] Monitor logs for anomalies

### Rate Limiting

Add to `config.yaml`:

```yaml
rate_limiting:
  enabled: true
  requests_per_minute: 100
  requests_per_hour: 1000
  ban_duration: 3600  # seconds
```

## Federation

### Connecting to Other Nodes

Add peer nodes in `config.yaml`:

```yaml
peers:
  - url: "https://node1.rustchain.org"
    trust_level: "high"
  - url: "https://node2.rustchain.org"
    trust_level: "medium"
```

### Consensus Participation

Enable validator mode:

```yaml
validator:
  enabled: true
  stake_amount: 1000.0  # RTC
  voting_power: 1
```

## Next Steps

- [API Reference](api-reference.md) - Understand node endpoints
- [Architecture Overview](architecture-overview.md) - System design
- [Contributing Guide](contributing-guide.md) - Improve RustChain
