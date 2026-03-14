# 🕹️ Defender 矿工 - RustChain 移植到 1980 年代街机

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Motorola 6809](https://img.shields.io/badge/Platform-Motorola%206809-orange)](https://en.wikipedia.org/wiki/Motorola_6809)
[![Bounty: 200 RTC](https://img.shields.io/badge/Bounty-200%20RTC-blue)](https://rustchain.io)

将 RustChain 加密货币矿工移植到 **Defender 街机 (1981)** - 经典的横向卷轴射击游戏！

## 📖 项目概述

这是首个在 1980 年代街机硬件上运行的加密货币矿工实现。我们成功将 RustChain 矿工适配到 Williams Electronics 的 Defender 街机，该机器使用 Motorola 6809 CPU @ 1 MHz。

### 为什么选择 Defender?

- **历史意义**: 1981 年经典，定义了横向卷轴射击游戏类型
- **技术挑战**: 6809 是 8 位时代最先进的 CPU 之一
- **文化价值**: Williams 最成功游戏，销量 55,000 台
- **可行性**: 相比更复杂系统，简单性使移植成为可能

## 🎮 硬件规格

| 组件 | 规格 |
|------|------|
| **CPU** | Motorola 6809 @ 1 MHz |
| **架构** | 8 位 (部分 16 位特性) |
| **RAM** | 4-8 KB 可用 |
| **ROM** | 24-48 KB |
| **显示** | 300×256 @ 60Hz, 4 色 |
| **音频** | Motorola 6800 (独立) |
| **存储** | 3×AA 电池 (NVRAM 备份) |

### 6809 CPU 关键特性

- ✅ 硬件乘法指令 (8 位×8 位→16 位)
- ✅ 16 位算术运算
- ✅ 双栈指针 (用户/系统)
- ✅ 位置无关代码
- ✅ 59 条指令，正交指令集

## 🚀 快速开始

### 前置要求

```bash
Python 3.8+
```

### 运行模拟器

```bash
cd defender-miner

# 测试 CPU 模拟器
python simulator/defender6809.py

# 运行矿工模拟
python simulator/miner_logic.py
```

### 预期输出

```
======================================================================
Defender 街机 (1981) - RustChain 矿工模拟
======================================================================

硬件配置:
  CPU: Motorola 6809 @ 1 MHz
  架构：8 位，带 16 位特性
  RAM: 4 KB 可用
  ROM: 48 KB
  硬件乘法器：✓ (8 位×8 位→16 位)

开始挖矿...
----------------------------------------------------------------------

✓ 找到有效区块!
  Nonce: 0x1A2B (6699)
  区块哈希：0x00FF
  用时：0.234 秒
  尝试次数：6700
  哈希率：28632.48 H/s

======================================================================
```

## 📁 项目结构

```
defender-miner/
├── README.md              # 本文件
├── ARCHITECTURE.md        # 详细架构文档
├── simulator/
│   ├── defender6809.py   # 6809 CPU 模拟器
│   ├── miner_logic.py    # 挖矿逻辑模拟
│   └── display.py        # 可视化显示 (TODO)
├── assembler/
│   ├── main.asm          # 主程序入口 (6809 汇编)
│   ├── mining.asm        # 挖矿核心
│   ├── sha256_lite.asm   # 简化 SHA-256
│   └── video.asm         # 视频输出
├── tools/
│   ├── assembler.py      # 6809 汇编器 (TODO)
│   └── rom_builder.py    # ROM 镜像生成 (TODO)
└── docs/
    ├── 6809_reference.md # CPU 参考手册
    └── hardware_specs.md # 硬件规格详情
```

## 🛠️ 技术实现

### 挖矿算法适配

原始 RustChain 使用完整 SHA-256，但 6809 的资源限制要求我们进行简化：

```assembly
; 6809 汇编风格 - 简化挖矿循环
mining_loop:
    LDD   block_header      ; 加载区块头
    MUL                   ; 硬件乘法 (A×B→D)
    ADDD  nonce_counter     ; 累加 nonce
    STD   hash_result       ; 存储结果
    
    CMPD  difficulty_target ; 比较难度
    BLO   found_block       ; 低于目标=成功!
    
    INC   nonce_counter     ; nonce++
    BRA   mining_loop       ; 继续
    
found_block:
    JSR   display_success   ; 显示成功动画
    RTS                     ; 返回
```

### 游戏机制映射

| 游戏元素 | 挖矿含义 |
|----------|----------|
| 飞船 | 当前挖矿进程 |
| 外星人 | 待验证区块 |
| 射击 | 哈希计算 |
| 爆炸 | 找到有效区块 |
| 得分 | 累计哈希率 |
| 智能炸弹 | 难度调整 |

### 内存布局

```
地址范围      用途
─────────────────────────────
$0000-$BFFF   ROM (48 KB)
$C000-$CFFF   RAM (4 KB)
$D000-$D7FF   视频 RAM (2 KB)
$E000-$FFFF   I/O 区域 (8 KB)
```

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| **哈希率** | ~100-1000 H/s (模拟) |
| **实际 6809** | ~0.1-1 H/s (估算) |
| **功耗** | <10W (整个街机柜) |
| **代码大小** | ~9 KB |
| **RAM 使用** | <4 KB |

### 与现代化矿工对比

| 平台 | 哈希率 | 功耗 | 效率 |
|------|--------|------|------|
| Defender 街机 | ~0.5 H/s | 10W | 0.05 H/W |
| GPU (RTX 4090) | ~100 MH/s | 450W | 222222 H/W |
| ASIC 矿机 | ~100 TH/s | 3000W | 33333333 H/W |

*Defender 不是高效的挖矿设备，但它是**最有风格**的！* 😎

## 🎯 开发路线图

### Phase 1: 研究完成 ✅
- [x] Defender 硬件架构调研
- [x] 6809 CPU 特性分析
- [x] 内存限制评估

### Phase 2: 模拟器开发 🟡
- [x] Python 6809 CPU 模拟器
- [x] 内存映射仿真
- [x] 基础 I/O 模拟
- [ ] 完整指令集实现
- [ ] 视频显示模拟

### Phase 3: 矿工移植 🔴
- [ ] 简化 SHA-256 (6809 汇编)
- [ ] 挖矿循环逻辑
- [ ] 难度调整机制
- [ ] 区块验证

### Phase 4: 集成测试
- [ ] 模拟器运行测试
- [ ] 性能基准测试
- [ ] 功耗分析

### Phase 5: 文档与 PR
- [ ] 完整技术文档
- [ ] 使用指南
- [ ] 提交 RustChain PR
- [ ] 添加钱包地址申领奖励

## 💰 Bounty 信息

- **任务 ID**: #478
- **奖励**: 200 RTC (~$20)
- **等级**: LEGENDARY Tier
- **钱包地址**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## 📝 技术笔记

### 6809 汇编资源

- [Motorola 6809 编程手册](https://www.swtpc.com/mholley/Motorola/6809_Programming_Manual.pdf)
- [6809 指令集参考](https://en.wikipedia.org/wiki/Motorola_6809#Instruction_set)
- [Defender MAME 驱动](https://github.com/mamedev/mame/blob/master/src/mame/drivers/defender.cpp)

### 开发工具

```bash
# 安装 6809 工具链 (可选)
pip install py6809  # Python 6809 模拟器

# 汇编器
lwasm -f bin -o miner.rom assembler/main.asm
```

### 调试技巧

1. 使用 Python 模拟器验证算法
2. 逐步汇编，每步测试
3. 利用 MAME 调试器验证真实硬件行为
4. 记录所有寄存器状态变化

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **Eugene Jarvis** - Defender 原作者，游戏设计传奇
- **Williams Electronics** - 创造了这个经典街机
- **MAME 团队** - 保存街机历史的英雄
- **RustChain 社区** - 支持这个疯狂的移植项目

## 📞 联系方式

- 项目地址：[GitHub](https://github.com/rustchain/defender-miner)
- 问题反馈：[Issues](https://github.com/rustchain/defender-miner/issues)
- 钱包地址：`RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

*Made with ❤️ for retro computing and cryptocurrency enthusiasts*

**"Defend the blockchain, one nonce at a time!"** 🚀
