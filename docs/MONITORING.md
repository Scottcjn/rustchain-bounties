# RustChain Monitoring: Prometheus + Grafana

This guide covers the Prometheus exporter and Grafana dashboard for
RustChain network observability.

## Architecture

```
RustChain Node (/health, /epoch, /api/miners)
        │
        ▼
┌──────────────────┐     ┌────────────┐     ┌──────────┐
│ Prometheus        │────▶│ Prometheus │────▶│ Grafana  │
│ Exporter (:9100)  │     │   (:9090)  │     │ (:3000)  │
└──────────────────┘     └────────────┘     └──────────┘
```

The exporter (`scripts/prometheus_exporter.py`) polls the RustChain node
API on a configurable interval and exposes OpenMetrics-compatible gauges
at `/metrics`.  Prometheus scrapes the exporter; Grafana visualises the
stored time series.

## Quick Start (Docker Compose)

```bash
cd monitoring/
docker compose up -d
```

| Service    | URL                         | Credentials   |
|------------|-----------------------------|---------------|
| Grafana    | http://localhost:3000        | admin / admin |
| Prometheus | http://localhost:9090        | —             |
| Exporter   | http://localhost:9100/metrics| —             |

The Grafana dashboard is auto-provisioned on startup.

## Running the Exporter Standalone

The exporter has **zero external dependencies** — it uses only the Python
standard library.

```bash
export RUSTCHAIN_NODE_URL="https://50.28.86.131"
export EXPORTER_PORT=9100
export SCRAPE_INTERVAL=30
python3 -m scripts.prometheus_exporter
```

Then configure your existing Prometheus to scrape
`http://<host>:9100/metrics`.

## Environment Variables

| Variable             | Default                      | Description                       |
|----------------------|------------------------------|-----------------------------------|
| `RUSTCHAIN_NODE_URL` | `https://50.28.86.131`       | RustChain node base URL           |
| `EXPORTER_PORT`      | `9100`                       | HTTP listen port                  |
| `SCRAPE_INTERVAL`    | `30`                         | Seconds between node API polls    |
| `VERIFY_TLS`         | `0`                          | `1` to verify TLS (self-signed)   |
| `HTTP_TIMEOUT`       | `15`                         | Per-request timeout in seconds    |

## Exposed Metrics

### Node Health (from `/health`)

| Metric                              | Type  | Description                           |
|-------------------------------------|-------|---------------------------------------|
| `rustchain_up`                      | gauge | 1 if the node is reachable, else 0    |
| `rustchain_node_uptime_seconds`     | gauge | Node uptime in seconds                |
| `rustchain_node_tip_age_slots`      | gauge | Chain tip age in slots                |
| `rustchain_node_backup_age_hours`   | gauge | Latest backup age in hours            |
| `rustchain_node_db_rw`             | gauge | 1 if database is read-write           |

### Epoch (from `/epoch`)

| Metric                              | Type  | Description                           |
|-------------------------------------|-------|---------------------------------------|
| `rustchain_epoch_current`           | gauge | Current epoch number                  |
| `rustchain_epoch_slot`              | gauge | Current slot within the epoch         |
| `rustchain_epoch_blocks_per_epoch`  | gauge | Blocks per epoch (config constant)    |
| `rustchain_epoch_pot_rtc`           | gauge | Epoch reward pot in RTC               |
| `rustchain_epoch_enrolled_miners`   | gauge | Miners enrolled in the current epoch  |

### Miners (from `/api/miners`)

| Metric                                      | Type  | Labels                                      | Description                       |
|----------------------------------------------|-------|----------------------------------------------|-----------------------------------|
| `rustchain_miners_active_total`              | gauge | —                                            | Total active miners               |
| `rustchain_miner_last_attest_timestamp`      | gauge | `miner`, `device_family`, `device_arch`, `hardware_type` | Last attestation (unix ts)        |
| `rustchain_miner_antiquity_multiplier`       | gauge | `miner`, `device_family`, `device_arch`, `hardware_type` | Antiquity multiplier              |

### Exporter Meta

| Metric                              | Type    | Description                          |
|-------------------------------------|---------|--------------------------------------|
| `rustchain_scrape_duration_seconds` | gauge   | Time for the last scrape cycle       |
| `rustchain_scrape_errors_total`     | counter | Cumulative scrape error count        |

## Grafana Dashboard

The pre-built dashboard (`monitoring/grafana/dashboards/rustchain.json`)
includes:

- **Network Overview** — node status, uptime, tip age, DB health, backup age
- **Epoch & Supply** — current epoch, slot progress gauge, epoch pot (RTC), enrolled miners
- **Miners** — active miner count, active miners over time, antiquity multipliers
- **Epoch & Uptime History** — time-series of epoch/slot progress and uptime
- **Supply Metrics** — epoch reward pot trend, exporter scrape health

## Tests

```bash
python -m pytest tests/test_prometheus_exporter.py -v
```

The test suite covers:
- Configuration from environment variables
- Prometheus text format rendering (labels, escaping, HELP/TYPE lines)
- Full scrape with mocked HTTP (all endpoints success, partial failure, empty miners)
- Graceful handling of malformed JSON, timeouts, HTTP errors
- Cumulative error counter across scrape cycles
- MetricsCollector thread-safe state management

## File Layout

```
scripts/
  prometheus_exporter.py          # Exporter (stdlib-only, zero deps)
monitoring/
  docker-compose.yml              # Full monitoring stack
  Dockerfile.exporter             # Exporter container image
  prometheus/
    prometheus.yml                # Prometheus scrape config
  grafana/
    dashboards/
      rustchain.json              # Pre-built Grafana dashboard
    provisioning/
      datasources/
        prometheus.yml            # Auto-register Prometheus datasource
      dashboards/
        provider.yml              # Auto-load dashboard JSON
tests/
  test_prometheus_exporter.py     # Comprehensive test suite
docs/
  MONITORING.md                   # This file
```
