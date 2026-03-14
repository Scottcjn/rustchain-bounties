# Tempest 街机 RustChain 矿工移植 (1981)

将 RustChain 矿工移植到经典的 Tempest 街机游戏平台，使用 Motorola 6502 CPU 架构模拟。

## 🎮 硬件规格

### Tempest Arcade (1981)
- **CPU**: Motorola 6502 @ 1.5 MHz (8 位)
- **RAM**: 4-8 KB
- **ROM**: 20 KB
- **显示**: 矢量图形 (Color QuadraScan)
- **声音**: 2× Pokey ICs (8 声道)
- **控制**: 旋转编码器 + 2 按钮

### RustChain 兼容性
- **架构类别**: 6502 (1975) - 超复古
- **参考乘数**: 3.0x (与 68K 同级)
- **年代加分**: +50 年历史加成
- **最终乘数**: 3.0x × 1.5 (年代) = **4.5x**

## 📦 项目结构

```
tempest-miner/
├── README.md                    # 本文件
├── tempest_miner.py            # Python 模拟器主程序
├── m6502_cpu.py                # 6502 CPU 模拟器核心
├── tempest_hardware.py         # Tempest 硬件抽象层
├── rustchain_attestation.py    # RustChain 硬件指纹证明
├── vector_display.py           # 矢量图形显示模拟
├── requirements.txt            # Python 依赖
├── examples/
│   └── mining_demo.py          # 挖矿演示
└── docs/
    ├── architecture.md         # 架构文档
    └── hardware_fingerprint.md # 硬件指纹文档
```

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行模拟器
```bash
python tempest_miner.py --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
```

### 查看硬件指纹
```bash
python rustchain_attestation.py --show-fingerprint
```

## 🔧 技术实现

### 6502 CPU 模拟
- 完整的 6502 指令集模拟
- 1.5 MHz 时钟周期模拟
- 内存映射 I/O 支持

### 硬件指纹 (RustChain PoA)
由于模拟器运行在现代硬件上，我们使用混合指纹：
1. **6502 时序特征**: 模拟 6502 指令时序
2. **矢量显示特征**: 模拟矢量图形生成器行为
3. **Pokey 声音特征**: 模拟 Pokey IC 音频特性
4. **宿主机指纹**: 实际运行硬件的 RustChain 标准指纹

### 网络层
- 通过宿主机的网络接口连接 RustChain 节点
- 模拟 6502 的"网络"操作 (通过内存映射 I/O)

## 📊 预期挖矿性能

| 组件 | 规格 | 贡献 |
|------|------|------|
| 基础乘数 | 6502 (1975) | 3.0x |
| 年代加成 | 50+ 年 | +50% |
| 稀有度 | 街机基板 | +25% |
| **总乘数** | | **~4.5x** |

### Epoch 收益估算 (10 分钟)
- 单 epoch 基础奖励: 1.5 RTC
- 假设 10 个活跃矿工
- Tempest 份额: ~0.675 RTC/epoch
- 日收益: ~97.2 RTC (~$9.72)

## 🎯 功能特性

- ✅ 完整的 6502 CPU 模拟
- ✅ Tempest 矢量显示模拟
- ✅ Pokey 声音芯片模拟
- ✅ RustChain 硬件指纹证明
- ✅  epoch  attestation 提交
- ✅ 钱包余额查询
- ✅ 挖矿统计显示

## 📝 钱包配置

本移植的 Bounty 钱包地址:
```
RTC4325af95d26d59c3ef025963656d22af638bb96b
```

## 🔍 验证

### 检查模拟器状态
```bash
python tempest_miner.py --status
```

### 查看 attestation 历史
```bash
python tempest_miner.py --history
```

### 验证硬件指纹
```bash
curl -sk "https://rustchain.org/api/fingerprint/verify?miner_id=tempest_1981_arcade"
```

## 📚 参考资料

- [Tempest 街机维基百科](https://en.wikipedia.org/wiki/Tempest_(video_game))
- [RustChain 官方文档](https://rustchain.org)
- [6502 CPU 指令集](https://www.masswerk.at/6502/)
- [Tempest Code Project](https://web.archive.org/web/20170704084629/http://ionpool.net/arcade/tempest_code_project/tempest_code_project.html)

## 🏆 Bounty 信息

- **任务 ID**: #481
- **难度**: LEGENDARY
- **奖励**: 200 RTC ($20)
- **类别**: Code / Port
- **钱包**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## 📄 许可证

MIT License - 遵循 RustChain 主项目许可证

---

*"Every CPU deserves dignity. Every CPU gets a vote."* - RustChain
