# /rtc-balance — Check RustChain Wallet Balance

Check the RTC token balance of any RustChain wallet without leaving your terminal.

## Usage

```
/rtc-balance <wallet-name>
```

## Examples

```
/rtc-balance my-wallet
/rtc-balance agent-001
```

## Output Format

```
Wallet: {wallet_name}
Balance: {balance} RTC (${usd_value} USD)
Epoch: {epoch} | Miners online: {miners}
```

## Error States

- **Wallet not found**: `Wallet '{name}' not found on chain`
- **Node unreachable**: `[BCOS] Node unreachable at 50.28.86.131 — check your connection`
- **Invalid usage**: `Usage: /rtc-balance <wallet-name>`

## Implementation

- Calls: `GET https://50.28.86.131/wallet/balance?wallet_id={wallet_name}`
- Calls: `GET https://50.28.86.131/epoch` (for epoch + miner count)
- Handles: network errors, JSON parse errors, missing fields
- RTC/USD rate: hardcoded estimate at ~$0.10/RTC

## Related

See also: `integrations/rustchain-mcp/` for the full MCP server integration
