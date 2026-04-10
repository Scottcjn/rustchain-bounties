---
name: rtc-balance
description: Check RustChain wallet balance and epoch info
tools:
  - type: function
    function:
      name: check_rtc_balance
      description: Check RTC wallet balance and network status
      input_schema:
        type: object
        properties:
          wallet_id:
            type: string
            description: The wallet name or address to check
        required:
          - wallet_id
---

# RTC Balance Checker

You can check RTC wallet balances using the /rtc-balance command.

## Usage

```
/rtc-balance <wallet_id>
```

## Implementation

The skill calls the RustChain node API:
- Balance: GET https://50.28.86.131/wallet/balance?wallet_id={wallet_id}
- Epoch: GET https://50.28.86.131/epoch
- Miners: GET https://50.28.86.131/miners

## Example Output

When user runs /rtc-balance developer-wallet, respond with:

```
Wallet: developer-wallet
Balance: 42.50 RTC ($4.25 USD)
Epoch: 1847 | Miners online: 14
```

## Error Handling

If wallet not found:
```
Wallet not found: <wallet_id>
Please check the wallet name and try again.
```

If node offline:
```
Error: RustChain node is offline. Please try again later.
```