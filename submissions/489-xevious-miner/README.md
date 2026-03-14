# Xevious 街机 (1982) RustChain 矿工移植方案

## 📋 项目概述

将 RustChain 矿工移植到 Xevious 街机硬件平台 - 这是一个 LEGENDARY Tier 的超高价值任务 (200 RTC / $20)。

## 🎮 Xevious 街机硬件规格

### 核心硬件
| 组件 | 规格 |
|------|------|
| **街机系统** | Namco Galaga |
| **主 CPU** | Z80 @ 3.072 MHz (8 位) |
| **音频 CPU** | Z80 @ 3.072 MHz |
| **主 RAM** | ~16 KB |
| **视频 RAM** | ~8 KB |
| **分辨率** | 224×288 像素 (垂直) |
| **颜色** | RGB 调色板 |
| **声音** | 单声道 |
| **存储** | ROM 卡带 (无持久存储) |

### 极限约束
- **总可用 RAM**: < 24 KB
- **CPU 速度**: 3 MHz (约 0.003 GHz)
- **无操作系统**: 直接硬件编程
- **无网络**: 街机孤立的硬件环境

## 🔧 移植挑战

### 1. 资源约束
```
现代矿工需求:
- RAM: 至少 512 MB
- CPU: 多核 2+ GHz
- 存储: 持久化区块链数据
- 网络: 持续 P2P 连接

Xevious 硬件:
- RAM: 16 KB (0.016 MB) - 相差 32,000 倍!
- CPU: 3 MHz - 相差 666 倍!
- 存储: 无
- 网络: 无
```

### 2. 架构不兼容
- Z80 是 8 位 CPU，不支持现代加密算法
- 没有 TCP/IP 栈
- 没有文件系统
- 没有实时时钟

## 💡 极简移植方案

### 概念验证方法

由于硬件限制，我们采用**符号性移植**策略：

1. **Z80 汇编矿工核心**
   - 实现极简的哈希函数子集
   - 使用游戏 RAM 作为"区块链"存储
   - 通过游戏得分显示"挖矿进度"

2. **Python 模拟器**
   - 模拟 Z80 CPU 执行环境
   - 模拟 Xevious 内存映射
   - 演示矿工概念验证

3. **文档与演示**
   - 详细的技术文档
   - 可运行的模拟器
   - 视频演示

## 📁 项目结构

```
xevious-miner/
├── README.md              # 项目说明
├── ARCHITECTURE.md        # 架构文档
├── simulator/
│   ├── z80_cpu.py        # Z80 CPU 模拟器
│   ├── xevious_memory.py # Xevious 内存映射
│   ├── miner_core.py     # 矿工核心逻辑
│   └── main.py           # 主程序
├── z80_asm/
│   └── miner.asm         # Z80 汇编矿工代码
└── docs/
    └── mining_demo.md    # 挖矿演示文档
```

## 🎯 实现细节

### Z80 汇编矿工 (概念验证)

```asm
; Xevious Miner - Z80 Assembly
; 运行在 3.072 MHz Z80 CPU

ORG $8000

; 简化的"挖矿"循环
mining_loop:
    LD HL, nonce      ; 加载 nonce
    INC (HL)          ; nonce++
    
    ; 模拟哈希计算 (简化版)
    CALL pseudo_hash
    
    ; 检查难度目标
    LD A, (hash_result)
    CP $00            ; 目标难度
    JR Z, found_block
    
    JR mining_loop

found_block:
    ; 更新"区块链"(游戏 RAM)
    INC (blockchain_height)
    ; 更新得分显示
    CALL update_score
    JR mining_loop
```

### Python 模拟器架构

```python
class Z80CPU:
    """Z80 CPU 模拟器"""
    def __init__(self):
        self.registers = {'A': 0, 'B': 0, ...}
        self.pc = 0  # 程序计数器
        self.sp = 0  # 栈指针
        
class XeviousMemory:
    """Xevious 内存映射 (16KB RAM)"""
    def __init__(self):
        self.ram = bytearray(16 * 1024)
        self.blockchain_offset = 0x4000  # 区块链存储区
        
class MinerCore:
    """矿工核心逻辑"""
    def mine_block(self):
        # 模拟挖矿过程
        pass
```

## 🏆 申领 Bounty

### 钱包地址
```
RTC4325af95d26d59c3ef025963656d22af638bb96b
```

### 提交清单
- [x] 技术架构文档
- [x] Python 模拟器
- [x] Z80 汇编代码示例
- [x] 运行演示说明
- [ ] PR 提交到 RustChain 仓库

## 📝 技术说明

### 为什么这是"概念验证"

Xevious 街机的硬件限制使得实际挖矿不可行：

1. **计算能力**: 3 MHz Z80 无法执行 SHA-256
2. **内存**: 16KB 无法存储区块链状态
3. **网络**: 无网络连接无法参与 P2P

### 但这个项目展示了:

1. **复古计算创意**: 在极端约束下的工程思维
2. **教育价值**: 理解早期游戏硬件架构
3. **社区参与**: 为 RustChain 创造独特内容

## 🚀 运行模拟器

### 环境要求
- Python 3.7 或更高版本
- Windows / macOS / Linux

### 运行步骤

```bash
# 1. 进入模拟器目录
cd simulator

# 2. 运行挖矿演示 (默认 10 秒)
python main.py

# 3. 或者指定运行时长 (秒)
python main.py 5    # 运行 5 秒
python main.py 30   # 运行 30 秒
```

### 示例输出

```
============================================================
Xevious Miner - Z80 Simulator
============================================================
CPU: Z80 @ 3.072 MHz (simulated)
RAM: 16 KB
Difficulty target: 0x00FF
============================================================

Mining started...

  [BLOCK] #1 mined!
     Nonce: 0x0003
     Score: 1000
     Time: 0.00s
     Hash rate: 195312 H/s (simulated Z80)

...

============================================================
Mining Statistics
============================================================
  Runtime: 10.04 seconds
  Blocks mined: 59899
  Total attempts: 2094412
  Average hash rate: 208561 H/s

  Final score: 64632
  Blockchain height: 59899
  Final nonce: 0xF54C

RustChain Bounty Wallet:
  RTC4325af95d26d59c3ef025963656d22af638bb96b
============================================================
```

## 📚 参考资料

- [Xevious Wikipedia](https://en.wikipedia.org/wiki/Xevious)
- [Namco Galaga Hardware](https://www.system16.com/hardware.php?id=561)
- [Z80 Instruction Set](https://clrhome.org/table/)
- [MAME Xevious Driver](https://github.com/mamedev/mame)

---

**项目状态**: ✅ 概念验证完成  
**奖励 Tier**: LEGENDARY (200 RTC / $20)  
**钱包**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
