# RustChain 白皮书核心要点解读

## 概述

RustChain 是一条基于 Proof-of-Antiquity（PoAn，古物证明）共识机制的区块链，核心理念是通过验证真实硬件的"年代值"来认证矿工身份并进行挖矿奖励。该项目又名 Flameholder，旨在反对电子垃圾（e-waste）文化，赋予老旧硬件新的生命和价值。

---

## 1. 架构设计

### 1.1 技术栈
- **主要语言**：Python（pyproject.toml 管理依赖，pytest 测试框架）
- **钱包组件**：Rust 实现位于 `rustchain-wallet` 子目录
- **数据存储**：SQLite（WAL 模式支持并发读）
- **API**：REST API，主端点 `https://rustchain.org`
- **部署**：Docker（Dockerfile.miner + docker-compose.yml 本地构建）

### 1.2 为什么选择 Python + 复古硬件？
- **低门槛**：Python 让更多开发者可以参与矿工和工具开发
- **硬件包容**：不追求最高算力，而是认证硬件的真实性和年代
- **反 e-waste**：通过赋予老旧硬件价值，减少电子垃圾
- **实用主义**：简洁的 REST API 和轻量级架构

---

## 2. 共识机制

### 2.1 Proof-of-Antiquity (PoAn, RIP-200)
RustChain 采用独特的 Proof-of-Antiquity 共识：
- **硬件指纹**：通过硬件特征（CPU、架构等）生成唯一指纹
- **年代值验证**：老旧硬件获得更高的年代值（antiquity score）
- **Epoch 奖励**：每个 epoch 产出 1.5 RTC，按矿工的年代值分配
- **反 Sybil**：硬件认证机制防止伪造身份

### 2.2 支持的硬件架构
- PowerPC（G4、POWER8 等）
- SPARC
- MIPS
- RISC-V
- m68k
- ARM SBC
- x86 复古机器
- 其他古董/嵌入式硬件

### 2.3 关键指标
- **Epoch 间隔**：约 300 秒
- **奖励**：1.5 RTC / epoch
- **共识类型**：硬件认证，非算力竞争

---

## 3. API 与交互

### 3.1 核心 API 端点
| 端点 | 用途 |
|------|------|
| `GET /health` | 节点健康检查 |
| `GET /api/miners` | 矿工列表和状态 |
| `GET /api/miners/{id}` | 单个矿工详情 |
| `GET /wallet/balance` | 钱包余额查询 |

### 3.2 矿工流程
1. 注册矿工 ID
2. 生成硬件指纹
3. 每个 epoch 提交认证（attestation）
4. Epoch 结算后按年代值分配奖励

---

## 4. 代币经济学（RTC）

### 4.1 代币分配
- **总供应量**：8,000,000 RTC
- **挖矿奖励**：7,925,000 RTC（99.0625%）
- **开发预留**：50,000 RTC
- **赏金池**：25,000 RTC

### 4.2 wRTC 桥接
- wRTC 是 RTC 在 Base 链上的 ERC-20 映射
- 最大桥接供应量：20,000 wRTC
- 桥接合约开源可审计

### 4.3 代币特点
- **无 ICO / 无预售 / 无融资**
- 纯粹的实用型代币（utility coin）
- 无流动性保证声明
- 挖矿是获取 RTC 的主要方式

---

## 5. 生态系统

### 5.1 赏金系统
RustChain 运营活跃的赏金计划（rustchain-bounties）：
- GitHub Issues 上发布各种赏金任务
- 完成任务获得 RTC 奖励
- 涵盖代码审计、文档、工具开发、创意内容等

### 5.2 社区工具
- **MCP Server**：让 AI 代理连接 RustChain
- **Prometheus Exporter**：监控指标导出
- **Health Check CLI**：节点健康检查工具
- **VS Code Extension**：矿工状态和赏金浏览
- **Telegram Bot**：钱包余额和矿工状态查询

---

## 6. 安全

### 6.1 安全审计
- 社区驱动的自审计（Self-Audit）赏金
- 对抗性钢人论证（Adversarial Steelman）分析
- 已发现和修复多个安全漏洞（CORS XSS、TOCTOU 竞态等）

### 6.2 供应链安全
- BCOS（Blockchain Certified Open Source）认证
- SPDX 许可证标识
- Supply-chain hygiene CI 检查

---

## 7. 总结

RustChain 的核心竞争力在于：
- **Proof-of-Antiquity**：独特的硬件认证共识，非传统 PoS/PoW
- **反 e-waste 理念**：赋予老旧硬件价值，而非追求最高性能
- **低门槛参与**：Python 为主的技术栈，任何人都可轻松参与
- **无 ICO 纯挖矿**：代币全部通过挖矿和赏金发放，无预售融资
- **活跃社区**：赏金驱动的发展模式，持续吸引贡献者

RustChain（Flameholder）描绘了一个技术独特、理念鲜明的区块链项目——不是为了与以太坊竞争，而是开创了"古董硬件挖矿"这一全新赛道。
