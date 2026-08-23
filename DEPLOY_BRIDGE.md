# BoTTube Bridge — Deployment Guide

Rewards BoTTube creators in RTC for uploads and view milestones, paid via signed RustChain transfers.

## Architecture

```
BoTTube API ──poll──> bottube_bridge.py ──deltas──> reward engine
                          │                            │
                     SQLite state               anti-abuse gates
                  (views, nonces,                        │
                   milestones, audit)             budget cap
                                                   │
                                        signed transfer (Ed25519)
                                                   │
                                          RustChain node
```

## Prerequisites

- Python 3.10+
- `pip install cryptography` (Ed25519 signing)
- A funded RustChain bridge wallet (address + private key, 64 hex chars)
- Outbound HTTPS to `bottube.ai` and your RustChain node

## Setup

1. Copy `bridge_config.json` next to `bottube_bridge.py`.
2. Set your bridge wallet address in the config (`bridge_wallet.address`).
3. Export the private key (never write it to disk):

```bash
export BRIDGE_PRIVATE_KEY=<64-hex-private-key>
```

4. First run writes the default config if missing and **refuses to sign** until `dry_run` is set to `false`.

```bash
python bottube_bridge.py --once          # single cycle, dry-run
python bottube_bridge.py                 # daemon mode
```

5. When you've reviewed the dry-run audit trail, flip `"dry_run": false`.

## Systemd unit

```ini
# /etc/systemd/system/bottube-bridge.service
[Unit]
Description=BoTTube RTC reward bridge
After=network-online.target

[Service]
User=bridge
Environment=BRIDGE_PRIVATE_KEY=__SET_AT_DEPLOY__
WorkingDirectory=/opt/bottube-bridge
ExecStart=/usr/bin/python3 bottube_bridge.py --config bridge_config.json --state /var/lib/bottube-bridge/state.db
Restart=on-failure
RestartSec=30

# hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/lib/bottube-bridge

[Install]
WantedBy=multi-user.target
```

## Anti-abuse summary

| Gate | Mechanism |
|---|---|
| View farming | Rewards accrue from poll-to-poll deltas only; absolute counts never pay |
| Bot velocity spikes | Growth above `max_views_per_hour` quarantines the decision |
| Low-effort content | `min_video_seconds` + upload-age gate before any reward |
| Reward runaway | Per-agent batching + hard global `daily_budget_rtc` ceiling |
| Replay attacks | Persistent per-wallet nonces; node enforces uniqueness |
| Accidental spend | Dry-run default; append-only payout audit log |

## Operational notes

- State DB is the source of truth for "already paid" — back it up; losing it can cause double payouts after threshold crossings.
- Payout addresses come from the config allowlist first; optionally auto-discovered from creators' video descriptions (`Payout wallet: RTC...`) when `discover_from_descriptions` is enabled.
- The node's transfer endpoint enforces nonce ordering; the daemon fetches the latest nonce each batch and increments locally.
