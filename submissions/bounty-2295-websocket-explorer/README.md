# RustChain Block Explorer — Real-Time WebSocket Feed

**Bounty #2295 — 75 RTC**

## Overview
Real-time WebSocket feed for the RustChain block explorer. Live block and attestation streaming without page refresh.

## Features
- WebSocket server polling all 4 RustChain nodes every 15 seconds
- Live block feed — new blocks appear without refresh
- Live attestation feed — miner attestations stream in real-time
- Connection status indicator with auto-reconnect (3s retry)
- Epoch settlement alert (visual + sound + browser notification)
- Miner count sparkline chart
- Mobile-friendly responsive layout
- Works with existing nginx proxy config

## Tech Stack
- **Backend**: Python 3 + `websockets` + `aiohttp`
- **Frontend**: Vanilla JS + HTML (no React, no dependencies)

## Setup

```bash
pip install websockets aiohttp
python server.py
```

Server starts on `ws://0.0.0.0:8765`.

## Nginx Config

```nginx
location /ws {
    proxy_pass http://127.0.0.1:8765;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}

location /explorer {
    alias /var/www/rustchain/explorer;
    try_files $uri $uri/ /explorer.html;
}
```

## Wallet
RTC Wallet: `RTC_ElromEvedElElyon_2295`
