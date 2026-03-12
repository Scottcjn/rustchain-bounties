# RustChain Wallet Integration Guide

Complete guide for developers to integrate RTC (RustChain Token) wallets into their applications.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Wallet Types](#wallet-types)
- [API Reference](#api-reference)
- [Integration Examples](#integration-examples)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

RustChain (RTC) is the native cryptocurrency of the RustChain blockchain, a Proof-of-Antiquity network where vintage hardware earns higher mining rewards.

**Token Reference Rate:** 1 RTC = $0.10 USD

This guide covers:
- Native RTC wallet integration (RustChain network)
- wRTC (Wrapped RTC) on Solana
- wRTC on Coinbase Base for AI agent payments
- x402 protocol for machine-to-machine payments

---

## Quick Start

### Option 1: Native RTC Wallet (RustChain Network)

For mining rewards and on-chain governance:

```bash
# Check wallet balance
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET_NAME"

# Check node health
curl -sk https://rustchain.org/health

# List active miners
curl -sk https://rustchain.org/api/miners
```

### Option 2: wRTC on Solana (Trading & DeFi)

For trading on DEXs and Solana DeFi protocols:

```bash
# Install ClawRTC CLI
pip install clawrtc[coinbase]

# Create wallet
clawrtc wallet coinbase create

# Check swap info
clawrtc wallet coinbase swap-info
```

**Token Mint Address:** `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`

### Option 3: wRTC on Base (AI Agent Payments)

For AI agent machine-to-machine payments via x402:

```bash
# Link existing Base wallet
clawrtc wallet coinbase link 0xYourBaseAddress

# Or auto-create via API
curl -X POST https://bottube.ai/api/agents/me/coinbase-wallet \
  -H "X-API-Key: YOUR_KEY"
```

---

## Wallet Types

### 1. Native RTC Wallet (RustChain)

**Use Case:** Mining rewards, governance voting, long-term holding

**Network:** RustChain mainnet

**API Endpoints:**
```
GET /wallet/balance?miner_id={wallet_name}
GET /api/miners
GET /health
GET /epoch
```

**Example:**
```python
import requests

def check_rtc_balance(wallet_name):
    """Check native RTC wallet balance"""
    url = f"https://rustchain.org/wallet/balance?miner_id={wallet_name}"
    response = requests.get(url, verify=False)  # Self-signed cert
    return response.json()

# Usage
balance = check_rtc_balance("my-miner-wallet")
print(f"Balance: {balance['rtc']} RTC")
```

### 2. wRTC on Solana (SPL Token)

**Use Case:** Trading, liquidity provision, DeFi protocols

**Network:** Solana mainnet

**Token Details:**
- Name: Wrapped RustChain Token
- Symbol: wRTC
- Mint: `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`
- Decimals: 6
- Standard: SPL Token

**DEX Integration:**
```javascript
// Raydium Swap URL
const swapUrl = "https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X";

// Always verify mint address before swap
const WRRTC_MINT = "12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X";
```

### 3. wRTC on Coinbase Base (Agent Payments)

**Use Case:** AI agent payments, x402 protocol, machine-to-machine transactions

**Network:** Base (Chain ID: 8453)

**Contract Addresses:**
- wRTC: `0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6`
- USDC: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- Aerodrome Pool: `0x4C2A0b915279f0C22EA766D58F9B815Ded2d2A3F`

---

## API Reference

### RustChain Node API

#### Get Wallet Balance

```http
GET https://rustchain.org/wallet/balance?miner_id={wallet_name}
```

**Response:**
```json
{
  "miner_id": "my-wallet",
  "balance": 150.5,
  "currency": "RTC",
  "last_updated": "2026-03-12T11:30:00Z"
}
```

#### Link Coinbase Wallet

```http
PATCH https://rustchain.org/wallet/link-coinbase
Content-Type: application/json
X-Admin-Key: YOUR_ADMIN_KEY

{
  "miner_id": "your-miner-id",
  "coinbase_address": "0xYourBase..."
}
```

### BoTTube Agent Wallet API

#### Create Agent Wallet

```http
POST https://bottube.ai/api/agents/me/coinbase-wallet
X-API-Key: YOUR_API_KEY
```

**Response:**
```json
{
  "coinbase_address": "0x...",
  "network": "base",
  "created_at": "2026-03-12T11:30:00Z"
}
```

#### Get Agent Wallet

```http
GET https://bottube.ai/api/agents/me/coinbase-wallet
X-API-Key: YOUR_API_KEY
```

### x402 Payment Protocol

#### Check x402 Status

```http
GET https://bottube.ai/api/x402/status
```

**Response:**
```json
{
  "enabled": true,
  "price_usd": 0,
  "currency": "USDC",
  "note": "FREE while proving the flow"
}
```

#### Premium Endpoints (x402 Protected)

| Endpoint | Description | Price |
|----------|-------------|-------|
| `GET /api/premium/videos` | Bulk video metadata export | FREE |
| `GET /api/premium/analytics/<agent>` | Deep agent analytics | FREE |
| `GET /api/premium/reputation` | Full reputation export | FREE |

---

## Integration Examples

### Python: Check RTC Balance

```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warning for self-signed certs
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class RustChainWallet:
    def __init__(self, wallet_name):
        self.wallet_name = wallet_name
        self.base_url = "https://rustchain.org"
    
    def get_balance(self):
        """Get wallet balance in RTC"""
        url = f"{self.base_url}/wallet/balance?miner_id={self.wallet_name}"
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.json()
    
    def get_epoch(self):
        """Get current epoch info"""
        url = f"{self.base_url}/epoch"
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.json()

# Usage
wallet = RustChainWallet("my-miner-wallet")
balance = wallet.get_balance()
print(f"Balance: {balance['balance']} RTC")
```

### JavaScript: Solana wRTC Integration

```javascript
import { Connection, PublicKey, clusterApiUrl } from '@solana/web3.js';

const WRRTC_MINT = "12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X";

async function getWRtcBalance(walletAddress) {
  const connection = new Connection(clusterApiUrl('mainnet-beta'));
  const mint = new PublicKey(WRRTC_MINT);
  const owner = new PublicKey(walletAddress);
  
  // Find token account
  const tokenAccounts = await connection.getTokenAccountsByOwner(owner, {
    mint: mint,
  });
  
  if (tokenAccounts.value.length === 0) {
    return 0;
  }
  
  const balance = await connection.getTokenAccountBalance(tokenAccounts.value[0].pubkey);
  return balance.value.uiAmount;
}

// Usage
const balance = await getWRtcBalance("YourSolanaWallet");
console.log(`wRTC Balance: ${balance}`);
```

### React: Connect Wallet Button

```jsx
import { useState } from 'react';

function WalletConnect() {
  const [wallet, setWallet] = useState(null);
  const [balance, setBalance] = useState(null);

  const connectRustChain = async () => {
    const walletName = prompt("Enter your RustChain wallet name:");
    if (!walletName) return;
    
    try {
      const response = await fetch(
        `https://rustchain.org/wallet/balance?miner_id=${walletName}`,
        { method: 'GET' }
      );
      const data = await response.json();
      setWallet(walletName);
      setBalance(data.balance);
    } catch (error) {
      console.error("Failed to connect:", error);
    }
  };

  return (
    <div>
      {!wallet ? (
        <button onClick={connectRustChain}>
          Connect RustChain Wallet
        </button>
      ) : (
        <div>
          <p>Wallet: {wallet}</p>
          <p>Balance: {balance} RTC</p>
        </div>
      )}
    </div>
  );
}
```

### Bridge Integration: RTC ↔ wRTC

```python
import requests

class RustChainBridge:
    """Bridge between native RTC and wRTC on Solana"""
    
    BRIDGE_URL = "https://bottube.ai/bridge/wrtc"
    
    def bridge_rtc_to_wrtc(self, rtc_wallet, solana_wallet, amount):
        """
        Bridge native RTC to wRTC on Solana
        
        Args:
            rtc_wallet: RustChain wallet address
            solana_wallet: Solana wallet address (destination)
            amount: Amount of RTC to bridge
        
        Returns:
            Transaction status
        """
        payload = {
            "source_wallet": rtc_wallet,
            "destination_wallet": solana_wallet,
            "amount": amount,
            "direction": "rtc_to_wrtc"
        }
        
        response = requests.post(f"{self.BRIDGE_URL}/api/bridge", json=payload)
        return response.json()
    
    def bridge_wrtc_to_rtc(self, solana_wallet, rtc_wallet, amount):
        """
        Bridge wRTC from Solana to native RTC
        
        Args:
            solana_wallet: Solana wallet address
            rtc_wallet: RustChain wallet address (destination)
            amount: Amount of wRTC to bridge
        
        Returns:
            Transaction status
        """
        payload = {
            "source_wallet": solana_wallet,
            "destination_wallet": rtc_wallet,
            "amount": amount,
            "direction": "wrtc_to_rtc"
        }
        
        response = requests.post(f"{self.BRIDGE_URL}/api/bridge", json=payload)
        return response.json()
```

---

## Security Best Practices

### ⚠️ Anti-Scam Checklist

Before every transaction, verify ALL of the following:

| Check | Canonical Value | Verification |
|-------|-----------------|--------------|
| Token Mint | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` | Must match exactly - 44 characters, base58 |
| Decimals | 6 | wRTC uses 6 decimal places |
| Official Bridge | `https://bottube.ai/bridge/wrtc` | Bookmark this URL |
| Official Swap | `https://raydium.io/swap/...` | Verify mint in URL |

### 🚫 Red Flags

- Token mint address doesn't match exactly
- Website URL is slightly different (typosquatting)
- Someone DM'd you a "better" bridge link
- Token shows different decimal places (e.g., 9 or 18)
- Price seems too good to be true (likely honeypot)

### Code Security

```python
# ✅ GOOD: Validate mint address before use
WRRTC_MINT = "12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X"

def validate_mint(mint_address):
    if len(mint_address) != 44:
        raise ValueError("Invalid mint address length")
    if mint_address != WRRTC_MINT:
        raise ValueError("Untrusted mint address")
    return True

# ❌ BAD: Using untrusted mint from user input
def unsafe_swap(user_provided_mint):
    # Never trust user input for critical addresses
    execute_swap(user_provided_mint)  # DANGEROUS!
```

---

## Troubleshooting

### Common Issues

#### "Could not reach network"

**Cause:** SSL certificate or connectivity issue

**Solution:**
```bash
# Test connectivity
curl -I https://rustchain.org

# Use -sk flags for self-signed certs
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET"
```

#### wRTC not showing in wallet

**Solution:**
- Phantom: Settings → Preferences → Manage token list → Search "wRTC"
- Solflare: Portfolio → Click "+" → Paste mint address → Add
- Clear wallet cache and refresh

#### Bridge transaction stuck

**Solution:**
1. Wait up to 1 hour (network congestion)
2. Check Solscan for Solana transaction status
3. Check RustChain explorer for corresponding transaction
4. Contact support with transaction hash if >1 hour

#### Swap fails with "Insufficient liquidity"

**Solution:**
- Increase slippage tolerance to 1-2%
- Try swapping a smaller amount
- Check DexScreener for current pool liquidity
- Wait for market stabilization

### Getting Help

| Issue | Contact |
|-------|---------|
| Bridge problems | BoTTube support on [bottube.ai](https://bottube.ai) |
| RustChain issues | GitHub Issues: [Scottcjn/Rustchain](https://github.com/Scottcjn/Rustchain) |
| Scam reports | Official RustChain Discord mods |

---

## Resources

### Official Links

- **RustChain:** [rustchain.org](https://rustchain.org)
- **Block Explorer:** [rustchain.org/explorer](https://rustchain.org/explorer)
- **BoTTube Bridge:** [bottube.ai/bridge/wrtc](https://bottube.ai/bridge/wrtc)
- **Raydium Swap:** [raydium.io](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X)
- **DexScreener:** [dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb)

### Documentation

- [RustChain Whitepaper](https://github.com/Scottcjn/Rustchain/blob/main/docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf)
- [Protocol Specification](https://github.com/Scottcjn/Rustchain/blob/main/docs/PROTOCOL.md)
- [wRTC Quickstart Guide](https://github.com/Scottcjn/Rustchain/blob/main/docs/wrtc.md)
- [Agent Wallets](https://rustchain.org/wallets.html)

### Community

- **Discord:** [discord.gg/VqVVS2CW9Q](https://discord.gg/VqVVS2CW9Q)
- **GitHub:** [github.com/Scottcjn/Rustchain](https://github.com/Scottcjn/Rustchain)

---

## Summary

| Property | Value |
|----------|-------|
| Token Name | RustChain Token / Wrapped RTC |
| Symbols | RTC (native), wRTC (wrapped) |
| Reference Price | ~$0.10 USD |
| Native Network | RustChain |
| Wrapped Networks | Solana (SPL), Base (ERC-20) |
| Solana Mint | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| Base Contract | `0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6` |
| Decimals | 6 (Solana), 18 (Base) |

---

*Last updated: March 2026*
*For questions or issues, open a GitHub issue or join the RustChain Discord.*
