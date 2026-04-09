# /rtc-balance

Check your RustChain wallet balance from Claude Code.

## Usage

```
/rtc-balance <wallet_name>
```

## What it does

1. Fetches wallet balance from RustChain node API
2. Shows current epoch info
3. Displays active miners count

## Example

```
/rtc-balance my-wallet

Wallet: my-wallet
Balance: 42.50 RTC ($4.25 USD)
Epoch: 1847 | Miners online: 14
```

## Setup

No additional setup required. The command calls the public RustChain node API.

## Error Handling

- If wallet not found: "Wallet not found"
- If node offline: "RustChain node is offline. Try again later."
