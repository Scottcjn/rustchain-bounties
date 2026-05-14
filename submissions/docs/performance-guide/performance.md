# RustChain Performance Optimization Guide

> Maximize throughput, minimize latency, and scale your RustChain infrastructure effectively.

---

## Table of Contents

1. [Node Optimization](#node-optimization)
2. [API Optimization](#api-optimization)
3. [Caching Strategies](#caching-strategies)
4. [Database Optimization](#database-optimization)
5. [Network Optimization](#network-optimization)
6. [Benchmarking & Profiling](#benchmarking--profiling)

---

## Node Optimization

### Hardware Recommendations

| Component | Minimum | Recommended | High Performance |
|-----------|---------|-------------|------------------|
| CPU | 4 cores | 8 cores (3.5+ GHz) | 16+ cores (4.0+ GHz) |
| RAM | 8 GB | 32 GB | 64+ GB |
| Storage | 500 GB SSD | 1 TB NVMe SSD | 2+ TB NVMe RAID |
| Network | 100 Mbps | 1 Gbps | 10 Gbps |
| OS | Ubuntu 20.04 | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |

### Configuration Tuning

```toml
# rustchain-node.toml 鈥?Performance-tuned configuration

[server]
# Match worker threads to CPU cores
worker_threads = 8
# Increase max connections for high-throughput scenarios
max_connections = 10000
# Request timeout (increase for complex queries)
request_timeout = "30s"

[blockchain]
# Parallel block processing
parallel_verification = true
verification_threads = 4
# State pruning to manage disk usage
pruning_mode = "archive"  # or "recent" for lower disk usage
pruning_depth = 100000

[mempool]
# Increase for high-TPS scenarios
max_size = 100_000
# Transaction expiry
max_tx_age = "30m"
# Minimum gas price to prevent spam
min_gas_price = 1_000

[network]
# Optimize peer count for your bandwidth
max_peers = 50
min_peers = 10
# Batch gossip for efficiency
batch_gossip = true
batch_size = 100
# Compression
enable_compression = true
compression_level = 3  # 1-9, lower = faster
```

### System-Level Tuning (Linux)

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Network buffer optimization
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"

# Disable swap for consistent performance
swapoff -a

# I/O scheduler for NVMe
echo "none" > /sys/block/nvme0n1/queue/scheduler
```

### Memory Management

```rust
// Use memory pools for frequent allocations
use rustchain_sdk::pool::MemoryPool;

let pool = MemoryPool::new()
    .with_block_size(4096)
    .with_max_blocks(10000)
    .with_prealloc(1000);

// Reuse buffers instead of reallocating
let mut buffer = pool.acquire();
buffer.clear();
// ... use buffer ...
pool.release(buffer);
```

---

## API Optimization

### Connection Pooling

```rust
use rustchain_sdk::client::ConnectionPool;

let pool = ConnectionPool::builder()
    .max_connections(100)
    .min_idle_connections(10)
    .idle_timeout(Duration::from_secs(300))
    .connection_timeout(Duration::from_secs(5))
    .build()?;

let client = RustChainClient::from_pool(pool);
```

### Request Batching

```rust
// Instead of individual requests:
// BAD
for addr in addresses {
    let balance = client.get_balance(&addr).await?;
    balances.push(balance);
}

// GOOD 鈥?Batch requests
let balances = client.get_balances_batch(&addresses).await?;
```

### Response Compression

```rust
use rustchain_sdk::middleware::Compression;

let app = Router::new()
    .route("/api/v1/*", any(handler))
    .layer(Compression::new()
        .gzip()
        .deflate()
        .quality(6));
```

### Pagination Best Practices

```rust
// Use cursor-based pagination for large datasets
#[derive(Deserialize)]
struct ListTransactions {
    after: Option<String>,  // cursor (tx hash)
    limit: Option<u32>,     // max 100
}

async fn list_transactions(params: ListTransactions) -> Json<Vec<Transaction>> {
    let limit = params.limit.unwrap_or(50).min(100);
    let query = match params.after {
        Some(cursor) => tx_table.query().after(cursor),
        None => tx_table.query(),
    };
    
    Json(query.limit(limit).execute().await)
}
```

### Async Processing

```rust
// Use background workers for heavy operations
use rustchain_sdk::queue::TaskQueue;

#[derive(Serialize)]
struct IndexTask {
    block_range: Range<u64>,
    priority: u8,
}

let queue = TaskQueue::new("block-indexing", redis_url)
    .workers(4)
    .retry_limit(3)
    .build()?;

// Enqueue heavy work
queue.push(IndexTask {
    block_range: 1000000..1001000,
    priority: 1,
}).await?;
```

---

## Caching Strategies

### Multi-Layer Caching Architecture

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?  Client     鈹? 鈫?Browser/SDK-level cache
鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?  CDN/Edge   鈹? 鈫?Static responses, public data
鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?  API Cache  鈹? 鈫?In-memory (Redis/Memcached)
鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?  DB Cache   鈹? 鈫?Query result cache
鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?  Blockchain  鈹? 鈫?Source of truth
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

### Redis Caching

```rust
use redis::AsyncCommands;

struct CachedBlockchainService {
    client: RustChainClient,
    redis: redis::aio::Connection,
}

impl CachedBlockchainService {
    async fn get_balance(&mut self, address: &str) -> Result<u64> {
        let cache_key = format!("balance:{}", address);
        
        // Try cache first
        if let Some(cached) = self.redis.get::<Option<String>>(&cache_key).await? {
            return Ok(cached.parse::<u64>()?);
        }
        
        // Cache miss 鈥?fetch from chain
        let balance = self.client.get_balance(address).await?;
        
        // Cache with TTL (balances change frequently)
        self.redis.set_ex(&cache_key, balance.to_string(), 10).await?;
        
        Ok(balance)
    }
    
    async fn get_transaction(&mut self, tx_hash: &str) -> Result<Transaction> {
        let cache_key = format!("tx:{}", tx_hash);
        
        // Confirmed transactions are immutable 鈥?long TTL
        if let Some(cached) = self.redis.get::<Option<String>>(&cache_key).await? {
            return Ok(serde_json::from_str(&cached)?);
        }
        
        let tx = self.client.get_transaction(tx_hash).await?;
        
        if tx.confirmed {
            // Immutable 鈥?cache for 24 hours
            self.redis.set_ex(&cache_key, serde_json::to_string(&tx)?, 86400).await?;
        } else {
            // Pending 鈥?short TTL
            self.redis.set_ex(&cache_key, serde_json::to_string(&tx)?, 5).await?;
        }
        
        Ok(tx)
    }
}
```

### Cache Invalidation Strategies

| Strategy | Use Case | TTL |
|----------|----------|-----|
| Time-based (TTL) | Balances, pending transactions | 5-30s |
| Event-driven | Account state changes | On new block |
| Write-through | Critical data that must be fresh | Immediate |
| Cache-aside | General purpose, read-heavy | Varies |

### Recommended TTLs

```
Balance queries:         10 seconds
Transaction status:      5 seconds (pending), 24h (confirmed)
Block data:              1 hour (confirmed blocks)
Smart contract state:    30 seconds
Token metadata:          1 hour
Network statistics:      60 seconds
Gas price estimates:     15 seconds
Validator info:          5 minutes
```

---

## Database Optimization

### Indexing Strategy

```sql
-- Critical indexes for blockchain data
CREATE INDEX idx_transactions_hash ON transactions (hash);
CREATE INDEX idx_transactions_from ON transactions (from_address, block_number DESC);
CREATE INDEX idx_transactions_to ON transactions (to_address, block_number DESC);
CREATE INDEX idx_transactions_block ON transactions (block_number DESC);
CREATE INDEX idx_blocks_number ON blocks (number DESC);
CREATE INDEX idx_blocks_hash ON blocks (hash);

-- Partial index for pending transactions
CREATE INDEX idx_transactions_pending ON transactions (hash)
WHERE confirmed = false;
```

### Query Optimization

```rust
// BAD: N+1 queries
async fn get_account_history_bad(address: &str) -> Vec<Transaction> {
    let tx_hashes = get_tx_hashes(address).await; // Query 1
    let mut txs = Vec::new();
    for hash in tx_hashes {
        txs.push(get_transaction(&hash).await); // N queries!
    }
    txs
}

// GOOD: Single optimized query
async fn get_account_history(address: &str, limit: u32) -> Vec<Transaction> {
    sqlx::query_as!(
        Transaction,
        "SELECT * FROM transactions 
         WHERE from_address = $1 OR to_address = $1
         ORDER BY block_number DESC, tx_index DESC
         LIMIT $2",
        address, limit
    )
    .fetch_all(&pool)
    .await
}
```

### Partitioning

For large-scale deployments, partition tables by block number ranges:

```sql
-- Partition transactions by block range (e.g., 1M blocks per partition)
CREATE TABLE transactions (
    hash TEXT NOT NULL,
    block_number BIGINT NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    value BIGINT NOT NULL,
    data BYTEA,
    PRIMARY KEY (hash, block_number)
) PARTITION BY RANGE (block_number);

CREATE TABLE transactions_0 PARTITION OF transactions
    FOR VALUES FROM (0) TO (1000000);
CREATE TABLE transactions_1 PARTITION OF transactions
    FOR VALUES FROM (1000000) TO (2000000);
-- Continue as needed...
```

---

## Network Optimization

### RPC Endpoint Load Balancing

```nginx
upstream rustchain_rpc {
    least_conn;
    server node1.internal:8545 weight=3;
    server node2.internal:8545 weight=3;
    server node3.internal:8545 weight=2;
    server node4.internal:8545 weight=1 backup;
}

server {
    listen 8545;
    location / {
        proxy_pass http://rustchain_rpc;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }
}
```

### WebSocket vs HTTP

Use WebSocket for real-time data, HTTP for one-off queries:

```rust
// Real-time: WebSocket
let ws = RustChainClient::websocket("wss://rpc.rustchain.io/ws").await?;
let mut stream = ws.subscribe_new_blocks().await?;
while let Some(block) = stream.next().await {
    process_block(block)?;
}

// One-off: HTTP
let client = RustChainClient::http("https://rpc.rustchain.io")?;
let balance = client.get_balance("rc1q...").await?;
```

---

## Benchmarking & Profiling

### Load Testing with k6

```javascript
// load-test.js
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
    let res = http.get('https://your-node.example/api/v1/block/latest');
    check(res, { 'status 200': (r) => r.status === 200 });
}
```

### Rust Profiling

```bash
# Build with profiling symbols
cargo build --release --features profiling

# CPU profiling with perf
perf record -g ./target/release/rustchain-node
perf report

# Flame graph generation
perf script | stackcollapse-perf.pl | flamegraph.pl > flamegraph.svg

# Memory profiling with valgrind
valgrind --tool=massif ./target/release/rustchain-node
ms_print massif.out.*
```

### Performance Metrics to Monitor

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Block processing time | < 100ms | > 500ms |
| API response time (p50) | < 50ms | > 200ms |
| API response time (p99) | < 500ms | > 2000ms |
| Memory usage | < 70% of total | > 85% |
| CPU usage (sustained) | < 60% | > 80% |
| Disk I/O wait | < 5ms | > 20ms |
| Peer propagation latency | < 100ms | > 500ms |
| Mempool size | < 50% capacity | > 80% |

---

## Quick Wins Checklist

- [ ] Enable response compression (gzip/brotli)
- [ ] Implement connection pooling
- [ ] Add Redis caching for hot data
- [ ] Use cursor-based pagination
- [ ] Batch API requests where possible
- [ ] Tune system ulimits and network buffers
- [ ] Set up load balancing for RPC endpoints
- [ ] Enable parallel block verification
- [ ] Configure appropriate cache TTLs per data type
- [ ] Set up monitoring and alerting

---

*This document is maintained by the RustChain community. Contributions welcome!*

*Last updated: 2025-01-15*
