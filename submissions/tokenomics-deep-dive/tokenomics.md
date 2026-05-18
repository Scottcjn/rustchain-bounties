# RustChain 代币经济学深入分析（RTC）

## 概述

本文档对 RustChain 原生代币 RTC 的经济模型进行深入分析，包括供应机制、分配方案、挖矿激励设计以及 wRTC 桥接代币机制。

---

## 1. 代币基础信息

| 属性 | 值 |
|------|-----|
| 代币名称 | RustChain Token |
| 代号 | RTC |
| 类型 | Utility Coin（实用型代币） |
| 所在链 | RustChain 主网 |
| 端点 | https://rustchain.org |
| 共识协议 | RIP-200 Proof-of-Antiquity (PoAn) |
| 基础设施 | Python 为主（pyproject.toml, tests/），Rust 钱包（rustchain-wallet） |

> **重要声明**：RTC 是实用型代币（Utility Coin），不是证券。详见 [RustChain Utility Coin - Not a Security](https://rustchain.org/docs/blog/rustchain-utility-coin-not-security)。

---

## 2. 供应机制

### 2.1 总供应量

- **最大供应量**：8,000,000 RTC（800 万枚，硬顶，不可增发）
- **无 ICO、无预售、无融资**

### 2.2 固定供应的意义

RustChain 选择固定供应模型的原因：
- **抗通胀**：总量确定，无增发稀释持有者
- **简单透明**：经济模型清晰，降低参与门槛
- **公平分发**：无预售、无团队预留大量代币，全部通过挖矿和明确用途分配

---

## 3. 代币分配

### 3.1 分配方案

```
总供应量: 8,000,000 RTC (100%)
├── 挖矿奖励 (Proof-of-Antiquity)    7,925,000  (99.0625%)
├── 开发基金                            50,000  ( 0.625%)
└── 赏金计划                            25,000  ( 0.3125%)
```

### 3.2 各部分详解

#### 挖矿奖励（7,925,000 RTC — 99.0625%）
- 用途：通过 Proof-of-Antiquity (PoAn) 共识协议，奖励活跃矿工
- 产出速率：**1.5 RTC / epoch**
- 硬件认证挖矿：矿工需通过硬件认证参与出块
- 这是 RTC 的核心分发机制，确保代币公平、去中心化地流入参与者手中
- 挖矿是持续的，直到 7,925,000 RTC 全部分发完毕

#### 开发基金（50,000 RTC — 0.625%）
- 用途：核心协议开发、安全审计、基础设施维护
- 管理：透明使用，社区可追踪

#### 赏金计划（25,000 RTC — 0.3125%）
- 用途：社区贡献激励、漏洞赏金、文档贡献、生态建设
- 管理：通过 GitHub Issues 和 Pull Requests 分发

### 3.3 分配特点

- **无私募轮/公开销售**：没有 ICO、预售或任何形式的融资
- **无团队/顾问预留**：没有大比例的团队代币分配
- **无空投预留**：所有代币通过挖矿或明确用途分配
- **挖矿为主**：99% 以上的代币通过 PoAn 挖矿产出

---

## 4. wRTC 桥接代币

### 4.1 概述

wRTC（Wrapped RTC）是 RTC 在 Base 链上的桥接代币，用于扩展 RTC 的使用场景。

| 属性 | 值 |
|------|-----|
| 代号 | wRTC |
| 最大供应量 | 20,000 wRTC |
| 所在链 | Base（Coinbase L2） |
| 锚定比例 | 1:1（桥接锁定） |
| 用途 | DeFi 交互、跨链流动性 |

### 4.2 桥接机制

```
RTC (RustChain) ←→ Bridge ←→ wRTC (Base)
                    │
                    ├── 锁定 RTC → 铸造 wRTC
                    └── 销毁 wRTC → 释放 RTC
```

- wRTC 的 MAX_SUPPLY 固定为 20,000，不可超过
- 桥接确保 RustChain 生态与更广泛的 DeFi 世界连通

---

## 5. 挖矿经济学

### 5.1 Proof-of-Antiquity (PoAn) 共识

RIP-200 定义的 Proof-of-Antiquity 是 RustChain 的核心共识协议：

- **硬件认证**：矿工通过硬件认证获得挖矿资格
- **活跃证明**：需要持续在线参与，证明"久远性"（Antiquity）
- **公平出块**：1.5 RTC / epoch，分配给活跃矿工

### 5.2 矿工激励模型

```
矿工运行节点 → 硬件认证 → 持续在线 → 获得epoch奖励
     │
     ├── 每个 epoch 奖励：1.5 RTC
     ├── 奖励分配给所有活跃矿工
     └── 总挖矿池：7,925,000 RTC
```

### 5.3 挖矿持续时间估算

| 场景 | 每 epoch 时长 | 年产出 | 挖矿池耗尽时间 |
|------|-------------|--------|--------------|
| 快速出块 | 1 分钟 | 788,400 RTC | ~10 年 |
| 中等出块 | 5 分钟 | 157,680 RTC | ~50 年 |
| 慢速出块 | 15 分钟 | 52,560 RTC | ~151 年 |

> 实际 epoch 时长由网络参数决定，以上仅为估算。

---

## 6. 技术架构与代币交互

### 6.1 核心端点

| 端点 | 用途 |
|------|------|
| `https://rustchain.org/health` | 节点健康检查 |
| `https://rustchain.org/api/miners` | 矿工状态查询 |
| `https://rustchain.org/wallet/balance` | 钱包余额查询 |

### 6.2 矿工部署

RustChain 矿工通过本地 Docker 构建：

```bash
# 本地构建矿工镜像（非预构建镜像）
docker build -f Dockerfile.miner -t rustchain-miner .

# 使用 docker-compose 运行
docker-compose up -d
```

- **注意**：没有 `rustchain/node:latest` 等预构建镜像
- 所有镜像从源码本地构建

### 6.3 项目结构

```
rustchain-bounties/
├── pyproject.toml          # Python 项目配置
├── tests/                  # Python 测试
├── rustchain-wallet/       # Rust 钱包子项目
│   ├── Cargo.toml
│   └── src/
└── Dockerfile.miner        # 矿工 Docker 构建
```

---

## 7. 对比分析

| 特性 | RustChain (RTC) | Bitcoin (BTC) | Ethereum (ETH) | Cosmos (ATOM) |
|------|-----------------|---------------|----------------|---------------|
| 供应模型 | 固定 | 固定 | 通缩 | 通胀 |
| 最大供应 | 8M | 21M | 无上限 | 无上限 |
| 共识 | Proof-of-Antiquity | Proof-of-Work | Proof-of-Stake | Proof-of-Stake |
| 分发方式 | 挖矿（99%+） | 挖矿（100%） | 预挖+质押 | 预挖+质押 |
| ICO/融资 | 无 | 无 | 有 | 有 |
| 桥接代币 | wRTC (Base) | WBTC | - | - |
| 开发语言 | Python + Rust | C++ | Solidity/Go | Go |

---

## 8. 总结

RustChain 的代币经济模型设计要点：

1. **固定供应**：800 万枚硬顶，消除通胀稀释
2. **公平分发**：99%+ 通过 PoAn 挖矿产出，无预售无融资
3. **硬件认证挖矿**：RIP-200 Proof-of-Antiquity 协议，1.5 RTC/epoch
4. **实用型代币**：明确声明非证券，纯 Utility Coin
5. **wRTC 桥接**：20,000 MAX_SUPPLY 的 Base 链桥接代币，连接 DeFi
6. **透明架构**：Python 为主的代码库，Rust 钱包，本地 Docker 构建

这一模型确保了公平性和可持续性：矿工通过硬件认证参与 → 持续获得 epoch 奖励 → 网络安全运行 → 生态持续发展。
