# Xonotic RustChain Arena Server Setup Guide

**Bounty #291** | **Reward: 15 RTC** | **Author: admin1douyin**

---

## Overview

Complete server setup guide for Xonotic RustChain Arena with RTC reward system.

## Requirements

- Linux server (Ubuntu 20.04+ or Debian 11+)
- Minimum 2 CPU cores, 4GB RAM
- 10GB disk space
- Static IP address
- Open ports: 26000/UDP (game), 80/TCP (web)

## Step 1: System Preparation

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip git wget curl nginx certbot
sudo useradd -m -s /bin/bash xonotic
```

## Step 2: Xonotic Server

```bash
sudo su - xonotic
mkdir -p ~/xonotic/{data,logs,config}
cd ~/xonotic
wget https://dl.xonotic.org/xonotic-0.8.5.zip
unzip xonotic-0.8.5.zip
```

## Step 3: RustChain Integration

```bash
cd ~/xonotic
git clone https://github.com/Scottcjn/xonotic-rustchain.git
pip3 install -r requirements.txt
```

## Step 4: Server Configuration

Create `~/.xonotic/server.cfg`:
```
hostname "Xonotic RustChain Arena"
maxplayers 16
sv_public 1
sv_rtc_enabled 1
sv_rtc_api_url "https://api.rustchain.org/rewards"
sv_rtc_wallet "YOUR_WALLET_ADDRESS"
```

## Step 5: Firewall

```bash
sudo ufw allow 26000/udp
sudo ufw allow 80/tcp
sudo ufw enable
```

## Step 6: Systemd Services

Create `/etc/systemd/system/xonotic.service`:
```ini
[Unit]
Description=Xonotic RustChain Arena Server
After=network.target

[Service]
Type=simple
User=xonotic
WorkingDirectory=/home/xonotic/xonotic-0.8.5
ExecStart=/home/xonotic/xonotic-0.8.5/xonotic-linux64-dedicated +set fs_game rustchain +exec server.cfg
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable xonotic
sudo systemctl start xonotic
```

## Step 7: Nginx Proxy

Create `/etc/nginx/sites-available/xonotic`:
```nginx
server {
    listen 80;
    server_name your-server.com;
    location / {
        proxy_pass http://127.0.0.1:26000;
    }
}
```

## Verification

```bash
sudo systemctl status xonotic
journalctl -u xonotic -f
```

## Submit

Fork https://github.com/Scottcjn/xonotic-rustchain, add files to `deploy/`, open PR.
