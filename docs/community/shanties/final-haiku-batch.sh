#!/bin/bash

# 最后一批 Haiku - 更多主题
haikus=(
  # GameFi/链游
  "axie-infinity-haiku.md|Axie Infinity|区块链游戏|Pokemon-style battles"
  "sandbox-haiku.md|The Sandbox|虚拟世界|own your land"
  "decentraland-haiku.md|Decentraland|元宇宙|NFT land"
  "gala-games-haiku.md|Gala Games|玩家拥有|play to own"
  "illuvium-haiku.md|Illuvium|开放世界|collect creatures"
  "stepn-haiku.md|StepN|move to earn|green lifestyle"
  "playko-haiku.md|Playko|gaming platform|earn while play"

  # NFT
  "opensea-haiku.md|OpenSea|NFT 市场|largest marketplace"
  "blur-haiku.md|Blur|交易聚合|professional trading"
  "foundation-haiku.md|Foundation|艺术平台|curated art"
  "rarible-haiku.md|Rarible|多链 NFT|create and trade"
  "superrare-haiku.md|SuperRare|艺术家市场|earn from art"
  "nifty-gateway-haiku.md|Nifty Gateway|NFT 铸造|art meets crypto"
  "zora-nft-haiku.md|Zora|NFT 协议|create freely"

  # 衍生品
  "gmx-protocol-haiku.md|GMX|去中心化合约|perpetual trading"
  "dydx-haiku.md|dYdX|保证金交易|leverage trading"
  "perpetual-protocol-haiku.md|Perpetual Protocol|vAMM|optimized liquidity"
  "gains-network-haiku.md|Gains Network|杠杆交易|synthetic assets"
  "mux-protocol-haiku.md|MUX Protocol|聚合杠杆|multi-asset"

  # 借贷
  "aave-v3-haiku.md|Aave V3|下一代借贷|enabled everywhere"
  "compound-v3-haiku.md|Compound V3|隔离市场|safer lending"
  "cream-finance-haiku.md|Cream Finance|创新借贷|risk adjusted"
  "idle-finance-haiku.md|Idle Finance|收益优化|automatic yields"
  "yearn-finance-haiku.md|Yearn Finance|收益聚合|automated strategies"

  # 稳定币
  "dai-stablecoin-haiku.md|DAI|去中心化稳定币|always $1"
  "frax-share-haiku.md|Frax Share|分数算法|algorithmic stability"
  "mim-atricrypto-haiku.md|MIM|利息收益|stable interest"
  "lusd-stablecoin-haiku.md|LUSD|锚定美元|simple stability"

  # 预言机
  "chainlink-v2-haiku.md|Chainlink V2|data feeds|secure price"
  "band-protocol-haiku.md|Band Protocol|跨链预言机|multi-chain"
  "tellor-oracle-haiku.md|Tellor|去中心化数据|dispute resolution"
  "api3-haiku.md|API3|first-party oracles|data sovereignty"

  # 隐私币
  "monero-haiku.md|Monero|隐私币|untraceable"
  "zcash-haiku.md|Zcash|零知识证明|shielded tx"
  "aztec-network-haiku.md|Aztec Network|隐私Layer2|confidential"

  # 域名
  "ens-domain-haiku.md|ENS|Ethereum 名称|.eth domains"
  "uns-domain-haiku.md|Unstoppable|去中心化域名|own your name"

  # 基础设施2
  "polygon-edge-haiku.md|Polygon Edge|模块化链|build your L2"
  "arbitrum-nitro-haiku.md|Arbitrum Nitro|速度提升|faster rollup"
  "optimism-bedrock-haiku.md|Optimism Bedrock|模块化OP stack"
  "zksync-era-haiku.md|zksync Era|zksync|zero knowledge"
  "starknet-haiku.md|StarkNet|Cairo|validity proofs"

  # 工具平台
  "tenderly-haiku.md|Tenderly|智能合约监控|debug faster"
  "tatum-haiku.md|Tatum|区块链API|easy development"
  "moralis-haiku.md|Moralis|Web3 数据|moralis powers"
  "quicknode-haiku.md|QuickNode|节点服务|infrastructure"

  # 审计
  "certik-audit-haiku.md|CertiK|形式化验证|security first"
  "trail-of-bits-haiku.md|Trail of Bits|安全审计|expert review"
  "open-zeppelin-audit-haiku.md|OpenZeppelin|合约审计|trusted security"
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
