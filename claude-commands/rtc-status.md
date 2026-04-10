# rtc-status — Check RustChain Network Status

## Usage
```
/rtc-status
```

## Description

Check the overall health and status of the RustChain network.

## Output Format

```
🔧 RustChain Network Status
━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 Status: Online
📋 Version: {version}
⏱ Uptime: {uptime_hours}h
⛏ Active Miners: {miner_count}
📅 Current Epoch: {epoch_number}
⏰ Next epoch in: {time_remaining}
💰 Total RTC in circulation: {estimated_supply}
```

## Error Handling

- If node offline: "❌ RustChain node unreachable"
