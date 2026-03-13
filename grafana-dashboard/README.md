# Grafana Dashboard for RustChain Metrics

**Bounty**: #1609
**Value**: 10 RTC (~$1)
**Status**: In Progress

---

## 📊 Dashboard Features

### Panels
1. **Current Epoch** - Real-time epoch display
2. **Active Miners** - Current miner count
3. **Network Hashrate** - Historical hashrate graph
4. **Top Miners** - Leaderboard table

### Auto-Refresh
- Every 10 seconds
- Real-time metrics

---

## 🚀 Quick Start

### 1. Install Grafana

```bash
# macOS
brew install grafana

# Linux
sudo apt-get install grafana
```

### 2. Start Grafana

```bash
grafana-server
# Access: http://localhost:3000
# Login: admin/admin
```

### 3. Import Dashboard

```bash
# Import via CLI
grafana-cli dashboards import rustchain-metrics.json

# Or via UI:
# 1. Go to Dashboards → Import
# 2. Upload rustchain-metrics.json
# 3. Select Prometheus datasource
```

### 4. Configure Datasource

Copy `datasources/prometheus.yml` to:
```
/etc/grafana/provisioning/datasources/
```

Restart Grafana:
```bash
sudo systemctl restart grafana-server
```

---

## 📈 Metrics

### Available Metrics

| Metric | Description |
|--------|-------------|
| `rustchain_epoch` | Current epoch number |
| `rustchain_active_miners` | Active miner count |
| `rustchain_hashrate` | Network hashrate |
| `rustchain_miner_reward` | Miner rewards |

---

## 📁 Files

- `dashboards/rustchain-metrics.json` - Dashboard definition
- `datasources/prometheus.yml` - Prometheus datasource config

---

## ✅ Progress

- [x] Create dashboard structure
- [x] Add epoch panel
- [x] Add miners panel
- [x] Add hashrate graph
- [x] Add top miners table
- [x] Configure datasource
- [ ] Test with live data
- [ ] Submit PR

---

**ETA**: 1 hour
