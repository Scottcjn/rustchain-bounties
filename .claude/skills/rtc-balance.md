# /rtc-balance

Check a RustChain wallet balance and network status from within Claude Code.

## Usage

```
/rtc-balance <wallet_id>
```

## Examples

```
/rtc-balance my-wallet
/rtc-balance developer-wallet
```

## What it does

When invoked, this skill:
1. Queries the RustChain node at `https://50.28.86.131/wallet/balance?wallet_id=<wallet_id>`
2. Queries current epoch info from `https://50.28.86.131/epoch`
3. Displays balance in RTC and USD (at $0.10/RTC)
4. Shows epoch number and active miner count
5. Handles errors gracefully (wallet not found, node offline)

## Implementation

Run this Python script with the wallet ID as argument:

```bash
python3 claude-slash-command/check_balance.py <wallet_id>
```

Or use inline:

```python
import urllib.request, json, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

NODE = "https://50.28.86.131"

def rtc_balance(wallet_id):
    try:
        r = urllib.request.urlopen(
            f"{NODE}/wallet/balance?wallet_id={wallet_id}",
            context=ctx, timeout=8
        )
        data = json.loads(r.read())
        balance = float(data.get("balance", 0))
        usd = balance * 0.10
        
        epoch_r = urllib.request.urlopen(f"{NODE}/epoch", context=ctx, timeout=8)
        epoch = json.loads(epoch_r.read())
        
        print(f"Wallet:  {wallet_id}")
        print(f"Balance: {balance:.2f} RTC (${usd:.2f} USD)")
        print(f"Epoch:   {epoch.get('epoch', '?')} | Miners online: {epoch.get('miners_online', '?')}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Wallet '{wallet_id}' not found on RustChain.")
        else:
            print(f"Node error: HTTP {e.code}")
    except Exception as e:
        print(f"Node offline or unreachable: {e}")
```

## Expected output

```
Wallet:  my-wallet
Balance: 42.50 RTC ($4.25 USD)
Epoch:   1847 | Miners online: 14
```

## Error output

```
Wallet 'unknown-wallet' not found on RustChain.
```

```
Node offline or unreachable: [Errno 111] Connection refused
```
