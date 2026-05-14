# RustChain API Rate Limits

Documentation for all rate limits applied to RustChain public RPC endpoints. Understanding these limits helps developers build reliable applications and avoid service interruptions.

---

## Overview

RustChain public RPC endpoints enforce rate limits to ensure fair usage and network stability. Limits vary by endpoint category, authentication level, and request complexity.

### Rate Limit Headers

All responses include rate limit information in HTTP headers:

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Maximum requests allowed in the current window |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | Unix timestamp when the rate limit window resets |
| `Retry-After` | Seconds until retry is allowed (only on 429 responses) |

### Rate Limit Tiers

| Tier | Auth | Requests/min | Requests/day | Burst |
|---|---|---|---|---|
| Public | None | 60 | 10,000 | 10/sec |
| Registered | API Key | 300 | 100,000 | 30/sec |
| Premium | API Key + Plan | 1,200 | 500,000 | 100/sec |
| Enterprise | Custom | Custom | Custom | Custom |

---

## Endpoint-Specific Limits

### Blockchain Data (Read)

| Method | Public | Registered | Premium |
|---|---|---|---|
| `eth_chainId` | 120/min | 600/min | Unlimited |
| `eth_blockNumber` | 120/min | 600/min | Unlimited |
| `eth_getBalance` | 60/min | 300/min | 1,200/min |
| `eth_getTransactionCount` | 60/min | 300/min | 1,200/min |
| `eth_getBlockByNumber` | 60/min | 300/min | 1,200/min |
| `eth_getBlockByHash` | 60/min | 300/min | 1,200/min |
| `eth_getTransactionByHash` | 60/min | 300/min | 1,200/min |
| `eth_getTransactionReceipt` | 60/min | 300/min | 1,200/min |
| `eth_getStorageAt` | 60/min | 300/min | 1,200/min |
| `eth_getCode` | 60/min | 300/min | 1,200/min |
| `eth_call` | 60/min | 300/min | 1,200/min |
| `eth_estimateGas` | 30/min | 150/min | 600/min |

### Transaction Submission (Write)

| Method | Public | Registered | Premium |
|---|---|---|---|
| `eth_sendRawTransaction` | 10/min | 60/min | 300/min |
| `eth_sendTransaction` | 10/min | 60/min | 300/min |

### Event Logs & Filters

| Method | Public | Registered | Premium |
|---|---|---|---|
| `eth_getLogs` | 30/min | 150/min | 600/min |
| `eth_newFilter` | 10/min | 60/min | 300/min |
| `eth_getFilterChanges` | 60/min | 300/min | 1,200/min |
| `eth_uninstallFilter` | 60/min | 300/min | 1,200/min |
| `eth_newBlockFilter` | 10/min | 60/min | 300/min |
| `eth_newPendingTransactionFilter` | 10/min | 60/min | 300/min |

### Subscriptions (WebSocket)

| Method | Public | Registered | Premium |
|---|---|---|---|
| `eth_subscribe` (newHeads) | 5 concurrent | 20 concurrent | 100 concurrent |
| `eth_subscribe` (logs) | 5 concurrent | 20 concurrent | 100 concurrent |
| `eth_subscribe` (pendingTx) | 5 concurrent | 20 concurrent | 100 concurrent |
| `eth_unsubscribe` | 60/min | 300/min | 1,200/min |

### Batch Requests

| Parameter | Public | Registered | Premium |
|---|---|---|---|
| Max batch size | 10 requests | 50 requests | 200 requests |
| Batch rate limit | 10 batches/min | 60 batches/min | 300 batches/min |

---

## Rate Limit Error Responses

### HTTP 429 - Too Many Requests

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32005,
    "message": "rate limit exceeded",
    "data": {
      "rate": {
        "limit": 60,
        "used": 60,
        "remaining": 0,
        "reset": 1716134400
      }
    }
  }
}
```

### HTTP 503 - Service Unavailable (under heavy load)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32006,
    "message": "service temporarily unavailable",
    "data": {
      "retry_after": 30
    }
  }
}
```

---

## `eth_getLogs` Query Restrictions

`eth_getLogs` has additional restrictions due to its computational cost:

| Parameter | Limit |
|---|---|
| Max block range per query | 5,000 blocks (public), 50,000 (registered), 500,000 (premium) |
| Max addresses per filter | 100 |
| Max topics per filter | 20 |
| Max response size | 10 MB |

### Example: Valid getLogs Request

```json
{
  "jsonrpc": "2.0",
  "method": "eth_getLogs",
  "params": [{
    "fromBlock": "0x1000000",
    "toBlock": "0x1001388",
    "address": "0xContractAddress",
    "topics": ["0xEventSignature"]
  }],
  "id": 1
}
```

---

## Best Practices

### 1. Implement Exponential Backoff

```python
import time
import json
import urllib.request

def rpc_call(method, params, max_retries=5):
    for attempt in range(max_retries):
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": 1
            }
            req = urllib.request.Request(
                "https://rpc.rustchain.io",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = min(2 ** attempt, 60)  # Cap at 60 seconds
            time.sleep(wait)
```

### 2. Cache Blockchain Data

```javascript
const cache = new Map();
const CACHE_TTL = 15000; // 15 seconds (approx 1 block on RustChain)

async function getCachedBlockNumber() {
  const cached = cache.get('blockNumber');
  if (cached && Date.now() - cached.time < CACHE_TTL) {
    return cached.value;
  }
  const blockNumber = await provider.getBlockNumber();
  cache.set('blockNumber', { value: blockNumber, time: Date.now() });
  return blockNumber;
}
```

### 3. Use Batch Requests Wisely

```javascript
// ✅ Good: Batch related queries
const batch = new provider.BatchRequest();
batch.add(provider.getBlockNumber());
batch.add(provider.getBalance(address));
batch.add(provider.getTransactionCount(address));
const results = await batch.execute();

// ❌ Bad: Sending individual requests in a loop
for (const addr of addresses) {
  await provider.getBalance(addr); // Each is a separate request
}
```

### 4. Use WebSocket for Real-Time Data

Instead of polling `eth_blockNumber` every second:

```javascript
const ws = new WebSocket("wss://ws.rustchain.io");

ws.onopen = () => {
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    method: "eth_subscribe",
    params: ["newHeads"],
    id: 1
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("New block:", data.params.result.number);
};
```

### 5. Respect Rate Limit Headers

```python
import time

def respectful_request(method, params):
    response = rpc_call(method, params)
    remaining = int(response.headers.get('X-RateLimit-Remaining', '999'))
    if remaining < 10:
        reset_time = int(response.headers.get('X-RateLimit-Reset', '0'))
        sleep_time = max(reset_time - time.time(), 0) + 1
        time.sleep(sleep_time)
    return response
```

### 6. Get an API Key

For production applications, register for an API key to unlock higher rate limits:

1. Visit the RustChain developer portal
2. Create an account
3. Generate an API key
4. Include in requests: `?apikey=YOUR_KEY` or header `X-API-Key: YOUR_KEY`

---

## Monitoring Your Usage

### Check Current Limits

```bash
curl -s -I "https://rpc.rustchain.io" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  | grep -i ratelimit
```

### Usage Dashboard

Registered and premium users can monitor usage through the developer dashboard at `https://portal.rustchain.io/dashboard`.

---

## Error Handling Summary

| Status | Code | Meaning | Action |
|---|---|---|---|
| 200 | — | Success | Process response |
| 429 | -32005 | Rate limited | Back off, retry after `Retry-After` |
| 503 | -32006 | Service unavailable | Back off, retry after delay |
| 400 | -32600 | Invalid request | Fix request format |
| 401 | -32001 | Unauthorized | Check API key |
| 403 | -32002 | Forbidden | Check permissions |

---

*Last updated: 2025-05*
