# RustChain FAQ & Troubleshooting

## General

### What is RustChain?
RustChain is a Proof of Antiquity blockchain where miners attest real hardware rather than solving computational puzzles. Rewards are distributed per epoch to enrolled miners.

### What is the native token?
RTC (RustChain Token). Total supply: 8,388,608 RTC.

### Where can I see my balance?
```bash
curl -k https://50.28.86.131/balance/YOUR_MINER_ID | jq .
```

Or visit the explorer: https://explorer.rustchain.org/

## Mining

### Can I mine on a VM?
VMs may attest but rewards can be penalized or denied. Use real hardware for best results.

### How do I enroll in an epoch?
Run the miner script with your miner ID. Enrollment happens automatically:
```bash
python3 miner.py --miner-id YOUR_MINER_ID
```

### How long is an epoch?
144 blocks at 600s block time ≈ 24 hours.

### What is the epoch reward?
1.5 RTC per epoch, split among enrolled miners.

## API Issues

### SSL certificate errors
The node uses a self-signed certificate. Use `-k` with curl:
```bash
curl -k https://50.28.86.131/health
```

In Python:
```python
import urllib3
urllib3.disable_warnings()
requests.get(url, verify=False)
```

### "KeyError" when parsing API responses
Make sure you use the correct field names. Verified field names for v2.2.1:

| Endpoint | Correct Fields |
|----------|---------------|
| `/health` | `ok`, `uptime_s`, `version`, `db_rw` |
| `/api/stats` | `epoch`, `total_miners`, `block_time` |
| `/epoch` | `epoch`, `slot`, `epoch_pot`, `total_supply_rtc` |

### Connection refused
- Check the node is online: `curl -k https://50.28.86.131/health`
- The node may be restarting; retry in 30 seconds

## Wallet & Withdrawals

### How do I withdraw RTC?
Use the withdrawal API endpoints:
```bash
# Register withdrawal key
curl -k -X POST https://50.28.86.131/withdraw/register -d '{"miner_pk":"YOUR_ID"}'

# Request withdrawal
curl -k -X POST https://50.28.86.131/withdraw/request -d '{"miner_pk":"YOUR_ID","amount":10}'

# Check status
curl -k https://50.28.86.131/withdraw/status/WITHDRAWAL_ID
```

### Where is my miner ID?
Generated when you run `python3 miner.py --keygen`. It's stored in the miner's local config.
