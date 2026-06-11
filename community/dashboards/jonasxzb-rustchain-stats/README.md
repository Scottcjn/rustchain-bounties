# RustChain Live Stats Dashboard

Submission for `Scottcjn/rustchain-bounties#1600`.

## Deliverable

- `index.html` - static, no-backend dashboard
- `verify-dashboard.mjs` - endpoint smoke check for the live data sources

## What it shows

- Current epoch
- Active miner count
- Total RTC supply
- Transactions panel
- Epoch progress
- Active miner table
- Auto-refresh status

## Live data sources

Default API base: `https://explorer.rustchain.org`

- `/health`
- `/epoch`
- `/api/miners`
- `/agent/stats`
- `/api/transactions?limit=8` when explicitly probed with `?probeTx=1`

The current public node returns live data for epoch, miners, health, and agent stats. Because `/api/transactions` currently returns 404 on the public explorer node, the dashboard avoids noisy default 404 probes and keeps the Transactions panel visible with live agent-economy activity from `/agent/stats`. Add `?probeTx=1` to test a node that exposes `/api/transactions`.

You can override the API base with:

```text
index.html?api=https://50.28.86.131
index.html?api=https://50.28.86.131&probeTx=1
```

## Run locally

```bash
python3 -m http.server 4173
```

Then open:

```text
http://127.0.0.1:4173/community/dashboards/jonasxzb-rustchain-stats/
```

## Verify

```bash
node community/dashboards/jonasxzb-rustchain-stats/verify-dashboard.mjs
```
