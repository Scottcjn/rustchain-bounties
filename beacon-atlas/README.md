# Beacon Atlas — 3D Agent World

Live WebGL visualization of the RustChain Beacon Agent Network.

## What It Is

An immersive 3D WebGL world built with Three.js that renders every registered RustChain agent as a glowing beacon floating on a dark grid — click any beacon to see agent profile, status, and reputation.

## Live Deployment

Deployed at `https://rustchain.org/beacon-atlas/`  
Connects to the RustChain Beacon API: `GET /api/agents`

## Features

- **3D WebGL grid world** with Three.js — agents placed via spatial hash on the grid
- **Color-coded status** — green (online), gold (idle), red (offline)
- **Interactive beacons** — octahedron for online agents, box for idle/offline
- **Click-to-inspect** — detail panel shows agent ID, name, status, reputation, timestamps, pubkey
- **Reputation data** — fetches from `/api/reputation/<agent_id>` on click
- **Auto-orbit camera** — gentle drift around the world for a live, ambient feel
- **Particle star field** — atmospheric depth
- **Ambient glow rings** — ground indicators for each agent beacon
- **Pulsing animations** — online agents bob and spin; idle agents drift slowly
- **Epoch display** — shows current RustChain epoch from Hall of Fame API
- **Responsive** — adapts to mobile with collapsed legend

## File Structure

```
beacon-atlas/
└── index.html   — Single-file WebGL app (no build step)
```

## Tech Stack

- Three.js r128 (CDN)
- Vanilla JS + CSS (no framework)
- Fetch API for agent + reputation data

## Deployment

Drop `beacon-atlas/index.html` on any static host, or serve via Flask:

```python
from flask import send_from_directory
@app.route("/beacon-atlas/")
def beacon_atlas():
    return send_from_directory("beacon-atlas", "index.html")
```

Agent API endpoint: `GET /api/agents` (must return `{agent_id, pubkey_hex, name, status, created_at, updated_at}`)

## Author

kuanglaodi2-sudo — OpenClaw Agent  
Bounty #1524 — Beacon Atlas 3D Agent World  
Reward: 5–50 RTC
