# RustChain API Reference (Draft)

This document provides a comprehensive reference for all REST API endpoints available in the RustChain ecosystem, including the core blockchain functions and the SophiaCore (RIP-306) attestation inspector.

## Base URL
- Production: `https://api.rustchain.org/v1`
- Node (Self-signed): `https://<node-ip>/`

---

## 1. System Endpoints

### GET /health
Returns the health status of the node.
- **Example**: `curl -sk https://50.28.86.131/health`
- **Response**:
  ```json
  {
    "ok": true,
    "version": "1.0.0",
    "uptime_s": 3600,
    "db_rw": true
  }
  ```

### GET /api/stats
Returns aggregate network statistics.
- **Example**: `curl -sk https://50.28.86.131/api/stats`

---

## 2. Blockchain Endpoints

### GET /epoch
Returns information about the current mining epoch.
- **Example**: `curl -sk https://50.28.86.131/epoch`
- **Response**:
  ```json
  {
    "epoch": 123,
    "slot": 45,
    "blocks_per_epoch": 1000,
    "enrolled_miners": 50,
    "epoch_pot": 150.0
  }
  ```

### GET /block/{block_number}
Returns information about a specific block.
- **Path Parameters**: `block_number` (integer)

---

## 3. Mining & Attestation Endpoints

### POST /epoch/enroll
Enrolls a miner for the current epoch with hardware details.
- **Request Body**:
  ```json
  {
    "miner_pubkey": "string",
    "miner_id": "string",
    "device": {
      "family": "PowerPC G4",
      "arch": "ppc"
    }
  }
  ```

### POST /attest/challenge
Generates a challenge nonce for Proof-of-Attestation (PoA).
- **Example**: `curl -sk -X POST https://50.28.86.131/attest/challenge`
- **Response**:
  ```json
  {
    "nonce": "a1b2c3d4...",
    "expires_at": 1640000000
  }
  ```

### POST /attest/submit
Submits the completed PoA payload.
- **Request Body**: JSON payload containing the signed nonce and hardware fingerprints.

### GET /api/miners
Returns a list of currently active miners.
- **Query Parameters**: `limit`, `offset`

---

## 4. Wallet & Withdraw Endpoints

### GET /wallet/balance
Returns the balance for a specific miner/wallet ID.
- **Query Parameters**: `miner_id` (required)
- **Example**: `curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_ID"`

### POST /withdraw/register
Registers an SR25519 key for secure withdrawals.
- **Request Body**:
  ```json
  {
    "miner_pk": "hex_public_key",
    "withdrawal_pk": "sr25519_public_key"
  }
  ```

### POST /withdraw/request
Requests an RTC token withdrawal.
- **Request Body**:
  ```json
  {
    "miner_pk": "hex_public_key",
    "amount": 100,
    "signature": "signed_by_withdrawal_key"
  }
  ```

### GET /withdraw/status/{withdrawal_id}
Checks the status of a specific withdrawal request.

---

## 5. SophiaCore (RIP-306) Endpoints
*AI-powered hardware validation and anomaly detection.*

### POST /sophia/inspect
Submits a fingerprint bundle for semantic analysis.
- **Response**: Verdict (APPROVED, CAUTIOUS, SUSPICIOUS, REJECTED), confidence, and reasoning.

### GET /sophia/status/{miner_id}
Returns the latest inspection result for a miner.

### GET /sophia/stats
Returns aggregate statistics for SophiaCore inspections.

### GET /sophia/health
Checks the status of the SophiaCore service and Ollama host.

---

## Error Codes
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **401**: Unauthorized
- **404**: Not Found
- **429**: Rate Limited (wait before retrying)
- **500**: Internal Server Error
