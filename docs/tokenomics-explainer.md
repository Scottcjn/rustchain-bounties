# RustChain Token Economics Explainer

## 概述

RustChain 是一个基于 **Proof-of-Antiquity**（复古证明）共识机制的区块链，其原生代币为 **RTC (RustChain Token)**。与传统 PoW 不同，RustChain 奖励的是硬件的"年龄"而非"速度"。

---

## 🪙 代币供应

| 指标 | 数值 |
|------|------|
| **总供应量** | 8,000,000 RTC |
| **预挖** | 75,000 RTC（开发/赏金） |
| **每 epoch 产出** | 1.5 RTC |
| **epoch 时长** | ~24 小时（144 个 slots） |
| **代币价格** | 1 RTC = $0.10 USD |

---

## 💰 RTC 分配机制

### 1. 挖矿奖励分配

每个 epoch 的奖励池（1.5 RTC）根据矿工的**硬件复古倍数**进行加权分配：

```
矿工奖励 = epoch 奖励池 × (矿工倍数 / 总权重)
```

**示例**（2 个矿工）：
- G4 矿工：2.5× 权重
- x86 矿工：1.0× 权重
- 总权重：3.5

**分配结果**：
- G4 获得：1.5 × (2.5/3.5) = **1.07 RTC**
- x86 获得：1.5 × (1.0/3.5) = **0.43 RTC**

### 2. 复古倍数表

硬件年龄决定挖矿奖励倍数：

| 硬件 | 年代 | 基础倍数 | 示例收益 |
|------|------|----------|----------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **Modern x86_64** | 当前 | **1.0×** | 0.12 RTC/epoch |

### 3. 时间衰减公式

复古硬件（>5 年）会经历每年 15% 的衰减，防止永久优势：

```
decay_factor = 1.0 - (0.15 × (硬件年龄 - 5) / 5)
final_multiplier = 1.0 + (复古奖励 × decay_factor)
```

**示例**：G4（基础 2.5×，24 年）
- 复古奖励：1.5（2.5 - 1.0）
- 衰减：1.0 - (0.15 × 19/5) = 0.43
- 最终倍数：1.0 + (1.5 × 0.43) = **1.645×**

### 4. 忠诚奖励

现代硬件通过在线时长可获得额外奖励（每年 +15%，上限 +50%）：

```
loyalty_bonus = min(0.5, 在线年数 × 0.15)
final = base + loyalty_bonus
```

---

## 📈 通胀机制

### 固定 epoch 产出

- **每 epoch 产出**：1.5 RTC（固定）
- **每天 epoch 数**：约 1 个（24 小时）
- **年通胀率**：约 6.84%（547.5 RTC / 8,000,000 RTC）

### 通胀控制

1. **固定产出**：不随矿工数量增加而增加
2. **时间衰减**：复古倍数随时间递减
3. **忠诚上限**：现代硬件奖励上限为 1.5×

---

## 🎁 奖励机制

### 1. 挖矿奖励

通过运行 RustChain 矿工软件，使用真实硬件参与共识：

- **基础流程**：
  1. 安装矿工：`curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash`
  2. 提交硬件指纹（6 项检测）
  3. 每个 epoch 获得加权奖励

- **硬件检测**（6 项）：
  - 时钟偏移与振荡器漂移
  - 缓存时序指纹
  - SIMD 单元识别
  - 热漂移熵
  - 指令路径抖动
  - 反虚拟化检测

### 2. 贡献赏金

通过贡献 RustChain 生态获得 RTC：

| 等级 | 奖励 | 示例 |
|------|------|------|
| Micro | 1-10 RTC | 拼写错误、小文档、简单测试 |
| Standard | 20-50 RTC | 功能开发、重构、新端点 |
| Major | 75-100 RTC | 安全修复、共识改进 |
| Critical | 100-150 RTC | 漏洞补丁、协议升级 |

**参与方式**：
1. 浏览 [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues)
2. 选择任务，提交 PR
3. 审核通过后获得 RTC

### 3. 治理投票

RTC 持有者可参与治理投票：

- **提案创建**：需持有 >10 RTC
- **投票资格**：活跃矿工
- **投票权重**：1 RTC = 1 票 × 硬件倍数
- **通过条件**：yes 权重 > no 权重

---

## 🌉 wRTC（Wrapped RTC）

RTC 可通过 BoTTube 桥接为 Solana 上的 wRTC：

| 属性 | 值 |
|------|-----|
| **代币名称** | Wrapped RustChain Token |
| **符号** | wRTC |
| **铸造地址** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **精度** | 6 位小数 |
| **网络** | Solana |
| **标准** | SPL Token |

**用途**：
- 在 Raydium 等 DEX 交易
- 提供流动性赚取费用
- Solana 生态 DeFi 集成

**桥接费用**：0.1-0.5%，耗时 5-30 分钟

---

## 🔒 安全机制

### 1. 反虚拟化

虚拟机/模拟器会被检测并获得极低奖励（10 亿分之一）：

```
真实 G4 Mac:    2.5× 倍数 = 0.30 RTC/epoch
模拟 G4:        0.0000000025× = 0.0000000003 RTC/epoch
```

### 2. 硬件绑定

每个硬件指纹绑定一个钱包，防止：
- 同一硬件多钱包
- 硬件欺骗
- Sybil 攻击

### 3. 密钥管理

- Ed25519 签名
- 矿工 ID 源自公钥
-无私钥恢复机制

---

## 📊 经济模型总结

| 特性 | 描述 |
|------|------|
| **总供应** | 8,000,000 RTC（固定上限） |
| **年通胀** | ~6.84%（固定产出） |
| **分配方式** | 挖矿（epoch 奖励）+ 贡献（赏金） |
| **价值支撑** | 硬件保护 + 生态贡献 + DeFi 流动性 |
| **治理** | RTC 持有者投票（加权） |

---

## 📚 参考资源

- [RustChain 白皮书](https://github.com/Scottcjn/Rustchain/blob/main/docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf)
- [协议规范](https://github.com/Scottcjn/Rustchain/blob/main/docs/PROTOCOL.md)
- [wRTC 快速指南](https://github.com/Scottcjn/Rustchain/blob/main/docs/wrtc.md)
- [API 参考](https://github.com/Scottcjn/Rustchain/blob/main/docs/API.md)
- [GitHub 仓库](https://github.com/Scottcjn/Rustchain)

---

*文档版本：1.0 | 最后更新：2026-03-12*
