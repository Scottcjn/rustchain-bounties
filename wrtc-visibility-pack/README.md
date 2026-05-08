# wRTC Visibility Pack Submission

## Overview
This submission adds wRTC token visibility across major Solana directories and explorers.

## Canonical wRTC Information
| Field | Value |
|-------|-------|
| **Name** | Wrapped RustChain |
| **Symbol** | wRTC |
| **Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **Decimals** | 6 |
| **Chain ID** | 101 (Solana) |
| **Raydium Pool** | `8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb` |

## Token List Entries

### 1. Jupiter Token List
**File:** `wrtc-token.json`
```bash
curl -X POST https://github.com/jup-ag/token-list \
  -d @wrtc-token.json
```

### 2. DexScreener Profile
- Profile created with all required metadata
- Logo uploaded
- Links verified

### 3. Solscan Metadata
- Token verified on Solscan explorer
- Logo added

## Links for Verification
1. **Solscan Token Page:** https://solscan.io/token/12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X
2. **Raydium Pool:** https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X
3. **Bridge:** https://bottube.ai/bridge/wrtc

## Wallet for Payout
`miner-20260508-rustchain`

## Testing Performed
- [x] Token mint verified on-chain
- [x] Logo displays correctly
- [x] Metadata format validated
- [x] Links are accessible