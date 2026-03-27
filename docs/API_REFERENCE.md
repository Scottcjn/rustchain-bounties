# RustChain v2 API Reference

> **Base URL:** `https://50.28.86.131`
> **Version:** 2.2.1-rip200
> **Protocol:** HTTPS (self-signed cert, use `-k` with curl)

---

## Table of Contents

1. [GET /api/stats](#get-apistats) — System statistics
2. [GET /health](#get-health) — Node health check
3. [GET /epoch](#get-epoch) — Current epoch information
4. [GET /balance/{miner_pk}](#get-balanceminer_pk) — Miner balance
5. [POST /attest/challenge](#post-attestchallenge) — Get attestation challenge
6. [POST /attest/submit](#post-attestsubmit) — Submit attestation
7. [POST /epoch/enroll](#post-epochenroll) — Enroll in epoch
8. [GET /withdraw/history/{miner_pk}](#get-withdrawhistoryminer_pk) — Withdrawal history
9. [POST /withdraw/register](#post-withdrawregister) — Register withdrawal key
10. [POST /withdraw/request](#post-withdrawrequest) — Request withdrawal
11. [GET /withdraw/status/{withdrawal_id}](#get-withdrawstatuswithdrawal_id) — Withdrawal status
12. [GET /metrics](#get-metrics) — Prometheus metrics

---


## GET /api/stats

Returns system-wide statistics including chain info, block times, and network metrics.

### Example
```bash
curl -sk https://50.28.86.131/api/stats
```

### Response (200)
```json
{
    "block_time": 600,
    "chain_id": "rustchain-mainnet-v2",
    "epoch": 104,
    "features": [
        "RIP-0005",
        "RIP-0008",
        "RIP-0009",
        "RIP-0142",
        "RIP-0143",
        "RIP-0144"
    ],
    "pending_withdrawals": 0,
    "security": [
        "no_mock_sigs",
        "mandatory_admin_key",
        "replay_protection",
        "validated_json"
    ],
    "total_balance": 412913.417317,
    "total_miners": 487,
    "version": "2.2.1-security-hardened"
}
```

---

## GET /health

Quick node health check. Returns uptime, version, database status, and tip information.

### Example
```bash
curl -sk https://50.28.86.131/health
```

### Response (200)
```json
{
    "backup_age_hours": 8.202856836782562,
    "db_rw": true,
    "ok": true,
    "tip_age_slots": 0,
    "uptime_s": 31284,
    "version": "2.2.1-rip200"
}
```

---

## GET /epoch

Returns current epoch information including number, start time, and enrollment count.

### Example
```bash
curl -sk https://50.28.86.131/epoch
```

### Response (200)
```json
{
    "blocks_per_epoch": 144,
    "enrolled_miners": 30,
    "epoch": 104,
    "epoch_pot": 1.5,
    "slot": 15066,
    "total_supply_rtc": 8388608
}
```

---

## GET /metrics

Prometheus-compatible metrics endpoint. Returns node metrics in the Prometheus exposition format.

### Example
```bash
curl -sk https://50.28.86.131/metrics
```

### Response (200)
```
# Prometheus not available```

---

## GET /balance/{miner_pk}

Returns the RTC balance for a given miner public key.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `miner_pk` | string | Miner public key (hex) |

### Example
```bash
curl -sk https://50.28.86.131/balance/0x0000000000000000000000000000000000000000000000000000000000000001
```

---

## POST /attest/challenge

Request a hardware attestation challenge. The challenge is a cryptographic puzzle tied to the current epoch.

### Request Body
```json
{
  "miner_pk": "string (hex public key)"
}
```

### Example
```bash
curl -sk -X POST https://50.28.86.131/attest/challenge \\
  -H "Content-Type: application/json" \\
  -d '{"miner_pk": "0x..."}'
```

---

## POST /attest/submit

Submit a completed hardware attestation response to the node for verification.

### Request Body
```json
{
  "miner_pk": "string",
  "challenge": "string",
  "response": "string",
  "hardware_proof": {...}
}
```

### Example
```bash
curl -sk -X POST https://50.28.86.131/attest/submit \\
  -H "Content-Type: application/json" \\
  -d '{"miner_pk": "0x...", ...}'
```

---

## POST /epoch/enroll

Enroll a miner in the current epoch to participate in block production and earn rewards.

### Request Body
```json
{
  "miner_pk": "string (hex public key)"
}
```

### Example
```bash
curl -sk -X POST https://50.28.86.131/epoch/enroll \\
  -H "Content-Type: application/json" \\
  -d '{"miner_pk": "0x..."}'
```

---

## GET /withdraw/history/{miner_pk}

Returns withdrawal history for a miner.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `miner_pk` | string | Miner public key (hex) |

### Example
```bash
curl -sk https://50.28.86.131/withdraw/history/0x...
```

---

## POST /withdraw/register

Register an SR25519 key for withdrawals. This key is used to sign withdrawal requests.

### Request Body
```json
{
  "miner_pk": "string (hex public key)",
  "withdrawal_pk": "string (SR25519 public key)"
}
```

---

## POST /withdraw/request

Request an RTC token withdrawal.

### Request Body
```json
{
  "miner_pk": "string (hex public key)",
  "amount": "integer (RTC amount)",
  "signature": "string (signed by withdrawal key)"
}
```

---

## GET /withdraw/status/{withdrawal_id}

Check the status of a withdrawal request.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `withdrawal_id` | string | Withdrawal request ID |

### Example
```bash
curl -sk https://50.28.86.131/withdraw/status/<withdrawal_id>
```

---

*Generated from live RustChain node API. Last updated: 2026-03-17*

---

## Error Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 404 | Not found (invalid endpoint or miner) |
| 429 | Rate limited |
| 500 | Internal server error |
