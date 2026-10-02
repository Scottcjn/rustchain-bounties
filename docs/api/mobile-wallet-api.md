
# Mobile Wallet API Specification

## Overview
This API provides endpoints for interacting with a mobile wallet, enabling users to check balances, sign transactions, view transaction history, and generate receive QR payloads.

## Base URL
`https://rustchain.org`

## Authentication
All endpoints require a valid JWT token in the `Authorization` header:
```
Authorization: Bearer <token>
```

## Endpoints

### 1. Get Wallet Balance
**Endpoint:** `/wallet/balance`

**Method:** GET

**Description:** Retrieve the current balance of the wallet.

**Parameters:**
- `miner_id` (required): RustChain wallet or miner identifier to query.

**Response:**
```json
{
  "status": "success",
  "data": {
    "balance": "123456789.00000000",
    "currency": "RUST"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing authentication token
- `500 Internal Server Error`: Server error

---

### 2. Get Transaction History
**Endpoint:** `/wallet/history`

**Method:** GET

**Description:** Retrieve the transaction history for the wallet.

**Parameters:**
- `miner_id` (required): RustChain wallet or miner identifier to query.
- `limit` (optional): Number of transactions to return (default: 20)
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "status": "success",
  "data": {
    "transactions": [
      {
        "id": "transaction_hash_1",
        "from": "wallet_address_1",
        "to": "wallet_address_2",
        "amount": "100.00000000",
        "timestamp": "2026-03-10T12:00:00Z",
        "status": "completed"
      },
      {
        "id": "transaction_hash_2",
        "from": "wallet_address_1",
        "to": "wallet_address_3",
        "amount": "50.00000000",
        "timestamp": "2026-03-11T10:30:00Z",
        "status": "pending"
      }
    ],
    "total": 50,
    "limit": 20,
    "offset": 0
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing or invalid `miner_id`
- `401 Unauthorized`: Invalid or missing authentication token
- `500 Internal Server Error`: Server error

---

### 3. Generate Receive QR Payload
**Endpoint:** `/wallet/receive-qr`

**Method:** GET

**Description:** Build a QR-ready receive payload for the wallet. Mobile clients can render the returned URI as a QR code and show the wallet name, requested amount, and optional memo on the receive screen.

**Parameters:**
- `miner_id` (required): RustChain wallet or miner identifier receiving funds.
- `amount` (optional): Requested RTC amount.
- `memo` (optional): Human-readable payment note.

**Response:**
```json
{
  "status": "success",
  "data": {
    "wallet": "wallet_address_1",
    "uri": "rustchain:wallet_address_1?amount=25.00000000&memo=bounty-payout",
    "qr_payload": "rustchain:wallet_address_1?amount=25.00000000&memo=bounty-payout"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing wallet identifier or invalid amount
- `401 Unauthorized`: Invalid or missing authentication token
- `500 Internal Server Error`: Server error

---

### 4. Sign Transaction
**Endpoint:** `/wallet/sign`

**Method:** POST

**Description:** Sign a transaction with the wallet's private key.

**Request Body:**
```json
{
  "transaction": {
    "from": "wallet_address_1",
    "to": "wallet_address_2",
    "amount": "100.00000000",
    "data": "optional_transaction_data"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "signed_transaction": "base64_encoded_signature",
    "transaction_hash": "transaction_hash_hex"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid transaction data
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: Insufficient balance
- `500 Internal Server Error`: Server error

---
