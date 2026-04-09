# RustChain API Reference

> All public API endpoints for the RustChain node (v2.2.1-rip200).
> Base URL: `https://50.28.86.131`
> Authentication: None (public endpoints)

---

## Table of Contents

1. [Health & Network Status](#1-health--network-status)
2. [Miners](#2-miners)
3. [Blocks & Chain](#3-blocks--chain)
4. [Epoch Data](#4-epoch-data)
5. [Wallet & Transactions](#5-wallet--transactions)

---

## 1. Health & Network Status

### GET /health

Returns the current health status of the attestation node.

```bash
curl -sk https://50.28.86.131/health
```

**Response:**

```json
{
  "ok": true,
  "backup_age_hours": 8.94,
  "db_rw": true,
  "tip_age_slots": 0,
  "uptime_s": 154336,
  "version": "2.2.1-rip200"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | Node is healthy |
| `backup_age_hours` | float | Hours since last backup |
| `db_rw` | boolean | Database read/write status |
| `tip_age_slots` | int | Age of the chain tip (slots) |
| `uptime_s` | int | Node uptime in seconds |
| `version` | string | Protocol version |

---

## 2. Miners

### GET /api/miners

Returns a paginated list of all active miners on the network.

```bash
curl -sk https://50.28.86.131/api/miners
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 100 | Max results per page |
| `offset` | int | 0 | Pagination offset |

**Response:**

```json
{
  "miners": [
    {
      "miner": "power8-s824-sophia",
      "hardware_type": "PowerPC (Vintage)",
      "device_family": "PowerPC",
      "device_arch": "POWER8",
      "antiquity_multiplier": 2.0,
      "entropy_score": 0.0,
      "first_attest": 1774820803,
      "last_attest": 1775736931
    },
    {
      "miner": "nox-ventures",
      "hardware_type": "x86-64 (Modern)",
      "device_family": "x86",
      "device_arch": "modern",
      "antiquity_multiplier": 0.8,
      "entropy_score": 0.0,
      "first_attest": 1774820604,
      "last_attest": 1775736950
    }
  ],
  "pagination": {
    "total": 13,
    "limit": 100,
    "offset": 0,
    "count": 13
  }
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `miner` | string | Unique miner identifier |
| `hardware_type` | string | Human-readable hardware classification |
| `device_family` | string | CPU family (PowerPC, x86, ARM, etc.) |
| `device_arch` | string | Specific architecture |
| `antiquity_multiplier` | float | Current mining multiplier (0.8 - 3.5+) |
| `entropy_score` | float | Entropy contribution score |
| `first_attest` | unix timestamp | First attestation time |
| `last_attest` | unix timestamp | Most recent attestation |

### GET /api/miners/:name

Get details for a specific miner.

```bash
curl -sk https://50.28.86.131/api/miners/power8-s824-sophia
```

---

## 3. Blocks & Chain

### GET /api/block/:hash

Get details for a specific block by hash.

```bash
curl -sk https://50.28.86.131/api/block/<hash>
```

### GET /api/blocks

Get a list of recent blocks.

```bash
curl -sk "https://50.28.86.131/api/blocks?limit=20&offset=0"
```

### GET /api/tx/:txid

Get details for a specific transaction.

```bash
curl -sk https://50.28.86.131/api/tx/<txid>
```

---

## 4. Epoch Data

### GET /api/epoch

Returns current epoch information. *(Note: endpoint may require specific node configuration)*

```bash
curl -sk https://50.28.86.131/api/epoch
```

---

## 5. Wallet & Transactions

### POST /api/wallet/create

Create a new wallet.

```bash
curl -sk -X POST https://50.28.86.131/api/wallet/create \
  -H "Content-Type: application/json"
```

### GET /api/balance/:address

Get the balance for a specific address.

```bash
curl -sk https://50.28.86.131/api/balance/<address>
```

**Response:**

```json
{
  "address": "RTCxxxxxxx",
  "balance": 123.456,
  "unit": "RTC"
}
```

### POST /api/send

Send RTC to another address.

```bash
curl -sk -X POST https://50.28.86.131/api/send \
  -H "Content-Type: application/json" \
  -d '{"to": "<recipient_address>", "amount": 10.5, "from": "<sender_address>"}'
```

**Response:**

```json
{
  "txid": "<transaction_id>",
  "status": "submitted",
  "fee": 0.001
}
```

---

## API Error Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `404` | Resource not found |
| `422` | Invalid parameters |
| `429` | Rate limited |
| `500` | Internal server error |
| `503` | Node unavailable (e.g., during epoch settlement) |

---

## Rate Limits

- Public read endpoints: **60 requests/minute**
- Write endpoints: **10 requests/minute**
- Burst allowance: 10 requests

---

## WebSocket (Real-time)

For real-time updates, connect to the WebSocket endpoint:

```
wss://50.28.86.131/ws
```

Example subscription to new blocks:

```javascript
const ws = new WebSocket('wss://50.28.86.131/ws');
ws.send(JSON.stringify({ action: 'subscribe', channel: 'new_blocks' }));
ws.onmessage = (event) => {
  console.log('New block:', JSON.parse(event.data));
};
```

---

## Example: Complete Miner Query

```bash
#!/bin/bash
# Fetch all active miners, sort by antiquity multiplier

echo "=== RustChain Active Miners ==="
echo ""

curl -sk https://50.28.86.131/api/miners | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
miners = data['miners']
miners.sort(key=lambda x: x['antiquity_multiplier'], reverse=True)
print(f'Total miners: {len(miners)}\n')
print(f'{\"Miner\":<35} {\"Multiplier\":<12} {\"Hardware Type\"}')
print('-' * 80)
for m in miners:
    print(f'{m[\"miner\"]:<35} {m[\"antiquity_multiplier\"]:<12.3f} {m[\"hardware_type\"]}')
"
```

Output:
```
=== RustChain Active Miners ===
Total miners: 13

Miner                              Multiplier   Hardware Type
--------------------------------------------------------------------------------
power8-s824-sophia                2.000        PowerPC (Vintage)
m2-mac-mini-sophia                1.200        Apple Silicon (Modern)
claw-qinlingrongdeMacBook-Pro     1.200        Apple Silicon M2
...
```
