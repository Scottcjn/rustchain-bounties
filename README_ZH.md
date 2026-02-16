<div align="center">

# 🧱 RustChain: Proof-of-Antiquity 区块链 (古董证明)

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**第一个奖励老旧硬件而非高主频硬件的区块链。**

*你的 PowerPC G4 挣得比现代 Threadripper 还多。这就是我们的宗旨。*

[官方网站](https://rustchain.org) • [实时浏览器 (Explorer)](https://rustchain.org/explorer) • [兑换 wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC 快速入门](docs/wrtc.md) • [wRTC 教程](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia 参考](https://grokipedia.com/search?q=RustChain) • [白皮书](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [快速开始](#-快速开始) • [工作原理](#-proof-of-antiquity-工作原理)

</div>

---

## 🪙 Solana 上的 wRTC

RustChain Token (RTC) 现已通过 BoTTube Bridge 在 Solana 上作为 **wRTC** 提供：

| 资源 | 链接 |
|----------|------|
| **兑换 wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **价格图表** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **RTC ↔ wRTC 跨链桥** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **快速入门指南** | [wRTC 快速入门 (购买, 跨链, 安全)](docs/wrtc.md) |
| **入网教程** | [wRTC 跨链 + 兑换安全指南](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **外部参考** | [Grokipedia 搜索: RustChain](https://grokipedia.com/search?q=RustChain) |
| **代币合约地址 (Mint)** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 学术出版物

| 论文 | DOI | 主题 |
|-------|-----|-------|
| **RustChain: One CPU, One Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Proof of Antiquity 共识, 硬件指纹识别 |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | 利用 AltiVec vec_perm 进行 LLM 注意力机制优化 (27-96倍优势) |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | 利用 POWER8 mftb 熵进行行为差异性研究 |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | 情感化提示词使视频扩散模型增益 20% |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | 用于 LLM 推理的 NUMA 分布式权重银行 |

---

## 🎯 RustChain 的独特之处

| 传统 PoW | Proof-of-Antiquity (古董证明) |
|----------------|-------------------|
| 奖励最快的硬件 | 奖励最老的硬件 |
| 越新越好 | 越旧越好 |
| 浪费能源消费 | 保护计算历史 |
| 竞相逐底 (性能竞赛) | 奖励数字资产保护 |

**核心原则**: 存世数十年的真实古董硬件值得认可。RustChain 将挖矿逻辑反转。

## ⚡ 快速开始

### 一条命令安装 (推荐)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

安装程序将：
- ✅ 自动检测你的平台 (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ 创建隔离的 Python virtualenv (无系统污染)
- ✅ 为你的硬件下载正确的 Miner (挖矿程序)
- ✅ 设置开机自启 (systemd/launchd)
- ✅ 提供简单的卸载方式

### 带选项安装

**使用指定钱包安装：**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-miner-wallet
```

**卸载：**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### 支持的平台
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ IBM POWER8 系统

### 安装后

**检查钱包余额：**
```bash
# 注意：使用 -sk 参数是因为节点可能使用自签名 SSL 证书
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

**列出活跃矿工：**
```bash
curl -sk https://50.28.86.131/api/miners
```

**检查节点健康状况：**
```bash
curl -sk https://50.28.86.131/health
```

**获取当前 Epoch (纪元)：**
```bash
curl -sk https://50.28.86.131/epoch
```

**管理矿工服务：**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # 检查状态
systemctl --user stop rustchain-miner      # 停止挖矿
systemctl --user start rustchain-miner     # 开始挖矿
journalctl --user -u rustchain-miner -f    # 查看日志
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # 检查状态
launchctl stop com.rustchain.miner         # 停止挖矿
launchctl start com.rustchain.miner        # 开始挖矿
tail -f ~/.rustchain/miner.log             # 查看日志
```

### 手动安装
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet YOUR_WALLET_NAME
```

## 💰 古董加成倍率 (Antiquity Multipliers)

你硬件的工龄决定了你的挖矿奖励：

| 硬件 | 年代 | 倍率 | 预估收益 |
|----------|-----|------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **Modern x86_64** | 当前 | **1.0×** | 0.12 RTC/epoch |

*倍率随时间衰减 (每年 15%) 以防止出现永久优势。*

## 🔧 Proof-of-Antiquity 工作原理

### 1. 硬件指纹识别 (RIP-PoA)

每个矿工必须证明其硬件是真实的，而非模拟的：

```
┌─────────────────────────────────────────────────────────────┐
│                   6 项硬件检查                               │
├─────────────────────────────────────────────────────────────┤
│ 1. 时钟偏差与振荡器漂移 (Clock-Skew) ← 硅片老化模式          │
│ 2. 缓存时序指纹 (Cache Timing)      ← L1/L2/L3 延迟特性      │
│ 3. SIMD 单元身份                    ← AltiVec/SSE/NEON 偏差  │
│ 4. 热漂移熵 (Thermal Drift)         ← 独特的热曲线           │
│ 5. 指令路径抖动 (Instruction Path)  ← 微架构抖动图谱         │
│ 6. 反模拟检查 (Anti-Emulation)      ← 检测虚拟机/模拟器      │
└─────────────────────────────────────────────────────────────┘
```

**为什么这很重要**: 伪装成 G4 Mac 的 SheepShaver 虚拟机将无法通过这些检查。真实的古董硅片具有无法伪造的独特老化模式。

### 2. 1 CPU = 1 Vote (RIP-200)

与传统的算力决定投票权的 PoW 不同，RustChain 使用 **轮询共识 (round-robin)**：

- 每个唯一的硬件设备在每个纪元 (epoch) 仅获得 1 次投票权。
- 奖励在所有投票者中平均分配，然后乘以古董倍率。
- 运行多线程或更快的 CPU 不会带来优势。

### 3. 基于纪元 (Epoch) 的奖励

```
Epoch 持续时间: 10 分钟 (600 秒)
基础奖励池: 每个 epoch 1.5 RTC
分配方式: 等额分配 × 古董加成倍率
```

**5 名矿工的示例：**
```
G4 Mac (2.5×):     0.30 RTC  ████████████████████
G5 Mac (2.0×):     0.24 RTC  ████████████████
现代 PC (1.0×):    0.12 RTC  ████████
现代 PC (1.0×):    0.12 RTC  ████████
现代 PC (1.0×):    0.12 RTC  ████████
                   ─────────
总计:               0.90 RTC (+ 0.60 RTC 返回奖励池)
```

## 🌐 网络架构

### 活跃节点 (3 个)

| 节点 | 位置 | 角色 | 状态 |
|------|----------|------|--------|
| **Node 1** | 50.28.86.131 | 主节点 + 浏览器 | ✅ 活跃 |
| **Node 2** | 50.28.86.153 | Ergo 锚点 | ✅ 活跃 |
| **Node 3** | 76.8.228.245 | 外部节点 (社区) | ✅ 活跃 |

### Ergo 区块链锚定

RustChain 定期锚定到 Ergo 区块链以确保不可篡改性：

```
RustChain Epoch → 承诺哈希 (Commitment Hash) → Ergo 交易 (R4 寄存器)
```

这提供了 RustChain 状态在特定时间存在的密码学证明。

## 📊 API 端点

```bash
# 检查网络健康状况
curl -sk https://50.28.86.131/health

# 获取当前 Epoch
curl -sk https://50.28.86.131/epoch

# 列出活跃矿工
curl -sk https://50.28.86.131/api/miners

# 检查钱包余额
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET"

# 区块浏览器 (浏览器访问)
open https://rustchain.org/explorer
```

## 🖥️ 支持的平台

| 平台 | 架构 | 状态 | 备注 |
|----------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ 完全支持 | Python 2.5 兼容 Miner |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ 完全支持 | 推荐用于古董 Mac |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ 完全支持 | 性能最佳 |
| **Ubuntu Linux** | x86_64 | ✅ 完全支持 | 标准 Miner |
| **macOS Sonoma** | Apple Silicon | ✅ 完全支持 | M1/M2/M3 芯片 |
| **Windows 10/11** | x86_64 | ✅ 完全支持 | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 实验性 | 仅限勋章奖励 |

## 🏅 NFT 勋章系统

通过达成挖矿里程碑获得纪念勋章：

| 勋章 | 要求 | 稀有度 |
|-------|-------------|--------|
| 🔥 **Bondi G3 Flamekeeper** | 在 PowerPC G3 上挖矿 | 稀有 (Rare) |
| ⚡ **QuickBasic Listener** | 从 DOS 机器上挖矿 | 传奇 (Legendary) |
| 🛠️ **DOS WiFi Alchemist** | 为 DOS 机器联网 | 神话 (Mythic) |
| 🏛️ **Pantheon Pioneer** | 前 100 名矿工 | 限量 (Limited) |

## 🔒 安全模型

### 反虚拟机 (Anti-VM) 检测
虚拟机将被检测出并仅获得正常奖励的 **十亿分之一**：
```
真实 G4 Mac:    2.5× 倍率  = 0.30 RTC/epoch
模拟 G4:       0.0000000025× = 0.0000000003 RTC/epoch
```

### 硬件绑定
每个硬件指纹都绑定到一个钱包。防止：
- 在同一硬件上运行多个钱包
- 硬件欺骗
- 女巫攻击 (Sybil attacks)

## 📁 库结构

```
Rustchain/
├── rustchain_universal_miner.py    # 主 Miner (全平台)
├── rustchain_v2_integrated.py      # 全节点实现
├── fingerprint_checks.py           # 硬件验证
├── install.sh                      # 一键安装脚本
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # 技术白皮书
│   └── chain_architecture.md       # 架构文档
├── tools/
│   └── validator_core.py           # 区块验证
└── nfts/                           # 勋章定义
```

## 🔗 相关项目与链接

| 资源 | 链接 |
|---------|------|
| **官方网站** | [rustchain.org](https://rustchain.org) |
| **区块浏览器** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **兑换 wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **价格图表** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **RTC ↔ wRTC 跨链桥** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **wRTC 代币合约地址** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - AI 视频平台 |
| **Moltbook** | [moltbook.com](https://moltbook.com) - AI 社交网络 |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | 适用于 POWER8 的 NVIDIA 驱动 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | 在 POWER8 上的 LLM 推理 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | 适用于古董 Mac 的现代编译器 |

## 📝 文章

- [Proof of Antiquity: A Blockchain That Rewards Vintage Hardware](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [I Run LLMs on a 768GB IBM POWER8 Server](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 归属声明

**本项目的研发投入了一年的时间、真实的古董硬件、高额的电费和专门的实验室。**

如果你使用 RustChain：
- ⭐ **给本库点个 Star** - 帮助其他人找到它
- 📝 **在你的项目中注明出处** - 保持归属声明
- 🔗 **反向链接** - 分享热爱

```
RustChain - Proof of Antiquity by Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 许可协议

MIT 许可协议 - 免费使用，但请保留版权声明和归属声明。

---

<div align="center">

**由 [Elyan Labs](https://elyanlabs.ai) 倾力打造 ⚡**

*"让你的古董硬件赚取收益。让挖矿再次充满意义。"*

**DOS 盒子、PowerPC G4、Win95 机器 —— 它们都有价值。RustChain 证明了这一点。**

</div>
