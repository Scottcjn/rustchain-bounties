# RustChain API Reference

Complete API documentation for the RustChain network.

## Base URL

```
https://50.28.86.131
```

**Note:** All endpoints use HTTPS. The `-k` flag (insecure) may be required for `curl` due to self-signed certificates.

---

## Health & Status

### Health Check

**Endpoint:** `GET /health`

Check the health status of the RustChain node.

**Example Request:**
```bash
curl -sk https://50.28.86.131/health
```

**Example Response:**
```json
{
  "ok": true,
  "version": "2.2.1-rip200",
  "uptime_s": 247060,
  "tip_age_slots": 0,
  "db_rw": true,
  "backup_age_hours": 12.8
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | Node health status |
| `version` | string | RustChain version (e.g., "2.2.1-rip200") |
| `uptime_s` | integer | Node uptime in seconds |
| `tip_age_slots` | integer | Age of the latest block in slots |
| `db_rw` | boolean | Database read/write status |
| `backup_age_hours` | float | Hours since last backup |

---

## Wallet API

### Check Balance

**Endpoint:** `GET /wallet/balance`

Get the RTC balance for a wallet/miner ID.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `miner_id` | string | Yes | Wallet or miner ID to check |

**Example Request:**
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=my-wallet-id"
```

**Example Response:**
```json
{
  "miner_id": "my-wallet-id",
  "balance": "15.5",
  "pending_rewards": "0.0"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `miner_id` | string | The queried wallet/miner ID |
| `balance` | string | Current RTC balance |
| `pending_rewards` | string | Pending epoch rewards |

---

## Mining API

### List Active Miners

**Endpoint:** `GET /api/miners`

Get a list of all active miners on the network.

**Example Request:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Example Response:**
```json
[
  {
    "miner": "modern-sophia-Pow-9862e3be",
    "hardware_type": "x86-64 (Modern)",
    "device_arch": "modern",
    "device_family": "x86_64",
    "antiquity_multiplier": 1.0,
    "last_attest": 1770912400,
    "entropy_score": 0.0
  },
  {
    "miner": "g5-selena-179",
    "hardware_type": "PowerPC G5 (Vintage)",
    "device_arch": "power8",
    "device_family": "PowerPC",
    "antiquity_multiplier": 2.0,
    "last_attest": 1770912226,
    "entropy_score": 0.0
  }
]
```

**Response Fields (per miner):**

| Field | Type | Description |
|-------|------|-------------|
| `miner` | string | Unique miner identifier (wallet ID) |
| `hardware_type` | string | Human-readable hardware description |
| `device_arch` | string | Architecture category |
| `device_family` | string | Device family name |
| `antiquity_multiplier` | float | Mining reward multiplier (1.0-2.5) |
| `last_attest` | integer | Unix timestamp of last attestation |
| `entropy_score` | float | Entropy score (0.0 = not yet calculated) |

---

## Network API

### Current Epoch

**Endpoint:** `GET /epoch`

Get information about the current epoch.

**Example Request:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Example Response:**
```json
{
  "epoch": 156,
  "start_slot": 15500,
  "end_slot": 15999,
  "rewards_per_epoch": 1.5,
  "remaining_slots": 412
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `epoch` | integer | Current epoch number |
| `start_slot` | integer | Starting slot of current epoch |
| `end_slot` | integer | Ending slot of current epoch |
| `rewards_per_epoch` | float | RTC rewards distributed per epoch |
| `remaining_slots` | integer | Slots remaining in current epoch |

---

## Block Explorer

**Endpoint:** `/explorer`

Web-based block explorer for viewing transactions, blocks, and addresses.

**Access:** Open in browser: https://50.28.86.131/explorer

**Features:**
- View current block height
- Search transactions by hash
- Browse wallet addresses
- View transaction history

---

## Miner Download

**Endpoint:** `GET /miner/download`

Download the RustChain universal miner script.

**Example Request:**
```bash
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
```

**Usage:**
```bash
python3 rustchain_miner.py --wallet YOUR_WALLET_ID --node https://50.28.86.131
```

---

## Rate Limits

There are no explicit rate limits, but please be respectful:
- Max 10 requests/second from a single IP
- Burst requests may be temporarily throttled

---

## Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{
  "error": "invalid_wallet_id",
  "message": "Wallet ID format is invalid"
}
```

**429 Too Many Requests:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please slow down."
}
```

**500 Internal Server Error:**
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

---

## Code Examples

### Python: Check Balance

```python
import requests

def get_balance(wallet_id):
    url = f"https://50.28.86.131/wallet/balance"
    params = {"miner_id": wallet_id}
    response = requests.get(url, params=params, verify=False)
    return response.json()

balance = get_balance("my-wallet-id")
print(f"Balance: {balance['balance']} RTC")
```

### Bash: Monitor Miner Activity

```bash
#!/bin/bash
# Monitor active miners count

while true; do
    miners=$(curl -sk https://50.28.86.131/api/miners | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
    echo "Active miners: $miners"
    sleep 60
done
```

### JavaScript: Fetch Epoch Info

```javascript
async function getEpoch() {
  const response = await fetch('https://50.28.86.131/epoch');
  const data = await response.json();
  return data;
}

getEpoch().then(epoch => {
  console.log(`Current epoch: ${epoch.epoch}`);
  console.log(`Rewards per epoch: ${epoch.rewards_per_epoch} RTC`);
});
```

---

## Support

- **Issues:** https://github.com/Scottcjn/rustchain-bounties/issues
- **Documentation:** See README.md for mining guides and tutorials

---

*Last updated: 2026-02-12*
*API Version: 2.2.1-rip200*
