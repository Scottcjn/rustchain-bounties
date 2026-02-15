# RustChain API Specification

## Base URL
The official node is available at:
`https://50.28.86.131`

> **Note:** The node uses a self-signed certificate. Use `-k` or `--insecure` with curl for testing.

---

## 1. Network Health
Returns the status of the node, database, and blockchain tip.

- **Endpoint:** `GET /health`
- **Curl Example:**
  ```bash
  curl -sk https://50.28.86.131/health
  ```
- **Response Example:**
  ```json
  {
    "backup_age_hours": 0.08,
    "db_rw": true,
    "ok": true,
    "tip_age_slots": 0,
    "uptime_s": 24000,
    "version": "2.2.1-rip200"
  }
  ```

---

## 2. Epoch & Slot Info
Returns the current slot number and epoch progress.

- **Endpoint:** `GET /epoch`
- **Curl Example:**
  ```bash
  curl -sk https://50.28.86.131/epoch
  ```
- **Response Example:**
  ```json
  {
    "blocks_per_epoch": 144,
    "enrolled_miners": 12,
    "epoch": 73,
    "epoch_pot": 1.5,
    "slot": 10554
  }
  ```

---

## 3. Active Miners
Returns a list of all currently attested and active miners.

- **Endpoint:** `GET /api/miners`
- **Curl Example:**
  ```bash
  curl -sk https://50.28.86.131/api/miners
  ```
- **Response Field Key:**
  - `miner`: Wallet address.
  - `antiquity_multiplier`: Reward bonus based on hardware.
  - `last_attest`: Unix timestamp of last valid proof.

---

## 4. Wallet Balance
Query the current RTC balance for a specific miner/wallet ID.

- **Endpoint:** `GET /wallet/balance`
- **Params:** `miner_id` (string, required)
- **Curl Example:**
  ```bash
  curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_MINER_ID"
  ```
- **Response Example:**
  ```json
  {
    "amount_i64": 265420827,
    "amount_rtc": 265.420827,
    "miner_id": "victus-x86-scott"
  }
  ```

---

## 5. Attestation Flow (RIP-200)

### Step A: Request Challenge
Miners must fetch a nonce before submitting a proof.

- **Endpoint:** `POST /attest/challenge`
- **Payload:** `{}`
- **Curl Example:**
  ```bash
  curl -sk -X POST https://50.28.86.131/attest/challenge -H "Content-Type: application/json" -d '{}'
  ```

### Step B: Submit Proof
Submit hardware fingerprint and entropy report.

- **Endpoint:** `POST /attest/submit`
- **Payload:** (See [Attestation Guide](./ATTESTATION.md) for full structure)
- **Curl Example:**
  ```bash
  curl -sk -X POST https://50.28.86.131/attest/submit -H "Content-Type: application/json" -d '{"miner": "...", "nonce": "...", "report": {...}, "device": {...}}'
  ```

### Step C: Enroll in Epoch
Final step to join the reward distribution for the current cycle.

- **Endpoint:** `POST /epoch/enroll`
- **Payload:**
  ```json
  {
    "miner_pubkey": "RTC_WALLET_ADDRESS",
    "miner_id": "FRIENDLY_ID",
    "device": { "family": "...", "arch": "..." }
  }
  ```

---

## 6. Rate Limiting
The node implements strict rate limiting for security:
- **HTTP 429**: Triggered when concurrent requests exceed the threshold.
- **Recommended Strategy**: Use **Exponential Backoff** (2s, 4s, 8s...) when 429 is encountered.

---
*Next: See [Glossary of Terms](./GLOSSARY.md).*
