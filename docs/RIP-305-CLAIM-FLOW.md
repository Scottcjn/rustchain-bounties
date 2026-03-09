# RIP-305 wRTC Claim Page & Eligibility Flow

## 1. Identity Verification (GitHub OAuth)
- **Flow**: User clicks "Connect GitHub" -> Redirects to GitHub OAuth -> Returns to claim page with auth code.
- **Requirements**: OAuth scopes restricted to `read:user`. The backend validates the user's ID, account creation date, and commits to prevent spoofing.

## 2. Wallet Connection
- **Solana**: Support via `@solana/wallet-adapter-react` (Phantom, Backpack, Solflare). Users must sign a standard SIWS (Sign-In With Solana) message to verify wallet ownership.
- **Base**: Support via `wagmi` / `viem` (MetaMask, Coinbase Wallet, WalletConnect). Users sign a SIWE (Sign-In With Ethereum) message.

## 3. Anti-Sybil Constraints
- **Checks**: 
  1. Minimum account age (created before the RIP-305 proposal snapshot).
  2. Minimum >5 valid PRs/commits in the `rustchain-bounties` repo or sister repos.
- **1:1 Mapping**: The backend maintains a unique index on `github_id`. A single GitHub account can only map to ONE wallet address (either Solana or Base). Attempting to link a second wallet will throw a `SybilViolationError`.

## 4. Eligibility Tiers
- **Tier 1 (Core Contributors)**: 10,000 wRTC
- **Tier 2 (Active Contributors)**: 5,000 wRTC
- **Tier 3 (General Participants)**: 1,000 wRTC

## 5. Claim State & Bridge Interaction
- **State Management**: Once claimed, the DB updates `claimed: true`. A Merkle proof is generated for the user's tier and wallet.
- **Bridge Tie-in**: If a user claims on Base, the protocol burns/locks the native allocation and utilizes LayerZero/Wormhole endpoints to mint/release wRTC on the Base network. The frontend listens for the bridge relayer's transaction receipt before showing the "Claim Successful" UI.