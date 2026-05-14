#!/bin/bash
#
# RustChain Node Setup Script
# ===========================
# One-click deployment for RustChain validator/full nodes.
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh                    # Interactive setup
#   ./setup.sh --type validator   # Non-interactive validator setup
#   ./setup.sh --type full        # Non-interactive full node
#   ./setup.sh --uninstall        # Remove RustChain node
#
# Supports: Ubuntu 20.04+, Debian 11+, CentOS 8+
#

set -euo pipefail

# ─── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Configuration ────────────────────────────────────────────────────────────
RUSTCHAIN_VERSION="1.2.0"
INSTALL_DIR="/opt/rustchain"
CONFIG_DIR="/etc/rustchain"
DATA_DIR="/var/lib/rustchain"
LOG_DIR="/var/log/rustchain"
BIN_DIR="/usr/local/bin"
SERVICE_NAME="rustchaind"
RPC_PORT=26657
P2P_PORT=26656
REST_PORT=1317
GRPC_PORT=9090

# ─── Utility Functions ────────────────────────────────────────────────────────
log_info()    { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*"; }
log_step()    { echo -e "\n${CYAN}━━━ $* ━━━${NC}\n"; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    elif [[ -f /etc/redhat-release ]]; then
        OS="centos"
        VER=""
    else
        log_error "Unsupported operating system"
        exit 1
    fi
    log_info "Detected OS: $OS $VER"
}

# ─── System Requirements ──────────────────────────────────────────────────────
check_requirements() {
    log_step "Checking System Requirements"
    
    local pass=true
    
    # CPU cores
    local cpu_cores=$(nproc)
    if [[ $cpu_cores -lt 2 ]]; then
        log_warn "CPU: $cpu_cores cores (recommended: 4+)"
        pass=false
    else
        log_info "CPU: $cpu_cores cores ✓"
    fi
    
    # RAM
    local ram_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $ram_gb -lt 4 ]]; then
        log_warn "RAM: ${ram_gb}GB (recommended: 8GB+)"
        pass=false
    else
        log_info "RAM: ${ram_gb}GB ✓"
    fi
    
    # Disk space
    local disk_gb=$(df -BG / | awk 'NR==2{print $4}' | tr -d 'G')
    if [[ $disk_gb -lt 100 ]]; then
        log_warn "Disk: ${disk_gb}GB free (recommended: 200GB+)"
        pass=false
    else
        log_info "Disk: ${disk_gb}GB free ✓"
    fi
    
    # Network
    if ping -c 1 -W 3 rpc.rustchain.io &>/dev/null; then
        log_info "Network: Connected ✓"
    else
        log_warn "Network: Cannot reach rpc.rustchain.io"
        pass=false
    fi
    
    if [[ "$pass" == "false" ]]; then
        log_warn "Some requirements not met. Continue anyway? (y/N)"
        read -r response
        [[ "$response" =~ ^[Yy]$ ]] || exit 1
    fi
}

# ─── Install Dependencies ─────────────────────────────────────────────────────
install_deps() {
    log_step "Installing Dependencies"
    
    case $OS in
        ubuntu|debian)
            apt-get update -qq
            apt-get install -y -qq \
                curl wget jq unzip software-properties-common \
                build-essential git cmake \
                ufw fail2ban \
                >/dev/null 2>&1
            ;;
        centos|rhel|fedora)
            yum install -y -q \
                curl wget jq unzip \
                gcc gcc-c++ make git cmake \
                firewalld fail2ban \
                >/dev/null 2>&1
            ;;
    esac
    
    log_info "Dependencies installed ✓"
}

# ─── Install RustChain Binary ─────────────────────────────────────────────────
install_rustchain() {
    log_step "Installing RustChain v${RUSTCHAIN_VERSION}"
    
    local arch=$(uname -m)
    local binary_url
    
    case $arch in
        x86_64)  binary_url="https://github.com/rustchain/rustchain/releases/download/v${RUSTCHAIN_VERSION}/rustchain_${RUSTCHAIN_VERSION}_linux_amd64.tar.gz" ;;
        aarch64) binary_url="https://github.com/rustchain/rustchain/releases/download/v${RUSTCHAIN_VERSION}/rustchain_${RUSTCHAIN_VERSION}_linux_arm64.tar.gz" ;;
        *)       log_error "Unsupported architecture: $arch"; exit 1 ;;
    esac
    
    log_info "Downloading from $binary_url"
    wget -q -O /tmp/rustchain.tar.gz "$binary_url"
    
    tar -xzf /tmp/rustchain.tar.gz -C /tmp/
    chmod +x /tmp/rustchaind
    mv /tmp/rustchaind "$BIN_DIR/"
    
    # Verify installation
    if rustchaind version &>/dev/null; then
        log_info "RustChain installed: $(rustchaind version) ✓"
    else
        log_error "Installation failed"
        exit 1
    fi
    
    rm -f /tmp/rustchain.tar.gz
}

# ─── Create System User ───────────────────────────────────────────────────────
create_user() {
    log_step "Creating System User"
    
    if id -u rustchain &>/dev/null; then
        log_info "User 'rustchain' already exists ✓"
    else
        useradd --system --no-create-home --shell /bin/false rustchain
        log_info "User 'rustchain' created ✓"
    fi
    
    mkdir -p "$INSTALL_DIR" "$CONFIG_DIR" "$DATA_DIR" "$LOG_DIR"
    chown -R rustchain:rustchain "$INSTALL_DIR" "$CONFIG_DIR" "$DATA_DIR" "$LOG_DIR"
}

# ─── Initialize Node ──────────────────────────────────────────────────────────
init_node() {
    local node_type=$1
    local moniker=${2:-"my-rustchain-node"}
    
    log_step "Initializing ${node_type} node: $moniker"
    
    sudo -u rustchain rustchaind init "$moniker" --home "$DATA_DIR"
    
    # Download genesis
    log_info "Downloading genesis file..."
    wget -q -O "$DATA_DIR/config/genesis.json" \
        "https://github.com/rustchain/networks/raw/main/mainnet/genesis.json"
    
    # Download address book
    log_info "Downloading peer addresses..."
    wget -q -O "$DATA_DIR/config/addrbook.json" \
        "https://github.com/rustchain/networks/raw/main/mainnet/addrbook.json"
    
    # Configure for hardware
    tune_config "$node_type"
    
    log_info "Node initialized ✓"
}

# ─── Tune Configuration ───────────────────────────────────────────────────────
tune_config() {
    local node_type=$1
    local config_toml="$DATA_DIR/config/config.toml"
    local app_toml="$DATA_DIR/config/app.toml"
    
    log_info "Tuning configuration for ${node_type}..."
    
    # Get system resources
    local cpu_cores=$(nproc)
    local ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local ram_mb=$((ram_kb / 1024))
    
    # config.toml tuning
    sed -i "s/^moniker = .*/moniker = \"$(hostname)\"/" "$config_toml"
    sed -i "s/^seeds = .*/seeds = \"seeds.rustchain.io:26656\"/" "$config_toml"
    sed -i "s/^persistent_peers = .*/persistent_peers = \"\"/" "$config_toml"
    
    # Performance settings
    local recv_rate=$((cpu_cores * 10))
    local send_rate=$((cpu_cores * 10))
    sed -i "s/^recv_rate = .*/recv_rate = ${recv_rate}000000/" "$config_toml"
    sed -i "s/^send_rate = .*/send_rate = ${send_rate}000000/" "$config_toml"
    
    # app.toml tuning
    if [[ "$node_type" == "validator" ]]; then
        sed -i 's/^pruning = .*/pruning = "everything"/' "$app_toml"
    else
        sed -i 's/^pruning = .*/pruning = "default"/' "$app_toml"
    fi
    
    # API settings
    sed -i 's/^enable = .*/enable = true/' "$app_toml" 2>/dev/null || true
    sed -i 's/^swagger = .*/swagger = true/' "$app_toml" 2>/dev/null || true
}

# ─── Systemd Service ──────────────────────────────────────────────────────────
create_service() {
    log_step "Creating Systemd Service"
    
    cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=RustChain Node
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=rustchain
Group=rustchain
ExecStart=${BIN_DIR}/rustchaind start --home ${DATA_DIR}
Restart=on-failure
RestartSec=5
LimitNOFILE=65535
Environment="RUSTCHAIN_HOME=${DATA_DIR}"

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=${DATA_DIR} ${LOG_DIR}
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    log_info "Service created and enabled ✓"
}

# ─── Firewall Setup ───────────────────────────────────────────────────────────
setup_firewall() {
    log_step "Configuring Firewall"
    
    case $OS in
        ubuntu|debian)
            ufw default deny incoming
            ufw default allow outgoing
            ufw allow ssh
            ufw allow ${P2P_PORT}/tcp comment 'RustChain P2P'
            ufw allow ${RPC_PORT}/tcp comment 'RustChain RPC'
            ufw allow ${REST_PORT}/tcp comment 'RustChain REST'
            ufw --force enable
            ;;
        centos|rhel|fedora)
            systemctl enable --now firewalld
            firewall-cmd --permanent --add-port=${P2P_PORT}/tcp
            firewall-cmd --permanent --add-port=${RPC_PORT}/tcp
            firewall-cmd --permanent --add-port=${REST_PORT}/tcp
            firewall-cmd --reload
            ;;
    esac
    
    log_info "Firewall configured ✓"
}

# ─── Monitoring Setup ─────────────────────────────────────────────────────────
setup_monitoring() {
    log_step "Setting up Health Check Cron"
    
    cat > "$INSTALL_DIR/healthcheck.sh" << 'EOF'
#!/bin/bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:26657/status)
if [[ "$RESPONSE" != "200" ]]; then
    echo "[$(date)] RustChain node unhealthy - restarting" >> /var/log/rustchain/healthcheck.log
    systemctl restart rustchaind
fi
EOF
    chmod +x "$INSTALL_DIR/healthcheck.sh"
    
    (crontab -l 2>/dev/null; echo "*/5 * * * * $INSTALL_DIR/healthcheck.sh") | crontab -
    
    log_info "Health check cron installed (every 5 min) ✓"
}

# ─── Start Node ───────────────────────────────────────────────────────────────
start_node() {
    log_step "Starting RustChain Node"
    
    systemctl start "$SERVICE_NAME"
    sleep 3
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_info "RustChain node is running ✓"
        log_info ""
        log_info "  RPC:  http://localhost:${RPC_PORT}"
        log_info "  REST: http://localhost:${REST_PORT}"
        log_info "  gRPC: localhost:${GRPC_PORT}"
        log_info "  P2P:  port ${P2P_PORT}"
        log_info ""
        log_info "  Logs: journalctl -u ${SERVICE_NAME} -f"
        log_info "  Status: systemctl status ${SERVICE_NAME}"
    else
        log_error "Failed to start node. Check: journalctl -u ${SERVICE_NAME} -n 50"
        exit 1
    fi
}

# ─── Uninstall ────────────────────────────────────────────────────────────────
uninstall() {
    log_step "Uninstalling RustChain Node"
    
    systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    systemctl disable "$SERVICE_NAME" 2>/dev/null || true
    rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
    systemctl daemon-reload
    
    rm -f "$BIN_DIR/rustchaind"
    userdel rustchain 2>/dev/null || true
    
    log_warn "Data directories preserved at:"
    log_warn "  $DATA_DIR"
    log_warn "  $CONFIG_DIR"
    log_warn "Use 'rm -rf $DATA_DIR $CONFIG_DIR' to remove all data."
    
    log_info "RustChain uninstalled ✓"
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
    local node_type="full"
    local moniker=""
    local skip_firewall=false
    local action="install"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --type)         node_type="$2"; shift 2 ;;
            --moniker)      moniker="$2"; shift 2 ;;
            --no-firewall)  skip_firewall=true; shift ;;
            --uninstall)    action="uninstall"; shift ;;
            --help|-h)
                echo "Usage: $0 [--type validator|full] [--moniker NAME] [--no-firewall] [--uninstall]"
                exit 0
                ;;
            *) log_error "Unknown option: $1"; exit 1 ;;
        esac
    done
    
    if [[ "$action" == "uninstall" ]]; then
        check_root
        uninstall
        exit 0
    fi
    
    # Interactive mode if no type specified
    if [[ -z "$moniker" ]]; then
        echo -e "${CYAN}"
        echo "  ╔═══════════════════════════════════════╗"
        echo "  ║     ⛓️  RustChain Node Installer      ║"
        echo "  ╚═══════════════════════════════════════╝"
        echo -e "${NC}"
        
        read -p "  Node moniker [$(hostname)]: " moniker
        moniker=${moniker:-$(hostname)}
        
        echo "  Node type:"
        echo "    1) Full Node (default)"
        echo "    2) Validator Node"
        read -p "  Select [1]: " type_choice
        [[ "$type_choice" == "2" ]] && node_type="validator"
        
        echo ""
    fi
    
    check_root
    detect_os
    check_requirements
    install_deps
    install_rustchain
    create_user
    init_node "$node_type" "$moniker"
    create_service
    
    [[ "$skip_firewall" == "false" ]] && setup_firewall
    
    setup_monitoring
    start_node
    
    echo ""
    echo -e "${GREEN}  ✅ RustChain ${node_type} node deployed successfully!${NC}"
    echo ""
    echo "  Useful commands:"
    echo "    rustchaind status                     # Node status"
    echo "    rustchaind query bank balances zp6    # Check balance"
    echo "    journalctl -u rustchaind -f           # View logs"
    echo "    systemctl restart rustchaind           # Restart node"
    echo ""
    
    if [[ "$node_type" == "validator" ]]; then
        echo -e "${YELLOW}  📋 Next steps for validation:"
        echo "    1. Fund your validator wallet"
        echo "    2. rustchaind tx staking create-validator \\"
        echo "         --amount=1000000urst \\"
        echo "         --pubkey=\$(rustchaind tendermint show-validator) \\"
        echo "         --moniker=\"${moniker}\" \\"
        echo "         --chain-id=rustchain-1 \\"
        echo "         --from=zp6"
        echo -e "${NC}"
    fi
}

main "$@"
