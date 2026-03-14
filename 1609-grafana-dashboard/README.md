# RustChain Grafana Dashboard

Grafana dashboard for monitoring RustChain metrics.

## Features

- Node health monitoring
- Block production rate
- Transaction throughput
- Network latency
- Peer connections

## Import

1. Open Grafana
2. Go to Dashboards → Import
3. Upload `rustchain-dashboard.json`
4. Select your Prometheus data source

## Metrics

- `rustchain_blocks_total` - Total blocks produced
- `rustchain_transactions_total` - Total transactions processed
- `rustchain_peers_connected` - Connected peers
- `rustchain_block_time_seconds` - Block time
- `rustchain_transaction_latency_seconds` - Transaction latency

## Screenshot

![Dashboard](screenshot.png)

---

Fixes #1609
