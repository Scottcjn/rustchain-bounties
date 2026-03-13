# ORACLE (1952) RustChain Miner

**橡树岭自动计算机 (Oak Ridge Automatic Computer) 移植项目**

## 📋 项目概述

将 RustChain 矿工移植到 1952 年的 ORACLE 计算机，实现 **5.0x 最高倍数** 的 Proof-of-Antiquity 挖矿！

### ORACLE 计算机规格

| 特性 | 规格 |
|------|------|
| 建造年份 | 1952 |
| 地点 | 橡树岭国家实验室，田纳西州 |
| 架构 | IAS (冯·诺依曼) |
| 字长 | 40 位 |
| 内存 | 威廉姆斯管 (1024 字 = 5KB) |
| 时钟 | ~1 MHz |
| 技术 | 真空管 (~1500 个) |

## 🏗️ 架构设计

采用**混合架构**：ORACLE 负责 SHA256 计算和硬件指纹生成，微控制器处理网络通信。

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   ORACLE 1952   │────▶│  微控制器桥接器  │────▶│  RustChain 节点  │
│ - SHA256 核心   │     │ - TCP/IP 栈      │     │ - HTTPS/API     │
│ - 硬件指纹      │     │ - TLS 1.3        │     │                 │
│ - 纸带 I/O      │     │ - 协议封装       │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## 📁 项目结构

```
oracle-miner/
├── README.md                 # 本文件
├── oracle-sim/               # ORACLE 模拟器 (Python)
│   └── oracle_cpu.py        # CPU 和内存模拟器
├── docs/                     # 文档
│   ├── architecture.md      # 架构设计
│   └── setup-guide.md       # 安装指南
└── hardware/                 # 硬件设计
    └── interface.sch        # 接口原理图
```

## 🚀 实现阶段

1. **模拟器开发** (50 RTC) - Python CPU 模拟器
2. **SHA256 实现** (75 RTC) - 40 位优化版本
3. **网络桥接** (50 RTC) - 微控制器固件
4. **硬件指纹** (25 RTC) - 威廉姆斯管特征
5. **文档验证** (25 RTC) - 视频和开源

## 💰 预期收益

- **基础奖励**: 0.12 RTC/epoch
- **5.0× 倍数**: 0.60 RTC/epoch
- **每天**: 86.4 RTC
- **每年**: ~31,104 RTC (~$3,110)

## 💳 赏金钱包

```
RTC4325af95d26d59c3ef025963656d22af638bb96b
```

## 📚 资源

- [GitHub Issue #1828](https://github.com/Scottcjn/rustchain-bounties/issues/1828)
- [橡树岭国家实验室档案馆](https://www.ornl.gov/library)
- [IAS 架构论文](https://www.ieeeghn.org/wiki/index.php/John_von_Neumann)

---

**Bounty Tier**: LEGENDARY (200 RTC / $20 USD)  
**Multiplier**: 5.0x (Maximum)
