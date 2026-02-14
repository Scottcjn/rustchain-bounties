# RustChain API Reference

Base URL:

```text
https://50.28.86.131
```

TLS note: the node currently uses a self-signed certificate. For quick tests:

```bash
curl -sk https://50.28.86.131/health
```

## Health

**Endpoint:** `GET /health`

```bash
curl -sk https://50.28.86.131/health
```

Example response:

```json
{"backup_age_hours":0.08,"db_rw":true,"ok":true,"tip_age_slots":0,"uptime_s":24000,"version":"2.2.1-rip200"}
```

## Epoch

**Endpoint:** `GET /epoch`

```bash
curl -sk https://50.28.86.131/epoch
```

Example response:

```json
{"blocks_per_epoch":144,"enrolled_miners":12,"epoch":73,"epoch_pot":1.5,"slot":10554}
```

## Miners

**Endpoint:** `GET /api/miners`

```bash
curl -sk https://50.28.86.131/api/miners
```

The response is a JSON array of active miners. Each entry typically includes:

- `miner` (string)
- `hardware_type` (string)
- `device_arch` (string)
- `device_family` (string)
- `antiquity_multiplier` (number)
- `last_attest` (unix timestamp)
- `entropy_score` (number)

## Wallet

**Endpoint:** `GET /wallet/balance`

Query param:

- `miner_id` (string, required)

```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_MINER_ID"
```

Example response:

```json
{"amount_i64":265420827,"amount_rtc":265.420827,"miner_id":"victus-x86-scott"}
```

## Attestation And Enrollment (Miner Clients)

These are the primary endpoints used by modern miner clients (RIP-200 PoA flow).

### Attestation Challenge

**Endpoint:** `POST /attest/challenge`

```bash
curl -sk -X POST https://50.28.86.131/attest/challenge -H 'Content-Type: application/json' -d '{}'
```

Example response:

```json
{"expires_at":1771038996,"nonce":"...","server_time":1771038696}
```

### Attestation Submit

**Endpoint:** `POST /attest/submit`

The miner builds an attestation payload and submits it here.

### Epoch Enroll

**Endpoint:** `POST /epoch/enroll`

The miner enrolls after a recent successful attestation. If you call this without a recent attestation, you'll get an error like:

```json
{"error":"no_recent_attestation","ttl_s":600}
```

### Lottery Eligibility (Optional)

**Endpoint:** `GET /lottery/eligibility`

```bash
curl -sk "https://50.28.86.131/lottery/eligibility?miner_id=YOUR_MINER_ID"
```

## Explorer

**Endpoint:** `GET /explorer` (HTTP redirect to the explorer UI)

```bash
curl -sk -I https://50.28.86.131/explorer
```

## Rate Limiting

If you hit HTTP 429, back off and retry with a delay (for example, exponential backoff).
