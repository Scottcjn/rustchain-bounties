# rtc-balance — Check RustChain Wallet Balance

## Usage
```
/rtc-balance <wallet_name>
```

## Description

Check the RTC balance of any RustChain wallet without leaving Claude Code.

## Examples

```
/rtc-balance nox-ventures
/rtc-balance my-miner
```

## Output Format

```
⚡ RustChain Wallet Balance
━━━━━━━━━━━━━━━━━━━━━━━━━
👛 Wallet: {wallet_name}
💰 Balance: {balance} RTC
💵 USD (~): ${usd_value}
⛏ Miners online: {miner_count}
📅 Epoch: {epoch_number}
⏱ Next epoch in: {time_remaining}
```

## Error Handling

- If wallet not found: "❌ Wallet '{wallet}' not found on RustChain"
- If node offline: "❌ RustChain node unreachable. Try again later."
- If no wallet specified: "Usage: /rtc-balance <wallet_name>"

## API Calls

1. `GET https://50.28.86.131/health` — Check node is online
2. `GET https://50.28.86.131/wallet/balance?wallet_id={wallet}` — Get balance
3. `GET https://50.28.86.131/api/miners` — Get miner count

## Notes

- Uses the live RustChain node at https://50.28.86.131
- Balance is in RTC units (1 RTC ≈ $0.10 reference rate)
- No authentication required for balance reads
