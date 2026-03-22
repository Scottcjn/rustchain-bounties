# wRTC (Track B) — Deployment Record

## Base Sepolia (testnet)

| Field | Value |
|-------|-------|
| Chain ID | 84532 |
| Compiler | Solidity 0.8.28, Cancun EVM, optimizer 200 runs |
| wRTC contract | `0xeCA54c82a4220083e9D68fF00292410859381DEE` |
| Deploy tx | `0x5980e34306296eafffebda06498dd734ba6b0835e8d0524b270d94fe04539b1f` |
| Sourcify (verified) | [repo.sourcify.dev](https://repo.sourcify.dev/contracts/full_match/84532/0xeCA54c82a4220083e9D68fF00292410859381DEE/) |
| BaseScan | [sepolia.basescan.org](https://sepolia.basescan.org/address/0xeCA54c82a4220083e9D68fF00292410859381DEE) |
| Constructor arg | `0x89C0cdCb27eF98053d616d5dB1189450385A7561` (deployer EOA) |
| Multisig (`DEFAULT_ADMIN_ROLE` + `PAUSER_ROLE`) | pending handover |
| Bridge / minter (`MINTER_ROLE`) | pending handover |

## Base (mainnet)

| Field | Value |
|-------|-------|
| Chain ID | 8453 |
| Compiler | Solidity 0.8.28, Cancun EVM, optimizer 200 runs |
| wRTC contract | `0x...` |
| Deploy tx | `0x...` |
| BaseScan (verified) | https://basescan.org/address/... |
| Multisig (`DEFAULT_ADMIN_ROLE` + `PAUSER_ROLE`) | `0x...` |
| Bridge / minter (`MINTER_ROLE`) | `0x...` |

## Notes

- **Mint cap:** 20,000 wRTC cumulative (6 decimals); `totalMinted` does not decrease when users burn.
- **Pausable:** Admin or pauser can freeze all transfers in emergencies.
- **ERC20Permit:** EIP-2612 gasless approvals for L2 UX.
- **AccessControl roles:** `DEFAULT_ADMIN_ROLE` (multisig), `MINTER_ROLE` (bridge), `PAUSER_ROLE` (ops).
- **Verification:** Sourcify (full match). BaseScan imports Sourcify verification automatically.
