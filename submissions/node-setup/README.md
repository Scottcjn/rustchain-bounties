# 🔧 RustChain Node Setup Scripts

One-click deployment for RustChain full nodes and validators.

## Quick Start

### Linux (Bash)
```bash
chmod +x setup.sh
sudo ./setup.sh
```

### Cross-Platform (Python)
```bash
python setup.py install
```

## Features

- **One-Click Deploy** — Single command to install and configure a node
- **Auto-Detection** — Detects OS, architecture, and system resources
- **Systemd Integration** — Automatic service creation with restart policies
- **Firewall Hardening** — Configures UFW/firewalld with minimal required ports
- **Health Monitoring** — Built-in cron-based health check with auto-restart
- **Validator Support** — Streamlined validator node setup with staking guide
- **Cross-Platform** — Python version works on Linux, macOS, and Windows
- **Config Snapshots** — Backup and restore configurations
- **Clean Uninstall** — Remove everything or keep data

## setup.sh (Bash — Linux)

Best for production Linux servers. Runs as root with systemd.

```bash
# Interactive install
sudo ./setup.sh

# Non-interactive validator
sudo ./setup.sh --type validator --moniker "my-node"

# Skip firewall configuration
sudo ./setup.sh --type full --no-firewall

# Uninstall
sudo ./setup.sh --uninstall
```

### What it does:
1. Checks system requirements (CPU, RAM, disk)
2. Installs dependencies (curl, jq, etc.)
3. Downloads RustChain binary for your architecture
4. Creates system user `rustchain`
5. Initializes node with genesis and peers
6. Tunes config.toml and app.toml for your hardware
7. Creates hardened systemd service
8. Configures firewall (UFW/firewalld)
9. Sets up health check cron job
10. Starts the node

### System Requirements
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 100 GB SSD | 200+ GB NVMe |
| Network | 10 Mbps | 100+ Mbps |

## setup.py (Python — Cross-Platform)

Works on Linux, macOS, and Windows. Python 3.7+.

```bash
# Install
python setup.py install --type validator --moniker "my-node"

# Check status
python setup.py status

# View logs
python setup.py logs -n 100

# Config snapshot
python setup.py snapshot

# Uninstall
python setup.py uninstall

# Upgrade
python setup.py upgrade
```

## Port Configuration

| Port | Service | Required |
|------|---------|----------|
| 26656 | P2P | Yes |
| 26657 | RPC | Yes |
| 1317 | REST API | Optional |
| 9090 | gRPC | Optional |

## Validator Setup

After installing a validator node:

```bash
# 1. Create or import key
rustchaind keys add my-validator
# or import:
rustchaind keys add my-validator --recover

# 2. Fund the wallet (get test tokens from faucet or transfer)

# 3. Create validator
rustchaind tx staking create-validator \
  --amount=1000000urst \
  --pubkey=$(rustchaind tendermint show-validator) \
  --moniker="my-validator" \
  --chain-id=rustchain-1 \
  --from=my-validator \
  --commission-rate="0.05" \
  --commission-max-rate="0.20" \
  --commission-max-change-rate="0.01" \
  --min-self-delegation="1"

# 4. Check validator status
rustchaind query staking validator $(rustchaind keys show my-validator --bech val -a)
```

## Post-Install

```bash
# Monitor sync progress
watch -n 1 'rustchaind status | jq ".sync_info"'

# Check connected peers
rustchaind net_info | jq '.result.n_peers'

# View logs
journalctl -u rustchaind -f

# Restart
sudo systemctl restart rustchaind
```

## License

MIT
