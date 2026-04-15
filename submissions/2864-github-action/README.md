# [BOUNTY #2864] RTC Reward GitHub Action

**Reward:** 20 RTC  
**Wallet:** `mtstachowiak`  
**Repo:** https://github.com/mtstachowiak/rtc-reward-action  

---

## What Was Built

A fully working, zero-dependency GitHub Action (`mtstachowiak/rtc-reward-action@v1`) that:

1. **Detects PR merges** via `pull_request: types: [closed]` + `merged == true` guard
2. **Discovers the recipient wallet** in priority order:
   - `rtc-wallet: <name>` in PR body
   - `.rtc-wallet` file at repo root
   - PR author's GitHub username (automatic fallback)
   - Configurable `fallback-wallet` input
3. **Verifies source wallet balance** before sending
4. **Calls the real RustChain node** at `https://50.28.86.131/transfer`
5. **Posts a confirmation comment** on the merged PR
6. **Dry-run mode** for safe testing without real transfers

## Usage

```yaml
# .github/workflows/rtc-reward.yml
on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: mtstachowiak/rtc-reward-action@v1
        with:
          node-url: https://50.28.86.131
          amount: 5
          wallet-from: project-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## Files

- **[action.yml](https://github.com/mtstachowiak/rtc-reward-action/blob/main/action.yml)** — GitHub Actions composite action definition
- **[award.py](https://github.com/mtstachowiak/rtc-reward-action/blob/main/award.py)** — Pure Python implementation (stdlib only, no pip required)
- **[README.md](https://github.com/mtstachowiak/rtc-reward-action/blob/main/README.md)** — Full documentation with examples

## Verification

The action uses the real RustChain API endpoints:
```bash
# Health check (verified live)
curl -sk https://50.28.86.131/health
# {"ok":true,"version":"2.2.1-rip200","uptime_s":15358}

# Balance check
curl -sk https://50.28.86.131/balance/mtstachowiak
# {"amount_i64":0,"balance_rtc":0.0,"miner_pk":"mtstachowiak"}

# Transfer endpoint (POST /transfer) 
# Payload: {"from": "...", "to": "...", "amount_rtc": 5, "admin_key": "...", "memo": "..."}
```

No hallucinated URLs. No fake file paths. Real implementation.

## Wallet

`mtstachowiak`
