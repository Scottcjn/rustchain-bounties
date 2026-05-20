# 教程 03：挖矿指南 — 参与 RustChain 网络安全

> **难度：** 🟡 中等 | **预计时间：** 45 分钟 | **作者钱包：** zp6

---

## 概述

本教程详解 RustChain 的挖矿机制，包括节点质押、验证者注册、出块奖励和挖矿优化。

RustChain 使用 **Nominated Proof-of-Stake (NPoS)** 共识机制，而非传统 PoW 挖矿。

---

## 前置条件

- ✅ 已完成 [教程 01](./01-getting-started.md) 和 [教程 02](./02-first-transaction.md)
- ✅ 账户中有足够的 RC 代币（建议 ≥ 100 RC）
- ✅ 稳定的网络连接（建议带宽 ≥ 10 Mbps）
- ✅ 服务器在线率 ≥ 99.5%（主网要求）

---

## 步骤 1：理解共识机制

RustChain 采用 NPoS 共识，分为两个角色：

| 角色 | 说明 | 最低质押 |
|------|------|----------|
| **验证者 (Validator)** | 出块、验证交易 | 100 RC |
| **提名人 (Nominator)** | 投票支持验证者 | 1 RC |

```
提名人 ──投票──▶ 验证者 ──出块──▶ 区块链
   │                │
   └── 获得分红 ────┘
```

> 💡 **提示：** 如果没有足够质押或不想维护服务器，可以当提名人赚取被动收益。

---

## 步骤 2：配置验证者节点

### 2.1 服务器准备

```bash
# 推荐配置
# CPU: 4+ cores
# RAM: 8+ GB
# SSD: 100+ GB
# OS: Ubuntu 22.04 LTS

# 更新系统
sudo apt update && sudo apt upgrade -y

# 同步系统时钟（对出块至关重要）
sudo apt install -y chrony
sudo systemctl enable chrony
```

### 2.2 启动验证者节点

```bash
# 编译 release 版本（性能更优）
cargo build --release

# 启动节点并连接到主网
./target/release/rustchain-node \
  --name "my-validator" \
  --validator \
  --chain mainnet \
  --base-path /data/rustchain \
  --rpc-port 9933 \
  --port 30333

# 等待节点完全同步
# 可以通过以下命令检查同步状态：
curl -s -H "Content-Type: application/json" \
  -d '{"id":1,"jsonrpc":"2.0","method":"system_syncState","params":[]}' \
  http://localhost:9933 | jq .result.currentBlock
```

<!-- 📸 截图占位符：节点同步进度 -->
> 📸 **截图：** 节点同步中，显示当前区块高度

### 2.3 生成 Session 密钥

```bash
# 在节点上生成新的 session 密钥
curl -s -H "Content-Type: application/json" \
  -d '{"id":1,"jsonrpc":"2.0","method":"author_rotateKeys","params":[]}' \
  http://localhost:9933 | jq

# 输出：
# {
#   "result": "0xabc123...def456"  ← 这是你的 session 密钥
# }
```

> ⚠️ **安全提示：** 妥善保管 session 密钥，不要泄露给他人。

---

## 步骤 3：注册为验证者

```bash
# 设置 session 密钥
./target/release/rustchain-cli session \
  --account alice \
  --set-key 0xabc123...def456

# 绑定质押（至少 100 RC）
./target/release/rustchain-cli staking \
  --account alice \
  --bond 100

# 注册为验证者
./target/release/rustchain-cli staking \
  --account alice \
  --validate \
  --commission 5  # 5% 佣金率

# 输出：
# ✅ Validator registered successfully
# 📊 Current validators: 127/200 slots
# 💰 Staked: 100 RC (self) + 0 RC (nominated)
```

<!-- 📸 截图占位符：验证者注册成功 -->
> 📸 **截图：** 验证者注册成功，显示在验证者列表中

---

## 步骤 4：作为提名人参与

如果你的质押不够或不想运维节点：

```bash
# 绑定质押
./target/release/rustchain-cli staking \
  --account bob \
  --bond 10

# 提名你信任的验证者（最多 16 个）
./target/release/rustchain-cli staking \
  --account bob \
  --nominate rc1q7x8f2k...3mn9p,rc1q5hk2mn...8qrst

# 输出：
# ✅ Nominations submitted
# 📋 Nominated 2 validators
```

---

## 步骤 5：监控出块和奖励

```bash
# 查看当前验证者状态
./target/release/rustchain-cli staking --info --account alice

# 输出：
# 👤 Validator: alice (rc1q7x8f2k...3mn9p)
# 💰 Total stake: 250 RC (100 self + 150 nominated)
# 📊 Commission: 5%
# 🏆 Era points: 1,247
# 💵 Pending reward: 2.35 RC

# 查看最近出块记录
./target/release/rustchain-cli blocks \
  --author rc1q7x8f2k...3mn9p \
  --last 100

# 实时监控
./target/release/rustchain-cli watch --staking-events
```

<!-- 📸 截图占位符：验证者仪表盘 -->
> 📸 **截图：** 验证者状态仪表盘

---

## 步骤 6：挖矿优化

### 6.1 硬件优化

```bash
# 使用 release 构建并启用 CPU 特定优化
RUSTFLAGS="-C target-cpu=native" cargo build --release

# 对于高端 CPU，可以调整并行度
export RAYON_NUM_THREADS=8
```

### 6.2 网络优化

```bash
# 增加文件描述符限制
ulimit -n 65536

# 在 systemd service 中配置
[Service]
LimitNOFILE=65536
```

### 6.3 监控告警脚本

```bash
#!/bin/bash
# health-check.sh — 验证者健康检查

BLOCK_HEIGHT=$(curl -s -H "Content-Type: application/json" \
  -d '{"id":1,"jsonrpc":"2.0","method":"system_syncState","params":[]}' \
  http://localhost:9933 | jq -r '.result.currentBlock')

PEER_COUNT=$(curl -s -H "Content-Type: application/json" \
  -d '{"id":1,"jsonrpc":"2.0","method":"system_health","params":[]}' \
  http://localhost:9933 | jq -r '.result.peers')

echo "Block: $BLOCK_HEIGHT | Peers: $PEER_COUNT | Time: $(date)"

if [ "$PEER_COUNT" -lt 5 ]; then
  echo "⚠️  LOW PEERS: $PEER_COUNT"
fi
```

---

## 常见问题 (FAQ)

### Q: 验证者被选中出块的概率有多大？
**A:** 与你的总质押量（自有 + 被提名）成正比。质押越多，被选中概率越高。

### Q: 验证者掉线会怎样？
**A:** 每个 Era（约 6 小时）如果验证者离线超过一定比例，会被扣除质押（Slashing）。轻微离线扣 0.1%，严重违规（如双签）最高扣 100%。

### Q: 佣金率设多少合适？
**A:** 建议设 2%-10%。太低没收益，太高吸引不到提名人。可以后期调整。

### Q: 如何解除质押？
**A:** 质押有 28 天解绑期：

```bash
./target/release/rustchain-cli staking --account alice --unbond 50
# 28 天后可以提取
```

### Q: 提名人收益怎么算？
**A:** 验证者出块奖励扣除佣金后，按各提名人的质押比例分配。

### Q: 如何迁移验证者到新服务器？
**A:** 先在新服务器启动并同步节点，然后在旧服务器停止节点前更新 session 密钥。确保切换期间不超过一个 Session（约 1 小时）。

---

## 下一步

🎉 你已经掌握了 RustChain 挖矿的核心知识！

接下来，请继续学习：
- **[教程 04：智能合约开发](./04-smart-contracts.md)** — 在 RustChain 上开发智能合约

---

*本教程由 [zp6](https://github.com/zp6) 贡献至 RustChain 社区。*
