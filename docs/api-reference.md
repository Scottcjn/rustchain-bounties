# RustChain API Reference

Complete reference for all RustChain API endpoints.

## Base URL

```
https://50.28.86.131
```

## Authentication

Most endpoints require a `miner_id` (wallet ID) parameter. No API keys required.

## Endpoints

### Health Check

Check if the node is operational.

**Endpoint:** `GET /health`

**Request:**
```bash
curl -sk https://50.28.86.131/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1704067200
}
```

### Get Wallet Balance

Retrieve the RTC balance for a wallet ID.

**Endpoint:** `GET /wallet/balance`

**Parameters:**
- `miner_id` (required): Your wallet ID

**Request:**
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

**Response:**
```json
{
  "wallet_id": "YOUR_WALLET_ID",
  "balance": 125.5,
  "pending": 0.0
}
```

### Download Miner

Download the latest miner script.

**Endpoint:** `GET /miner/download`

**Request:**
```bash
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
```

**Response:**
Returns the Python miner script as plain text.

### Transfer RTC

Transfer RTC from one wallet to another.

**Endpoint:** `POST /wallet/transfer`

**Parameters:**
- `from_wallet` (required): Source wallet ID
- `to_wallet` (required): Destination wallet ID
- `amount` (required): Amount of RTC to transfer
- `signature` (required): Signed transaction payload

**Request:**
```bash
curl -sk -X POST https://50.28.86.131/wallet/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_wallet": "sender_wallet_id",
    "to_wallet": "recipient_wallet_id",
    "amount": 10.0,
    "signature": "signed_payload_hash"
  }'
```

**Response:**
```json
{
  "status": "success",
  "tx_hash": "0x1234567890abcdef",
  "from_wallet": "sender_wallet_id",
  "to_wallet": "recipient_wallet_id",
  "amount": 10.0,
  "timestamp": 1704067200
}
```

### Get Current Epoch

Retrieve the current epoch information.

**Endpoint:** `GET /epoch`

**Request:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Response:**
```json
{
  "epoch": 12345,
  "reward_per_epoch": 1.5,
  "active_miners": 127,
  "start_time": 1704067200,
  "end_time": 1704070800
}
```

### Get Active Miners

List all active miners on the network.

**Endpoint:** `GET /api/miners`

**Request:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Response:**
```json
{
  "total_miners": 127,
  "miners": [
    {
      "wallet_id": "miner_1",
      "hardware": "PowerPC_G5",
      "multiplier": 2.0,
      "uptime": 86400
    },
    {
      "wallet_id": "miner_2",
      "hardware": "x86_64",
      "multiplier": 1.0,
      "uptime": 43200
    }
  ]
}
```

### Submit Attestation

Submit hardware attestation for mining rewards.

**Endpoint:** `POST /attestation/submit`

**Parameters:**
- `miner_id` (required): Your wallet ID
- `hardware_fingerprint` (required): 6-point hardware fingerprint
- `proof_of_work` (required): Attestation proof

**Request:**
```bash
curl -sk -X POST https://50.28.86.131/attestation/submit \
  -H "Content-Type: application/json" \
  -d '{
    "miner_id": "YOUR_WALLET_ID",
    "hardware_fingerprint": {
      "cpu_model": "PowerPC_G5",
      "cpu_cores": 2,
      "arch": "ppc64",
      "vendor_id": "IBM",
      "physical_id": "unique_hw_id",
      "timestamp": 1704067200
    },
    "proof_of_work": "attestation_hash"
  }'
```

**Response:**
```json
{
  "status": "accepted",
  "miner_id": "YOUR_WALLET_ID",
  "multiplier": 2.0,
  "estimated_reward": 1.5
}
```

## Error Codes

- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid wallet ID
- `404 Not Found`: Endpoint does not exist
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Node error

## Rate Limits

- 100 requests per minute per wallet ID
- 1000 requests per hour per IP address

## WebSocket API

Real-time updates available via WebSocket connection.

**Endpoint:** `wss://50.28.86.131/ws`

**Subscribe to balance updates:**
```json
{
  "action": "subscribe",
  "channel": "balance",
  "wallet_id": "YOUR_WALLET_ID"
}
```

**Subscribe to epoch updates:**
```json
{
  "action": "subscribe",
  "channel": "epoch"
}
```
