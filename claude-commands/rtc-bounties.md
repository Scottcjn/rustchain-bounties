# rtc-bounties — List Open RustChain Bounties

## Usage
```
/rtc-bounties [limit]
```

## Description

List open RustChain bounty issues from GitHub.

## Examples

```
/rtc-bounties
/rtc-bounties 10
```

## Output Format

```
💰 Open RustChain Bounties
━━━━━━━━━━━━━━━━━━━━━━━━━
#2861 | 50 RTC | Autonomous AI Agent That Claims Bounties
#2868 | 30 RTC | VS Code Extension — Wallet & Miner Dashboard
#2867 | 100RTC | Security Audit
...
```

## Error Handling

- If GitHub API fails: "❌ Could not fetch bounties"
