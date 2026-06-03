# RustChain API Reference

> Last updated: 2025-04-03

This document describes the public endpoints available for interacting with RustChain nodes and services.

## Base URL

All API endpoints are served over HTTPS. The primary RustChain block explorer API is:

```
https://explorer.rustchain.org/api
```

Attestation nodes also expose a read-only API:

```
http://<node-ip>:31415/api
```

## Authentication

Some endpoints require an API key. To obtain one, join the [Discord](https://discord.gg/VqVVS2CW9Q) and request a key in the #dev channel.

---

## 1. Block Endpoints

### `GET /api/block/latest`

Returns the current tip block.

**Example:**

```bash
curl https://explorer.rustchain.org/api/block/latest
```

**Response:**

```json
{
  "height": 123456,
  "hash": "0xabc...",
  "timestamp": 1712000000,
  "miner": "0xdead...",
  "tx_count": 5
}
```

### `GET /api/block/{height}`

Returns block details by height.

**Example:**

```bash
curl https://explorer.rustchain.org/api/block/100000
```

---

## 2. Transaction Endpoints

### `GET /api/tx/{hash}`

Returns transaction details.

**Example:**

```bash
curl https://explorer.rustchain.org/api/tx/0x123...
```

**Response:**

```json
{
  "hash": "0x123...",
  "from": "0xabc...",
  "to": "0xdef...",
  "value": "10.5",
  "fee": "0.001",
  "confirmations": 42
}
```

### `POST /api/tx/send`

Broadcasts a signed transaction.

**Request Body:**

```json
{
  "raw_tx": "0x...signed_hex..."
}
```

---

## 3. Node Status Endpoints

### `GET /api/node/health`

Returns health information for all official attestation nodes.

**Example:**

```bash
curl https://explorer.rustchain.org/api/node/health
```

**Response:**

```json
[
  {
    "ip": "50.28.86.131",
    "status": "online",
    "version": "1.0.0",
    "uptime": "12h34m",
    "db_rw": true,
    "tip_age_sec": 2
  },
  {
    "ip": "50.28.86.153",
    "status": "online",
    "version": "1.0.0",
    "uptime": "12h32m",
    "db_rw": true,
    "tip_age_sec": 1
  },
  {
    "ip": "76.8.228.245",
    "status": "online",
    "version": "1.0.0",
    "uptime": "12h30m",
    "db_rw": true,
    "tip_age_sec": 3
  }
]
```

### `GET /api/node/{ip}/peers`

Returns peers of a specific node.

---

## 4. Account Endpoints

### `GET /api/account/{address}`

Returns balance and transaction history.

**Example:**

```bash
curl https://explorer.rustchain.org/api/account/0xdeadbeef...
```

---

## 5. Explorer Endpoints (Web UI)

| Endpoint | Description |
|----------|-------------|
| `/` | Homepage with latest blocks |
| `/block/{height}` | Block detail page |
| `/tx/{hash}` | Transaction detail page |
| `/address/{addr}` | Address detail page |
| `/mempool` | Pending transactions |
| `/search?q=...` | Search by block/tx/address |

---

## Error Codes

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 400 | Bad request (invalid params) |
| 404 | Resource not found |
| 500 | Internal server error |

---

*This document is part of the [RustChain Documentation Sprint](https://github.com/Scottcjn/rustchain-bounties/issues/72).*