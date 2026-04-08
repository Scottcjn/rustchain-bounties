#!/bin/bash

# 更多 Haiku 主题
haikus=(
  # 区块链/DeFi
  "lido-staking-haiku.md|Lido|ETH staking pools|grow with the network"
  "rocket-pool-haiku.md|Rocket Pool|decentralized ETH2|staking made simple"
  "frax-finance-haiku.md|Frax Finance|algorithmic stablecoins|market finds balance"
  "fei-protocol-haiku.md|Fei Protocol|stable by volume| protocol owned liquidity"
  "terraclassic-haiku.md|Terra Classic|classic survives|still in the game"
  "osmosis-haiku.md|Osmosis|AMM innovation|interchain DeFi"
  "gravity-bridge-haiku.md|Gravity Bridge|bridging worlds|ETH cosmos connect"
  "sifchain-haiku.md|Sifchain|Omnichain DeFi|row to the future"

  # 身份/Auth
  "ceramic-network-haiku.md|Ceramic Network|self-sovereign data|identity returns"
  "spruce-id-haiku.md|Spruce ID|decentralized identity|you own your ID"
  "brightid-haiku.md|BrightID|social identity|proven human here"
  "gitcoin-passport-haiku.md|Gitcoin Passport|prove humanity|unlock grants"

  # 存储
  "skynet-haiku.md|Skynix|decentralized web|hosting reborn"
  "filebase-haiku.md|Filebase|S3 compatible|decentralized storage"
  "storj-haiku.md|Storj|distributed storage|pay only for used"
  "crust-network-haiku.md|Crust Network|IPFS layer|storage everywhere"
  "pinata-haiku.md|Pinata|IPFS pinning|your content stays"

  # 支付
  "bitpay-haiku.md|BitPay|crypto payments|merchant friendly"
  "coinbase-commerce-haiku.md|Coinbase Commerce|payments simplified|crypto accepted"
  "stripe-crypto-haiku.md|Stripe Crypto|fiat onramp|into the future"
  "ramp-network-haiku.md|Ramp Network|buy crypto easily|on ramp ready"

  # 社交/DAO
  "lens-protocol-haiku.md|Lens Protocol|social graphs|own your followers"
  "farcaster-haiku.md|Farcaster|decentralized social|protocol freedom"
  "galaxy-quest-haiku.md|Galaxy|onchain reputation|earn your cred"
  "rabbithole-haiku.md|Rabbithole|skill to earn|onchain journey"

  # 基础设施
  "the-graph-haiku.md|The Graph|indexing Web3|queries answered"
  "livepeer-haiku.md|Livepeer|video streaming|transcoding power"
  "render-network-haiku.md|Render Network|GPU rendering|distributed compute"
  "akash-network-haiku.md|Akash Network|cloud computing|decentralized AWS"
  "flux-os-haiku.md|Flux|Web3 cloud|infrastructure reborn"

  # 开发工具
  "foundry-haiku.md|Foundry|blazing fast|smart contracts"
  "hardhat-haiku.md|Hardhat|Ethereum dev|flexible and extensible"
  "brownie-haiku.md|Brownie|Python smart contracts|eth development"
  "waffle-haiku.md|Waffle|testing library|smart and clean"
  " ethers-js-haiku.md|Ethers.js|lightweight ETH|easy interactions"
  "viem-haiku.md|Viem|typesafe ETH|interface perfection"
  "wagmi-haiku.md|Wagmi|React hooks|for ETH apps"

  # 测试工具
  "solhint-haiku.md|Solhint|linting Solidity|clean code"
  "slither-haiku.md|Slither|static analysis|find those bugs"
  "mythril-haiku.md|Mythril|Symbolic execution|security first"
  "echidna-haiku.md|Echidna|fuzzing Solidity|property testing"
  "forge-std-haiku.md|forge-std|testing standard|mock and assert"

  # 合约库
  "openzeppelin-haiku.md|OpenZepenlin|secure contracts|industry standard"
  "solmate-haiku.md|Solmate|optimized Solidity|gas efficient"
  "rari-capital-haiku.md|Rari Capital|利息收益|compound interest"
  "uniswap-v3-haiku.md|Uniswap V3|concentrated liquidity|range trading"

  # 跨链
  "layerzero-haiku.md|LayerZero|omnichain|message passing"
  "wormhole-haiku.md|Wormhole|cross-chain bridge|guardians secure"
  "axelar-network-haiku.md|Axelar|interchain|secure routing"
  "allbridge-haiku.md|AllBridge|bridge any asset|universal swap"

  # 数据
  "dune-analytics-haiku.md|Dune Analytics|query the data|insights await"
  "nansen-haiku.md|Nansen|onchain analytics|smart money"
  "glassnode-haiku.md|Glassnode|on-chain insights|market intelligence"
  "cryptoquant-haiku.md|CryptoQuant|bitcoin analytics|whale tracking"
  "santiment-haiku.md|Santiment|alternative data|sentiment matters"
)

for item in "${haikus[@]}"; do
  IFS='|' read -r filename title desc1 desc2 <<< "$item"
  cat > "$filename" << HAIKU
---
title: $title Haiku
description: A haiku about $title for the RustChain community shanty collection
---

# $title Haiku

\`\`\`
$title
$desc1
$desc2
\`\`\`

*An original haiku celebrating $title in the RustChain ecosystem.*
HAIKU
done
echo "Created ${#haikus[@]} new Haiku files"
