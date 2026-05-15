# Award RTC on PR Merge

A GitHub Action that automatically awards RustChain Token (RTC) when a pull request is merged.

## Usage

```yaml
name: Award RTC
on:
  pull_request:
    types: [closed]

jobs:
  award:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: onchito-walks/award-rtc-action@v1
        with:
          rtc-amount: '5'
          wallet-address: ${{ secrets.RTC_WALLET_ADDRESS }}
          rpc-endpoint: ${{ secrets.RUSTCHAIN_RPC_ENDPOINT }}
```

## Configuration

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `rtc-amount` | Yes | `5` | Amount of RTC to award |
| `wallet-address` | Yes | — | Recipient wallet address |
| `rpc-endpoint` | Yes | `https://rpc.rustchain.network` | RustChain RPC endpoint |

## How it works

1. Triggers on PR merge event
2. Submits award transaction to RustChain RPC
3. Posts a comment on the merged PR with the TX ID
4. Outputs the `rtc_tx_id` for downstream workflows

## License

MIT
