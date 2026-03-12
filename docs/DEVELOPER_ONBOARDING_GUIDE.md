# RustChain 开发者入职指南

> **目标**: 帮助新开发者在 30 分钟内完成首次 RustChain 贡献
> **适用人群**: 区块链开发者、Python 开发者、开源贡献者、复古硬件爱好者

---

## 📋 目录

1. [RustChain 简介](#1-rustchain-简介)
2. [快速开始 (5 分钟)](#2-快速开始 -5-分钟)
3. [开发环境设置](#3-开发环境设置)
4. [第一次 API 调用](#4-第一次-api-调用)
5. [参与赏金任务](#5-参与赏金任务)
6. [提交 PR 流程](#6-提交-pr-流程)
7. [常见问题](#7-常见问题)
8. [资源链接](#8-资源链接)

---

## 1. RustChain 简介

### 什么是 RustChain？

RustChain 是一个 **Proof-of-Antiquity (PoA)** 区块链，独特之处在于：
- 🕰️ **复古硬件获得更高奖励**: PowerPC G4 (2.5×), G5 (2.0×), G3 (1.8×)
- 🔍 **6 重硬件指纹验证**: 防止虚拟机和模拟器作弊
- 🎯 **平等共识**: 每个独特硬件设备每轮获得 1 票，与速度无关
- 💰 **RTC 代币**: 1 RTC = $0.10 USD，可通过贡献或挖矿获得

### 核心特性

| 特性 | 说明 |
|------|------|
| 共识机制 | Proof-of-Antiquity (奖励老旧硬件) |
| 区块时间 | 10 分钟/epoch |
| 基础奖励 | 1.5 RTC/epoch |
| 硬件验证 | 6 重指纹检查 (时钟偏移、缓存时序、SIMD 身份等) |
| 跨链桥 | Solana (wRTC), Coinbase Base |

---

## 2. 快速开始 (5 分钟)

### 步骤 1: 加入社区

```
Discord: https://discord.gg/VqVVS2CW9Q
```

### 步骤 2: 浏览赏金任务

访问 [rustchain-bounties/issues](https://github.com/Scottcjn/rustchain-bounties/issues) 查看开放任务。

**新手推荐**: 查找带有 `good first issue` 标签的任务 (1-5 RTC)

### 步骤 3: 认领任务

在任务 Issue 下评论：
```
I would like to work on this
```

### 步骤 4: 开始工作

根据任务类型：
- **代码任务**: Fork 仓库 → 创建分支 → 实现功能 → 提交 PR
- **内容任务**: 创建内容 → 在 Issue 中提交链接
- **社区任务**: 按说明完成 (如 Star 仓库、分享内容)

---

## 3. 开发环境设置

### 基础要求

- Python 3.10+
- Git
- 代码编辑器 (VS Code 推荐)

### 安装 miner (可选，用于挖矿)

```bash
# Linux/macOS
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash

# 指定钱包安装
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-miner-wallet

# 预览安装 (不实际执行)
bash install-miner.sh --dry-run --wallet YOUR_WALLET_NAME
```

### 创建钱包

RustChain 使用 Ed25519 密钥对：

```python
import hashlib
from nacl.signing import SigningKey

# 生成密钥对
signing_key = SigningKey.generate()
verify_key = signing_key.verify_key

private_key_hex = signing_key.encode().hex()
public_key_hex = verify_key.encode().hex()

# 派生 RustChain 地址 (RTC 开头)
rustchain_address = "RTC" + hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest()[:40]

print(f"地址：{rustchain_address}")
print(f"公钥：{public_key_hex}")
print(f"私钥：{private_key_hex} (妥善保管!)")
```

**⚠️ 安全警告**: 
- 私钥永远不要提交到代码仓库
- 不要与他人分享私钥
- 建议使用环境变量或密钥管理工具存储

---

## 4. 第一次 API 调用

### 节点信息

```bash
NODE_URL="https://50.28.86.131"
```

**注意**: 节点使用自签名证书，curl 需要加 `-k` 或 `--insecure` 参数。

### 4.1 健康检查

```bash
curl -k "$NODE_URL/health"
```

**响应示例**:
```json
{
  "ok": true,
  "version": "2.2.1-rip200",
  "uptime_s": 3966,
  "backup_age_hours": 20.74,
  "db_rw": true,
  "tip_age_slots": 0
}
```

### 4.2 查看当前 Epoch

```bash
curl -k "$NODE_URL/epoch"
```

**响应示例**:
```json
{
  "epoch": 96,
  "slot": 13845,
  "blocks_per_epoch": 144,
  "enrolled_miners": 16,
  "epoch_pot": 1.5,
  "total_supply_rtc": 8388608
}
```

### 4.3 查询钱包余额

```bash
curl -k "$NODE_URL/wallet/balance?miner_id=YOUR_RTC_ADDRESS"
```

### 4.4 发送转账 (签名交易)

```python
import hashlib
import json
import time
import requests
from nacl.signing import SigningKey

NODE_URL = "https://50.28.86.131"
PRIVATE_KEY_HEX = "your_private_key_hex_here"
TO_ADDRESS = "RTC89abcdef0123456789abcdef0123456789abcdef"
AMOUNT_RTC = 1.0
MEMO = "Test transfer"
NONCE = int(time.time())

# 加载密钥
signing_key = SigningKey(bytes.fromhex(PRIVATE_KEY_HEX))
public_key_hex = signing_key.verify_key.encode().hex()
from_address = "RTC" + hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest()[:40]

# 创建规范消息 (服务器验证的格式)
tx_data = {
    "from": from_address,
    "to": TO_ADDRESS,
    "amount": AMOUNT_RTC,
    "memo": MEMO,
    "nonce": str(NONCE),
}

# 签名
message = json.dumps(tx_data, sort_keys=True, separators=(",", ":")).encode()
signature_hex = signing_key.sign(message).signature.hex()

# 构建请求
payload = {
    "from_address": from_address,
    "to_address": TO_ADDRESS,
    "amount_rtc": AMOUNT_RTC,
    "memo": MEMO,
    "nonce": NONCE,
    "public_key": public_key_hex,
    "signature": signature_hex,
}

# 发送
response = requests.post(
    f"{NODE_URL}/wallet/transfer/signed",
    json=payload,
    verify=False,
    timeout=15,
)

print(f"状态码：{response.status_code}")
print(f"响应：{response.json()}")
```

**⚠️ 常见错误**:
| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `invalid_from_address_format` | 地址不是 RTC 格式 | 从 Ed25519 公钥派生地址 |
| `Invalid signature` | 签名消息格式不匹配 | 使用规范 JSON (字母排序键，紧凑分隔符) |
| `REPLAY_DETECTED` | Nonce 重复使用 | 每次交易使用新 nonce (时间戳) |
| `insufficient_balance` | 余额不足 | 先查询余额 |

---

## 5. 参与赏金任务

### 赏金类别

| 类别 | 难度 | 奖励范围 | 示例 |
|------|------|----------|------|
| **新手任务** | `good first issue` | 1-5 RTC | 文档修正、简单测试 |
| **标准任务** | `standard` | 5-25 RTC | 功能开发、重构 |
| **重要任务** | `major` | 25-100 RTC | 安全修复、共识改进 |
| **关键任务** | `critical`, `red-team` | 100-200 RTC | 漏洞修复、协议升级 |

### 任务流程

```
1. 浏览任务 → 2. 认领 → 3. 开发 → 4. 提交 → 5. 审核 → 6. 获得奖励
```

### 提交要求

**代码任务**:
```markdown
1. 在 Issue 评论: "PR submitted: #[PR 编号]"
2. PR 描述包含:
   - 变更内容
   - 测试方法
   - 关联的 Issue/Bounty
3. 确保没有提交密钥/敏感信息
```

**内容任务**:
```markdown
1. 创建内容 (文章、视频、教程)
2. 在 Issue 评论中提交链接
3. 附上简短说明
```

### 领取奖励

完成任务并通过审核后，RTC 将发送到你的钱包地址。

**首次参与者**: 在 Issue 评论中提供你的 RustChain 地址，团队会协助设置。

---

## 6. 提交 PR 流程

### 6.1 Fork 仓库

```bash
git clone https://github.com/YOUR_USERNAME/Rustchain.git
cd Rustchain
```

### 6.2 创建分支

```bash
git checkout -b feat/your-feature-name
# 或
git checkout -b fix/your-bug-fix
# 或
git checkout -b docs/your-doc-update
```

### 6.3 开发与测试

```bash
# 本地测试变更
# 确保示例命令可运行
# 验证 API 端点响应
```

### 6.4 提交代码

```bash
git add .
git commit -m "feat: add your feature description"
git push origin feat/your-feature-name
```

### 6.5 创建 PR

1. 访问 GitHub 仓库
2. 点击 "New Pull Request"
3. 选择你的分支
4. 填写 PR 描述:
   ```markdown
   ## 变更内容
   简要描述做了什么
   
   ## 为什么需要
   解释变更原因
   
   ## 测试方法
   如何验证功能
   
   ## 关联 Issue
   Closes #XXX
   ```

### 6.6 PR 检查清单

- [ ] PR 标题清晰描述意图
- [ ] 描述说明变更内容和原因
- [ ] 链接到相关 Issue/Bounty
- [ ] 文档已更新 (如有行为变更)
- [ ] 没有提交密钥/敏感信息
- [ ] 代码通过本地测试

---

## 7. 常见问题

### Q: 我没有复古硬件，可以参与吗？

**A**: 可以！大部分开发任务不需要挖矿。你可以：
- 贡献代码 (bug 修复、功能开发)
- 编写文档和教程
- 参与社区建设
- 安全审计

### Q: 如何获取第一个 RTC？

**A**: 
1. 完成新手赏金任务 (1-5 RTC)
2. 参与社区活动
3. 从其他参与者转账

### Q: RustChain 地址和以太坊地址有什么区别？

**A**: 
| 链 | 格式 | 示例 |
|----|------|------|
| RustChain | `RTC` + 40 字符 | `RTC0123456789abcdef...` |
| Ethereum | `0x` + 40 字符 | `0x742d35Cc6634C053...` |
| Solana | Base58, 32-44 字符 | `7xKXtg2CW87d97TX...` |

**转账时必须使用 RustChain 地址 (RTC 开头)**

### Q: 提交 PR 后多久能获得奖励？

**A**: 
- 简单任务: 1-3 天审核
- 复杂任务: 3-7 天审核
- 安全相关: 可能需要更长时间验证

### Q: 如何验证我的硬件是否符合要求？

**A**: 运行 miner 会自动进行 6 重硬件检查：
```bash
clawrtc mine --dry-run
```

查看支持的硬件列表和倍率：
- PowerPC G4 (1999-2005): 2.5×
- PowerPC G5 (2003-2006): 2.0×
- PowerPC G3 (1997-2003): 1.8×
- IBM POWER8 (2014): 1.5×
- 其他硬件: 1.0-1.3×

### Q: 遇到问题如何求助？

**A**: 
1. 查看 [FAQ & Troubleshooting](https://github.com/Scottcjn/Rustchain/blob/main/docs/FAQ_TROUBLESHOOTING.md)
2. 在 Issue 中提问
3. 加入 Discord 社区

---

## 8. 资源链接

### 核心文档

| 文档 | 链接 |
|------|------|
| 白皮书 | [RustChain Whitepaper](https://github.com/Scottcjn/Rustchain/blob/main/docs/RustChain_Whitepaper_Flameholder_v0.97.pdf) |
| 协议规范 | [PROTOCOL.md](https://github.com/Scottcjn/Rustchain/blob/main/docs/PROTOCOL.md) |
| API 参考 | [API.md](https://github.com/Scottcjn/Rustchain/blob/main/docs/API.md) |
| 贡献指南 | [CONTRIBUTING.md](https://github.com/Scottcjn/Rustchain/blob/main/docs/CONTRIBUTING.md) |
| 术语表 | [GLOSSARY.md](https://github.com/Scottcjn/Rustchain/blob/main/docs/GLOSSARY.md) |

### 开发工具

| 工具 | 链接 |
|------|------|
| 区块浏览器 | [rustchain.org/explorer](https://rustchain.org/explorer) |
| 节点健康检查 | [rustchain.org/health](https://rustchain.org/health) |
| wRTC 交换 | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| 跨链桥 | [BoTTube Bridge](https://bottube.ai/bridge) |

### 社区

| 平台 | 链接 |
|------|------|
| Discord | [discord.gg/VqVVS2CW9Q](https://discord.gg/VqVVS2CW9Q) |
| GitHub | [github.com/Scottcjn/Rustchain](https://github.com/Scottcjn/Rustchain) |
| 赏金任务 | [rustchain-bounties/issues](https://github.com/Scottcjn/rustchain-bounties/issues) |

### 外部资源

| 资源 | 链接 |
|------|------|
| Dev.to 文章 | [Proof of Antiquity](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) |
| Grokipedia | [RustChain 搜索](https://grokipedia.com/search?q=RustChain) |

---

## 🎯 下一步

1. ✅ 完成本指南阅读
2. ✅ 加入 Discord 社区
3. ✅ 浏览开放赏金任务
4. ✅ 认领第一个任务
5. ✅ 开始贡献！

**欢迎加入 RustChain 社区！🔥**

---

*最后更新*: 2026-03-12  
*维护者*: RustChain 社区  
*许可证*: MIT
