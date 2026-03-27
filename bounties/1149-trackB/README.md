# Track B: wRTC ERC-20 on Base

**Bounty:** #1149 - Track B (75 RTC)  
**Status:** ✅ Implementation Complete  
**Deployer:** ma-moon

---

## 📋 Deliverables

| Item | Status | Location |
|------|--------|----------|
| ERC-20 Contract | ✅ Complete | `wRTC-ERC20.sol` |
| Deployment Script | ✅ Complete | `deploy.js` |
| Documentation | ✅ Complete | This file |
| BaseScan Verification | ⏳ Pending | After deployment |

---

## 🔧 Contract Specification

### Token Details

| Property | Value |
|----------|-------|
| Name | Wrapped RTC |
| Symbol | wRTC |
| Decimals | 6 (matches RTC) |
| Standard | ERC-20 + ERC-20Burnable |
| Access Control | Ownable |

### Features

1. **Mint/Burn for Bridge Integration**
   - `mint(address to, uint256 amount)` - Bridge can mint wRTC
   - `burn(uint256 amount)` - Users can burn wRTC
   - `burnFrom(address account, uint256 amount)` - Bridge can burn user tokens

2. **6 Decimal Precision**
   - Matches RTC main chain precision
   - Ensures 1:1 peg representation

3. **Ownable Access Control**
   - Owner can mint new tokens
   - Ownership transferable to bridge contract
   - `transferBridgeOwnership(address)` helper function

4. **Event Tracking**
   - `TokensMinted(address indexed to, uint256 amount)`
   - `TokensMinted(address indexed from, uint256 amount)`

---

## 🚀 Deployment

### Prerequisites

```bash
# Install dependencies
npm install @openzeppelin/contracts

# Install Hardhat (if not already installed)
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
```

### Configuration

Add Base networks to `hardhat.config.js`:

```javascript
module.exports = {
  networks: {
    base: {
      url: "https://mainnet.base.org",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 8453
    },
    baseSepolia: {
      url: "https://sepolia.base.org",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 84541
    }
  },
  etherscan: {
    apiKey: {
      base: process.env.BASESCAN_API_KEY
    }
  }
};
```

### Deploy to Testnet (Recommended First)

```bash
# Deploy to Base Sepolia testnet
npx hardhat run scripts/deploy.js --network baseSepolia
```

### Deploy to Mainnet

```bash
# Deploy to Base mainnet
npx hardhat run scripts/deploy.js --network base
```

### Verify on BaseScan

```bash
# Verify contract source code
npx hardhat verify --network base <CONTRACT_ADDRESS>
```

---

## 📖 Usage Examples

### Mint Tokens (Bridge Operator Only)

```javascript
// Connect to contract
const wrtc = await ethers.getContractAt("wRTC", contractAddress);

// Mint 1000 wRTC (6 decimals = 1000000000)
await wrtc.mint(userAddress, ethers.parseUnits("1000", 6));
```

### Burn Tokens

```javascript
// User burns their own tokens
await wrtc.burn(ethers.parseUnits("100", 6));

// Bridge burns from user (requires approval)
await wrtc.approve(contractAddress, ethers.parseUnits("100", 6));
await wrtc.burnFrom(userAddress, ethers.parseUnits("100", 6));
```

### Transfer Ownership to Bridge

```javascript
// After deployment, transfer ownership to bridge contract
await wrtc.transferBridgeOwnership(bridgeContractAddress);
```

---

## 🔒 Security Considerations

1. **Owner Privileges**
   - Owner can mint unlimited tokens
   - Owner should be bridge contract (not EOA) in production
   - Consider multi-sig for additional security

2. **Decimal Precision**
   - 6 decimals matches RTC main chain
   - Ensure all integrations use correct decimal conversion

3. **Access Control**
   - Only owner can mint
   - Anyone can burn their own tokens
   - BurnFrom requires prior approval

---

## 📊 Airdrop Integration

### Eligibility Check (Off-Chain)

Before minting airdrop tokens, verify user eligibility:

| Tier | Requirement | wRTC Amount |
|------|------------|-------------|
| Stargazer | 10+ repos starred | 25 wRTC |
| Contributor | 1+ merged PR | 50 wRTC |
| Builder | 3+ merged PRs | 100 wRTC |
| Security | Verified vulnerability | 150 wRTC |
| Core | 5+ merged PRs / Star King | 200 wRTC |
| Miner | Active attestation | 100 wRTC |

### Minting Airdrop

```javascript
// Example: Mint airdrop for eligible user
const airdropAmount = ethers.parseUnits("100", 6); // 100 wRTC
await wrtc.mint(eligibleUserAddress, airdropAmount);
```

---

## 📁 File Structure

```
bounties/1149-trackB/
├── wRTC-ERC20.sol      # ERC-20 contract
├── deploy.js           # Deployment script
├── README.md           # This documentation
└── test/
    └── wRTC.test.js    # Unit tests (optional)
```

---

## 🧪 Testing (Optional)

```bash
# Run unit tests
npx hardhat test test/wRTC.test.js

# Run with coverage
npx hardhat coverage
```

---

## 📞 Support

For questions about this bounty implementation:
- Comment on Issue #1149
- Contact: @ma-moon on GitHub

---

**Bounty Claim:** 75 RTC  
**Wallet:** [Your RTC Wallet Address]  
**Deployment TX:** [Transaction Hash After Deployment]
