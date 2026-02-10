# RustChain Wallet User Guide

Complete guide to managing RTC with RustChain wallets.

## Wallet Types

RustChain supports multiple wallet types:

1. **Testnet Wallet**: Any string (e.g., `alice`, `my-agent-name`)
2. **CLI Wallet**: Command-line interface wallet
3. **Web Wallet**: Browser-based wallet (coming soon)
4. **Hardware Wallet**: Ledger/Trezor support (coming soon)

## Creating a Wallet

### Testnet Wallet

Testnet wallets require no setup. Simply choose a unique identifier:

```bash
export WALLET_ID="my-wallet-$(date +%s)"
echo "Your wallet ID: $WALLET_ID"
```

### CLI Wallet (Production)

For production use with wRTC bridging:

```bash
pip install rustchain-cli
rustchain wallet create --name my-wallet
```

This generates:
- **Wallet ID**: Public identifier
- **Private Key**: Keep secret, never share
- **Seed Phrase**: 12-word backup phrase

**Save your seed phrase securely! Loss = permanent loss of funds.**

### Import Existing Wallet

```bash
rustchain wallet import --seed "word1 word2 word3 ... word12"
```

## Checking Balance

### Via API

```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

**Response:**
```json
{
  "wallet_id": "YOUR_WALLET_ID",
  "balance": 125.5,
  "pending": 2.3
}
```

### Via CLI

```bash
rustchain wallet balance --wallet YOUR_WALLET_ID
```

### Via Python

```python
from rustchain import RustChainClient

client = RustChainClient()
balance = client.get_balance("YOUR_WALLET_ID")
print(f"Balance: {balance['balance']} RTC")
```

## Receiving RTC

### Share Your Wallet ID

To receive RTC, provide your wallet ID to the sender:

```
Wallet ID: my-wallet-id
```

### Mining

Earn RTC by running a miner:

```bash
python3 rustchain_miner.py --wallet YOUR_WALLET_ID --node https://50.28.86.131
```

Rewards distributed per epoch (typically 1 hour).

### Bounties

Earn RTC by completing bounties on the [RustChain Bounty Board](https://github.com/Scottcjn/rustchain-bounties).

## Sending RTC

### CLI Transfer

```bash
rustchain wallet send \
  --from YOUR_WALLET_ID \
  --to RECIPIENT_WALLET_ID \
  --amount 10.0 \
  --key /path/to/private.key
```

### Python Transfer

```python
import hashlib
import time
import requests

def transfer_rtc(from_wallet, to_wallet, amount, private_key):
    timestamp = int(time.time())
    payload = f"{from_wallet}:{to_wallet}:{amount}:{timestamp}"
    signature = hashlib.sha256(f"{payload}:{private_key}".encode()).hexdigest()
    
    response = requests.post(
        "https://50.28.86.131/wallet/transfer",
        json={
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": amount,
            "signature": signature
        },
        verify=False
    )
    
    return response.json()

result = transfer_rtc(
    from_wallet="alice",
    to_wallet="bob",
    amount=10.0,
    private_key="your_private_key"
)

print(f"Transaction: {result['tx_hash']}")
```

### Verify Transaction

Check transaction on the explorer:

```
https://rustchain.org/explorer/tx/YOUR_TX_HASH
```

## Bridging to Solana (wRTC)

wRTC is the wrapped version of RTC on Solana, enabling trading on DEXes.

### RTC → wRTC (Deposit)

1. Visit [bottube.ai/bridge](https://bottube.ai/bridge)
2. Connect your Solana wallet (Phantom, Solflare, etc.)
3. Enter RustChain wallet ID
4. Enter amount to bridge
5. Confirm transaction
6. Wait 5-10 minutes for wRTC to arrive

**Via CLI:**

```bash
rustchain bridge deposit \
  --wallet YOUR_WALLET_ID \
  --amount 100.0 \
  --solana-address YOUR_SOLANA_ADDRESS
```

### wRTC → RTC (Withdraw)

1. Visit [bottube.ai/bridge](https://bottube.ai/bridge)
2. Connect Solana wallet
3. Enter RustChain wallet ID to receive RTC
4. Enter wRTC amount to withdraw
5. Confirm Solana transaction
6. Wait 5-10 minutes for RTC to arrive

**Via CLI:**

```bash
rustchain bridge withdraw \
  --solana-wallet YOUR_SOLANA_WALLET \
  --amount 100.0 \
  --rtc-wallet YOUR_WALLET_ID
```

## Trading wRTC

### Raydium DEX

Trade wRTC on [Raydium](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X):

1. Visit the link above
2. Connect Solana wallet
3. Select wRTC (token mint: `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`)
4. Enter amount to swap
5. Review slippage settings (0.5-1% recommended)
6. Confirm swap

### Price Chart

Monitor wRTC price on [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb).

## Security Best Practices

### Protect Your Private Key

- **Never share** your private key or seed phrase
- **Store offline** in a secure location
- **Use hardware wallet** for large amounts
- **Enable 2FA** on CLI wallet if available

### Verify Addresses

- **Double-check** recipient wallet ID before sending
- **Test with small amount** first
- **No undo**: RTC transfers are irreversible

### Beware of Scams

- **No admin** will ask for your private key
- **Verify URLs**: Only use official RustChain sites
- **Check token mint**: wRTC mint is `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`

## Wallet Recovery

### Lost Wallet ID

If you lost your wallet ID but have the private key:

```bash
rustchain wallet recover --key /path/to/private.key
```

### Lost Private Key

If you have the seed phrase:

```bash
rustchain wallet recover --seed "word1 word2 ... word12"
```

**No seed phrase or private key = permanent loss of funds.**

## Advanced Features

### Multi-Signature Wallet

Create a wallet requiring multiple signatures:

```bash
rustchain wallet create-multisig \
  --signers wallet1,wallet2,wallet3 \
  --threshold 2
```

### Scheduled Transfers

Schedule recurring transfers:

```bash
rustchain wallet schedule \
  --from YOUR_WALLET_ID \
  --to RECIPIENT \
  --amount 10.0 \
  --interval daily \
  --duration 30d
```

### Transaction History

```bash
rustchain wallet history --wallet YOUR_WALLET_ID --limit 50
```

**Via API:**

```bash
curl -sk "https://50.28.86.131/wallet/history?miner_id=YOUR_WALLET_ID&limit=50"
```

## Troubleshooting

### Balance Not Updating

**Problem:** Balance shows 0 after mining

**Solution:**
1. Wait for epoch completion (check `/epoch` endpoint)
2. Verify miner is running on real hardware (not VM)
3. Check wallet ID is correct

### Transfer Failed

**Problem:** Transfer returns error

**Solution:**
1. Check balance is sufficient
2. Verify recipient wallet ID
3. Ensure signature is valid (check private key)
4. Check node status: `curl -sk https://50.28.86.131/health`

### Bridge Stuck

**Problem:** wRTC not received after bridging

**Solution:**
1. Wait 10-15 minutes for finality
2. Check transaction status on Solana explorer
3. Verify Solana address is correct
4. Contact support: bridge@rustchain.org

### Lost Access

**Problem:** Forgot seed phrase and lost private key

**Solution:**
Unfortunately, funds are irrecoverable. There is no centralized recovery system.

## FAQ

**Q: What's the difference between RTC and wRTC?**
A: RTC is native to RustChain. wRTC is wrapped RTC on Solana for trading on DEXes.

**Q: Are there transaction fees?**
A: No. RTC transfers on RustChain are free.

**Q: How long do transfers take?**
A: RTC transfers are instant. Bridge transfers take 5-10 minutes.

**Q: Can I mine to multiple wallets?**
A: Yes. Run separate miner instances with different wallet IDs.

**Q: Is there a wallet app?**
A: Web and mobile wallets are coming soon. CLI wallet available now.

## Next Steps

- [Miner Setup Guide](miner-setup-guide.md) - Start earning RTC
- [Python SDK Tutorial](python-sdk-tutorial.md) - Automate wallet operations
- [API Reference](api-reference.md) - Full API documentation
