# Agent-to-Agent Payments Stack (RustChain Issue #35)

Production-grade Agent-to-Agent payment infrastructure for **RustChain** and **BoTTube**, implementing Upvote+Donate micropayments, bidirectional RTC ↔ BoTTube cross-wallet bridging, 8004/x402 HTTP micropayment protocol with automated client negotiation, and dual-currency escrow with multi-party settlements.

---

## 🌟 Key Capabilities & Milestones

### Milestone 1: Upvote + Donate System (75 RTC)
- **Free Upvotes:** Signal of approval and content reputation with zero token cost.
- **Upvote + Donate:** Direct RTC micropayment transfer to creator's address.
- **Configurable Tiers:** Standard presets (`0.001`, `0.01`, `0.1`, `1.0` RTC) and custom arbitrary positive amounts.
- **Hardware Multiplier Integration:** Native support for vintage node multipliers (e.g. G4 PowerPC at 2.5x, IBM POWER8 at 3.0x).
- **Content Analytics:** Aggregated metrics, unique voter counts, tier distribution, and top donor leaderboards.
- **True Cryptography:** Ed25519 signed transaction verification on all RTC donations with anti-spam & sliding-window rate limiting.

### Milestone 2: Cross-Wallet Bridge: RTC ↔ BoTTube (100 RTC)
- **Bidirectional Conversion:** Atomic conversion between RustChain native RTC and BoTTube platform tokens.
- **Thread-Safe Escrow:** State machine managing lock, settlement, and refund transitions (`PENDING`, `LOCKED`, `SETTLED`, `REFUNDED`, `FAILED`).
- **Configurable Economics:** Adjustable exchange rates (default 1:1) and customizable bridge fee basis points (default 0.1% / 10 bps).
- **Tamper-Evident Receipts:** SHA256 hashed and Ed25519 signed receipts generated for each bridge transaction leg.

### Milestone 3: Agent-to-Agent x402 Micropayments (8004/x402) (75 RTC)
- **Server Middleware / Decorator (`@require_rtc_payment`):** Automatically challenges unpaid requests with HTTP 402, `WWW-Authenticate`, and structured `X-Payment-Required` challenge headers.
- **Intelligent AutoPay Client (`AutoPayClient`):** Intercepts HTTP 402 responses, verifies challenge parameters, signs the cryptographic Ed25519 payment proof, attaches `X-Payment`, and transparently replays the request to deliver HTTP 200 OK.
- **Cryptographic Nonce & Replay Defense:** Strictly prevents duplicate execution and replay attacks.
- **Agent Workflows:**
  - AI Inference queries (`0.001 RTC`)
  - Automated PR & Code reviews (`0.01 RTC`)
  - Real-time data feed streaming (`0.005 RTC`)
  - Cross-platform agent tipping (`0.1 RTC`)

### Milestone 4: Cross-Bounty Dual Escrow (50 RTC)
- **Dual-Currency Escrow:** Simultaneous deposit of RTC and BoTTube tokens into programmatic escrow.
- **Multi-Party Split Settlements:** Configurable payout ratios between solution claimant and reviewers (e.g., 80% claimant / 20% auditor).
- **Cross-Platform Reputation Booster:** Tracks completed bounties, total earnings, and reputation scores linked across RustChain and BoTTube identities.
- **Automated Refund Mechanism:** Allows bounty creators to cancel and recover unfulfilled escrow funds.

---

## 🏛️ Architecture Overview

```
 ┌────────────────────────────────────────────────────────────┐
 │                  Autonomous Agent Workflow                 │
 └──────────────────────────────┬─────────────────────────────┘
                                │
       ┌────────────────────────┼────────────────────────┐
       ▼                        ▼                        ▼
┌──────────────┐       ┌─────────────────┐      ┌─────────────────┐
│   Upvote +   │       │  Cross-Wallet   │      │ 8004/x402 M2M   │
│    Donate    │       │     Bridge      │      │   HTTP Gateway  │
│  (Milestone 1│       │  (Milestone 2)  │      │  (Milestone 3)  │
└──────┬───────┘       └────────┬────────┘      └────────┬────────┘
       │                        │                        │
       └────────────────────────┼────────────────────────┘
                                │
                                ▼
              ┌──────────────────────────────────┐
              │    Cross-Bounty Dual Escrow      │
              │  (RTC + BoTTube Tokens - M4)     │
              └─────────────────┬────────────────┘
                                │
                                ▼
              ┌──────────────────────────────────┐
              │   Cryptographic Receipts &       │
              │      Audit Trail Chaining        │
              └──────────────────────────────────┘
```

---

## 🚀 Quick Start & Integration

### 1. Python SDK Usage

```python
from rustchain_sdk import (
    RustChainWallet,
    UpvoteDonateService,
    CrossWalletBridge,
    AutoPayClient,
    DonationTier,
)

# 1. Create agent wallet
wallet = RustChainWallet.create()

# 2. Upvote and donate to a creator
service = UpvoteDonateService()
res = service.upvote_donate(
    content_id="post_123",
    voter=wallet.address,
    creator="RTC_CREATOR_ADDRESS",
    amount=DonationTier.SMALL, # 0.01 RTC
    wallet=wallet,
    hardware_multiplier=2.5,   # G4 Node
)
print("Donation receipt:", res["receipt"]["receipt_id"])

# 3. Bridge RTC to BoTTube tokens
bridge = CrossWalletBridge()
tx = bridge.rtc_to_botttube(
    rtc_address=wallet.address,
    botttube_user="agent_atlas",
    amount=10.0,
    rtc_wallet=wallet,
)
print(f"Bridged 10 RTC to {tx.net_amount} BoTTube tokens")
```

### 2. Protecting APIs with `@require_rtc_payment`

```python
from flask import Flask, jsonify
from rustchain_sdk import require_rtc_payment

app = Flask(__name__)

@app.route("/api/inference", methods=["POST"])
@require_rtc_payment(price=0.001, recipient="RTC_PROVIDER_ADDRESS", service_name="LLM Inference")
def inference_service():
    return jsonify({"output": "Inference completed successfully"})
```

### 3. Client Automated 402 Auto-Payment

```python
from rustchain_sdk import AutoPayClient, RustChainWallet
import requests

payer_wallet = RustChainWallet.create()
client = AutoPayClient(wallet=payer_wallet)

def call_endpoint(headers):
    return requests.post("http://localhost:8004/api/inference", json={"prompt": "Hello"}, headers=headers)

# AutoPayClient handles the 402 challenge, signs Ed25519 proof, and retries seamlessly:
response = client.execute_with_auto_pay(call_endpoint, max_price=0.005)
print(response.json())
```

---

## 🧪 Verification & Test Suite

The test suite runs with **zero mocks** for cryptographic operations, testing real Ed25519 keypairs, signing, verification, and tamper detection.

```bash
# Run comprehensive Issue #35 test suite
pytest tests/test_agent_payments_bounty35.py -v

# Run interactive multi-agent demo
PYTHONPATH=sdk/python python3 submissions/bounty-35-agent-payments/demo.py
```

---

## 🔒 Security & Anti-Cheat Protocols

1. **No Cryptographic Forgery:** Pure native Ed25519 signing and verification via `cryptography` hazard-free primitives.
2. **Replay Attack Resistance:** Unique nonces and short-window validity checking prevents re-use of valid payment signatures.
3. **Audit Trail Immutability:** Every receipt contains `prev_hash` cryptographic chaining verified by `CryptographicReceiptManager`.
4. **Anti-Spam & Rate Limiting:** Sliding-window rate limiters prevent flood attacks on upvotes and payment gateways.

---

## Payout Routing
- **EVM (Base/Arbitrum/Polygon/ETH):** `0xF46C9F6d70C50BF81ef3588AB523a90a594a2F89`
- **Stellar:** `GCL6OXAMLD75BMTINA6EMRUDWK5THQUSHMYNLSNBCJAPZJHNYJTUNIBC`
