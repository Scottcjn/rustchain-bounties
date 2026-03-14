# RustChain Miner for Atari Breakout (1976)

## 🎮 项目概述

将 RustChain 矿工移植到 Atari Breakout 街机 (1976) - 可能是最古老的 RustChain 移植目标！

**目标硬件**: Atari Breakout Arcade
- **CPU**: MOS Technology 6502 @ 1.5 MHz
- **架构**: 8 位
- **RAM**: 仅几 KB (估计 4-8 KB)
- **年代**: 1976 年
- **预期古老倍率**: **5.0x** (比 8086 的 4.0x 更高！)

## 📋 技术规格

### 6502 处理器特性
- 8 位数据总线
- 16 位地址总线 (64KB 寻址空间)
- 56 条指令
- 约 3,500 个晶体管
- NMOS 工艺

### 内存限制
```
总可用内存：~4-8 KB
矿工代码：    ~2 KB
熵收集缓冲：  ~256 bytes
钱包存储：    ~128 bytes
网络缓冲：    ~512 bytes (如果有网络)
```

## 🏗️ 移植架构

### 极简设计原则
1. **汇编语言实现** - 直接使用 6502 汇编，无编译器依赖
2. **轮询式熵收集** - 利用 VBLANK 中断和玩家输入
3. **离线优先** - 通过 LED 闪烁编码输出证明
4. **最小内存占用** - 所有操作原地进行

### 熵源
```assembly
1. VBLANK 定时器 (60Hz)
2. 玩家拨盘位置
3. 球碰撞时序
4. 砖块破坏模式
5. CPU 周期计数器
```

### 钱包生成
```assembly
; 使用硬件熵生成钱包
- 读取 VBLANK 计数器 (16 位)
- 读取拨盘位置 (8 位)
- 读取游戏状态 (8 位)
- 混合生成 256 位私钥
- 导出钱包地址到屏幕显示
```

## 📁 文件结构

```
breakout-miner/
├── README.md                 # 本文档
├── miner.asm                 # 6502 汇编矿工主程序
├── entropy.asm               # 熵收集例程
├── wallet.asm                # 钱包生成例程
├── breakout_simulator.py     # Python 6502 模拟器
├── breakout_hardware.json    # 硬件规格定义
└── docs/
    ├── 6502_instruction_set.md
    ├── memory_map.md
    └── attestation_protocol.md
```

## 🔧 开发环境

### 6502 汇编工具
- **CA65** (cc65 套件的一部分)
- **Kick Assembler**
- **64tass**

### 模拟器
- **Py65** - Python 6502 模拟器
- **MAME** - Breakout 街机模拟

## 🎯 实现步骤

### 阶段 1: 环境设置
- [x] 研究 Breakout 硬件架构
- [x] 设计极简移植方案
- [ ] 设置 6502 汇编工具链
- [ ] 创建 Python 模拟器

### 阶段 2: 核心实现
- [ ] 实现熵收集例程
- [ ] 实现钱包生成
- [ ] 实现证明循环
- [ ] 实现 LED 编码输出

### 阶段 3: 测试与验证
- [ ] 在模拟器中测试
- [ ] 验证熵质量
- [ ] 测试钱包生成
- [ ] 文档完善

### 阶段 4: 提交
- [ ] 创建 GitHub 仓库
- [ ] 提交 PR 到 RustChain
- [ ] 添加钱包地址申领 bounty
- [ ] 编写技术博客

## 💰 Bounty 信息

- **任务 ID**: #472
- **奖励**: 200 RTC ($20) - LEGENDARY Tier
- **钱包地址**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## 📊 古老性倍率计算

| CPU | 年代 | 倍率 |
|-----|------|------|
| 6502 (Breakout) | 1976 | **5.0x** (目标) |
| 8086 | 1978-1982 | 4.0x |
| 286 | 1982-1985 | 3.8x |
| 386 | 1985-1989 | 3.5x |
| 486 | 1989-1993 | 3.0x |
| Pentium | 1993-1997 | 2.5x |

## 🔬 技术挑战

### 挑战 1: 内存极度受限
**解决方案**: 
- 使用页面零 (Zero Page) 存储关键变量
- 代码覆盖技术 (overlay)
- 最小化栈使用

### 挑战 2: 无网络支持
**解决方案**:
- LED 闪烁编码 (Morse 码变体)
- 屏幕显示钱包地址
- 手动转录证明数据

### 挑战 3: 无标准库
**解决方案**:
- 所有函数手写汇编
- 使用 ROM 中的例程 (如果有)
- 最小化依赖

## 📝 汇编代码示例

```assembly
; ============================================
; RustChain Breakout Miner - 熵收集例程
; ============================================

        .ORG $0200          ; 起始地址

; VBLANK 中断处理程序
VBLANK_IRQ:
        PHA                 ; 保存累加器
        LDA $C040           ; 读取 VBLANK 计数器
        STA ENTROPY_BUF     ; 存储到熵缓冲
        PLA
        RTI

; 主熵收集循环
COLLECT_ENTROPY:
        LDA $C060           ; 读取拨盘位置
        EOR ENTROPY_BUF     ; 混合熵
        STA ENTROPY_BUF
        
        LDA $C061           ; 读取游戏状态
        EOR ENTROPY_BUF+1
        STA ENTROPY_BUF+1
        
        RTS

; 钱包地址显示 (通过砖块颜色编码)
DISPLAY_WALLET:
        ; 将钱包地址编码为砖块颜色模式
        ; 黄色=00, 绿色=01, 橙色=10, 红色=11
        ; 每块砖存储 2 位
        RTS

        .END
```

## 🚀 快速开始

```bash
# 1. 安装 cc65 工具链
# Windows: 下载 https://cc65.github.io/
# macOS: brew install cc65
# Linux: sudo apt install cc65

# 2. 汇编矿工
ca65 miner.asm -o miner.o
ld65 miner.o -o miner.bin

# 3. 在模拟器中运行
python breakout_simulator.py miner.bin

# 4. 查看生成的钱包
cat wallet.txt
```

## 📚 参考资料

- [6502 指令集文档](https://www.masswerk.at/6502/6502_instruction_set.html)
- [Breakout 街机原理图](https://www.arcade-museum.com/)
- [RustChain DOS Miner](https://github.com/Scottcjn/rustchain-dos-miner)
- [Proof-of-Antiquity 白皮书](https://rustchain.org/whitepaper)

## ⚠️ 注意事项

1. 这是概念验证实现，实际运行需要真实 Breakout 街机或精确模拟器
2. 网络功能通过 LED 闪烁编码实现，需要外部解码
3. 钱包地址需要手动备份 (拍照或转录)

## 📄 许可证

MIT License - 与 RustChain 项目保持一致

---

**"Every vintage computer has historical potential"**
**"Every arcade machine has mining potential"** 🕹️
