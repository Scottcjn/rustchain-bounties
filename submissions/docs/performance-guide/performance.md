# RustChain Performance Optimization Guide

> Maximize throughput, minimize latency, and scale your RustChain miner infrastructure effectively.

---

## Table of Contents

1. [Miner Performance Optimization](#miner-performance-optimization)
2. [API Optimization](#api-optimization)
3. [Caching Strategies](#caching-strategies)
4. [Database Optimization](#database-optimization)
5. [Network Optimization](#network-optimization)
6. [Benchmarking & Profiling](#benchmarking--profiling)

---

## Miner Performance Optimization

### Hardware Recommendations

RustChain uses Proof-of-Antiquity (RIP-200) which rewards vintage hardware attestation. Performance recommendations differ from typical blockchain nodes.

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| CPU | 1 core (any arch) | 2 cores | Vintage architectures (PowerPC, SPARC, MIPS) welcome |
| RAM | 256 MB | 1 GB | Python miner is lightweight |
| Storage | 100 MB | 1 GB SSD | SQLite database, minimal disk usage |
| Network | 1 Mbps | 10 Mbps | API calls to rustchain.org are lightweight |
| OS | Linux/macOS | Ubuntu 22.04 LTS | Windows supported via WSL |

### Configuration Tuning

The RustChain miner is configured via environment variables and `config.json`:

```json
{
    "miner_id": "your-miner-id",
    "api_endpoint": "https://rustchain.org",
    "epoch_interval": 300,
    "hardware_fingerprint": true,
    "log_level": "INFO"
}
```

Key environment variables:

```bash
# RustChain miner configuration
export RUSTCHAIN_ENDPOINT="https://rustchain.org"
export RUSTCHAIN_MINER_ID="your-miner-id"
export RUSTCHAIN_LOG_LEVEL="INFO"

# Python performance tuning
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
```

### Docker Deployment

RustChain uses local Docker builds (no pre-built images):

```bash
# Build the miner image
docker build -f Dockerfile.miner -t rustchain-miner .

# Run with docker-compose
docker-compose up -d
```

Example `docker-compose.yml`:

```yaml
version: "3.8"
services:
  miner:
    build:
      context: .
      dockerfile: Dockerfile.miner
    environment:
      - RUSTCHAIN_ENDPOINT=https://rustchain.org
      - RUSTCHAIN_MINER_ID=${MINER_ID}
    restart: unless-stopped
```

### System-Level Tuning (Linux)

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Network buffer optimization (for API polling)
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728

# For NVMe storage (if used for SQLite WAL)
echo "none" > /sys/block/nvme0n1/queue/scheduler
```

### Python-Specific Tuning

```python
# Use connection pooling for API requests
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
session.mount("https://rustchain.org", adapter)

# Reuse session across all API calls
response = session.get("https://rustchain.org/health")
```

---

## API Optimization

### Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_api_session():
    """Create a pooled, retry-capable session for RustChain API."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=10,
        pool_maxsize=20,
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
```

### Request Batching

```python
# BAD: Individual requests in a loop
for miner_id in miner_ids:
    resp = requests.get(f"https://rustchain.org/api/miners/{miner_id}")
    miners.append(resp.json())

# GOOD: Batch where possible, reuse session
session = create_api_session()
for miner_id in miner_ids:
    resp = session.get(f"https://rustchain.org/api/miners/{miner_id}")
    miners.append(resp.json())
```

### Response Compression

The RustChain API at `rustchain.org` supports gzip compression:

```python
session = requests.Session()
session.headers.update({"Accept-Encoding": "gzip, deflate"})
```

### Pagination Best Practices

```python
def list_miners(session, limit=50, offset=0):
    """Paginate through miner listings."""
    miners = []
    while True:
        resp = session.get(
            "https://rustchain.org/api/miners",
            params={"limit": limit, "offset": offset},
        )
        batch = resp.json()
        if not batch:
            break
        miners.extend(batch)
        offset += limit
    return miners
```

### Async Processing

```python
import asyncio
import aiohttp

async def fetch_miner_status(session, miner_id):
    """Fetch individual miner status asynchronously."""
    async with session.get(f"https://rustchain.org/api/miners/{miner_id}") as resp:
        return await resp.json()

async def fetch_all_miners(miner_ids):
    """Fetch multiple miner statuses concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_miner_status(session, mid) for mid in miner_ids]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

---

## Caching Strategies

### Multi-Layer Caching Architecture

```
Layer 1    Client-side     ->  Local Python cache / in-memory dict
Layer 2    API Cache       ->  Redis or Memcached
Layer 3    SQLite Cache    ->  Local query result cache
Layer 4    RustChain API   ->  Source of truth (rustchain.org)
```

### Redis Caching

```python
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0)

def get_wallet_balance(address: str) -> float:
    """Get wallet balance with caching."""
    cache_key = f"balance:{address}"

    # Try cache first
    cached = r.get(cache_key)
    if cached:
        return float(cached)

    # Cache miss - fetch from API
    resp = requests.get(f"https://rustchain.org/wallet/balance?address={address}")
    balance = resp.json()["balance"]

    # Cache with short TTL (balances change frequently)
    r.setex(cache_key, 10, str(balance))
    return balance
```

### Cache Invalidation Strategies

| Strategy | Use Case | TTL |
|----------|----------|-----|
| Time-based (TTL) | Wallet balances, miner status | 5-30s |
| Event-driven | Epoch settlement changes | On new epoch |
| Write-through | Critical data that must be fresh | Immediate |
| Cache-aside | General purpose, read-heavy | Varies |

### Recommended TTLs

```
Wallet balance:          10 seconds
Miner status:            30 seconds
Health endpoint:         60 seconds
Network statistics:      60 seconds
Miner leaderboard:       5 minutes
Epoch info:              30 seconds (active), 5 min (settled)
```

---

## Database Optimization

### SQLite Indexing

RustChain uses SQLite for local storage. Proper indexing is critical:

```sql
-- Critical indexes for miner data
CREATE INDEX IF NOT EXISTS idx_miners_id ON miners (miner_id);
CREATE INDEX IF NOT EXISTS idx_epochs_settled ON epochs (settled_at DESC);
CREATE INDEX IF NOT EXISTS idx_attestations_miner ON attestations (miner_id, epoch);

-- Partial index for active miners
CREATE INDEX IF NOT EXISTS idx_miners_active ON miners (miner_id)
WHERE active = 1;
```

### Query Optimization

```python
# BAD: N+1 queries
def get_miner_history_bad(miner_id):
    epoch_ids = get_epoch_ids(miner_id)  # Query 1
    results = []
    for eid in epoch_ids:
        results.append(get_attestation(eid))  # N queries!
    return results

# GOOD: Single optimized query
def get_miner_history(miner_id, limit=50):
    cursor = db.execute(
        """
        SELECT a.*, e.settled_at
        FROM attestations a
        JOIN epochs e ON a.epoch = e.id
        WHERE a.miner_id = ?
        ORDER BY e.settled_at DESC
        LIMIT ?
        """,
        (miner_id, limit),
    )
    return cursor.fetchall()
```

### WAL Mode for Concurrency

```python
# Enable WAL mode for better concurrent read performance
import sqlite3

conn = sqlite3.connect("rustchain.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
conn.execute("PRAGMA temp_store=MEMORY")
```

---

## Network Optimization

### API Endpoint Load Balancing

If running multiple API consumers, use nginx to balance:

```nginx
upstream rustchain_api {
    least_conn;
    server consumer1.internal:8080 weight=3;
    server consumer2.internal:8080 weight=3;
    server consumer3.internal:8080 weight=2;
}

server {
    listen 8080;
    location / {
        proxy_pass https://rustchain.org;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }
}
```

### Polling vs Webhooks

For miner monitoring, use efficient polling intervals:

```python
import time

# Recommended polling intervals
HEALTH_CHECK_INTERVAL = 60      # seconds
MINER_STATUS_INTERVAL = 30      # seconds
WALLET_BALANCE_INTERVAL = 60    # seconds
EPOCH_CHECK_INTERVAL = 15       # seconds (during epoch settlement)

def poll_miner_status(session):
    """Efficient polling loop for miner status."""
    last_epoch = None
    while True:
        resp = session.get("https://rustchain.org/api/miners")
        status = resp.json()

        current_epoch = status.get("current_epoch")
        if current_epoch != last_epoch:
            # Epoch changed - process settlement
            process_epoch_settlement(status)
            last_epoch = current_epoch

        time.sleep(MINER_STATUS_INTERVAL)
```

---

## Benchmarking & Profiling

### Load Testing with k6

```javascript
// load-test.js - Test RustChain API endpoints
import http from 'k6/http';
import { check } from 'k6';

export let options = {
    stages: [
        { duration: '30s', target: 50 },   // Ramp up
        { duration: '2m', target: 50 },     // Sustain
        { duration: '30s', target: 200 },   // Spike
        { duration: '1m', target: 200 },    // Sustain spike
        { duration: '30s', target: 0 },     // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],   // 95% under 500ms
        http_req_failed: ['rate<0.01'],     // < 1% failure rate
    },
};

export default function () {
    let res = http.get('https://rustchain.org/health');
    check(res, { 'status 200': (r) => r.status === 200 });
}
```

### Python Profiling

```bash
# Profile the miner with cProfile
python -m cProfile -o miner.prof miner.py

# Analyze the profile
python -m pstats miner.prof

# Memory profiling with memory_profiler
pip install memory_profiler
python -m memory_profiler miner.py
```

### Performance Metrics to Monitor

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| API response time (p50) | < 100ms | > 500ms |
| API response time (p99) | < 500ms | > 2000ms |
| Miner heartbeat interval | < 30s drift | > 60s drift |
| SQLite query time | < 10ms | > 50ms |
| Memory usage | < 200 MB | > 500 MB |
| CPU usage (sustained) | < 10% | > 50% |
| Epoch settlement time | < 5s | > 30s |
| Attestation success rate | > 99% | < 95% |

---

## Quick Wins Checklist

- [ ] Enable API response compression (gzip)
- [ ] Implement connection pooling with retries
- [ ] Add local caching for wallet balance and miner status
- [ ] Use SQLite WAL mode for concurrent reads
- [ ] Batch API requests where possible
- [ ] Tune Python environment variables
- [ ] Set up Docker health checks
- [ ] Monitor epoch settlement timing
- [ ] Configure appropriate cache TTLs per data type
- [ ] Set up monitoring and alerting for miner health

---

*This document is maintained by the RustChain community. Contributions welcome!*

*Last updated: 2026-05-17*
