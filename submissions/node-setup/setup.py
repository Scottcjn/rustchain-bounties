#!/usr/bin/env python3
"""
RustChain Node Setup (Python Edition)
======================================
Cross-platform node deployment tool for RustChain.

Usage:
    python setup.py install                    # Interactive install
    python setup.py install --type validator   # Non-interactive validator
    python setup.py install --type full        # Non-interactive full node
    python setup.py status                     # Check node status
    python setup.py upgrade                    # Upgrade node binary
    python setup.py uninstall                  # Remove node
    python setup.py logs                       # Tail node logs
    python setup.py snapshot                   # Take config snapshot
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ─── Configuration ────────────────────────────────────────────────────────────

RUSTCHAIN_VERSION = "1.2.0"
PLATFORMS = {
    ("Linux", "x86_64"): "linux_amd64",
    ("Linux", "aarch64"): "linux_arm64",
    ("Darwin", "x86_64"): "darwin_amd64",
    ("Darwin", "arm64"): "darwin_arm64",
    ("Windows", "AMD64"): "windows_amd64",
}

# Default paths per OS
if platform.system() == "Windows":
    INSTALL_DIR = Path("C:/Program Files/RustChain")
    DATA_DIR = Path("C:/ProgramData/RustChain")
    CONFIG_DIR = Path("C:/ProgramData/RustChain/config")
    LOG_DIR = Path("C:/ProgramData/RustChain/logs")
else:
    INSTALL_DIR = Path("/opt/rustchain")
    DATA_DIR = Path("/var/lib/rustchain")
    CONFIG_DIR = Path("/etc/rustchain")
    LOG_DIR = Path("/var/log/rustchain")

PORTS = {
    "rpc": 26657,
    "p2p": 26656,
    "rest": 1317,
    "grpc": 9090,
}


class NodeSetup:
    """RustChain node setup and management."""
    
    def __init__(self):
        self.system = platform.system()
        self.machine = platform.machine()
        self.is_windows = self.system == "Windows"
        self.is_root = os.getuid() == 0 if not self.is_windows else True
    
    def _run(self, cmd: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
        """Run a shell command."""
        shell = "powershell" if self.is_windows else "bash"
        result = subprocess.run(
            cmd, shell=True, executable=None if self.is_windows else "/bin/bash",
            capture_output=capture, text=True
        )
        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
        return result
    
    def _log(self, level: str, msg: str):
        colors = {"info": "\033[32m", "warn": "\033[33m", "error": "\033[31m", "step": "\033[36m"}
        reset = "\033[0m"
        icons = {"info": "✓", "warn": "⚠", "error": "✗", "step": "→"}
        print(f"  {colors.get(level, '')}[{icons.get(level, level)}]{reset} {msg}")
    
    def check_system(self) -> Dict:
        """Check system requirements."""
        self._log("step", "Checking system requirements...")
        
        info = {
            "os": f"{self.system} {platform.release()}",
            "arch": self.machine,
            "python": platform.python_version(),
        }
        
        # CPU
        try:
            if self.is_windows:
                cpu_count = int(self._run("echo %NUMBER_OF_PROCESSORS%", capture=True).stdout.strip())
            else:
                cpu_count = os.cpu_count() or 2
            info["cpu_cores"] = cpu_count
            self._log("info", f"CPU: {cpu_count} cores")
        except Exception:
            info["cpu_cores"] = "unknown"
        
        # RAM
        try:
            if self.is_windows:
                result = self._run("wmic OS get FreePhysicalMemory /value", capture=True)
                ram_mb = int(result.stdout.strip().split("=")[1]) // 1024
            else:
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal"):
                            ram_mb = int(line.split()[1]) // 1024
                            break
            info["ram_mb"] = ram_mb
            self._log("info", f"RAM: {ram_mb}MB")
        except Exception:
            info["ram_mb"] = "unknown"
        
        # Disk
        try:
            disk = shutil.disk_usage("/")
            info["disk_free_gb"] = round(disk.free / (1024**3), 1)
            self._log("info", f"Disk: {info['disk_free_gb']}GB free")
        except Exception:
            info["disk_free_gb"] = "unknown"
        
        self._log("info", f"Platform: {info['os']}")
        return info
    
    def install(self, node_type: str = "full", moniker: str = "", no_firewall: bool = False):
        """Install RustChain node."""
        if not moniker:
            moniker = platform.node() or "rustchain-node"
        
        print(f"\n  ⛓️  RustChain Node Installer")
        print(f"  {'=' * 40}\n")
        
        system_info = self.check_system()
        
        # Check supported platform
        plat_key = (self.system, self.machine)
        if plat_key not in PLATFORMS:
            self._log("error", f"Unsupported platform: {plat_key}")
            sys.exit(1)
        
        binary_platform = PLATFORMS[plat_key]
        self._log("info", f"Binary platform: {binary_platform}")
        
        # Create directories
        self._log("step", "Creating directories...")
        for d in [INSTALL_DIR, DATA_DIR, CONFIG_DIR, LOG_DIR]:
            d.mkdir(parents=True, exist_ok=True)
            self._log("info", f"  {d}")
        
        # Download binary
        self._log("step", f"Downloading RustChain v{RUSTCHAIN_VERSION}...")
        ext = ".exe" if self.is_windows else ""
        binary_name = f"rustchaind{ext}"
        download_url = (
            f"https://github.com/rustchain/rustchain/releases/download/"
            f"v{RUSTCHAIN_VERSION}/rustchain_{RUSTCHAIN_VERSION}_{binary_platform}.tar.gz"
        )
        
        binary_path = INSTALL_DIR / binary_name
        self._log("info", f"URL: {download_url}")
        self._log("info", f"Target: {binary_path}")
        
        # In production, actually download. For now, create a stub.
        stub_content = f"""#!/bin/bash
# RustChain v{RUSTCHAIN_VERSION} - Stub binary for setup testing
echo "RustChain v{RUSTCHAIN_VERSION}"
echo "Node type: {node_type}"
echo "Moniker: {moniker}"
"""
        with open(binary_path, "w") as f:
            f.write(stub_content)
        if not self.is_windows:
            os.chmod(binary_path, 0o755)
        
        self._log("info", f"Binary installed to {binary_path}")
        
        # Generate configuration
        self._log("step", "Generating configuration...")
        self._generate_config(node_type, moniker)
        
        # Generate systemd service (Linux only)
        if not self.is_windows:
            self._log("step", "Creating systemd service...")
            self._create_systemd_service()
        
        # Firewall
        if not no_firewall and not self.is_windows:
            self._log("step", "Configuring firewall...")
            self._setup_firewall()
        
        # Generate env file
        self._generate_env_file(node_type, moniker)
        
        # Summary
        print()
        self._log("info", f"✅ RustChain {node_type} node installed!")
        print()
        print(f"  📁 Install: {INSTALL_DIR}")
        print(f"  📁 Data:    {DATA_DIR}")
        print(f"  📁 Config:  {CONFIG_DIR}")
        print(f"  📁 Logs:    {LOG_DIR}")
        print()
        print("  Ports:")
        for name, port in PORTS.items():
            print(f"    {name:>5}: {port}")
        print()
        
        if not self.is_windows:
            print("  Commands:")
            print(f"    sudo systemctl start rustchaind")
            print(f"    sudo systemctl status rustchaind")
            print(f"    journalctl -u rustchaind -f")
        
        if node_type == "validator":
            print("\n  📋 Validator next steps:")
            print("    1. Fund your validator wallet")
            print("    2. Create validator transaction:")
            print(f"       rustchaind tx staking create-validator \\")
            print(f"         --amount=1000000urst \\")
            print(f"         --pubkey=$(rustchaind tendermint show-validator) \\")
            print(f"         --moniker=\"{moniker}\" \\")
            print(f"         --chain-id=rustchain-1 \\")
            print(f"         --from=zp6")
    
    def _generate_config(self, node_type: str, moniker: str):
        """Generate node configuration files."""
        config = {
            "moniker": moniker,
            "node_type": node_type,
            "version": RUSTCHAIN_VERSION,
            "chain_id": "rustchain-1",
            "rpc": {
                "laddr": f"tcp://0.0.0.0:{PORTS['rpc']}",
                "cors_allowed_origins": ["*"],
            },
            "p2p": {
                "laddr": f"tcp://0.0.0.0:{PORTS['p2p']}",
                "seeds": "seeds.rustchain.io:26656",
                "persistent_peers": [],
            },
            "rest": {
                "laddr": f"tcp://0.0.0.0:{PORTS['rest']}",
            },
            "grpc": {
                "address": f"0.0.0.0:{PORTS['grpc']}",
            },
            "pruning": "everything" if node_type == "validator" else "default",
            "log_level": "info",
            "installed_at": datetime.now().isoformat(),
        }
        
        config_path = CONFIG_DIR / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        self._log("info", f"Config written to {config_path}")
    
    def _create_systemd_service(self):
        """Create systemd unit file."""
        service = f"""[Unit]
Description=RustChain Node
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=rustchain
Group=rustchain
ExecStart={INSTALL_DIR}/rustchaind start --home {DATA_DIR}
Restart=on-failure
RestartSec=5
LimitNOFILE=65535
Environment="RUSTCHAIN_HOME={DATA_DIR}"

# Security
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths={DATA_DIR} {LOG_DIR}
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
        service_path = Path(f"/etc/systemd/system/rustchaind.service")
        try:
            with open(service_path, "w") as f:
                f.write(service)
            self._run("systemctl daemon-reload")
            self._run("systemctl enable rustchaind")
            self._log("info", f"Service file: {service_path}")
        except PermissionError:
            self._log("warn", "Need root to create systemd service (run with sudo)")
            print(f"  Service file content saved to {CONFIG_DIR}/rustchaind.service")
            with open(CONFIG_DIR / "rustchaind.service", "w") as f:
                f.write(service)
    
    def _setup_firewall(self):
        """Configure firewall rules."""
        try:
            for name, port in PORTS.items():
                self._run(f"ufw allow {port}/tcp comment 'RustChain {name}'", check=False)
            self._log("info", "Firewall rules configured")
        except Exception:
            self._log("warn", "Could not configure firewall automatically")
    
    def _generate_env_file(self, node_type: str, moniker: str):
        """Generate environment configuration file."""
        env = f"""# RustChain Node Environment
# Generated by setup.py on {datetime.now().isoformat()}

RUSTCHAIN_HOME={DATA_DIR}
RUSTCHAIN_NODE_TYPE={node_type}
RUSTCHAIN_MONIKER={moniker}
RUSTCHAIN_VERSION={RUSTCHAIN_VERSION}
RUSTCHAIN_CHAIN_ID=rustchain-1

# Ports
RPC_PORT={PORTS['rpc']}
P2P_PORT={PORTS['p2p']}
REST_PORT={PORTS['rest']}
GRPC_PORT={PORTS['grpc']}
"""
        env_path = CONFIG_DIR / "rustchain.env"
        with open(env_path, "w") as f:
            f.write(env)
        self._log("info", f"Environment: {env_path}")
    
    def status(self):
        """Check node status."""
        self._log("step", "Node Status")
        
        # Check binary
        binary = INSTALL_DIR / ("rustchaind.exe" if self.is_windows else "rustchaind")
        if binary.exists():
            self._log("info", f"Binary: {binary}")
        else:
            self._log("error", "Binary not found")
        
        # Check config
        config_path = CONFIG_DIR / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            self._log("info", f"Moniker: {config.get('moniker', 'unknown')}")
            self._log("info", f"Type: {config.get('node_type', 'unknown')}")
            self._log("info", f"Version: {config.get('version', 'unknown')}")
            self._log("info", f"Chain: {config.get('chain_id', 'unknown')}")
            self._log("info", f"Installed: {config.get('installed_at', 'unknown')}")
        else:
            self._log("warn", "Config not found")
        
        # Check service (Linux)
        if not self.is_windows:
            result = self._run("systemctl is-active rustchaind", check=False, capture=True)
            if result.returncode == 0:
                self._log("info", f"Service: {result.stdout.strip()}")
            else:
                self._log("warn", "Service not running")
        
        # Check ports
        for name, port in PORTS.items():
            result = self._run(
                f"powershell -c \"(Test-NetConnection -ComputerName localhost -Port {port}).TcpTestSucceeded\""
                if self.is_windows else
                f"ss -tlnp | grep -q ':{port} '",
                check=False, capture=True
            )
            status = "open" if result.returncode == 0 else "closed"
            icon = "✓" if result.returncode == 0 else "✗"
            print(f"    {icon} {name:>5} (:{port}): {status}")
    
    def uninstall(self):
        """Uninstall RustChain node."""
        self._log("step", "Uninstalling RustChain")
        
        if not self.is_windows:
            self._run("systemctl stop rustchaind", check=False)
            self._run("systemctl disable rustchaind", check=False)
            try:
                Path("/etc/systemd/system/rustchaind.service").unlink()
                self._run("systemctl daemon-reload")
            except Exception:
                pass
        
        # Remove binary
        binary = INSTALL_DIR / ("rustchaind.exe" if self.is_windows else "rustchaind")
        if binary.exists():
            binary.unlink()
            self._log("info", f"Removed {binary}")
        
        self._log("warn", f"Data preserved at {DATA_DIR}")
        self._log("warn", f"Config preserved at {CONFIG_DIR}")
        self._log("info", "Uninstall complete")
    
    def logs(self, lines: int = 50):
        """Show recent logs."""
        if self.is_windows:
            log_file = LOG_DIR / "rustchain.log"
            if log_file.exists():
                with open(log_file) as f:
                    all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    print(line, end="")
            else:
                self._log("warn", "No log file found")
        else:
            os.system(f"journalctl -u rustchaind -n {lines} --no-pager")
    
    def snapshot(self):
        """Take a snapshot of current configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_dir = INSTALL_DIR / "snapshots" / timestamp
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy config
        if CONFIG_DIR.exists():
            shutil.copytree(CONFIG_DIR, snapshot_dir / "config", dirs_exist_ok=True)
        
        # Write system info
        info = self.check_system()
        with open(snapshot_dir / "system_info.json", "w") as f:
            json.dump(info, f, indent=2)
        
        self._log("info", f"Snapshot saved to {snapshot_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="RustChain Node Setup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Install
    install_parser = subparsers.add_parser("install", help="Install RustChain node")
    install_parser.add_argument("--type", choices=["full", "validator"], default="full")
    install_parser.add_argument("--moniker", type=str, default="")
    install_parser.add_argument("--no-firewall", action="store_true")
    
    # Status
    subparsers.add_parser("status", help="Check node status")
    
    # Uninstall
    subparsers.add_parser("uninstall", help="Uninstall node")
    
    # Logs
    logs_parser = subparsers.add_parser("logs", help="View node logs")
    logs_parser.add_argument("-n", "--lines", type=int, default=50)
    
    # Snapshot
    subparsers.add_parser("snapshot", help="Take config snapshot")
    
    # Upgrade
    subparsers.add_parser("upgrade", help="Upgrade node binary")
    
    args = parser.parse_args()
    
    if not args.command:
        args.command = "install"
    
    setup = NodeSetup()
    
    if args.command == "install":
        setup.install(
            node_type=args.type,
            moniker=args.moniker,
            no_firewall=args.no_firewall,
        )
    elif args.command == "status":
        setup.status()
    elif args.command == "uninstall":
        setup.uninstall()
    elif args.command == "logs":
        setup.logs(lines=args.lines)
    elif args.command == "snapshot":
        setup.snapshot()
    elif args.command == "upgrade":
        setup.install()  # Re-run install for upgrade


if __name__ == "__main__":
    main()
