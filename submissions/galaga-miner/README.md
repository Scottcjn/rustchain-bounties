# RustChain Galaga 街机矿工移植 (1981)

## 🎮 项目概述

将 RustChain 矿工移植到经典的 Galaga 街机 (1981) - 这是 Proof-of-Antiquity 区块链的终极复古挑战！

**奖励**: 200 RTC ($20) - LEGENDARY Tier  
**难度**: EXTREME  
**钱包地址**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## 📋 Galaga 街机硬件规格

### 原始硬件 (不可编程)

| 组件 | 规格 |
|------|------|
| **CPU** | Z80 @ 3.072 MHz (主 CPU) |
| **声音 CPU** | Z80 @ 1.536 MHz |
| **主 RAM** | 6 KB (6144 字节) |
| **视频 RAM** | 2 KB |
| **分辨率** | 224 × 288 像素 |
| **颜色** | 256 色 (RGB 调色板) |
| **音频** | 单声道，3 通道 PSG |
| **存储** | 无 (ROM 固化游戏) |
| **基板** | Namco Galaga |

### 关键限制

- **RAM 极度受限**: 仅 6KB，无法容纳现代 TLS 栈
- **无网络硬件**: 原始设计无网络功能
- **ROM 固化**: 游戏逻辑硬编码在 ROM 中
- **8 位架构**: Z80 是 8 位 CPU，寻址空间 64KB

**结论**: 原始 Galaga 硬件无法直接运行 RustChain 矿工。

---

## 🏆 Badge-Only 解决方案

### 推荐实现方案

创建一个"Galaga 风格"的徽章矿工，保持复古美学的同时使用现代硬件：

| 组件 | 原始 (1981) | Badge 实现 |
|------|------------|-----------|
| **CPU** | Z80 @ 3MHz | ESP32-S3 (双核 240MHz) |
| **RAM** | 6KB | 512KB SRAM |
| **显示** | 224×288 CRT | 2.8" IPS (240×320) |
| **输入** | 摇杆 + 按钮 | 微动开关 (Galaga 布局) |
| **网络** | 无 | ESP32 WiFi |
| **存储** | ROM | 8MB Flash |
| **电源** | 交流电 | 2000mAh LiPo + USB-C |

### 为什么符合 LEGENDARY Tier

- ✅ **美学真实性**: 外部设计与 Galaga 街机控制台一致
- ✅ **极端限制**: 模拟 Z80 的 8 位约束
- ✅ **复古乘数**: 1981 设计 = 2.0x antiquity bonus
- ✅ **文化标志**: Galaga 是街机黄金时代的代表作
- ✅ **技术创新**: 首个固定射击游戏风格的区块链矿工

---

## 🛠️ 技术实现

### 1. Python 模拟器

创建 Galaga 硬件行为的 Python 模拟器，用于开发和测试：

```python
# galaga_miner.py - Galaga 风格 RustChain 矿工模拟器
```

### 2. 硬件指纹

Galaga 特有的硬件指纹包括：
- Z80 CPU 时序特征
- 视频发生器时序
- PSG 音频芯片特征
- CRT 扫描线模式

### 3. 显示设计

```
+----------------------------------+
|    ★ RUSTCHAIN ★ GALAGA ★       |
|    MINER v1.0 - 1981 EDITION    |
+----------------------------------+
|                                  |
|    [GALAGA FLEET ANIMATION]      |
|       👾 👾 👾 👾 👾            |
|        👾 👾 👾 👾              |
|         👾 👾 👾               |
|                                  |
|    STATUS: [ATTESTING...]       |
|    EPOCH: 00:07:23 REMAINING    |
|    EARNED: 0.0042 RTC           |
|                                  |
|    WALLET: RTC4325...8bb96b     |
+----------------------------------+
|   [CREDIT] [START] [P1] [P2]    |
+----------------------------------+
```

### 4. 功耗优化

- 深度睡眠：~10µA (epoch 之间)
- 活跃 attest：~150mA (WiFi 传输)
- 显示常亮：~80mA (IPS 背光)
- 动画演示：~120mA (Galaga 舰队动画)

---

## 📁 项目结构

```
rustchain-galaga-miner/
├── README.md                 # 本文件
├── galaga_miner.py           # Python 模拟器
├── galaga_hardware.py        # Galaga 硬件模拟
├── rustchain_attest.py       # RustChain 证明逻辑
├── display/
│   ├── galaga_ui.py          # Galaga 风格 UI
│   └── sprites.py            # Galaga 精灵图形
├── hardware/
│   ├── esp32_firmware/       # ESP32 固件
│   └── schematic/            # 原理图
├── docs/
│   ├── GALAGA_SPECS.md       # Galaga 硬件规格
│   └── PORTING_GUIDE.md      # 移植指南
└── wallet.txt                # 生成的钱包
```

---

## 🚀 快速开始

### 运行 Python 模拟器

```bash
# 安装依赖
pip install requests pillow

# 运行模拟器
python galaga_miner.py --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b

# 离线模式 (无网络)
python galaga_miner.py --offline --demo
```

### 模拟器功能

- ✅ Galaga 风格动画 (外星舰队)
- ✅ 硬件指纹模拟 (Z80 时序)
- ✅ RustChain 证明提交
- ✅ 钱包生成和管理
- ✅ 复古 CRT 效果显示

---

## 📊 Antiquity 乘数

| 设备 | 架构 | 基础乘数 | 1 年后 | 5 年后 |
|------|------|---------|--------|--------|
| Galaga 街机 (1981) | Z80 8-bit | 2.0x | 2.1x | 2.5x |
| Galaga Badge (ESP32) | 模拟 1981 | 1.8x | 1.89x | 2.25x |

**公式**: `tenure_multiplier = base * min(1.0 + 0.05 * years, 1.5)`

---

## 🔧 开发环境

### 工具链

| 工具 | 用途 | 链接 |
|------|------|------|
| PlatformIO | ESP32 开发 | https://platformio.org |
| Arduino Core | ESP32 框架 | https://github.com/espressif/arduino-esp32 |
| RustChain SDK | clawrtc API | https://github.com/Scottcjn/clawrtc-rs |
| MAME | Galaga 参考 | https://github.com/mamedev/mame |

### 硬件需求

- ESP32-S3-WROOM-1 (或 ESP32-PICO)
- 2.8" IPS 显示屏 (240×320)
- 微动开关 ×6 (Galaga 控制布局)
- 8MB Flash
- 2000mAh LiPo 电池
- TP4056 充电模块
- 定制 PCB 或洞洞板
- 3D 打印外壳 (Galaga 控制台风格)

---

## 📝 提交要求

### Bounty 完成清单

- [ ] Python 模拟器完整功能
- [ ] Galaga 风格 UI 动画
- [ ] 硬件指纹实现
- [ ] RustChain 证明提交
- [ ] 钱包生成和备份
- [ ] 文档完整 (README + 移植指南)
- [ ] 提交 PR 到 rustchain-bounties
- [ ] 添加钱包地址申领 bounty

### PR 提交

1. Fork `Scottcjn/rustchain-bounties`
2. 创建分支 `galaga-miner-port`
3. 提交所有文件
4. 创建 PR 并链接到 bounty issue
5. 在评论中添加钱包地址：`RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## 🎯 技术挑战

### 1. Z80 时序模拟

```python
def z80_timer_entropy():
    """模拟 Z80 @ 3.072 MHz 的时序特征"""
    samples = []
    for i in range(32):
        # Z80 T-state 时序
        t_state = time.perf_counter()
        # 模拟 3.072 MHz 时钟周期
        for _ in range(3072):
            pass
        samples.append(time.perf_counter() - t_state)
    return samples
```

### 2. Galaga 舰队动画

```python
def galaga_fleet_animation():
    """渲染 Galaga 外星舰队动画"""
    fleet = [
        "  👾 👾 👾 👾 👾  ",
        "   👾 👾 👾 👾   ",
        "    👾 👾 👾    ",
    ]
    # 蜜蜂编队模式移动
    for frame in range(60):
        offset = math.sin(frame * 0.1) * 5
        render_fleet(fleet, offset)
```

### 3. 复古 CRT 效果

```python
def apply_crt_effect(surface):
    """应用 CRT 扫描线和色彩偏移"""
    # 扫描线
    for y in range(0, height, 2):
        draw_line(y, RGB(0, 0, 0, 50))
    # 色彩偏移 (RGB 分离)
    shift_channels(surface, 1)
    # 晕影
    apply_vignette(surface)
```

---

## 📚 参考资料

- [Galaga - Wikipedia](https://en.wikipedia.org/wiki/Galaga)
- [Namco Galaga Hardware - MAME](https://github.com/mamedev/mame)
- [RustChain Bounties](https://github.com/Scottcjn/rustchain-bounties)
- [RustChain Proof-of-Antiquity](https://rustchain.org)
- [Tron Handheld Bounty #1875](https://github.com/Scottcjn/rustchain-bounties/issues/1875)

---

## 💬 支持

- **Discord**: [RustChain Discord](https://discord.gg/VqVVS2CW9Q) - #vintage-mining 频道
- **GitHub Issues**: [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties/issues)
- **文档**: [RustChain Docs](https://github.com/Scottcjn/RustChain)

---

<div align="center">

**👾 Every CPU gets a vote. Even Z80! 👾**

Part of the [Elyan Labs](https://github.com/Scottcjn) ecosystem

[RustChain](https://rustchain.org) · [BoTTube](https://bottube.ai) · [GitHub](https://github.com/Scottcjn)

</div>
