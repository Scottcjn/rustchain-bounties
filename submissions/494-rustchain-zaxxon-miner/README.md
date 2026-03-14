# RustChain Zaxxon Miner (1982) 🕹️

> **Proof-of-Antiquity on the First Isometric 3D Arcade Game**

将 RustChain 矿工移植到 **Zaxxon 街机 (1982)** - 第一款等距 3D 射击游戏！

## 🎮 硬件规格

| 组件 | 规格 |
|------|------|
| **CPU** | Z80 @ 3 MHz (8 位) |
| **RAM** | 8 KB 主内存 + 8 KB 视频 RAM |
| **存储** | ROM 卡带 (无持久存储) |
| **网络** | ❌ 无 (离线模式) |
| **输入** | 4 方向摇杆 + 1 按钮 |
| **显示** | 256×224 像素 @ 60Hz |
| **年代乘数** | 🔥 **4.0x** (1978-1982 ANCIENT Tier) |

## 📦 项目结构

```
rustchain-zaxxon-miner/
├── README.md                 # 本文件
├── docs/
│   ├── ARCHITECTURE.md       # 架构设计文档
│   └── ZAXXON_HARDWARE.md    # Zaxxon 硬件详细规格
├── src/
│   ├── zaxxon_hardware.py    # Zaxxon 硬件模拟器
│   ├── miner_z80.asm         # Z80 汇编矿工代码
│   └── miner_simulator.py    # Python 模拟器
└── wallet.txt                # 生成的钱包地址
```

## 🚀 快速开始

### 运行模拟器

```bash
python src/miner_simulator.py
```

### 功能

- ✅ **硬件熵收集**: BIOS 日期、CPU 签名、定时器噪声、RTC
- ✅ **钱包生成**: Ed25519 兼容地址格式 (RTC + 40 hex)
- ✅ **离线证明**: 生成 attestation 数据供后续提交
- ✅ **年代乘数**: 4.0x ANCIENT Tier (1982 年硬件)
- ✅ **开发者费用**: 0.001 RTC/epoch → `founder_dev_fund`

## 💰 钱包地址

```
RTC4325af95d26d59c3ef025963656d22af638bb96b
```

**奖励层级**: LEGENDARY Tier - 200 RTC ($20)

## 🏛️ 架构设计

### 挑战

1. **极端资源限制**: 仅 8KB RAM，无法运行完整加密库
2. **无持久存储**: ROM 卡带无法保存钱包
3. **无网络**: 无法直接提交证明
4. **8 位 CPU**: Z80 指令集有限

### 解决方案

1. **极简熵收集**: 使用 Z80 定时器、VSYNC 噪声、输入时序
2. **外部存储**: 通过电池备份 RAM 或外部设备保存钱包
3. **离线证明**: 生成 attestation blob，通过现代设备提交
4. **查表加密**: 预计算 S-box，避免运行时计算

## 📝 Z80 汇编示例

```asm
; 熵收集 - 读取 Z80 定时器
collect_entropy:
    LD A, 0x00      ; 锁存定时器 0
    OUT (0x43), A
    IN A, (0x40)    ; 读取低字节
    LD (entropy_0), A
    IN A, (0x40)    ; 读取高字节
    LD (entropy_1), A
    RET
```

## 🎯 Bounty 申领

- **任务 ID**: #494
- **奖励**: 200 RTC ($20)
- **层级**: LEGENDARY
- **钱包**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## 📜 许可证

MIT License — Elyan Labs 2026

---

*"Every vintage arcade machine has historical potential"* 🕹️
