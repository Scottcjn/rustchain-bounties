# RustChain Multi-Node Health Dashboard

**Bounty #2300 — 50 RTC**

## Overview
Public status page monitoring all 4 RustChain attestation nodes in real-time. "Is It Down" for the RustChain network.

## Features
- Polls all 4 nodes every 60 seconds
- Shows: status (up/down/degraded), response time, version, uptime, active miners, current epoch
- 24-hour uptime history with visual timeline per node
- Incident log with automatic detection (node goes down → incident opens, comes back → resolves)
- Response time graph per node (latency sparkline)
- Mobile-friendly responsive layout
- RSS/Atom feed for incidents (`/rss`)
- Geographic map showing node locations
- SQLite storage (auto-prunes records older than 48h)

## Nodes Monitored
| Node | Endpoint | Location |
|------|----------|----------|
| Node 1 | https://50.28.86.131/health | LiquidWeb US |
| Node 2 | https://50.28.86.153/health | LiquidWeb US |
| Node 3 | http://76.8.228.245:8099/health | Ryan's Proxmox |
| Node 4 | http://38.76.217.189:8099/health | Hong Kong |

## Setup

```bash
pip install aiohttp
python server.py
# Dashboard at http://localhost:8080
# API at http://localhost:8080/api/status
# RSS at http://localhost:8080/rss
```

## API Endpoints
- `GET /` — Dashboard HTML
- `GET /api/status` — Current node status (JSON)
- `GET /api/history/{node-id}?hours=24` — Historical data
- `GET /api/incidents` — Incident log
- `GET /rss` — RSS feed for incidents

## Nginx Config

```nginx
location /status {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Deploy Target
`rustchain.org/status`

## Wallet
RTC Wallet: `RTC_ElromEvedElElyon_2300`
