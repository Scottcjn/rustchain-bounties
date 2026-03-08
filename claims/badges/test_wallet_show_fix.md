# Test: clawrtc wallet show fix

## Issue
`clawrtc wallet show` displayed `(could not reach network)` even when balance API was healthy.

## Root Cause
CLI was calling wrong endpoint:
- **Bug**: `GET /api/balance?wallet={address}` → 404
- **Fix**: `GET /wallet/balance?miner_id={address}` → 200 OK

Also wrong field name in response parsing.

## Fix Applied
```diff
- url = f"{NODE_URL}/api/balance?wallet={address}"
+ url = f"{NODE_URL}/wallet/balance?miner_id={address}"

- balance = data.get("balance_rtc", data.get("balance", 0))
+ balance = data.get("amount_rtc", data.get("balance_rtc", data.get("balance", 0)))
```

## Evidence

### Before Fix
```
Balance: (could not reach network)
```

### After Fix
```
Balance: 0.0 RTC
```

### API Test
```bash
$ curl -sk "https://50.28.86.131/wallet/balance?miner_id=RTC8ec8c073feb71b007ded0b89b427dc085ed90dca"
{"amount_i64":0,"amount_rtc":0.0,"miner_id":"RTC8ec8c073feb71b007ded0b89b427dc085ed90dca"}
```

## Files Modified
- `/Users/cell941/Library/Python/3.9/lib/python/site-packages/clawrtc/cli.py`

## Target Issue
- RustChain#524
- Bounty #1490
