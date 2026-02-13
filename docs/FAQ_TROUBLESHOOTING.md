# RustChain FAQ & Troubleshooting

Frequently asked questions and solutions to common issues.

---

## General Questions

### What is RustChain?

RustChain is a decentralized blockchain using RIP-200 Proof-of-Attestation consensus. It rewards miners for contributing computational power with hardware fingerprinting to ensure fairness.

### What is RIP-200?

RIP-200 (RustChain Improvement Proposal 200) defines the Proof-of-Attestation consensus mechanism that:
- Uses CPU for mining (no GPU/ASIC advantage)
- Validates real hardware (VMs earn nothing)
- Rewards vintage hardware with bonus multipliers
- Provides 1.5 RTC per epoch to active miners

### What is RTC?

RTC (RustChain Token) is the native cryptocurrency of the RustChain network. Used for:
- Transaction fees
- Staking rewards
- Bounty payments
- Network governance

---

## Mining FAQ

### How do I start mining?

```bash
# Download miner
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py

# Run miner
python3 rustchain_miner.py --wallet YOUR_WALLET_ID --node https://50.28.86.131
```

### Why am I not earning rewards?

**Common reasons:**

| Reason | Solution |
|--------|-----------|
| Running in VM | Use real hardware |
| Not in miner list yet | Wait 5-10 minutes |
| Firewall blocking | Allow outbound connections |
| Node unreachable | Check node URL |
| Low hashrate | More CPU = more rewards |

### Does RustChain detect VMs?

**Yes!** RustChain actively detects virtual machines:
- VMware, VirtualBox, QEMU, KVM
- Cloud VMs (AWS, GCP, Azure)
- Any emulated environment

**VMs will not earn rewards.**

### What hardware multipliers exist?

| Architecture | Multiplier | Notes |
|--------------|------------|-------|
| PowerPC G4 | **2.5x** | Highest bonus! |
| PowerPC G5 | **2.0x** | Vintage bonus |
| PowerPC G3 | **1.8x** | Legacy bonus |
| Pentium 4 | **1.5x** | Retro bonus |
| Retro x86 | **1.4x** | Older x86 |
| Apple Silicon | **1.2x** | M1/M2/M3 |
| Modern x86_64 | **1.0x** | Standard |

### Can I mine with multiple computers?

**Yes!** Each computer needs:
- Unique wallet ID (recommended)
- Separate mining process
- All point to same node URL

```bash
# Computer 1
python3 rustchain_miner.py --wallet "miner-1" --node https://50.28.86.131

# Computer 2
python3 rustchain_miner.py --wallet "miner-2" --node https://50.28.86.131
```

---

## Wallet FAQ

### How do I create a wallet?

```bash
# CLI wallet
rustchain-wallet create my-wallet

# Online: https://wallet.rustchain.io
```

### Is my recovery phrase secure?

**Yes, if you protect it:**
- Write on paper, store safely
- Never share online
- Never input on phishing sites
- Consider metal backup for fire protection

### Can I recover my wallet without phrase?

**No!** The recovery phrase is the master key. Without it:
- No password reset
- No account recovery
- No alternative access

**Write it down!**

### How long do transactions take?

| Transaction Type | Time |
|-----------------|------|
| Standard | ~2 seconds |
| Priority | ~0.5 seconds |

### What are transaction fees?

| Fee Type | Cost |
|----------|------|
| Standard | 0.001 RTC |
| Priority | 0.005 RTC |
| Minimum | 0.0001 RTC |

---

## Staking FAQ

### How does staking work?

1. Delegate RTC to a validator
2. Validator includes your stake in consensus
3. Earn share of epoch rewards
4. Unbonding takes 21 days

### What is the unbonding period?

**21 days** - After undelegating, your RTC is locked for 21 days before becoming transferable.

### Can I lose staked RTC?

** slashing may occur for:**
- Validator going offline frequently
- Validator trying to attack network
- Double-signing transactions

**Delegators share validator's slashing risk.**

---

## Technical FAQ

### What is the current epoch?

```bash
curl -sk https://50.28.86.131/epoch
```

### How many miners are active?

```bash
curl -sk https://50.28.86.131/api/miners | python3 -c "import sys,json; print(f'Active miners: {len(json.load(sys.stdin))}')"
```

### Can I run a full node?

**Yes!** See [NODE_OPERATOR_GUIDE.md](./NODE_OPERATOR_GUIDE.md)

### What ports need to be open?

| Direction | Port | Purpose |
|-----------|------|---------|
| Outbound | 443 | HTTPS API |
| Outbound | 80 | HTTP fallback |
| Inbound (optional) | 8080 | RPC server |

---

## Bounty FAQ

### How do I claim a bounty?

1. Find bounty issue labeled "bounty"
2. Comment with wallet ID
3. Do the work, submit PR
4. Maintainer reviews and approves
5. RTC transferred to your wallet

### When do I get paid?

**After PR is merged:**
- Bounty owner receives notification
- Owner releases payment via x402
- RTC arrives in wallet within 30 seconds

### How to track payouts?

```bash
# Check balance
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

---

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to node

```bash
# Test connectivity
curl -sk https://50.86.131/health

# If fails:
# 1. Check internet connection
# 2. Verify URL is correct
# 3. Try with -v for verbose output
# 4. Check firewall rules
```

**Solution:**
```bash
# Firewall (Ubuntu)
sudo ufw allow 443
sudo ufw allow 80

# Test with verbose
curl -v -sk https://50.28.86.131/health
```

---

### Miner Not Appearing

**Problem:** Miner running but not in list

```bash
# Check if miner is running
ps aux | grep rustchain

# Check logs
tail -f miner.log

# Common fixes:
# 1. Wait 5-10 minutes for first attestation
# 2. Verify node URL is correct
# 3. Check wallet ID format
# 4. Ensure real hardware (not VM)
```

**Diagnostic:**
```bash
# Check node health
curl -sk https://50.28.86.131/health

# Check your balance (proves wallet exists)
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_ID"
```

---

### Balance Not Updating

**Problem:** Sent RTC but balance unchanged

**Explanation:**
- Transactions need block confirmations
- Typically 1-2 blocks for finality

**Solution:**
```bash
# Wait 2-5 minutes
# Check transaction status
# View transaction history
```

---

### Transaction Stuck

**Problem:** Transaction pending for >5 minutes

**Solutions:**

1. **Increase gas price:**
```bash
rustchain-wallet send \
  --to "0x..." \
  --amount 10 \
  --gas-price 0.005
```

2. **Wait for natural processing**
3. **Contact support if >30 minutes**

---

### Wallet Import Failed

**Problem:** Cannot import existing wallet

**Check recovery phrase:**
```bash
# Must be exactly 12 words
# No extra spaces
# No capitalization differences
# Words must be in English dictionary
```

**Common mistakes:**
- Extra space at beginning/end
- Words in wrong order
- Typos in similar words (e.g., "apple" vs "appel")

---

### Out of Memory

**Problem:** Node or miner using too much RAM

**Solutions:**
```bash
# Check memory usage
free -h

# Reduce mining intensity
python3 rustchain_miner.py --wallet "id" --low-memory

# For nodes: reduce cache
# Edit config.toml:
# [storage]
# cache_size_mb = 128
```

---

### Hardware Not Detected

**Problem:** Bonus multiplier not applied

**Diagnosis:**
```bash
# Check your entry in miners list
curl -sk https://50.28.86.131/api/miners | \
  python3 -c "import sys,json; \
  m=[x for x in json.load(sys.stdin) if 'YOUR_ID' in x['miner']]; \
  print(m[0] if m else 'Not found')"
```

**Causes:**
- VM detected (1.0x multiplier)
- New hardware (takes time to fingerprint)
- Network issue preventing attestation

---

## Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `ECONNREFUSED` | Cannot reach node | Check URL, firewall |
| `ETIMEDOUT` | Connection timeout | Retry, check internet |
| `ENODATA` | No DNS record | Verify domain |
| `ECONNRESET` | Connection dropped | Retry |
| `EADDRINUSE` | Port in use | Use different port |
| `VM_DETECTED` | Virtual machine | Use real hardware |
| `INVALID_WALLET` | Bad wallet ID | Check format |

---

## Support Channels

| Need | Contact |
|------|---------|
| Bug report | GitHub Issues |
| Mining help | Discord #mining |
| Wallet support | Discord #support |
| Bounty questions | Discord #bounties |
| General questions | Discord #general |

---

## Quick Reference

### Essential Commands

| Task | Command |
|------|---------|
| Start mining | `python3 rustchain_miner.py --wallet ID` |
| Check balance | `curl -sk "https://50.28.86.131/wallet/balance?miner_id=ID"` |
| Node health | `curl -sk https://50.28.86.131/health` |
| List miners | `curl -sk https://50.28.86.131/api/miners` |
| Current epoch | `curl -sk https://50.28.86.131/epoch` |

### Important URLs

| Service | URL |
|---------|-----|
| Node API | https://50.28.86.131 |
| Block Explorer | https://50.28.86.131/explorer |
| Web Wallet | https://wallet.rustchain.io |
| Bounty Board | https://github.com/Scottcjn/rustchain-bounties |
| Docs | https://docs.rustchain.io |

---

*Last updated: 2026-02-12*
*For RustChain v2.2.1-rip200*
