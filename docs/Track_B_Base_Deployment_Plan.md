# Track B: Base ERC-20 Deployment Plan for wRTC (RIP-305)

## Overview
This module delivers the Base-side ERC-20 `wRTC` token deployment path. It utilizes OpenZeppelin's `AccessControl` to guarantee explicit boundaries for Phase 1 bridge controls instead of generic `Ownable` models.

## Ownership & Permission Boundaries
- **DEFAULT_ADMIN_ROLE**: Has the exclusive right to grant and revoke other roles. This should be assigned to a MultiSig wallet (e.g., Safe) deployed on Base.
- **MINTER_ROLE**: Authorized to mint new wRTC. Designed specifically to be assigned to the Track C Bridge contract.
- **BURNER_ROLE**: Authorized to burn wRTC from users returning assets across the bridge. Assigned to the Track C Bridge contract.
- **Decimals**: Explicitly set to `18` to maintain EVM standard equivalence and prevent precision errors during cross-chain calculations.

## Repeatable Deployment & Verification
Using Foundry, the deployment can be repeatedly tested and deterministically verified on Base mainnet and testnets (Base Sepolia).

### Prerequisites
Configure your `.env` or export variables:
```bash
export PRIVATE_KEY="<deployer_private_key>"
export ADMIN_ADDRESS="<multisig_admin_address>"
export BASESCAN_API_KEY="<basescan_api_key>"
export BASE_RPC_URL="https://mainnet.base.org" # or Base Sepolia RPC
```

### Execution & Verification
Run the deployment script. The `--verify` flag directly triggers Basescan verification using your API key.
```bash
forge script script/DeployWRTC.s.sol:DeployWRTC --rpc-url $BASE_RPC_URL --broadcast --verify -vvvv
```

## Track C Bridge Dependencies
To proceed with the Track C Bridge work, the following dependencies must be met from this module:
1. **Contract Address**: The deployed address of `wRTC` from the execution step above.
2. **Access Provisioning**: Post-deployment, the MultiSig holding `DEFAULT_ADMIN_ROLE` must call `grantRole(MINTER_ROLE, bridgeAddress)` and `grantRole(BURNER_ROLE, bridgeAddress)` on the wRTC contract.
3. **Interface Alignment**: The Track C bridge contract should expect `mint(address,uint256)` and `burn(address,uint256)` function signatures rather than standard `ERC20Burnable` allowances, simplifying the Phase 1 trust model.
