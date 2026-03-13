# RustChain 治理参与指南

> **RustChain** 是一个 Proof-of-Antiquity 区块链，奖励使用真实复古硬件（PowerPC G4/G5、68K Macs、SPARC 等）的矿工比现代机器获得更高的挖矿倍数。网络使用 6 项硬件指纹检查来防止虚拟机和模拟器获得奖励。

本指南说明如何参与 RustChain 的去中心化治理，包括投票、创建提案和参与决策。

---

## 📋 目录

1. [治理概述](#治理概述)
2. [参与资格](#参与资格)
3. [如何投票](#如何投票)
4. [如何创建提案](#如何创建提案)
5. [提案生命周期](#提案生命周期)
6. [投票权重计算](#投票权重计算)
7. [治理 API 参考](#治理-api 参考)
8. [常见问题](#常见问题)

---

## 治理概述

RustChain 治理系统允许 RTC 持有者对网络变更进行提案和投票，包括：

- 新的 RIP（RustChain Improvement Proposals）
- 挖矿倍数调整
- 赏金资金分配
- 网络参数变更

**当前状态：** 治理系统正在开发中（参见 [Issue #50](https://github.com/Scottcjn/rustchain-bounties/issues/50)）

**网络信息：**
- 节点健康检查：`curl -sk https://50.28.86.131/health`
- 活跃矿工：`curl -sk https://50.28.86.131/api/miners`
- 浏览器：`https://50.28.86.131/explorer`

---

## 参与资格

### 投票资格
- 持有 **任意数量** 的 RTC 代币
- 必须是 **活跃矿工**（通过硬件认证）
- 钱包地址需与矿工地址绑定

### 创建提案资格
- 持有 **≥10 RTC** 代币
- 必须是活跃矿工
- 提案需支付少量 Gas 费（以 RTC 计）

---

## 如何投票

### 步骤 1：连接到治理界面

访问治理 Web UI（开发中）或使用 API：

```bash
# 获取活跃提案列表
curl -sk https://50.28.86.131/governance/proposals
```

### 步骤 2：查看提案详情

```bash
# 获取特定提案详情
curl -sk https://50.28.86.131/governance/proposal/{id}
```

提案详情包括：
- 提案标题和描述
- 提案类别（RIP、赏金、参数变更）
- 当前投票统计
- 剩余投票时间
- 通过所需条件

### 步骤 3：签署投票

使用你的钱包私钥签署投票：

```python
# 使用 rustchain_crypto.py 签署投票
from rustchain_crypto import sign_vote

vote_data = {
    "proposal_id": 123,
    "vote": "yes",  # 或 "no", "abstain"
    "voter_address": "your_wallet_address"
}

signed_vote = sign_vote(vote_data, private_key)
```

### 步骤 4：提交投票

```bash
# 提交签署的投票
curl -sk -X POST https://50.28.86.131/governance/vote \
  -H "Content-Type: application/json" \
  -d '{
    "proposal_id": 123,
    "vote": "yes",
    "voter_address": "your_wallet_address",
    "signature": "ed25519_signature_here"
  }'
```

### 步骤 5：确认投票

```bash
# 验证投票已记录
curl -sk https://50.28.86.131/governance/proposal/123 | jq '.votes'
```

---

## 如何创建提案

### 步骤 1：准备提案内容

提案应包含：

```markdown
# 提案标题

## 摘要
简要描述提案内容（2-3 句话）

## 动机
为什么需要这个变更？解决什么问题？

## 详细方案
技术实现细节、参数调整等

## 影响分析
- 对网络的影响
- 对矿工的影响
- 对 RTC 价值的影响

## 实施计划
时间表和里程碑

## 预算（如适用）
所需 RTC 资金
```

### 步骤 2：检查资格要求

```bash
# 验证你的 RTC 余额
curl -sk https://50.28.86.131/wallet/balance/your_address

# 验证矿工状态
curl -sk https://50.28.86.131/api/miners/your_address
```

### 步骤 3：提交提案

```bash
# 创建提案
curl -sk -X POST https://50.28.86.131/governance/propose \
  -H "Content-Type: application/json" \
  -d '{
    "title": "RIP-201: 增加 G4 挖矿倍数至 3.0x",
    "description": "提案详细内容...",
    "category": "RIP",
    "proposer_address": "your_wallet_address",
    "stake_amount": 10,
    "signature": "ed25519_signature_here"
  }'
```

### 步骤 4：提案审核

提交后，提案将经历：
1. **自动验证**：检查签名和资格
2. **社区讨论**：在 GitHub 或论坛讨论
3. **正式投票**：进入 7 天投票期

---

## 提案生命周期

```
┌─────────────┐
│   草稿期    │ ← 社区讨论和修改
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   投票期    │ ← 7 天投票窗口
│  (7 天)      │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   已通过    │     │   未通过    │
│  等待执行   │     │   结束      │
└──────┬──────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│   已执行    │ ← 自动或手动实施
└─────────────┘
```

### 各阶段说明

| 阶段 | 时长 | 说明 |
|------|------|------|
| 草稿 | 不限 | 社区讨论、修改完善 |
| 投票 | 7 天 | RTC 持有者投票 |
| 执行 | 视情况 | 自动或手动实施 |

### 通过条件

- **简单多数**：>50% 投票支持
- **法定人数**：至少 30% 活跃矿工参与投票（拟议）
- **硬件加权**：按古董倍数加权计算

---

## 投票权重计算

RustChain 使用 **硬件加权投票** 系统，复古硬件矿工的投票权重更高。

### 权重公式

```
投票权重 = RTC 持有量 × 古董倍数
```

### 古董倍数参考

| 硬件平台 | 古董倍数 | 示例 |
|----------|----------|------|
| PowerPC G4 | 2.5x | PowerMac G4, iBook G4 |
| PowerPC G5 | 3.0x | PowerMac G5 |
| Motorola 68K | 4.0x | Macintosh II, SE |
| SPARC | 3.5x | SPARCstation |
| x86 (现代) | 1.0x | Intel/AMD 现代 CPU |

### 计算示例

```
矿工 A:
- 持有：100 RTC
- 硬件：PowerMac G4 (2.5x)
- 投票权重：100 × 2.5 = 250 票

矿工 B:
- 持有：50 RTC
- 硬件：SPARCstation (3.5x)
- 投票权重：50 × 3.5 = 175 票

矿工 C:
- 持有：200 RTC
- 硬件：现代 x86 (1.0x)
- 投票权重：200 × 1.0 = 200 票
```

### 查看你的投票权重

```bash
# 获取你的矿工信息和权重
curl -sk https://50.28.86.131/api/miners/your_address | jq '.antiquity_multiplier, .rtc_balance, .voting_power'
```

---

## 治理 API 参考

### 创建提案

```http
POST /governance/propose
Content-Type: application/json

{
  "title": "提案标题",
  "description": "详细描述",
  "category": "RIP|bounty|parameter_change",
  "proposer_address": "钱包地址",
  "stake_amount": 10,
  "signature": "Ed25519 签名"
}
```

**响应：**
```json
{
  "success": true,
  "proposal_id": 123,
  "status": "draft",
  "voting_start": "2026-03-15T00:00:00Z",
  "voting_end": "2026-03-22T00:00:00Z"
}
```

### 获取提案列表

```http
GET /governance/proposals?status=active|past|all
```

**响应：**
```json
{
  "proposals": [
    {
      "id": 123,
      "title": "RIP-201: 增加 G4 挖矿倍数",
      "status": "active",
      "votes_for": 1500,
      "votes_against": 300,
      "votes_abstain": 100,
      "voting_end": "2026-03-22T00:00:00Z"
    }
  ]
}
```

### 获取提案详情

```http
GET /governance/proposal/{id}
```

**响应：**
```json
{
  "id": 123,
  "title": "RIP-201: 增加 G4 挖矿倍数至 3.0x",
  "description": "...",
  "category": "RIP",
  "proposer": "0x...",
  "status": "active",
  "created_at": "2026-03-10T00:00:00Z",
  "voting_start": "2026-03-15T00:00:00Z",
  "voting_end": "2026-03-22T00:00:00Z",
  "votes": {
    "for": 1500,
    "against": 300,
    "abstain": 100,
    "total_weight": 1900
  },
  "vote_details": [
    {
      "voter": "0x...",
      "vote": "yes",
      "weight": 250,
      "timestamp": "2026-03-16T12:00:00Z"
    }
  ]
}
```

### 投票

```http
POST /governance/vote
Content-Type: application/json

{
  "proposal_id": 123,
  "vote": "yes|no|abstain",
  "voter_address": "钱包地址",
  "signature": "Ed25519 签名"
}
```

**响应：**
```json
{
  "success": true,
  "vote_recorded": true,
  "voting_power_used": 250
}
```

---

## 常见问题

### Q: 我需要多少 RTC 才能参与治理？

**A:** 
- **投票**：任意数量的 RTC（但必须是活跃矿工）
- **创建提案**：至少 10 RTC

### Q: 如何成为活跃矿工？

**A:** 
1. 在复古硬件上运行 RustChain 矿工
2. 通过 6 项硬件指纹验证
3. 向网络注册你的矿工地址

详见 [矿工设置指南](https://github.com/Scottcjn/Rustchain/blob/main/docs/miner-setup.md)

### Q: 投票可以更改吗？

**A:** 可以。在投票期结束前，你可以随时更改投票。只有最后一次投票会被计数。

### Q: 提案通过后多久执行？

**A:** 
- **参数调整**：自动执行，通常在投票结束后 24 小时内
- **RIP 实施**：由开发团队安排，时间表在提案中说明
- **赏金资金**：需要财务多签确认，通常 3-5 天

### Q: 我可以委托我的投票权吗？

**A:** 投票委托功能正在开发中（参见 Issue #50 Nice to Have）。

### Q: 如果法定人数不足怎么办？

**A:** 提案将自动失败，需要重新提案或延长投票期。

### Q: 如何查看历史提案？

**A:** 
```bash
curl -sk https://50.28.86.131/governance/proposals?status=past
```

### Q: 治理合约在哪里？

**A:** RustChain 治理目前通过节点 API 实现，未来计划迁移到智能合约。

---

## 资源链接

- [RustChain 主仓库](https://github.com/Scottcjn/Rustchain)
- [赏金任务](https://github.com/Scottcjn/rustchain-bounties)
- [治理系统开发 Issue #50](https://github.com/Scottcjn/rustchain-bounties/issues/50)
- [RIP-200: 轮询共识机制](https://github.com/Scottcjn/Rustchain/blob/main/docs/protocol/rip_200_round_robin_1cpu1vote.py)
- [网络浏览器](https://50.28.86.131/explorer)

---

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2026-03-12 | 初始版本，基于 Issue #50 规范 |

---

*最后更新：2026-03-12*
*维护者：RustChain 社区*
