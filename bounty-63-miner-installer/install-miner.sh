#!/bin/bash
#
# RustChain Miner - Universal One-Line Installer
# curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
#
# Supports:
#   - Ubuntu 20.04/22.04/24.04
#   - Debian 11/12
#   - macOS (Intel + Apple Silicon)
#   - Raspberry Pi (ARM64)
#   - IBM POWER8/ppc64le
#
# Features:
#   - Python 3.8+ virtualenv isolation
#   - systemd user service (Linux) / launchd (macOS)
#   - Checksum verification of downloaded scripts
#   - --dry-run mode for preview
#   - First attestation test
#
# Author: Raj (@Rajkoli145) - Bounty #63
#

set -e

# Configuration
REPO_BASE="https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners"
CHECKSUM_URL="https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/checksums.sha256"
INSTALL_DIR="$HOME/.rustchain"
VENV_DIR="$INSTALL_DIR/venv"
NODE_URL="https://50.28.86.131"
SERVICE_NAME="rustchain-miner"
VERSION="1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Parse command line arguments
DRY_RUN=false
UNINSTALL=false
WALLET_ARG=""
SKIP_SERVICE=false
SKIP_CHECKSUM=false

print_usage() {
    echo "RustChain Miner Installer v$VERSION"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dry-run         Preview installation without making changes"
    echo "  --wallet NAME     Set wallet name (skips interactive prompt)"
    echo "  --uninstall       Remove RustChain miner and all files"
    echo "  --skip-service    Skip auto-start service setup"
    echo "  --skip-checksum   Skip checksum verification (not recommended)"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  curl -sSL .../install-miner.sh | bash"
    echo "  curl -sSL .../install-miner.sh | bash -s -- --wallet my-wallet"
    echo "  curl -sSL .../install-miner.sh | bash -s -- --dry-run"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        --wallet)
            WALLET_ARG="$2"
            shift 2
            ;;
        --skip-service)
            SKIP_SERVICE=true
            shift
            ;;
        --skip-checksum)
            SKIP_CHECKSUM=true
            shift
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# Dry-run wrapper for commands
run_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY-RUN]${NC} Would run: $*"
    else
        "$@"
    fi
}

# Dry-run wrapper for file creation
create_file() {
    local path=$1
    local content=$2
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY-RUN]${NC} Would create: $path"
    else
        echo "$content" > "$path"
    fi
}

# ============================================================================
# UNINSTALL MODE
# ============================================================================
if [ "$UNINSTALL" = true ]; then
    echo -e "${CYAN}[*] Uninstalling RustChain miner...${NC}"
    
    # Stop and remove systemd service (Linux)
    if [ "$(uname -s)" = "Linux" ] && command -v systemctl &>/dev/null; then
        if systemctl --user list-unit-files 2>/dev/null | grep -q "$SERVICE_NAME.service"; then
            echo -e "${YELLOW}[*] Stopping systemd service...${NC}"
            run_cmd systemctl --user stop "$SERVICE_NAME.service" 2>/dev/null || true
            run_cmd systemctl --user disable "$SERVICE_NAME.service" 2>/dev/null || true
            run_cmd rm -f "$HOME/.config/systemd/user/$SERVICE_NAME.service"
            run_cmd systemctl --user daemon-reload 2>/dev/null || true
            echo -e "${GREEN}[+] Systemd service removed${NC}"
        fi
    fi
    
    # Stop and remove launchd service (macOS)
    if [ "$(uname -s)" = "Darwin" ]; then
        PLIST_PATH="$HOME/Library/LaunchAgents/com.rustchain.miner.plist"
        if [ -f "$PLIST_PATH" ]; then
            echo -e "${YELLOW}[*] Stopping launchd service...${NC}"
            run_cmd launchctl unload "$PLIST_PATH" 2>/dev/null || true
            run_cmd rm -f "$PLIST_PATH"
            echo -e "${GREEN}[+] Launchd service removed${NC}"
        fi
    fi
    
    # Remove installation directory
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}[*] Removing installation directory...${NC}"
        run_cmd rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}[+] Installation directory removed${NC}"
    fi
    
    # Remove symlink
    if [ -L "/usr/local/bin/rustchain-mine" ]; then
        run_cmd rm -f "/usr/local/bin/rustchain-mine" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}[✓] RustChain miner uninstalled successfully${NC}"
    exit 0
fi

# ============================================================================
# BANNER
# ============================================================================
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║          RustChain Miner - Proof of Antiquity                     ║"
echo "║       Earn RTC by running vintage & modern hardware               ║"
echo "║                        Installer v$VERSION                           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}${BOLD}>>> DRY-RUN MODE - No changes will be made <<<${NC}"
    echo ""
fi

# ============================================================================
# DETECT PLATFORM
# ============================================================================
detect_platform() {
    local os=$(uname -s)
    local arch=$(uname -m)
    local platform=""
    local distro=""
    local distro_version=""
    
    case "$os" in
        Linux)
            # Check for distro
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                distro="$ID"
                distro_version="$VERSION_ID"
            fi
            
            case "$arch" in
                x86_64)
                    # Check for POWER8 running in compatibility mode
                    if grep -q "POWER8" /proc/cpuinfo 2>/dev/null; then
                        platform="power8"
                    else
                        platform="linux"
                    fi
                    ;;
                aarch64|arm64)
                    # Check for Raspberry Pi
                    if grep -qi "raspberry" /proc/cpuinfo 2>/dev/null; then
                        platform="rpi"
                    elif [ -f /sys/firmware/devicetree/base/model ] && grep -qi "raspberry" /sys/firmware/devicetree/base/model 2>/dev/null; then
                        platform="rpi"
                    else
                        platform="linux"  # Generic ARM64
                    fi
                    ;;
                ppc64le|ppc64)
                    if grep -q "POWER8" /proc/cpuinfo 2>/dev/null; then
                        platform="power8"
                    else
                        platform="ppc"
                    fi
                    ;;
                ppc|powerpc)
                    platform="ppc"
                    ;;
                armv7l|armhf)
                    platform="rpi"  # Older Pi
                    ;;
                *)
                    platform="linux"
                    ;;
            esac
            ;;
        Darwin)
            case "$arch" in
                arm64)
                    platform="macos"  # Apple Silicon
                    ;;
                x86_64)
                    platform="macos"  # Intel Mac
                    ;;
                Power*|ppc*)
                    platform="ppc"    # PowerPC Mac (vintage!)
                    ;;
                *)
                    platform="macos"
                    ;;
            esac
            ;;
        *)
            platform="unknown"
            ;;
    esac
    
    echo "$platform|$distro|$distro_version|$arch"
}

check_distro_support() {
    local distro=$1
    local version=$2
    
    case "$distro" in
        ubuntu)
            case "$version" in
                20.04|22.04|24.04)
                    echo -e "${GREEN}[+] Supported: Ubuntu $version${NC}"
                    return 0
                    ;;
                *)
                    echo -e "${YELLOW}[!] Ubuntu $version is not officially tested${NC}"
                    return 0
                    ;;
            esac
            ;;
        debian)
            case "$version" in
                11|12)
                    echo -e "${GREEN}[+] Supported: Debian $version${NC}"
                    return 0
                    ;;
                *)
                    echo -e "${YELLOW}[!] Debian $version is not officially tested${NC}"
                    return 0
                    ;;
            esac
            ;;
        raspbian)
            echo -e "${GREEN}[+] Supported: Raspbian (Raspberry Pi OS)${NC}"
            return 0
            ;;
        *)
            if [ -n "$distro" ]; then
                echo -e "${YELLOW}[!] $distro is not officially tested but may work${NC}"
            fi
            return 0
            ;;
    esac
}

# ============================================================================
# CHECK PYTHON
# ============================================================================
check_python() {
    local python_cmd=""
    local python_version=""
    
    # Try python3 first
    if command -v python3 &>/dev/null; then
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        if [ -n "$python_version" ]; then
            # Check if version >= 3.8
            major=$(echo "$python_version" | cut -d. -f1)
            minor=$(echo "$python_version" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
                echo "python3|$python_version"
                return 0
            elif [ "$major" -ge 3 ]; then
                # Allow 3.6+ with warning
                echo -e "${YELLOW}[!] Python $python_version detected. 3.8+ recommended.${NC}" >&2
                echo "python3|$python_version"
                return 0
            fi
        fi
    fi
    
    # Fallback to python
    if command -v python &>/dev/null; then
        python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        if [ -n "$python_version" ]; then
            major=$(echo "$python_version" | cut -d. -f1)
            if [ "$major" -ge 3 ]; then
                echo "python|$python_version"
                return 0
            fi
        fi
    fi
    
    echo ""
    return 1
}

install_python_hint() {
    local distro=$1
    echo -e "${RED}[!] Python 3.8+ not found${NC}"
    echo ""
    case "$distro" in
        ubuntu|debian|raspbian)
            echo "Install Python with:"
            echo "  sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
            ;;
        fedora)
            echo "Install Python with:"
            echo "  sudo dnf install -y python3 python3-pip"
            ;;
        *)
            echo "Please install Python 3.8 or later"
            ;;
    esac
}

# ============================================================================
# CHECKSUM VERIFICATION
# ============================================================================
verify_checksum() {
    local file=$1
    local expected=$2
    
    if [ "$SKIP_CHECKSUM" = true ]; then
        return 0
    fi
    
    if [ -z "$expected" ]; then
        echo -e "${YELLOW}[!] No checksum available for $file${NC}"
        return 0
    fi
    
    local actual=""
    if command -v sha256sum &>/dev/null; then
        actual=$(sha256sum "$file" 2>/dev/null | cut -d' ' -f1)
    elif command -v shasum &>/dev/null; then
        actual=$(shasum -a 256 "$file" 2>/dev/null | cut -d' ' -f1)
    else
        echo -e "${YELLOW}[!] No sha256 tool found, skipping checksum${NC}"
        return 0
    fi
    
    if [ "$actual" = "$expected" ]; then
        echo -e "${GREEN}[+] Checksum verified: $(basename "$file")${NC}"
        return 0
    else
        echo -e "${RED}[!] Checksum FAILED for $file${NC}"
        echo -e "${RED}    Expected: $expected${NC}"
        echo -e "${RED}    Got:      $actual${NC}"
        return 1
    fi
}

# ============================================================================
# INSTALL DEPENDENCIES
# ============================================================================
install_deps() {
    local python_cmd=$1
    echo -e "${YELLOW}[*] Setting up Python virtual environment...${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY-RUN]${NC} Would create virtualenv at $VENV_DIR"
        return 0
    fi
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Create virtualenv
    if ! $python_cmd -m venv "$VENV_DIR" 2>/dev/null; then
        echo -e "${YELLOW}[*] venv module not available, trying virtualenv...${NC}"
        $python_cmd -m pip install --user virtualenv 2>/dev/null || pip install --user virtualenv 2>/dev/null || true
        if ! $python_cmd -m virtualenv "$VENV_DIR" 2>/dev/null; then
            echo -e "${RED}[!] Could not create virtual environment${NC}"
            echo -e "${RED}[!] Please install python3-venv:${NC}"
            echo "    sudo apt install python3-venv"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}[+] Virtual environment created${NC}"
    
    # Install dependencies
    local venv_pip="$VENV_DIR/bin/pip"
    echo -e "${YELLOW}[*] Installing dependencies...${NC}"
    $venv_pip install --upgrade pip -q 2>/dev/null || true
    $venv_pip install requests -q 2>/dev/null || {
        echo -e "${RED}[!] Could not install requests. Check your internet connection.${NC}"
        exit 1
    }
    
    echo -e "${GREEN}[+] Dependencies installed${NC}"
}

# ============================================================================
# DOWNLOAD MINER
# ============================================================================
download_miner() {
    local platform=$1
    echo -e "${YELLOW}[*] Downloading miner for platform: ${BOLD}$platform${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY-RUN]${NC} Would download miner files to $INSTALL_DIR"
        return 0
    fi
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Download based on platform
    case "$platform" in
        linux|rpi)
            echo -e "${CYAN}[*] Downloading Linux/ARM miner...${NC}"
            curl -sSL "$REPO_BASE/linux/rustchain_linux_miner.py" -o rustchain_miner.py || {
                echo -e "${RED}[!] Failed to download miner${NC}"
                exit 1
            }
            curl -sSL "$REPO_BASE/linux/fingerprint_checks.py" -o fingerprint_checks.py 2>/dev/null || true
            ;;
        macos)
            echo -e "${CYAN}[*] Downloading macOS miner...${NC}"
            curl -sSL "$REPO_BASE/macos/rustchain_mac_miner_v2.4.py" -o rustchain_miner.py || {
                echo -e "${RED}[!] Failed to download miner${NC}"
                exit 1
            }
            curl -sSL "$REPO_BASE/linux/fingerprint_checks.py" -o fingerprint_checks.py 2>/dev/null || true
            ;;
        ppc)
            echo -e "${CYAN}[*] Downloading PowerPC miner...${NC}"
            curl -sSL "$REPO_BASE/ppc/rustchain_powerpc_g4_miner_v2.2.2.py" -o rustchain_miner.py || {
                echo -e "${RED}[!] Failed to download miner${NC}"
                exit 1
            }
            ;;
        power8)
            echo -e "${CYAN}[*] Downloading POWER8 miner...${NC}"
            curl -sSL "$REPO_BASE/power8/rustchain_power8_miner.py" -o rustchain_miner.py || {
                echo -e "${RED}[!] Failed to download miner${NC}"
                exit 1
            }
            curl -sSL "$REPO_BASE/power8/fingerprint_checks_power8.py" -o fingerprint_checks.py 2>/dev/null || true
            ;;
        *)
            echo -e "${YELLOW}[!] Unknown platform, using generic Linux miner${NC}"
            curl -sSL "$REPO_BASE/linux/rustchain_linux_miner.py" -o rustchain_miner.py
            curl -sSL "$REPO_BASE/linux/fingerprint_checks.py" -o fingerprint_checks.py 2>/dev/null || true
            ;;
    esac
    
    chmod +x rustchain_miner.py
    echo -e "${GREEN}[+] Miner downloaded${NC}"
    
    # Verify checksums if available
    if [ "$SKIP_CHECKSUM" != true ]; then
        echo -e "${YELLOW}[*] Verifying checksums...${NC}"
        # Try to get checksums file
        if curl -sSL "$CHECKSUM_URL" -o checksums.sha256 2>/dev/null; then
            local expected_miner=$(grep "rustchain_miner.py" checksums.sha256 2>/dev/null | awk '{print $1}')
            if [ -n "$expected_miner" ]; then
                verify_checksum "rustchain_miner.py" "$expected_miner" || {
                    echo -e "${RED}[!] Checksum verification failed. Aborting.${NC}"
                    exit 1
                }
            else
                echo -e "${YELLOW}[!] No checksum found in checksums file${NC}"
            fi
            rm -f checksums.sha256
        else
            echo -e "${YELLOW}[!] Could not fetch checksums file, skipping verification${NC}"
        fi
    fi
}

# ============================================================================
# CONFIGURE WALLET
# ============================================================================
configure_wallet() {
    local wallet_name=""
    
    if [ -n "$WALLET_ARG" ]; then
        wallet_name="$WALLET_ARG"
        echo -e "${GREEN}[+] Using wallet: ${BOLD}$wallet_name${NC}"
    else
        if [ "$DRY_RUN" = true ]; then
            wallet_name="dry-run-wallet"
            echo -e "${CYAN}[DRY-RUN]${NC} Would prompt for wallet name"
        else
            echo ""
            echo -e "${CYAN}[?] Enter your wallet name (or press Enter for auto-generated):${NC}"
            read -r wallet_name < /dev/tty
            
            if [ -z "$wallet_name" ]; then
                wallet_name="miner-$(hostname | tr '.' '-')-$(date +%s | tail -c 6)"
                echo -e "${YELLOW}[*] Using auto-generated wallet: ${BOLD}$wallet_name${NC}"
            fi
        fi
    fi
    
    # Validate wallet name
    if [[ ! "$wallet_name" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo -e "${RED}[!] Wallet name must be alphanumeric (hyphens and underscores allowed)${NC}"
        exit 1
    fi
    
    WALLET_NAME="$wallet_name"
}

# ============================================================================
# CREATE START SCRIPT
# ============================================================================
create_start_script() {
    local wallet=$1
    local venv_python="$VENV_DIR/bin/python"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY-RUN]${NC} Would create start script at $INSTALL_DIR/start.sh"
        return 0
    fi
    
    cat > "$INSTALL_DIR/start.sh" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
$venv_python rustchain_miner.py --wallet "$wallet"
EOF
    chmod +x "$INSTALL_DIR/start.sh"
    
    # Create symlink if possible
    if [ -w "/usr/local/bin" ]; then
        ln -sf "$INSTALL_DIR/start.sh" /usr/local/bin/rustchain-mine 2>/dev/null || true
    fi
    
    echo -e "${GREEN}[+] Start script created${NC}"
}

# ============================================================================
# SETUP SYSTEMD SERVICE (Linux)
# ============================================================================
setup_systemd_service() {
    local wallet=$1
    local venv_python="$VENV_DIR/bin/python"
    
    if [ "$SKIP_SERVICE" = true ]; then
        echo -e "${YELLOW}[!] Skipping service setup as requested${NC}"
        return 0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY-RUN]${NC} Would create systemd user service"
        return 0
    fi
    
    echo -e "${YELLOW}[*] Setting up systemd service...${NC}"
    
    mkdir -p "$HOME/.config/systemd/user"
    
    cat > "$HOME/.config/systemd/user/$SERVICE_NAME.service" << EOF
[Unit]
Description=RustChain Miner - Proof of Antiquity
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$venv_python $INSTALL_DIR/rustchain_miner.py --wallet $wallet
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/miner.log
StandardError=append:$INSTALL_DIR/miner.log

[Install]
WantedBy=default.target
EOF
    
    systemctl --user daemon-reload
    systemctl --user enable "$SERVICE_NAME.service" 2>/dev/null
    systemctl --user start "$SERVICE_NAME.service" 2>/dev/null
    
    echo -e "${GREEN}[+] Systemd service installed and started${NC}"
    echo -e "${CYAN}[i] Service commands:${NC}"
    echo "    Status:  systemctl --user status $SERVICE_NAME"
    echo "    Stop:    systemctl --user stop $SERVICE_NAME"
    echo "    Start:   systemctl --user start $SERVICE_NAME"
    echo "    Logs:    journalctl --user -u $SERVICE_NAME -f"
}

# ============================================================================
# SETUP LAUNCHD SERVICE (macOS)
# ============================================================================
setup_launchd_service() {
    local wallet=$1
    local venv_python="$VENV_DIR/bin/python"
    
    if [ "$SKIP_SERVICE" = true ]; then
        echo -e "${YELLOW}[!] Skipping service setup as requested${NC}"
        return 0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY-RUN]${NC} Would create launchd agent"
        return 0
    fi
    
    echo -e "${YELLOW}[*] Setting up launchd service...${NC}"
    
    mkdir -p "$HOME/Library/LaunchAgents"
    
    cat > "$HOME/Library/LaunchAgents/com.rustchain.miner.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rustchain.miner</string>
    <key>ProgramArguments</key>
    <array>
        <string>$venv_python</string>
        <string>-u</string>
        <string>$INSTALL_DIR/rustchain_miner.py</string>
        <string>--wallet</string>
        <string>$wallet</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$INSTALL_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$INSTALL_DIR/miner.log</string>
    <key>StandardErrorPath</key>
    <string>$INSTALL_DIR/miner.log</string>
</dict>
</plist>
EOF
    
    launchctl load "$HOME/Library/LaunchAgents/com.rustchain.miner.plist" 2>/dev/null
    
    echo -e "${GREEN}[+] Launchd service installed and started${NC}"
    echo -e "${CYAN}[i] Service commands:${NC}"
    echo "    Status:  launchctl list | grep rustchain"
    echo "    Stop:    launchctl stop com.rustchain.miner"
    echo "    Start:   launchctl start com.rustchain.miner"
    echo "    Logs:    tail -f $INSTALL_DIR/miner.log"
}

# ============================================================================
# RUN ATTESTATION TEST
# ============================================================================
run_attestation_test() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}[DRY-RUN]${NC} Would run attestation test"
        return 0
    fi
    
    echo ""
    echo -e "${YELLOW}[*] Running first attestation test...${NC}"
    
    local venv_python="$VENV_DIR/bin/python"
    
    # Quick Python test
    timeout 30 $venv_python -c "
import warnings
warnings.filterwarnings('ignore')
import requests
import json

NODE = '$NODE_URL'
print('[*] Connecting to RustChain node...')

try:
    # Test health
    resp = requests.get(f'{NODE}/health', timeout=10, verify=False)
    if resp.status_code == 200:
        health = resp.json()
        if health.get('ok'):
            print('[+] Node health: OK')
        else:
            print('[-] Node health check returned:', health)
    else:
        print('[-] Health check failed:', resp.status_code)
    
    # Test challenge
    resp = requests.post(f'{NODE}/attest/challenge', json={}, timeout=10, verify=False)
    if resp.status_code == 200:
        challenge = resp.json()
        nonce = challenge.get('nonce', '')[:16]
        print(f'[+] Challenge received: {nonce}...')
        print('[+] Attestation system: READY')
    else:
        print('[-] Challenge failed:', resp.status_code)
    
    # Get epoch info
    resp = requests.get(f'{NODE}/epoch', timeout=10, verify=False)
    if resp.status_code == 200:
        epoch = resp.json()
        print(f'[+] Current epoch: {epoch.get(\"epoch\", \"unknown\")}')
    
except Exception as e:
    print(f'[-] Test error: {e}')
    print('[!] Node may be temporarily unavailable')
" 2>/dev/null || {
    echo -e "${YELLOW}[!] Attestation test timed out (node may be busy)${NC}"
}
    
    echo ""
}

# ============================================================================
# PRINT SUMMARY
# ============================================================================
print_summary() {
    local wallet=$1
    local platform=$2
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    if [ "$DRY_RUN" = true ]; then
        echo -e "${GREEN}║              Dry-Run Complete - No Changes Made                  ║${NC}"
    else
        echo -e "${GREEN}║              Installation Complete!                              ║${NC}"
    fi
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${CYAN}To perform actual installation, run without --dry-run${NC}"
        echo ""
        return
    fi
    
    echo -e "${BOLD}Wallet:${NC}    $wallet"
    echo -e "${BOLD}Platform:${NC}  $platform"
    echo -e "${BOLD}Install:${NC}   $INSTALL_DIR"
    echo ""
    
    echo -e "${CYAN}Start mining manually:${NC}"
    echo "  cd $INSTALL_DIR && ./start.sh"
    echo ""
    
    if [ -L "/usr/local/bin/rustchain-mine" ]; then
        echo -e "${CYAN}Or use the convenience command:${NC}"
        echo "  rustchain-mine"
        echo ""
    fi
    
    echo -e "${CYAN}Check your balance:${NC}"
    echo "  curl -sk \"$NODE_URL/wallet/balance?miner_id=$wallet\""
    echo ""
    
    echo -e "${CYAN}View active miners:${NC}"
    echo "  curl -sk $NODE_URL/api/miners"
    echo ""
    
    echo -e "${CYAN}Uninstall:${NC}"
    echo "  curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall"
    echo ""
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    # Detect platform
    local platform_info=$(detect_platform)
    local platform=$(echo "$platform_info" | cut -d'|' -f1)
    local distro=$(echo "$platform_info" | cut -d'|' -f2)
    local distro_version=$(echo "$platform_info" | cut -d'|' -f3)
    local arch=$(echo "$platform_info" | cut -d'|' -f4)
    
    echo -e "${GREEN}[+] Platform: ${BOLD}$platform${NC} (${arch})"
    
    # Check distro support
    if [ -n "$distro" ]; then
        check_distro_support "$distro" "$distro_version"
    fi
    
    # Check Python
    local python_info=$(check_python)
    if [ -z "$python_info" ]; then
        install_python_hint "$distro"
        exit 1
    fi
    local python_cmd=$(echo "$python_info" | cut -d'|' -f1)
    local python_version=$(echo "$python_info" | cut -d'|' -f2)
    echo -e "${GREEN}[+] Python: ${BOLD}$python_version${NC} ($python_cmd)"
    
    # Install dependencies
    install_deps "$python_cmd"
    
    # Download miner
    download_miner "$platform"
    
    # Configure wallet
    configure_wallet
    
    # Create start script
    create_start_script "$WALLET_NAME"
    
    # Setup service based on OS
    local os=$(uname -s)
    if [ "$os" = "Linux" ]; then
        if command -v systemctl &>/dev/null; then
            if [ "$DRY_RUN" != true ]; then
                echo ""
                echo -e "${CYAN}[?] Set up auto-start on boot? (y/n):${NC}"
                read -r setup_service < /dev/tty
                if [ "$setup_service" = "y" ] || [ "$setup_service" = "Y" ]; then
                    setup_systemd_service "$WALLET_NAME"
                fi
            else
                echo -e "${CYAN}[DRY-RUN]${NC} Would ask about auto-start setup"
            fi
        fi
    elif [ "$os" = "Darwin" ]; then
        if [ "$DRY_RUN" != true ]; then
            echo ""
            echo -e "${CYAN}[?] Set up auto-start on login? (y/n):${NC}"
            read -r setup_service < /dev/tty
            if [ "$setup_service" = "y" ] || [ "$setup_service" = "Y" ]; then
                setup_launchd_service "$WALLET_NAME"
            fi
        else
            echo -e "${CYAN}[DRY-RUN]${NC} Would ask about auto-start setup"
        fi
    fi
    
    # Run attestation test
    run_attestation_test
    
    # Print summary
    print_summary "$WALLET_NAME" "$platform"
}

main "$@"
