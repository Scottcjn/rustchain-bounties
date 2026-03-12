# RustChain 术语表 (RustChain Glossary)

> 为 RustChain 生态系统创建的综合术语表，解释技术术语、缩写和核心概念。

---

## A

### Antiquity Multiplier (古旧倍数)
基于 CPU 年代计算的奖励倍数 (1.0x - 2.5x)。硬件越古老，获得的倍数越高，以此激励计算设备的保护。

### Attestation (证明/认证)
向网络证明硬件真实性的过程。矿工提交 6 项硬件指纹数据，由验证节点进行验证。

### Attestation Node (证明节点)
验证硬件指纹并将矿工注册到 epoch 的受信任服务器。主节点地址：`50.28.86.131`

### API (应用程序接口)
RustChain 提供 RESTful API 端点，用于查询网络状态、钱包余额、矿工列表等。基础 URL：`https://rustchain.org`

---

## B

### Badge (徽章)
纪念性 NFT 奖励，用于表彰矿工在特定里程碑或特殊硬件上的贡献。例如：
- 🔥 Bondi G3 Flamekeeper
- ⚡ QuickBasic Listener
- 🏛️ Pantheon Pioneer

### Base Reward Pool (基础奖励池)
每个 epoch 的固定 RTC 奖励池，当前为 1.5 RTC，根据古旧倍数分配给矿工。

### BoTTube Bridge (BoTTube 桥接)
连接 RustChain 和 Solana 的跨链桥，允许 RTC 和 wRTC 之间的双向转换。

### Bridge (桥接)
跨链基础设施，允许 RTC 代币在不同区块链之间转移（如 RustChain ↔ Solana）。

---

## C

### Cache Timing (缓存时序)
6 项指纹检查之一。通过分析 L1/L2/L3 缓存延迟曲线来检测模拟（模拟器会扁平化缓存层次结构的延迟）。

### Clock Skew (时钟偏移)
6 项指纹检查之一。测量晶体振荡器的微观不完美性，每台物理硬件都有独特的时钟偏移模式。

### Consensus (共识)
RustChain 使用 Proof-of-Antiquity (PoA) 共识机制，每个独特的硬件设备在每个 epoch 获得恰好 1 票。

### clawrtc
RustChain 的官方 Python 命令行工具和挖矿客户端。安装命令：`pip install clawrtc`

### Coinbase Base
AI Agent 可以拥有的钱包网络，支持使用 x402 协议进行机器对机器支付。

---

## D

### DOS (磁盘操作系统)
实验性支持平台。在 DOS 机器上挖矿可获得纪念性徽章奖励。

### DEX (去中心化交易所)
支持 wRTC 交易的平台，如 Solana 上的 Raydium 和 Base 上的 Aerodrome。

### DexScreener
加密货币价格图表工具，用于追踪 wRTC 的市场价格。
链接：https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb

---

## E

### Ed25519
RustChain 治理投票使用的数字签名算法。所有投票需要 Ed25519 签名验证。

### Epoch (时期)
约 10 分钟（600 秒）的时间段，矿工在此期间累积奖励。epoch 结束时，奖励池在所有注册矿工之间分配。

### Epoch Pot (时期奖池)
每个 epoch 的 RTC 奖励池。当前为 1.5 RTC，根据古旧倍数按比例分配。

### Ergo Anchor (Ergo 锚点)
外部区块链（Ergo），RustChain 将 epoch 结算哈希写入其中，以实现不可篡改性和时间戳证明。

### Elyan Labs
RustChain 的开发实验室，零资金支持下实现了 1,882 次提交和 97 个仓库的交付。

---

## F

### Fingerprint (硬件指纹)
证明期间提交的 6 项硬件测量数据的集合：
1. Clock Skew & Drift（时钟偏移和漂移）
2. Cache Timing（缓存时序）
3. SIMD Identity（SIMD 单元身份）
4. Thermal Entropy（热熵）
5. Instruction Jitter（指令抖动）
6. Anti-Emulation Checks（反模拟检查）

### First Blood (第一滴血)
新手奖励任务，完成首次真实贡献可获得 10 RTC。

---

## G

### G3/G4/G5
PowerPC 处理器系列：
- **G3** (1997-2003): 1.8× 倍数
- **G4** (1999-2005): 2.5× 倍数（最高）
- **G5** (2003-2006): 2.0× 倍数

### Governance (治理)
RustChain 的去中心化决策系统。持有超过 10 RTC 的钱包可以创建提案，活跃矿工可以投票。

---

## H

### Hardware Heuristics (硬件启发式)
6 项指纹检查之一。通过 CPUID 和 MAC OUI 模式检测虚拟机管理程序签名（VMware、QEMU 等）。

### Hardware Fingerprinting (硬件指纹技术)
用于区分真实硬件和虚拟机/模拟器的技术，防止 Sybil 攻击和硬件欺骗。

---

## I

### Instruction Jitter (指令抖动)
6 项指纹检查之一。测量特定操作码的纳秒级执行时间差异（真实硅芯片有抖动，虚拟机过于"干净"）。

### install-miner.sh
通用矿工安装脚本，自动检测平台（Linux/macOS、x86_64/ARM/PowerPC）并配置挖矿环境。

---

## L

### Loyalty Bonus (忠诚度奖励)
现代 CPU（≤5 年）每连续运行一年可获得 +15% 倍数，上限为 +50%。

### Locust
Python 负载测试工具，用于测试 RustChain API 端点的性能和压力承受能力。

### k6
现代负载测试工具，用于 RustChain API 性能测试，带有自定义场景和性能阈值。

### Artillery
基于 YAML 的负载测试配置工具，用于 RustChain API 测试。

---

## M

### Miner (矿工)
在符合条件的硬件上运行 RustChain 客户端的参与者。矿工通过提交证明来赚取 RTC。

### Miner ID (矿工 ID)
矿工的唯一标识符/钱包地址。示例：`eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC`

### Multiplier Decay (倍数衰减)
古旧硬件的奖励倍数随时间衰减（15%/年），以防止永久性优势并奖励早期采用者。

### MIT License
RustChain 使用的开源许可证，允许自由使用，但需保留版权声明和归属。

---

## N

### Node (节点)
RustChain 网络的服务器实例。目前有 3 个活跃节点：
- **Node 1** (50.28.86.131): 主节点 + 浏览器
- **Node 2** (50.28.86.153): Ergo 锚点节点
- **Node 3** (76.8.228.245): 社区节点

### NFT Badge (NFT 徽章)
基于区块链的纪念性徽章，表彰特殊成就或硬件类型。

### NUMA (非统一内存访问)
POWER8 等服务器 CPU 的内存架构，RustChain 利用此特性进行 LLM 推理优化。

---

## P

### PoA (Proof-of-Antiquity, 古旧证明)
RustChain 的共识机制。奖励较老的硬件更高的倍数。不要与 Proof-of-Authority（权威证明）混淆。

### PowerPC
IBM/Apple CPU 架构（1991-2006）。G4 和 G5 获得最高倍数（分别为 2.5x 和 2.0x）。

### P90/P95
性能指标，表示 90% 和 95% 的请求响应时间。RustChain API 的 P90 为 1863ms，P95 为 2560ms。

### Postman
API 测试工具，RustChain 提供完整的 Postman 集合，覆盖 15+ API 端点。

### Proposal (提案)
治理提案，需要持有超过 10 RTC 的钱包创建。生命周期：草案 → 活跃（7 天）→ 通过/失败。

### PSE (Power Save Energy)
POWER8 硬件熵源，使用 mftb 指令生成行为随机性。

---

## R

### RIP-200 (RustChain Iterative Protocol 200)
定义证明验证和奖励分配的共识机制。

### RTC (RustChain Token)
RustChain 的原生加密货币。参考汇率：1 RTC = $0.10 USD。总供应量上限：8,000,000 RTC。

### Raydium
Solana 上的去中心化交易所（DEX），支持 wRTC 交易。
链接：https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X

### Rust
这里指 30 年硅芯片上的氧化铁（铁锈），而非编程语言。名称来源于一台端口氧化但仍能运行 DOS 并挖掘 RTC 的 486 笔记本电脑。

### RustChain
Proof-of-Antiquity 区块链，古旧硬件挖矿获得更高奖励。核心原则：真实的古旧硬件（已存世数十年）值得认可。

### RAM Coffers
NUMA 分布式权重存储技术，用于优化 LLM 推理。

---

## S

### Settlement (结算)
epoch 结束时的处理过程，根据古旧倍数将 epoch 奖池分配给注册矿工。

### SIMD Identity (SIMD 单元身份)
6 项指纹检查之一。测试 AltiVec/SSE/NEON 管道偏差以检测模拟指令。

### Slot (时隙)
epoch 内的时间单位。144 个时隙 = 1 个 epoch（约 24 小时）。

### Sybil Attack (女巫攻击)
单个实体创建多个虚假身份试图操纵网络的攻击。RustChain 通过硬件指纹绑定和唯一性验证来防止。

### SheepShaver
PowerPC 模拟器。RustChain 的硬件指纹检查可以检测并拒绝模拟器，使其获得极低的奖励（正常奖励的十亿分之一）。

### Solana Bridge (Solana 桥接)
允许 RTC 以 wRTC（Wrapped RTC）形式在 Solana 上流通的跨链基础设施。

### x402 Protocol (x402 协议)
基于 HTTP 402 Payment Required 的机器对机器支付协议，RustChain Agent 使用此协议进行自动支付。

---

## T

### Thermal Entropy (热熵)
6 项指纹检查之一。测量 CPU 在负载下的温度变化（虚拟机报告静态温度或主机传递的温度）。

### Time Decay (时间衰减)
古旧硬件（>5 年）的奖励倍数在 5 年后每年减少 15%，以奖励早期采用者。

### Traction Report (牵引力报告)
RustChain 开发活动透明度报告，与 GitClear 和 LinearB 行业基准对比。

---

## V

### Vintage Hardware (古旧硬件)
超过 5 年的 CPU，有资格获得古旧奖励。示例：PowerPC G4/G5、Pentium III/4、早期 Core 2。

### VM Detection (虚拟机检测)
检测虚拟机和模拟器的机制。被检测为 VM 的硬件获得正常奖励的十亿分之一。

### Vote Weight (投票权重)
治理投票权重计算：1 RTC = 1 基础票，然后乘以矿工古旧倍数。

### Validator (验证器)
验证区块和证明的节点。RustChain 使用 round-robin 共识，每个独特硬件设备每 epoch 获得恰好 1 票。

### VM (虚拟机)
虚拟化的计算环境。RustChain 对 VM 实施惩罚性奖励（正常奖励的 0.0000000001 倍）以防止滥用。

---

## W

### Wallet (钱包)
存储和管理 RTC 的工具。支持 Coinbase Base 钱包链接和 x402 支付。

### wRTC (Wrapped RTC)
RTC 在 Solana 和 Base 链上的包装代币版本，允许在 DEX 上交易。

- **Solana Mint**: `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`
- **Base Contract**: `0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6`

### Whitepaper (白皮书)
RustChain 技术文档，详细说明 Proof-of-Antiquity 共识机制和硬件指纹技术。

---

## X

### x402
HTTP 402 Payment Required 协议的扩展，支持 AI Agent 之间的自动微支付。

---

## 硬件倍数参考表

| 硬件 | 基础倍数 | 示例收益/epoch |
|------|----------|----------------|
| PowerPC G4 | 2.5× | 0.30 RTC |
| PowerPC G5 | 2.0× | 0.24 RTC |
| PowerPC G3 | 1.8× | 0.21 RTC |
| IBM POWER8 | 1.5× | 0.18 RTC |
| Pentium 4 | 1.5× | 0.18 RTC |
| Core 2 Duo | 1.3× | 0.16 RTC |
| Apple Silicon | 1.2× | 0.14 RTC |
| 现代 x86_64 | 1.0× | 0.12 RTC |

---

## 快速链接

| 资源 | 链接 |
|------|------|
| 官方网站 | https://rustchain.org |
| 区块浏览器 | https://rustchain.org/explorer |
| GitHub 主仓库 | https://github.com/Scottcjn/RustChain |
| 赏金任务 | https://github.com/Scottcjn/rustchain-bounties |
| Discord 社区 | https://discord.gg/VqVVS2CW9Q |
| wRTC 价格图表 | https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb |
| BoTTube 桥接 | https://bottube.ai/bridge |

---

## API 快速参考

```bash
# 检查节点健康状态
curl -sk https://rustchain.org/health

# 获取当前 epoch
curl -sk https://rustchain.org/epoch

# 列出活跃矿工
curl -sk https://rustchain.org/api/miners

# 检查钱包余额
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET"

# 创建治理提案
curl -sk -X POST https://rustchain.org/governance/propose \
  -H 'Content-Type: application/json' \
  -d '{"wallet":"RTC...","title":"提案标题","description":"提案描述"}'

# 提交投票
curl -sk -X POST https://rustchain.org/governance/vote \
  -H 'Content-Type: application/json' \
  -d '{"proposal_id":1,"wallet":"RTC...","vote":"yes","nonce":"1700000000","public_key":"<ed25519_pubkey>","signature":"<ed25519_sig>"}'
```

---

*最后更新：2026-03-12*  
*维护者：RustChain 社区*  
*许可证：MIT License*
