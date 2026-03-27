# Advanced wRTC Guide

This guide covers advanced topics for wRTC users, developers, and integrators.

## Table of Contents

- [Developer APIs](#developer-apis)
- [Integration Guide](#integration-guide)
- [Mining Setup](#mining-setup)
- [Bridge Technical Details](#bridge-technical-details)
- [Token Economics](#token-economics)

## Developer APIs

### Solana Token Program

wRTC is an SPL Token on Solana. Use the following details for integration:

```javascript
const WRTC_MINT = "12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X";
const WRTC_DECIMALS = 6;
```

### Reading wRTC Balance

```typescript
import { Connection, PublicKey } from '@solana/web3.js';
import { Token } from '@solana/spl-token';

async function getWRTCBalance(walletAddress: string) {
  const connection = new Connection('https://api.mainnet-beta.solana.com');
  const wallet = new PublicKey(walletAddress);
  const mintPubkey = new PublicKey(WRTC_MINT);

  const tokenAccounts = await connection.getTokenAccountsByOwner(wallet, {
    mint: mintPubkey
  });

  if (tokenAccounts.value.length === 0) {
    return 0;
  }

  const accountInfo = await connection.getTokenAccountBalance(
    tokenAccounts.value[0].pubkey
  );

  return parseFloat(accountInfo.value.amount) / Math.pow(10, WRTC_DECIMALS);
}
```

### Transferring wRTC

```typescript
import {
  Connection,
  Keypair,
  PublicKey,
  Transaction
} from '@solana/web3.js';
import {
  Token,
  TOKEN_PROGRAM_ID
} from '@solana/spl-token';

async function transferWRTC(
  fromKeypair: Keypair,
  toAddress: string,
  amount: number
) {
  const connection = new Connection('https://api.mainnet-beta.solana.com');
  const mintPubkey = new PublicKey(WRTC_MINT);
  const toPubkey = new PublicKey(toAddress);

  // Get sender's token account
  const fromTokenAccount = await Token.getAssociatedTokenAddress(
    TOKEN_PROGRAM_ID,
    mintPubkey,
    fromKeypair.publicKey
  );

  // Get or create recipient's token account
  const toTokenAccount = await Token.getAssociatedTokenAddress(
    TOKEN_PROGRAM_ID,
    mintPubkey,
    toPubkey
  );

  const transaction = new Transaction().add(
    Token.createTransferInstruction(
      TOKEN_PROGRAM_ID,
      fromTokenAccount,
      toTokenAccount,
      fromKeypair.publicKey,
      [],
      amount * Math.pow(10, WRTC_DECIMALS)
    )
  );

  const signature = await connection.sendTransaction(
    transaction,
    [fromKeypair]
  );

  await connection.confirmTransaction(signature);
  return signature;
}
```

## Integration Guide

### Adding wRTC to Your DApp

#### 1. Display wRTC Balance

```javascript
// React example using @solana/web3.js
import { useConnection, useWallet } from '@solana/wallet-adapter-react';

function WalletBalance() {
  const { connection } = useConnection();
  const { publicKey } = useWallet();

  const [balance, setBalance] = useState(0);

  useEffect(() => {
    if (!publicKey) return;

    const fetchBalance = async () => {
      const tokenAccounts = await connection.getTokenAccountsByOwner(
        publicKey,
        { mint: new PublicKey(WRTC_MINT) }
      );

      if (tokenAccounts.value.length > 0) {
        const accountInfo = await connection.getTokenAccountBalance(
          tokenAccounts.value[0].pubkey
        );
        setBalance(parseFloat(accountInfo.value.amount) / 1e6);
      }
    };

    fetchBalance();
  }, [publicKey, connection]);

  return <div>wRTC Balance: {balance} wRTC</div>;
}
```

#### 2. Swap Integration (Jupiter)

```javascript
import { Jupiter, RouteInfo, TOKEN_LIST_URL } from '@jup-ag/core';

async function swapToWRTC(wallet, amountInSol) {
  const jupiter = await Jupiter.load({
    connection,
    wallet,
    routeMap: (await fetch(TOKEN_LIST_URL)).json()
  });

  const routes = await jupiter.computeRoutes({
    inputMint: new PublicKey('So11111111111111111111111111111111111111112'), // SOL
    outputMint: new PublicKey(WRTC_MINT),
    inputAmount: amountInSol * 1e9, // SOL decimals
    slippageBps: 50 // 0.5%
  });

  if (routes!.routesInfos.length === 0) {
    throw new Error('No routes found');
  }

  const { execute } = await jupiter.exchange({
    routeInfo: routes!.routesInfos[0]
  });

  const result = await execute();
  return result.txid;
}
```

### Building with wRTC

#### Tipping Integration

```typescript
interface TipRequest {
  creatorId: string;
  amount: number; // wRTC amount
  message?: string;
}

async function tipCreator(
  wallet: Keypair,
  request: TipRequest
): Promise<string> {
  // 1. Convert wRTC to BoTTube credits via bridge
  const bridgeTx = await bridgeWRTCToCredits(
    wallet.publicKey,
    request.amount
  );

  // 2. Send credits to creator
  const tipTx = await sendTipToCreator({
    creatorId: request.creatorId,
    amount: request.amount,
    message: request.message
  });

  return tipTx.signature;
}
```

## Mining Setup

### Prerequisites

- Linux or macOS system
- Python 3.8+
- Hardware with GPU (optional but recommended)
- RustChain miner software

### Installation

```bash
# Clone the repository
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties/miner

# Install dependencies
pip install -r requirements.txt

# Configure miner
cp config.example.yaml config.yaml
nano config.yaml
```

### Configuration

```yaml
# config.yaml
miner:
  wallet_address: "your_wallet_address"
  thread_count: 4
  gpu_enabled: true
  gpu_device: 0

network:
  rpc_url: "https://mainnet.rustchain.ai"
  pool_address: "pool.rustchain.ai:8888"

rewards:
  auto_bridge: true
  bridge_destination: "wrtc"
  minimum_payout: 100
```

### Running the Miner

```bash
# Start the miner
python miner.py --config config.yaml

# Monitor logs
tail -f logs/miner.log

# Check status
python status.py
```

### Performance Optimization

1. **GPU Configuration:**
   ```yaml
   gpu:
     enabled: true
     device: 0
     batch_size: 32
     memory_limit: 4096
   ```

2. **Network Optimization:**
   ```yaml
   network:
     connection_pool_size: 10
     request_timeout: 30
     retry_attempts: 3
   ```

3. **Power Management:**
   ```yaml
   power:
     max_power_consumption: 500  # Watts
     thermal_throttling: true
     auto_shutdown: false
   ```

## Bridge Technical Details

### Bridge Architecture

The wRTC bridge operates as a two-way peg system:

```
┌─────────────────┐
│  RustChain L1   │
│   (Native RTC)  │
└────────┬────────┘
         │
         │ Bridge Transaction
         │
┌────────▼────────┐
│  Bridge Contract │
│   (Solana)       │
└────────┬────────┘
         │
         │ Mint/Burn
         │
┌────────▼────────┐
│  wRTC (SPL)     │
│   (Solana)      │
└─────────────────┘
```

### Bridge Transaction Flow

**RTC → wRTC:**
1. User initiates bridge on RustChain L1
2. User locks native RTC in bridge contract
3. Bridge contract emits event
4. Oracle validates transaction
5. wRTC minted to user's Solana address

**wRTC → RTC:**
1. User burns wRTC on Solana
2. Bridge contract verifies burn
3. Bridge contract unlocks native RTC
4. Native RTC sent to user's RustChain address

### Bridge Smart Contract Address

```
Solana Bridge: FUTURE_ADDRESS_HERE
RustChain Bridge: FUTURE_ADDRESS_HERE
```

### Bridge Fees

| Direction | Fee | Notes |
|-----------|-----|-------|
| RTC → wRTC | 0.5% | + gas fees |
| wRTC → RTC | 0.5% | + gas fees |
| Minimum | 0.001 wRTC | Anti-spam |

### Monitoring Bridge Transactions

```typescript
import { Connection, PublicKey } from '@solana/web3.js';

async function monitorBridgeTransactions() {
  const connection = new Connection('https://api.mainnet-beta.solana.com');
  const bridgeAddress = new PublicKey('BRIDGE_ADDRESS');

  const signatures = await connection.getSignaturesForAddress(
    bridgeAddress,
    { limit: 10 }
  );

  for (const sig of signatures) {
    const tx = await connection.getParsedTransaction(sig.signature);
    console.log('Bridge Transaction:', tx);
  }
}
```

## Token Economics

### Supply Mechanics

- **Total Supply:** Capped at 1,000,000,000 RTC
- **wRTC Supply:** Bridge-governed (max = total RTC supply)
- **Circulating Supply:** Dynamic based on bridge deposits

### Inflation Schedule

| Year | Annual Inflation | Daily Emissions |
|------|-------------------|-----------------|
| 1 | 10% | ~274,000 RTC |
| 2 | 8% | ~219,000 RTC |
| 3 | 6% | ~164,000 RTC |
| 4 | 4% | ~110,000 RTC |
| 5+ | 2% | ~55,000 RTC |

### Value Drivers

1. **Mining Demand:** Compute power required for AI agents
2. **Tipping Utility:** BoTTube creator economy
3. **Bridge Activity:** Cross-chain liquidity
4. **Staking Returns:** APY from network fees
5. **Governance:** Voting power on protocol upgrades

### Token Distribution

- **Mining Rewards:** 70%
- **Team & Advisors:** 15% (vested 4 years)
- **Community Treasury:** 10%
- **Foundation:** 5%

## Security Considerations

### Smart Contract Audits

- ✅ RustChain Bridge: Pending Audit
- ✅ wRTC SPL Implementation: Standard SPL Program
- 🚀 Scheduled: Q2 2026 full security audit

### Best Practices for Developers

1. **Always verify contract addresses**
2. **Use official SDKs when available**
3. **Test on devnet before mainnet**
4. **Implement proper error handling**
5. **Monitor gas prices and optimize transactions**

### Known Vulnerabilities

None reported as of 2026-02-14. Report issues via [GitHub Security](https://github.com/Scottcjn/rustchain-bounties/security).

## Troubleshooting

### Common Issues

#### Bridge Stuck

```bash
# Check bridge status
curl https://api.rustchain.ai/bridge/status

# Restart bridge transaction
python scripts/restart_bridge.py --tx <tx_id>
```

#### Balance Not Updating

```javascript
// Force refresh wallet balance
await connection.refresh();
```

#### Transaction Failed

- Check SOL balance for gas fees
- Verify token allowance if using DEX
- Increase slippage tolerance
- Check network congestion

## API Reference

### RustChain API

#### Get Token Info
```http
GET /api/v1/token/wrtc
```

#### Get Bridge Status
```http
GET /api/v1/bridge/status
```

#### Get Mining Stats
```http
GET /api/v1/mining/stats?wallet=<address>
```

### BoTTube API

#### Tip Creator
```http
POST /api/v1/tip
{
  "creator_id": "string",
  "amount": number,
  "message": "string (optional)",
  "tx_signature": "string"
}
```

#### Get Creator Balance
```http
GET /api/v1/creator/<id>/balance
```

## Contributing

We welcome contributions to the wRTC ecosystem!

### Reporting Issues

1. Search existing issues on [GitHub](https://github.com/Scottcjn/rustchain-bounties)
2. Create a new issue with detailed description
3. Include code examples or logs if applicable

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit PR with clear description

### Developer Discord

Join our developer community for real-time support:
[Discord Link](https://discord.gg/rustchain)

## License

MIT License - See LICENSE file for details.

## Contact

- **Technical Support:** support@rustchain.ai
- **Business Inquiries:** business@rustchain.ai
- **Security:** security@rustchain.ai

---

**Version:** 1.0.0
**Last Updated:** 2026-02-14
