# 教程 02：第一笔交易 — RustChain 转账实操

> **难度：** 🟢 入门 | **预计时间：** 20 分钟 | **作者钱包：** zp6

---

## 概述

本教程将指导你完成第一笔 RustChain 交易，包括钱包创建、账户充值、发起转账和查询交易状态。

---

## 前置条件

- ✅ 已完成 [教程 01：从零开始](./01-getting-started.md)
- ✅ 本地 RustChain 节点正在运行
- ✅ `curl` 和 `jq` 已安装

---

## 步骤 1：创建钱包账户

```bash
# 使用 RustChain CLI 创建新账户
./target/debug/rustchain-cli account new --name alice

# 输出示例：
# 🔑 Generated new account: alice
# 📬 Address: rc1q7x8f2k...3mn9p
# ⚠️  Important: backup your mnemonic phrase!
#    abandon amount bridge... (24 words)
```

创建第二个账户用于接收：

```bash
./target/debug/rustchain-cli account new --name bob

# 📬 Address: rc1q9y3j4n...7kl2w
```

> ⚠️ **重要：** 务必安全备份助记词！丢失助记词意味着永久失去资产访问权。

<!-- 📸 截图占位符：账户创建输出 -->
> 📸 **截图：** 成功创建 alice 和 bob 账户

---

## 步骤 2：获取测试代币

在开发网络中，你可以使用 faucet 获取测试代币：

```bash
# 方法 1：通过 CLI faucet
./target/debug/rustchain-cli faucet --address $(cat ~/.rustchain/keystore/alice.addr) --amount 1000

# 方法 2：通过 RPC 调用（开发链自动注入资金）
curl -s -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "jsonrpc": "2.0",
    "method": "dev_faucet",
    "params": ["rc1q7x8f2k...3mn9p", 1000]
  }' \
  http://localhost:9933 | jq
```

查询余额确认：

```bash
./target/debug/rustchain-cli balance --address rc1q7x8f2k...3mn9p

# 💰 Balance: 1000.000 RC
```

<!-- 📸 截图占位符：余额查询结果 -->
> 📸 **截图：** 显示账户余额为 1000 RC

---

## 步骤 3：发起转账

```bash
# 从 alice 转账 100 RC 到 bob
./target/debug/rustchain-cli transfer \
  --from alice \
  --to rc1q9y3j4n...7kl2w \
  --amount 100

# 输出：
# 📤 Transaction submitted
# 🆔 TX Hash: 0x8a3f...c7d2
# ⏳ Waiting for confirmation...
# ✅ Transaction confirmed in block #42
# 💸 Transferred 100.000 RC → rc1q9y3j4n...7kl2w
```

<!-- 📸 截图占位符：转账成功输出 -->
> 📸 **截图：** 交易提交并确认

---

## 步骤 4：使用 RPC 直接构造交易

对于更高级的用法，可以通过 JSON-RPC 手动构造交易：

```bash
# 获取账户 nonce
curl -s -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "jsonrpc": "2.0",
    "method": "account_nonce",
    "params": ["rc1q7x8f2k...3mn9p"]
  }' \
  http://localhost:9933 | jq

# 构造并发送交易
curl -s -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "jsonrpc": "2.0",
    "method": "author_submitExtrinsic",
    "params": ["0x...signed_tx_hex..."]
  }' \
  http://localhost:9933 | jq
```

---

## 步骤 5：查询交易状态

```bash
# 通过交易哈希查询
./target/debug/rustchain-cli tx --hash 0x8a3f...c7d2

# 输出：
# 📋 Transaction Details
#    Hash:    0x8a3f...c7d2
#    From:    rc1q7x8f2k...3mn9p
#    To:      rc1q9y3j4n...7kl2w
#    Amount:  100.000 RC
#    Fee:     0.001 RC
#    Block:   #42
#    Status:  ✅ Confirmed
```

确认双方余额变化：

```bash
./target/debug/rustchain-cli balance --address rc1q7x8f2k...3mn9p  # ~899.999 RC
./target/debug/rustchain-cli balance --address rc1q9y3j4n...7kl2w  # 100.000 RC
```

<!-- 📸 截图占位符：双方余额更新 -->
> 📸 **截图：** 转账后双方余额

---

## 步骤 6：交易事件监听

```bash
# 实时监听新区块和交易事件
./target/debug/rustchain-cli watch --events

# 输出：
# 📦 Block #43 — 2 extrinsics
#   🔄 Transfer: rc1q... → rc1q... (50.000 RC)
#   ⛏️  New block authored by: rc1q7x8f2k...3mn9p
# 📦 Block #44 — 1 extrinsic
#   ...
```

---

## 常见问题 (FAQ)

### Q: 交易一直显示 "Pending"？
**A:** 检查节点是否在正常出块。如果是单节点开发网，确认节点以 `--dev` 模式启动且挖矿已开启。

### Q: 余额不足但转账没有报错？
**A:** RustChain 交易是异步的。使用 `tx --hash` 查询实际状态。如果余额不足，交易会被打包但标记为失败，手续费仍会扣除。

### Q: 如何查看交易的详细错误信息？
**A:**

```bash
./target/debug/rustchain-cli tx --hash 0x... --verbose
```

### Q: 开发网络的代币和主网一样吗？
**A:** 不一样。开发网络使用测试代币，没有任何实际价值。

### Q: 转账手续费是多少？
**A:** 基础转账手续费为 0.001 RC。智能合约调用根据计算复杂度收取更多 Gas。

---

## 下一步

🎉 你已经成功完成了第一笔 RustChain 交易！

接下来，请继续学习：
- **[教程 03：挖矿指南](./03-mining-guide.md)** — 学习如何参与 RustChain 挖矿

---

*本教程由 [zp6](https://github.com/zp6) 贡献至 RustChain 社区。*
