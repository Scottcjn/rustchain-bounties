# RustChain API Quick Reference

> **Base URL:** `https://50.28.86.131`
> **Version:** 2.2.1-rip200
> **Protocol:** HTTPS (self-signed cert, use `-k` with curl)

This is a quick-reference supplement to the full [API_REFERENCE.md](./API_REFERENCE.md).

---

## Core Endpoints

### GET /health

Node health check.

**Live response fields:**

```json
{
  "ok": true,
  "uptime_s": 459718,
  "backup_age_hours": 5.62,
  "db_rw": true,
  "tip_age_slots": 0,
  "version": "2.2.1-rip200"
}
```

```bash
curl -k https://50.28.86.131/health | jq .
```

### GET /api/stats

System-wide statistics.

**Live response fields:**

```json
{
  "epoch": 162,
  "total_miners": 661,
  "block_time": 600,
  "chain_id": "rustchain-mainnet-v2",
  "total_balance": 437075.354584,
  "pending_withdrawals": 0,
  "version": "2.2.1-security-hardened",
  "features": ["RIP-0005", "RIP-0008", "RIP-0009", "RIP-0142", "RIP-0143", "RIP-0144"],
  "security": ["no_mock_sigs", "mandatory_admin_key", "replay_protection", "validated_json"]
}
```

```bash
curl -k https://50.28.86.131/api/stats | jq .
```

### GET /epoch

Current epoch information.

**Live response fields:**

```json
{
  "epoch": 162,
  "slot": 23403,
  "blocks_per_epoch": 144,
  "epoch_pot": 1.5,
  "enrolled_miners": 13,
  "total_supply_rtc": 8388608
}
```

```bash
curl -k https://50.28.86.131/epoch | jq .
```

### GET /balance/{miner_pk}

Check miner balance. Replace `{miner_pk}` with your miner ID / wallet name.

```bash
curl -k https://50.28.86.131/balance/YOUR_MINER_ID
```

---

## Quick Examples

### Python

```python
import requests
import urllib3
urllib3.disable_warnings()

BASE = "https://50.28.86.131"

# Health check
health = requests.get(f"{BASE}/health", verify=False).json()
print(f"Node OK: {health['ok']}, uptime: {health['uptime_s']}s")

# Stats
stats = requests.get(f"{BASE}/api/stats", verify=False).json()
print(f"Epoch: {stats['epoch']}, Miners: {stats['total_miners']}")

# Current epoch
epoch = requests.get(f"{BASE}/epoch", verify=False).json()
print(f"Epoch {epoch['epoch']}, Pot: {epoch['epoch_pot']} RTC")

# Balance
balance = requests.get(f"{BASE}/balance/YOUR_MINER_ID", verify=False).json()
print(f"Balance: {balance}")
```

### JavaScript (Node.js)

```javascript
const https = require('https');
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

function get(path) {
  return new Promise((resolve, reject) => {
    https.get('https://50.28.86.131' + path, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve(JSON.parse(d)));
    }).on('error', reject);
  });
}

async function main() {
  const health = await get('/health');
  console.log('OK:', health.ok, 'Uptime:', health.uptime_s);

  const stats = await get('/api/stats');
  console.log('Epoch:', stats.epoch, 'Miners:', stats.total_miners);

  const epoch = await get('/epoch');
  console.log('Epoch pot:', epoch.epoch_pot, 'RTC');
}
main();
```

---

For the complete API including attestation, enrollment, and withdrawal endpoints, see [API_REFERENCE.md](./API_REFERENCE.md).
