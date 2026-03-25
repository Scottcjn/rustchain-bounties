# RustChain Node REST API Reference

**Node Version:** 2.2.1-rip200  
**Base URL:** `https://50.28.86.131`  
**TLS:** Self-signed certificate. Use `curl -k` or `requests(..., verify=False)` for development.  
**Protocol:** REST/JSON  
**Rate Limits:** HTTP 429 when exceeded; implement exponential backoff with jitter.

---

## Overview

The RustChain node exposes a REST API for querying chain state, managing wallets, submitting attestations, and interacting with the epoch/lottery system. All endpoints return JSON.

This document covers the complete API surface available at the primary node. The MCP server (`integrations/rustchain-mcp/`) wraps all these endpoints — see `docs/MCP_SERVER_TOOL_REFERENCE.md` for the MCP-level documentation.

---

## Base Request Conventions

- **Base URL:** `https://50.28.86.131`
- **Authentication:** None (public read endpoints); wallet ID used as identifier
- **Content-Type:** `application/json` for POST/PUT requests
- **SSL:** The node uses a self-signed certificate. In production, install the node's CA cert; in development use `-k`/`verify=False`
- **Rate Limiting:** HTTP 429 Too Many Requests. On 429, retry with exponential backoff starting at 1 second, doubling up to 60 seconds max
- **Error Format:** All errors return a JSON body with an `error` field:
  ```json
  {
    "error": "error_code_slug",
    "message": "Human-readable description",
    "ttl_s": 600
  }
  ```

---

## Node Endpoints

---

### `GET /health`

Returns the operational health status of the RustChain node.

**Request:**
```bash
curl -sk https://50.28.86.131/health
```

**Response:**
```json
{
  "ok": true,
  "version": "2.2.1-rip200",
  "uptime_s": 24000,
  "db_rw": true,
  "backup_age_hours": 0.08,
  "tip_age_slots": 0
}
```

| Field | Type | Description |
|---|---|---|
| `ok` | `boolean` | `true` if node is healthy and serving requests |
| `version` | `string` | Software version string |
| `uptime_s` | `integer` | Node uptime in seconds |
| `db_rw` | `boolean` | Database read/write status. `false` indicates read-only mode (backup mode) |
| `backup_age_hours` | `number` | Hours since last Ergo anchor backup was written |
| `tip_age_slots` | `integer` | How many slots behind the chain tip the node is (0 = fully synced) |

**Error codes:** None (always returns 200 if the node is running, even in degraded mode)

---

### `GET /epoch`

Returns the current epoch state and reward information.

**Request:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Response:**
```json
{
  "epoch": 73,
  "slot": 10554,
  "enrolled_miners": 12,
  "epoch_pot": 1.5,
  "blocks_per_epoch": 144
}
```

| Field | Type | Description |
|---|---|---|
| `epoch` | `integer` | Current epoch number (increments from genesis) |
| `slot` | `integer` | Absolute slot counter since genesis (always increasing) |
| `enrolled_miners` | `integer` | Number of miners enrolled for the current epoch |
| `epoch_pot` | `number` | Total RTC reward pool for this epoch (in RTC) |
| `blocks_per_epoch` | `integer` | Protocol constant: expected number of blocks per full epoch |

---

### `GET /api/miners`

Returns all active miners currently enrolled with the RustChain network.

**Request:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Response:**
```json
[
  {
    "miner": "victus-x86-scott",
    "hardware_type": "x86_64",
    "device_arch": "zen3",
    "device_family": "amd-ryzen-5000",
    "antiquity_multiplier": 1.0,
    "last_attest": 1771038696,
    "entropy_score": 0.87
  },
  {
    "miner": "mac-mini-m2-dong",
    "hardware_type": "arm64",
    "device_arch": "m2",
    "device_family": "apple-silicon-m2",
    "antiquity_multiplier": 1.5,
    "last_attest": 1771038660,
    "entropy_score": 0.94
  }
]
```

| Field | Type | Description |
|---|---|---|
| `miner` | `string` | Miner/wallet identifier |
| `hardware_type` | `string` | CPU architecture (`x86_64`, `arm64`, `ppc64`, etc.) |
| `device_arch` | `string` | Microarchitecture identifier (`zen3`, `m2`, `g4`, etc.) |
| `device_family` | `string` | Marketing/hardware family name |
| `antiquity_multiplier` | `number` | Reward multiplier applied to this miner (1.0–4.0+) |
| `last_attest` | `integer` | Unix timestamp of last successful attestation |
| `entropy_score` | `number` | Entropy quality of last attestation (0.0–1.0) |

---

### `GET /wallet/balance`

Queries the RTC balance for a miner/wallet ID.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `miner_id` | `string` | ✅ Yes | Miner or wallet identifier to query |

**Request:**
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=victus-x86-scott"
```

**Response:**
```json
{
  "miner_id": "victus-x86-scott",
  "amount_rtc": 265.420827,
  "amount_i64": 265420827
}
```

| Field | Type | Description |
|---|---|---|
| `miner_id` | `string` | The queried miner ID |
| `amount_rtc` | `number` | Balance in RTC (decimal, 6 decimal places precision) |
| `amount_i64` | `integer` | Balance in raw integer units (1 RTC = 1,000,000 units) |

**Notes:**
- Unknown `miner_id` returns `amount_rtc: 0, amount_i64: 0` (not an error)
- `amount_i64` is the authoritative value; `amount_rtc` is a convenience conversion

---

### `POST /wallet/transfer/signed`

Broadcasts a pre-signed RTC transfer transaction. The node does **not** sign transactions — the client must sign externally with the sender's Ed25519 private key and provide the raw signed transaction bytes.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "signed_tx_hex": "7b22767273696f6e223a312c2273656e646572223a22...",
  "broadcast": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `signed_tx_hex` | `string` | ✅ Yes | Hex-encoded signed transaction bytes |
| `broadcast` | `boolean` | No | `true` (default) to broadcast; `false` to validate only (dry run) |

**Response (success):**
```json
{
  "tx_id": "tx_7f3a9b2ce14d...",
  "status": "confirmed",
  "fee_rtc": 0.001,
  "block_slot": 10580
}
```

| Field | Type | Description |
|---|---|---|
| `tx_id` | `string` | Unique transaction identifier |
| `status` | `string` | `pending` (not yet in a block), `confirmed` (in a block), `rejected` (invalid) |
| `fee_rtc` | `number` | Transaction fee charged in RTC |
| `block_slot` | `integer` | Slot number of the block containing this tx (only if confirmed) |

**Response (validation-only mode, `broadcast: false`):**
```json
{
  "tx_id": "tx_7f3a9b2ce14d...",
  "status": "validated",
  "fee_rtc": 0.001,
  "valid": true,
  "signatures_valid": true
}
```

**Error Response (invalid signature):**
```json
{
  "error": "invalid_signature",
  "message": "Transaction signature verification failed",
  "tx_id": "tx_7f3a9b2ce14d..."
}
```

**Error Response (insufficient balance):**
```json
{
  "error": "insufficient_balance",
  "available_rtc": 5.25,
  "requested_rtc": 10.0
}
```

---

### `GET /stats`

Returns aggregated network statistics for the entire RustChain network.

**Request:**
```bash
curl -sk https://50.28.86.131/stats
```

**Response:**
```json
{
  "total_miners": 47,
  "total_rtc": 14280.5,
  "avg_attestation_time_ms": 342,
  "total_attestations": 18934,
  "active_epochs": 73
}
```

| Field | Type | Description |
|---|---|---|
| `total_miners` | `integer` | Total registered miners (active + historical) |
| `total_rtc` | `number` | Total RTC minted/distributed across all time |
| `avg_attestation_time_ms` | `number` | Network-average attestation round-trip time in milliseconds |
| `total_attestations` | `integer` | Cumulative total successful attestation count |
| `active_epochs` | `integer` | Current active epoch number |

---

## Attestation Endpoints

These are the primary endpoints used by the miner client during the RIP-200 attestation flow.

---

### `POST /attest/challenge`

Requests a new attestation challenge from the node. The challenge consists of a server-side nonce and server timestamp, which the miner will use to build a proof of hardware possession.

**Request Body:** Empty object or omit body:
```bash
curl -sk -X POST https://50.28.86.131/attest/challenge \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**Response:**
```json
{
  "nonce": "a3f8c2d1e9b4f7a6...",
  "server_time": 1771038696,
  "expires_at": 1771038996
}
```

| Field | Type | Description |
|---|---|---|
| `nonce` | `string` | Random challenge nonce (hex-encoded, at least 32 bytes) |
| `server_time` | `integer` | Server Unix timestamp at time of challenge generation |
| `expires_at` | `integer` | Unix timestamp after which this challenge is invalid (server_time + 300s) |

**Error Response (no available slot):**
```json
{
  "error": "challenge_rate_limited",
  "ttl_s": 60,
  "message": "Too many challenge requests; wait before retrying"
}
```

> ⏱️ **Timing:** Challenges expire after 300 seconds. Complete fingerprinting and submit before `expires_at`. The miner script handles this automatically.

---

### `POST /attest/submit`

Submits a completed attestation. The body must include the hardware fingerprint data computed by the miner.

**Request Body:**
```json
{
  "miner_id": "victus-x86-scott",
  "nonce": "a3f8c2d1e9b4f7a6...",
  "fingerprint": {
    "cache_timing": {
      "probe_results": [12.4, 13.1, 12.8, 45.2, 46.1, 44.9],
      "variance_ppm": 12000
    },
    "clock_drift": {
      "drift_ppm": 3.2,
      "direction": "fast",
      "ntp_offset_ms": 12
    },
    "simd": {
      "extensions": ["sse4.2", "avx2", "fma"],
      "avx2_throughput_ops_per_cycle": 8.0
    },
    "thermal": {
      "idle_celsius": 38.5,
      "peak_celsius": 71.2,
      "cool_down_rate_celsius_per_sec": 0.8
    }
  },
  "entropy_score": 0.91
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `miner_id` | `string` | ✅ Yes | Miner identifier |
| `nonce` | `string` | ✅ Yes | Challenge nonce from `/attest/challenge` |
| `fingerprint` | `object` | ✅ Yes | Hardware fingerprint data |
| `fingerprint.cache_timing` | `object` | ✅ Yes | Cache timing probe results |
| `fingerprint.clock_drift` | `object` | ✅ Yes | Clock drift measurement |
| `fingerprint.simd` | `object` | ✅ Yes | SIMD feature detection |
| `fingerprint.thermal` | `object` | No | Thermal profile (if enabled) |
| `entropy_score` | `number` | ✅ Yes | Combined entropy quality (0.0–1.0) |

**Response (success):**
```json
{
  "attestation_id": "att_f9b3c2a1e8d4...",
  "miner_id": "victus-x86-scott",
  "entropy_score": 0.91,
  "attested_at_slot": 10554,
  "next_challenge_available_at": 1771038996
}
```

**Error Response (nonce expired):**
```json
{
  "error": "nonce_expired",
  "message": "Challenge nonce has expired",
  "server_time": 1771039001
}
```

**Error Response (signature mismatch):**
```json
{
  "error": "fingerprint_invalid",
  "message": "Hardware fingerprint does not match expected pattern for this miner"
}
```

---

### `GET /lottery/eligibility`

Checks whether a miner is eligible for the current epoch's reward lottery.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `miner_id` | `string` | ✅ Yes | Miner identifier to check |

**Request:**
```bash
curl -sk "https://50.28.86.131/lottery/eligibility?miner_id=victus-x86-scott"
```

**Response:**
```json
{
  "miner_id": "victus-x86-scott",
  "eligible": true,
  "last_attestation_epoch": 72,
  "current_epoch": 73,
  "tickets": 2,
  "effective_multiplier": 1.15
}
```

| Field | Type | Description |
|---|---|---|
| `miner_id` | `string` | The queried miner ID |
| `eligible` | `boolean` | Whether miner qualifies for the current epoch lottery |
| `last_attestation_epoch` | `integer` | Epoch number of most recent successful attestation |
| `current_epoch` | `integer` | The epoch being queried |
| `tickets` | `integer` | Number of lottery tickets earned (higher entropy = more tickets) |
| `effective_multiplier` | `number` | Combined multiplier (hardware × entropy bonus) applied to ticket weight |

**Ineligible response:**
```json
{
  "miner_id": "victus-x86-scott",
  "eligible": false,
  "reason": "no_recent_attestation",
  "last_attestation_epoch": 70,
  "current_epoch": 73,
  "tickets": 0
}
```

---

## Epoch Endpoints

---

### `POST /epoch/enroll`

Enrolls a miner for the current epoch. Enrollment requires a successful attestation in the current or prior epoch.

**Request Body:**
```json
{
  "miner_id": "victus-x86-scott"
}
```

**Response (success):**
```json
{
  "enrolled": true,
  "miner_id": "victus-x86-scott",
  "epoch": 73,
  "enrolled_at_slot": 10554
}
```

**Error Response (no recent attestation):**
```json
{
  "error": "no_recent_attestation",
  "message": "Miner must attest successfully before enrolling in epoch 73",
  "ttl_s": 600,
  "last_attest_epoch": 70
}
```

> **Note:** If you receive `no_recent_attestation`, wait up to 10 minutes for your attestation to propagate to the enrollment system, then retry. The `ttl_s` value indicates when you should retry.

---

## Explorer Endpoint

---

### `GET /explorer`

Returns an HTTP redirect to the block explorer web UI.

**Request:**
```bash
curl -sk -I https://50.28.86.131/explorer
```

**Response:**
```
HTTP/1.1 302 Found
Location: https://explorer.rustchain.io/?node=https://50.28.86.131
```

---

## Rate Limiting

The node enforces rate limits on write operations. Read operations (`GET /health`, `GET /epoch`, `GET /api/miners`, `GET /stats`) have generous limits.

| Endpoint Pattern | Limit |
|---|---|
| `GET /*` (read) | 120 req/min per IP |
| `POST /attest/challenge` | 6 req/min per miner_id |
| `POST /attest/submit` | 6 req/min per miner_id |
| `POST /wallet/transfer/signed` | 10 req/min per wallet |
| `POST /epoch/enroll` | 3 req/min per miner_id |

**429 Response:**
```json
{
  "error": "rate_limited",
  "retry_after_s": 30,
  "message": "Too many requests"
}
```

**Retry strategy:**
```python
import time, random

def request_with_retry(fn, max_retries=5):
    for attempt in range(max_retries):
        response = fn()
        if response.status_code == 429:
            wait = min(60, (2 ** attempt) + random.uniform(0, 1))
            print(f"Rate limited. Retrying in {wait:.1f}s...")
            time.sleep(wait)
            continue
        return response
    raise RuntimeError(f"Max retries exceeded for {fn}")
```

---

## Error Reference

| Error Code | HTTP Status | Description |
|---|---|---|
| `nonce_expired` | 400 | Attestation challenge nonce has expired |
| `invalid_signature` | 400 | Transaction signature is invalid |
| `fingerprint_invalid` | 400 | Hardware fingerprint rejected by the node |
| `insufficient_balance` | 400 | Wallet has insufficient RTC for transfer |
| `no_recent_attestation` | 400 | Miner has not attested recently enough for enrollment |
| `challenge_rate_limited` | 429 | Too many challenge requests; back off and retry |
| `rate_limited` | 429 | Generic rate limit exceeded |
| `unknown_miner` | 404 | Miner ID not found in the registry |
| `node_not_synced` | 503 | Node is behind the chain tip (wait for sync) |

---

## WebSocket (Future)

Real-time subscription to chain events via WebSocket is planned for v2.3.0. Planned subscriptions include:
- `epoch.tick` — fires at the start of each new epoch
- `miner.attested` — fires when any miner successfully attests
- `miner.enrolled` — fires when a miner enrolls in an epoch
- `lottery.drawn` — fires when the lottery for an epoch completes
