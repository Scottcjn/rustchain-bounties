# RustChain Node Host Preflight Checklist

Use this checklist before applying for node-host bounty/weekly host payout review.

## 1) Minimum Host Specs

| Class | CPU | RAM | Disk | Network |
|---|---|---|---|---|
| Vintage host | 2+ cores | 4 GB | 20 GB free | Stable public IP, inbound reachability |
| Modern host | 4+ cores | 8 GB | 40 GB free | Stable public IP, inbound reachability |

Required ports:
- `8099/tcp` (API)
- `443/tcp` if fronted by TLS proxy

## 2) Required Endpoint Checks

Run from a remote machine:

```bash
curl -sk https://YOUR_NODE/health
curl -sk https://YOUR_NODE/epoch
curl -sk https://YOUR_NODE/api/miners
```

Expected shape:

- `/health` must include keys:
  - `ok` (bool, must be `true`)
  - `version` (string)
  - `uptime_s` (number)

Example (current network shape):

```json
{
  "ok": true,
  "version": "2.2.1-rip200",
  "uptime_s": 32804,
  "db_rw": true,
  "tip_age_slots": 0
}
```

- `/epoch` must include keys:
  - `epoch`
  - `slot`
  - `blocks_per_epoch`
  - `enrolled_miners`

Example:

```json
{
  "epoch": 79,
  "slot": 11480,
  "blocks_per_epoch": 144,
  "enrolled_miners": 49,
  "epoch_pot": 1.5
}
```

- `/api/miners` must return a non-empty JSON array with miner entries including:
  - `miner`
  - `last_attest`
  - `device_family`
  - `antiquity_multiplier`

## 3) Version Gate

Your node version must match network version (or be upgraded within 24h when flagged).

```bash
# Step 1: Download network version to file
curl -sk https://50.28.86.131/health > network_health.json

# Step 2: Extract version with Python
python3 -c "
import json
with open('network_health.json', 'r') as f:
    health = json.load(f)
print('Network version:', health['version'])
"

# Step 1: Download your node version to file  
curl -sk https://YOUR_NODE/health > your_health.json

# Step 2: Extract version with Python
python3 -c "
import json
with open('your_health.json', 'r') as f:
    health = json.load(f)
print('Your version:', health['version'])
"
```

If mismatch persists, payout can be held until upgrade is confirmed.

## 4) 30-Minute Smoke Test

```bash
# from rustchain-bounties repo
python3 scripts/node_miner_weekly_scan.py \
  --node-url https://YOUR_NODE \
  --expected-miners-file expected_miners.txt
```

Pass criteria:
- Node appears in scan output as online.
- `payout_eligible` is `yes` (`pay_weekly` or `pay_weekly_and_upgrade_node`).
- Active miner set is visible and fresh.

## 5) 14-Day Uptime Proof Format (for reliability bonus)

Post one daily line (UTC) in your claim thread/log:

```text
YYYY-MM-DDTHH:MM:SSZ | node_url=https://YOUR_NODE | ok=true | version=2.2.1-rip200 | uptime_s=123456 | miners_seen=14
```

At end of 14 days include:
- 14 timestamped lines (or equivalent exported log)
- one `/health` sample from day 1 and day 14
- one `node_miner_weekly_scan.py` output generated during the window

## 6) Weekly Payout Pass/Fail Rules

Pass:
- node is active + online
- `/health.ok == true`
- endpoints responsive
- no persistent split-state issues
- version mismatch (if any) corrected within SLA

Fail / Hold:
- node offline or unstable during review window
- stale/outdated version without remediation
- missing endpoint evidence
- repeated split-state or unverifiable host identity

## 7) Host Application Template

```markdown
**Node Host Application**
- Region:
- Hardware class: vintage / modern
- Host spec: CPU / RAM / disk / network
- Node URL:
- Wallet:
- Uptime target:
- Contact handle:
- Preflight proof:
  - /health
  - /epoch
  - /api/miners
```