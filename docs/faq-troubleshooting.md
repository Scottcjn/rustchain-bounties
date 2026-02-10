# FAQ & Troubleshooting

Common questions and solutions for RustChain users.

## General Questions

### What is RustChain?

RustChain is a CPU-based blockchain using RIP-200 Proof-of-Attestation consensus. It rewards real hardware (especially vintage hardware) for participating in network attestation.

### What is RTC?

RTC (RustChain Token) is the native currency of RustChain. Total supply: 8.3M RTC. Reference rate: 1 RTC = $0.10 USD.

### What is wRTC?

wRTC is wrapped RTC on Solana, enabling trading on DEXes like Raydium. Token mint: `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`.

### How do I get RTC?

1. **Mining**: Run a miner to earn rewards
2. **Bounties**: Complete tasks on GitHub
3. **Trading**: Buy wRTC on Raydium, bridge to RTC
4. **Receive**: Accept transfers from other users

### Are there transaction fees?

No. RTC transfers on RustChain are completely free.

### How long do transfers take?

RTC transfers are instant. Bridge transfers (RTC ↔ wRTC) take 5-10 minutes.

## Mining Questions

### Can I mine on a VM?

No. VMs are detected and earn 0 rewards. RustChain requires real hardware to prevent large-scale VM farms.

### What hardware earns the most?

Vintage PowerPC hardware earns the highest multipliers:
- PowerPC G4: 2.5x
- PowerPC G5: 2.0x
- PowerPC G3: 1.8x

### How much can I earn per day?

Depends on hardware and uptime:
- Modern x86_64 (1.0x): ~1-2 RTC/day
- Apple Silicon (1.2x): ~1.5-2.5 RTC/day
- PowerPC G5 (2.0x): ~3-4 RTC/day

### Do I need to keep my computer on 24/7?

No, but uptime affects earnings. Rewards are proportional to uptime within each epoch (1 hour).

### Can I mine with multiple computers?

Yes. Run separate miner instances with the same wallet ID on each machine.

### Why is my balance not increasing?

Common reasons:
1. Mining on a VM (earns 0)
2. Incorrect wallet ID
3. Miner not connected to node
4. Waiting for epoch to complete

## Wallet Questions

### How do I create a wallet?

Testnet: Any string works (e.g., `alice`, `my-wallet-123`).

Production CLI:
```bash
rustchain wallet create --name my-wallet
```

### What if I lose my wallet ID?

If you have the private key or seed phrase, you can recover it:
```bash
rustchain wallet recover --seed "word1 word2 ... word12"
```

### What if I lose my private key and seed phrase?

Funds are irrecoverable. There is no centralized recovery system.

### Can I change my wallet ID?

No. Wallet IDs are immutable. Create a new wallet and transfer your RTC.

### How do I check my balance?

```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

## Bridge Questions

### How do I bridge RTC to wRTC?

Visit [bottube.ai/bridge](https://bottube.ai/bridge) and follow the instructions.

### How long does bridging take?

5-10 minutes for finality on both chains.

### Are there bridge fees?

Small Solana transaction fees (~0.000005 SOL) for minting/burning wRTC.

### Is the bridge safe?

Yes. Multi-signature contract, time-locks, and proof-of-reserve audits ensure security.

### Can I bridge back from wRTC to RTC?

Yes. Use the same bridge interface to withdraw.

## Trading Questions

### Where can I trade wRTC?

[Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X)

### What is the wRTC token mint address?

`12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`

### How do I view the price chart?

[DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb)

### What is the liquidity?

Check current liquidity on DexScreener or Raydium.

## Troubleshooting

### Miner Won't Start

**Error:** `Connection refused`

**Solution:**
1. Check node URL: `curl -sk https://50.28.86.131/health`
2. Verify firewall allows HTTPS (port 443)
3. Check Python version: `python3 --version` (must be 3.7+)

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
pip install requests
```

### Balance Shows 0

**Problem:** Mined for hours but balance is 0

**Solution:**
1. Verify not running in VM:
   ```bash
   systemd-detect-virt  # Should output "none"
   ```
2. Check wallet ID in miner command
3. Wait for epoch completion:
   ```bash
   curl -sk https://50.28.86.131/epoch
   ```
4. Check miner logs for errors

### Transfer Failed

**Error:** `Insufficient balance`

**Solution:**
Check balance before sending:
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

**Error:** `Invalid signature`

**Solution:**
Verify private key is correct and signature algorithm matches.

### Bridge Stuck

**Problem:** wRTC not received after deposit

**Solution:**
1. Wait 15 minutes for finality
2. Check Solana transaction on [Solscan](https://solscan.io)
3. Verify Solana address is correct
4. Contact support: bridge@rustchain.org

### High CPU Usage

**Problem:** Miner uses 100% CPU

**Solution:**
Limit threads:
```bash
python3 rustchain_miner.py --wallet YOUR_WALLET_ID --threads 2
```

### SSL Certificate Errors

**Error:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
Node uses self-signed certificate. Use `-k` flag:
```bash
curl -sk https://50.28.86.131/health
```

In Python:
```python
import requests
requests.get(url, verify=False)
```

### Node Connection Timeout

**Problem:** Miner can't connect to node

**Solution:**
1. Check internet connection
2. Verify node is online: `curl -sk https://50.28.86.131/health`
3. Try alternative node (if available)
4. Check firewall/proxy settings

### Rewards Lower Than Expected

**Problem:** Expected 2.0x multiplier but earning less

**Solution:**
1. Verify hardware is correctly detected:
   - Check miner logs for hardware fingerprint
2. Ensure uptime is high (rewards proportional to uptime)
3. Check epoch status: `curl -sk https://50.28.86.131/epoch`

### Python Version Issues

**Error:** `SyntaxError: invalid syntax`

**Solution:**
Upgrade Python:
```bash
python3 --version  # Must be 3.7+
sudo apt install python3.9  # Ubuntu
brew install python@3.9     # macOS
```

### Wallet Not Found

**Error:** `Wallet does not exist`

**Solution:**
Wallets are created on first use. Mine or receive a transfer to initialize.

### Database Errors (Node Operators)

**Error:** `FATAL: database "rustchain" does not exist`

**Solution:**
```bash
sudo -u postgres psql
CREATE DATABASE rustchain;
```

### Port Already in Use

**Error:** `Address already in use: 8443`

**Solution:**
Change port in config.yaml or kill existing process:
```bash
sudo lsof -i :8443
sudo kill -9 <PID>
```

## Performance Issues

### Slow API Responses

**Problem:** API calls take >1 second

**Solution:**
1. Check node load: `top` or `htop`
2. Add database indexes
3. Enable query caching in config.yaml
4. Use regional node closer to you

### High Memory Usage (Node)

**Problem:** Node using >8GB RAM

**Solution:**
Reduce connection pool in config.yaml:
```yaml
database:
  max_connections: 20
```

## Security Issues

### Suspicious Activity

**Problem:** Unauthorized transfers from wallet

**Solution:**
1. Immediately transfer remaining balance to new wallet
2. Check if private key was compromised
3. Review transaction history on explorer
4. Report to security@rustchain.org

### Phishing Attempts

**Warning Signs:**
- Emails asking for private keys
- Fake bridge sites
- Wrong token mint addresses

**Solution:**
Only use official URLs:
- Bridge: https://bottube.ai/bridge
- Raydium: https://raydium.io
- wRTC mint: `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`

## Getting Help

### Documentation

- [API Reference](api-reference.md)
- [Miner Setup Guide](miner-setup-guide.md)
- [Wallet User Guide](wallet-user-guide.md)
- [Node Operator Guide](node-operator-guide.md)

### Community Support

- **GitHub Issues**: [rustchain-bounties/issues](https://github.com/Scottcjn/rustchain-bounties/issues)
- **Discord**: discord.gg/rustchain (coming soon)
- **Email**: support@rustchain.org

### Reporting Bugs

Open an issue on GitHub with:
1. Description of the problem
2. Steps to reproduce
3. Expected vs actual behavior
4. System info (OS, Python version, hardware)
5. Relevant logs

### Feature Requests

Submit feature requests on GitHub:
1. Search existing requests first
2. Describe use case
3. Explain expected behavior
4. Consider submitting a bounty PR

## Next Steps

- [Miner Setup Guide](miner-setup-guide.md) - Start mining
- [Wallet User Guide](wallet-user-guide.md) - Manage your RTC
- [Contributing Guide](contributing-guide.md) - Help improve RustChain
