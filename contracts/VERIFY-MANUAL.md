# Verify wRTC on BaseScan without Hardhat (fallback)

Use this if `npx hardhat verify` fails with API key errors. The explorer form uses the same metadata Hardhat would send.

## You need

- Contract address on Base Sepolia (or mainnet)
- **Compiler:** `v0.8.28+commit.7893614a` (match `hardhat.config.ts`; exact build from your `artifacts/`)
- **EVM Version:** `cancun`
- **License:** MIT
- **Constructor argument** (ABI-encoded address): the deployer EOA you passed to `wRTC.deploy(deployer)` — 32-byte zero-padded hex

## Constructor encoding (single `address`)

For constructor `wRTC(address admin)`:

1. Take deployer address, e.g.: `0x89C0cdCb27eF98053d616d5dB1189450385A7561`
2. Drop `0x`, lowercase OK.
3. Pad left to 64 hex chars (32 bytes).
4. Prefix `0x`.

Example:

`0x` + `000000000000000000000000` + `89c0cdcb27ef98053d616d5db1189450385a7561`

→ `0x00000000000000000000000089c0cdcb27ef98053d616d5db1189450385a7561`

## Standard JSON input

1. Run `npx hardhat compile` in `contracts/`.
2. Open the newest file under `artifacts/build-info/` (one big JSON).
3. Copy the whole **`input`** object (`language`, `sources`, `settings` — **not** the `output` section).
4. Go to [sepolia.basescan.org/verifyContract](https://sepolia.basescan.org/verifyContract).
5. Choose **Solidity (Standard-Json-Input)**.
6. Compiler: `v0.8.28+commit.7893614a` (or match your artifact).
7. Paste the JSON, fill constructor ABI-encoded arg above, submit.

## Contract name in JSON

If the form asks for the fully qualified name, use:

`contracts/wRTC.sol:wRTC`
