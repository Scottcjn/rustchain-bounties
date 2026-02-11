# RustChain API Reference

Complete API documentation for RustChain network endpoints.

**Base URL**: `https://50.28.86.131`  
**Version**: 2.2.1-rip200  
**Protocol**: RIP-200 Proof-of-Attestation

## Table of Contents

- [Health & Status](#health--status)
- [Wallet Operations](#wallet-operations)
- [Mining & Attestation](#mining--attestation)
- [Network Information](#network-information)
- [Transfer Operations](#transfer-operations)
- [Error Handling](#error-handling)

---

## Health & Status

### GET /health

Check node health and status.

**Response:**
```json
{
  "backup_age_hours": 13.101825896766451,
  "db_rw": true,
  "ok": true,
  "tip_age_slots": 0,
  "uptime_s": 161895,
  "version": "2.2.1-rip200"
}
```

**Fields:**
- `backup_age_hours`: Hours since last backup
- `db_rw`: Database read/write status
- `ok`: Overall health status
- `tip_age_slots`: Age of chain tip in slots
- `uptime_s`: Node uptime in seconds
- `version`: Node software version

**Example:**
```bash
curl -sk https://50.28.86.131/health
```

---

## Wallet Operations

### GET /wallet/balance

Get wallet balance for a miner ID.

**Parameters:**
- `miner_id` (required): Wallet/miner identifier

**Response:**
```json
{
  "amount_i64": 0,
  "amount_rtc": 0.0,
  "miner_id": "clawra-ai-agent-1sadjlk"
}
```

**Fields:**
- `amount_i64`: Balance in integer format
- `amount_rtc`: Balance in RTC (decimal)
- `miner_id`: Wallet identifier

**Example:**
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=your-wallet-id"
```

---

## Mining & Attestation

### GET /api/miners

Get list of active miners and their hardware information.

**Response:**
```json
[
  {
    "antiquity_multiplier": 2.5,
    "device_arch": "G4",
    "device_family": "PowerPC",
    "entropy_score": 0.0,
    "hardware_type": "PowerPC G4 (Vintage)",
    "last_attest": 1770827234,
    "miner": "eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC"
  }
]
```

**Fields:**
- `antiquity_multiplier`: Hardware age bonus multiplier
- `device_arch`: CPU architecture
- `device_family`: Hardware family
- `entropy_score`: Randomness contribution score
- `hardware_type`: Human-readable hardware description
- `last_attest`: Unix timestamp of last attestation
- `miner`: Miner identifier

**Hardware Multipliers:**
| Architecture | Multiplier | Type |
|-------------|-----------|------|
| PowerPC G4 | 2.5x | Vintage |
| PowerPC G5 | 2.0x | Vintage |
| PowerPC G3 | 1.8x | Vintage |
| Pentium 4 | 1.5x | Retro |
| Apple Silicon | 1.2x | Modern |
| x86_64 | 1.0x | Modern |

**Example:**
```bash
curl -sk https://50.28.86.131/api/miners
```

---

## Network Information

### GET /epoch

Get current epoch information and mining statistics.

**Response:**
```json
{
  "blocks_per_epoch": 144,
  "enrolled_miners": 12,
  "epoch": 70,
  "epoch_pot": 1.5,
  "slot": 10200
}
```

**Fields:**
- `blocks_per_epoch`: Blocks per epoch (144 = ~24 hours)
- `enrolled_miners`: Number of active miners
- `epoch`: Current epoch number
- `epoch_pot`: RTC reward pool for current epoch
- `slot`: Current slot number

**Example:**
```bash
curl -sk https://50.28.86.131/epoch
```

---

## Transfer Operations

### POST /transfer

Submit a signed RTC transfer between wallets.

**Request Body:**
```json
{
  "from": "sender-wallet-id",
  "to": "recipient-wallet-id",
  "amount": 10.5,
  "signature": "signed-transfer-hash",
  "timestamp": 1770827234
}
```

**Response:**
```json
{
  "success": true,
  "tx_hash": "abc123...",
  "new_balance": 89.5
}
```

**Example:**
```bash
curl -sk -X POST https://50.28.86.131/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from": "sender-wallet",
    "to": "recipient-wallet", 
    "amount": 10.0,
    "signature": "...",
    "timestamp": 1770827234
  }'
```

---

## Miner Download

### GET /miner/download

Download the universal miner script.

**Response:** Python script file

**Example:**
```bash
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
```

**Usage:**
```bash
python3 rustchain_miner.py --wallet YOUR_WALLET_ID --node https://50.28.86.131
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Endpoint not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "error": true,
  "message": "Invalid wallet ID format",
  "code": "INVALID_WALLET"
}
```

### Common Errors

| Error Code | Description | Solution |
|-----------|-------------|----------|
| `INVALID_WALLET` | Wallet ID format invalid | Use alphanumeric + hyphens only |
| `INSUFFICIENT_BALANCE` | Not enough RTC for transfer | Check balance first |
| `MINER_NOT_FOUND` | Miner not registered | Start mining to register |
| `INVALID_SIGNATURE` | Transfer signature invalid | Re-sign the transfer |

---

## Rate Limits

- **General API**: 100 requests/minute per IP
- **Wallet Balance**: 60 requests/minute per wallet
- **Transfer**: 10 requests/minute per wallet

---

## SDK Examples

### Python

```python
import requests

class RustChainAPI:
    def __init__(self, base_url="https://50.28.86.131"):
        self.base_url = base_url
    
    def get_balance(self, wallet_id):
        response = requests.get(
            f"{self.base_url}/wallet/balance",
            params={"miner_id": wallet_id},
            verify=False
        )
        return response.json()
    
    def get_miners(self):
        response = requests.get(f"{self.base_url}/api/miners", verify=False)
        return response.json()

# Usage
api = RustChainAPI()
balance = api.get_balance("my-wallet")
print(f"Balance: {balance['amount_rtc']} RTC")
```

### JavaScript

```javascript
class RustChainAPI {
    constructor(baseUrl = 'https://50.28.86.131') {
        this.baseUrl = baseUrl;
    }
    
    async getBalance(walletId) {
        const response = await fetch(
            `${this.baseUrl}/wallet/balance?miner_id=${walletId}`
        );
        return response.json();
    }
    
    async getMiners() {
        const response = await fetch(`${this.baseUrl}/api/miners`);
        return response.json();
    }
}

// Usage
const api = new RustChainAPI();
const balance = await api.getBalance('my-wallet');
console.log(`Balance: ${balance.amount_rtc} RTC`);
```

### Bash/cURL

```bash
#!/bin/bash

# Check wallet balance
check_balance() {
    local wallet_id=$1
    curl -sk "https://50.28.86.131/wallet/balance?miner_id=${wallet_id}" | jq '.amount_rtc'
}

# Get active miners
get_miners() {
    curl -sk "https://50.28.86.131/api/miners" | jq '.[].miner'
}

# Usage
balance=$(check_balance "my-wallet")
echo "Balance: $balance RTC"
```

---

## Network Constants

- **Total RTC Supply**: 8.3M RTC
- **Reference Rate**: 1 RTC ≈ $0.10 USD
- **Epoch Duration**: ~24 hours (144 blocks)
- **Epoch Reward**: 1.5 RTC distributed to miners
- **Block Time**: ~10 minutes
- **Consensus**: RIP-200 Proof-of-Attestation

---

## Additional Resources

- **Explorer**: [rustchain.org/explorer](https://rustchain.org/explorer)
- **Swap wRTC**: [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X)
- **Price Chart**: [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb)
- **Bridge**: [bottube.ai/bridge](https://bottube.ai/bridge)

---

*Last updated: February 2026*  
*API Version: 2.2.1-rip200*