# RustChain API Reference

## Base URL

```
https://50.28.86.131
```

> **Note**: The API uses a self-signed certificate. Use `-k` with curl or disable certificate verification in your HTTP client.

## Authentication

Most read endpoints are public. Write operations require:
- **User transfers**: Cryptographic signature (`/wallet/transfer/signed`)
- **Admin operations**: Admin key (`/wallet/transfer`)

---

## Health & Status

### GET /health

Check node health and status.

**Request:**
```bash
curl -sk https://50.28.86.131/health
```

**Response:**
```json
{
  "ok": true,
  "version": "2.2.1-rip200",
  "uptime_s": 98511,
  "db_rw": true,
  "tip_age_slots": 0,
  "backup_age_hours": 0.19
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | Overall health status |
| `version` | string | Node software version |
| `uptime_s` | number | Uptime in seconds |
| `db_rw` | boolean | Database read/write status |
| `tip_age_slots` | number | Slots since last block |
| `backup_age_hours` | number | Hours since last backup |

---

### GET /api/stats

Get network statistics and chain information.

**Request:**
```bash
curl -sk https://50.28.86.131/api/stats
```

**Response:**
```json
{
  "chain_id": "rustchain-mainnet-v2",
  "version": "2.2.1-security-hardened",
  "block_time": 600,
  "epoch": 64,
  "total_miners": 12183,
  "total_balance": 199719.835243,
  "pending_withdrawals": 0,
  "features": [
    "RIP-0005",
    "RIP-0008",
    "RIP-0009",
    "RIP-0142",
    "RIP-0143",
    "RIP-0144"
  ],
  "security": [
    "no_mock_sigs",
    "mandatory_admin_key",
    "replay_protection",
    "validated_json"
  ]
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `chain_id` | string | Network identifier |
| `version` | string | Software version with tags |
| `block_time` | number | Target block time in seconds |
| `epoch` | number | Current epoch number |
| `total_miners` | number | Total registered miners |
| `total_balance` | number | Total RTC in circulation |
| `pending_withdrawals` | number | Pending withdrawal count |
| `features` | array | Enabled RIP features |
| `security` | array | Active security measures |

---

## Epoch Information

### GET /epoch

Get current epoch information.

**Request:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Response:**
```json
{
  "epoch": 64,
  "slot": 9258,
  "blocks_per_epoch": 144,
  "epoch_pot": 1.5,
  "enrolled_miners": 2
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `epoch` | number | Current epoch number |
| `slot` | number | Current slot within epoch |
| `blocks_per_epoch` | number | Blocks per epoch (144) |
| `epoch_pot` | number | RTC reward pool for epoch |
| `enrolled_miners` | number | Active miners this epoch |

---

## Miners

### GET /api/miners

Get list of active miners with their hardware info.

**Request:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Response:**
```json
[
  {
    "miner": "eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC",
    "hardware_type": "PowerPC G4 (Vintage)",
    "device_family": "PowerPC",
    "device_arch": "G4",
    "antiquity_multiplier": 2.5,
    "entropy_score": 0.0,
    "last_attest": 1770262230
  },
  {
    "miner": "apple_silicon_c318209d4dadd5e8b2f91e08999d1af7efec85RTC",
    "hardware_type": "Apple Silicon (Modern)",
    "device_family": "Apple Silicon",
    "device_arch": "M2",
    "antiquity_multiplier": 0.8,
    "entropy_score": 0.0,
    "last_attest": 1770262228
  }
]
```

**Miner Object Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `miner` | string | Miner wallet ID |
| `hardware_type` | string | Human-readable hardware description |
| `device_family` | string | Hardware family (PowerPC, x86_64, etc.) |
| `device_arch` | string | Specific architecture (G4, M2, etc.) |
| `antiquity_multiplier` | number | Mining reward multiplier |
| `entropy_score` | number | Hardware entropy measurement |
| `last_attest` | number | Unix timestamp of last attestation |

---

## Wallet Operations

### GET /wallet/balance

Get wallet balance.

**Request:**
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

**Example:**
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC"
```

**Response:**
```json
{
  "miner_id": "eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC",
  "amount_rtc": 118.357193,
  "amount_i64": 118357193
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `miner_id` | string | Yes | Wallet identifier |

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `miner_id` | string | Wallet identifier |
| `amount_rtc` | number | Balance in RTC (decimal) |
| `amount_i64` | number | Balance in micro-RTC (integer) |

---

### POST /wallet/transfer/signed

Transfer RTC between wallets (user-initiated, requires signature).

**Request:**
```bash
curl -sk -X POST https://50.28.86.131/wallet/transfer/signed \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "sender_wallet_id",
    "to_address": "recipient_wallet_id",
    "amount": 1000000,
    "nonce": 1,
    "signature": "hex_encoded_signature",
    "public_key": "hex_encoded_public_key"
  }'
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from_address` | string | Yes | Sender wallet ID |
| `to_address` | string | Yes | Recipient wallet ID |
| `amount` | integer | Yes | Amount in micro-RTC |
| `nonce` | integer | Yes | Transaction nonce (for replay protection) |
| `signature` | string | Yes | Hex-encoded Ed25519 signature |
| `public_key` | string | Yes | Hex-encoded public key |

**Response (Success):**
```json
{
  "success": true,
  "tx_id": "abc123..."
}
```

**Response (Error):**
```json
{
  "error": "Missing required fields (from_address, to_address, signature, public_key, nonce)"
}
```

---

### POST /wallet/transfer

Admin-only transfer endpoint.

**Request:**
```bash
curl -sk -X POST https://50.28.86.131/wallet/transfer \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -d '{
    "from_address": "sender",
    "to_address": "recipient",
    "amount": 1000000
  }'
```

**Response (Unauthorized):**
```json
{
  "error": "Unauthorized - admin key required",
  "hint": "Use /wallet/transfer/signed for user transfers"
}
```

> **Note**: This endpoint requires admin privileges. Regular users should use `/wallet/transfer/signed`.

---

## Error Responses

All endpoints may return error responses:

### 400 Bad Request
```json
{
  "error": "Description of the error"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized - admin key required",
  "hint": "Additional information"
}
```

### 404 Not Found
```html
<title>404 Not Found</title>
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "..."
}
```

---

## Rate Limits

Currently, no rate limits are enforced. This may change as network grows.

---

## Code Examples

### Python

```python
import requests
import urllib3

# Disable SSL warnings for self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://50.28.86.131"

def get_health():
    response = requests.get(f"{BASE_URL}/health", verify=False)
    return response.json()

def get_balance(wallet_id):
    response = requests.get(
        f"{BASE_URL}/wallet/balance",
        params={"miner_id": wallet_id},
        verify=False
    )
    return response.json()

def get_miners():
    response = requests.get(f"{BASE_URL}/api/miners", verify=False)
    return response.json()

# Usage
print(get_health())
print(get_balance("my-wallet"))
print(get_miners())
```

### JavaScript (Node.js)

```javascript
const https = require('https');

const BASE_URL = 'https://50.28.86.131';

// Ignore self-signed cert
const agent = new https.Agent({ rejectUnauthorized: false });

async function getHealth() {
  const response = await fetch(`${BASE_URL}/health`, { agent });
  return response.json();
}

async function getBalance(walletId) {
  const response = await fetch(
    `${BASE_URL}/wallet/balance?miner_id=${walletId}`,
    { agent }
  );
  return response.json();
}

async function getMiners() {
  const response = await fetch(`${BASE_URL}/api/miners`, { agent });
  return response.json();
}
```

### Rust

```rust
use reqwest::Client;
use serde::Deserialize;

#[derive(Deserialize)]
struct Health {
    ok: bool,
    version: String,
    uptime_s: u64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::builder()
        .danger_accept_invalid_certs(true)
        .build()?;
    
    let health: Health = client
        .get("https://50.28.86.131/health")
        .send()
        .await?
        .json()
        .await?;
    
    println!("Node version: {}", health.version);
    Ok(())
}
```

---

## API Changelog

### v2.2.1-rip200 (Current)
- Added RIP-0142 signed transfers
- Added RIP-0143 replay protection
- Added RIP-0144 admin key validation
- Security hardening

### v2.1.0
- Added `/api/stats` endpoint
- Added antiquity multipliers (RIP-0008)

### v2.0.0
- Initial RIP-200 implementation
- Proof-of-Attestation consensus
