# Tempest 矿工架构文档

## 概述

本项目将 RustChain 矿工移植到 1981 年的 Tempest 街机游戏平台。由于原始硬件的限制，我们采用**混合模拟架构**：在 6502 CPU 模拟器上运行核心逻辑，通过现代宿主机的网络接口进行实际通信。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Tempest Miner System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  6502 CPU    │  │   Tempest    │  │  RustChain   │       │
│  │  Emulator    │  │   Hardware   │  │  Attestation │       │
│  │              │  │   Abstraction│  │   Layer      │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│         └─────────────────┼─────────────────┘                │
│                           │                                  │
│                  ┌────────▼────────┐                         │
│                  │  Miner Core     │                         │
│                  │  (Python)       │                         │
│                  └────────┬────────┘                         │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐                │
│         │                 │                 │                │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐       │
│  │  Network     │  │   Display    │  │   Input      │       │
│  │  Interface   │  │   Simulator  │  │   Handler    │       │
│  │  (HTTP/API)  │  │  (Vector)    │  │  (Rotary)    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 组件详解

### 1. M6502 CPU 模拟器 (`m6502_cpu.py`)

完整的 Motorola 6502 CPU 模拟器，支持：
- 所有 56 条官方指令
- 9 种寻址模式
- 完整的状态标志处理
- 内存映射 I/O 支持
- 可配置时钟速度 (默认 1.5 MHz)

**关键特性**:
```python
class M6502:
    - 寄存器：A, X, Y, SP, PC, P
    - 内存：64KB 可寻址空间
    - 回调：read_callback, write_callback
    - 周期计数：精确的时序模拟
```

### 2. Tempest 硬件抽象层 (`tempest_hardware.py`)

模拟 Tempest 街机的所有硬件组件：

#### 内存映射
```
地址范围      用途
─────────────────────────────────
$0000-$0FFF   4KB RAM
$4000-$FFFF   ROM (16KB 镜像)
$C000-$C00F   Pokey 声音芯片 1
$C010-$C01F   Pokey 声音芯片 2
$D000-$D00F   矢量显示控制器
$E000-$E00F   输入设备 (旋转编码器/按钮)
$F000-$F0FF   网络接口缓冲区
```

#### 硬件组件

**Pokey 声音芯片**:
- 2 个 Pokey ICs
- 总共 8 个音频通道
- 通过内存映射寄存器控制

**矢量显示**:
- X/Y 坐标寄存器 (12 位精度)
- 亮度控制
- 电子束开关

**输入设备**:
- 旋转编码器 (8 位，256 位置)
- Fire 按钮
- Superzap 按钮

### 3. RustChain 证明层

#### 硬件指纹 (6 层)

1. **时钟偏移与振荡器漂移**
   - 模拟 6502 晶体振荡器的老化特征
   - 测量指令执行时间的微小变化

2. **缓存时序指纹**
   - L1/L2 延迟特征
   - 6502 无缓存，但宿主机有

3. **SIMD 单元标识**
   - 6502: 无 SIMD (标记为 `6502_BASIC`)
   - 宿主机 SIMD 作为辅助指纹

4. **热漂移熵**
   - 温度变化引起的时序漂移
   - 随机但可重复的模式

5. **指令路径抖动**
   - 每条指令执行时间的微小变化
   - 基于物理硬件特性

6. **反模拟检查**
   - 检测是否在 VM 中运行
   - 置信度评分

#### Attestation 数据包

```json
{
  "hardware_id": "abc123...",
  "cpu_type": "Motorola 6502",
  "cpu_speed_mhz": 1.5,
  "architecture": "6502",
  "era": 1975,
  "platform": "Tempest Arcade",
  "manufacturer": "Atari Inc.",
  "year": 1981,
  "ram_kb": 4,
  "rom_kb": 20,
  "display": "Vector (Color QuadraScan)",
  "sound": "2x Pokey (8 voices)",
  "host_platform": "Windows-10-...",
  "host_machine": "AMD64",
  "timestamp": 1710432000,
  "wallet": "RTC4325af95d26d59c3ef025963656d22af638bb96b",
  "simulator_version": "1.0.0",
  "rustchain_protocol": "PoA-v2"
}
```

### 4. 网络接口

#### 模拟网络 (6502 侧)
```python
# 6502 通过内存映射 I/O 进行"网络"通信
NETWORK_BASE = 0xF000

# 写入网络缓冲区
cpu.write_byte(0xF000, ord('G'))
cpu.write_byte(0xF001, ord('E'))
# ...

# 触发网络操作
cpu.write_byte(0xF100, 0x01)  # SEND 命令
```

#### 实际网络 (宿主机侧)
```python
import requests

# 提交 attestation
response = requests.post(
    'https://rustchain.org/api/attestation',
    json=attestation_data,
    headers={'Content-Type': 'application/json'}
)

# 检查余额
response = requests.get(
    f'https://rustchain.org/wallet/balance?miner_id={wallet_id}'
)
```

## 挖矿流程

### Epoch 周期 (10 分钟)

```
1. 准备阶段 (0-30 秒)
   ├─ 收集硬件指纹
   ├─ 构建 attestation 数据包
   └─ 签名 (使用钱包密钥)

2. 提交阶段 (30-60 秒)
   ├─ 发送到 RustChain 节点
   ├─ 等待确认
   └─ 记录交易 ID

3. 等待阶段 (60-540 秒)
   ├─ 运行 6502 模拟器 (空闲循环)
   ├─ 更新矢量显示 (动画)
   └─ 监听网络事件

4. 奖励阶段 (540-600 秒)
   ├─ 接收 epoch 结果
   ├─ 计算奖励 (基于乘数)
   └─ 更新钱包余额
```

### 奖励计算

```python
# Tempest 6502 乘数
base_multiplier = 3.0      # 6502 (1975) 基础乘数
era_bonus = 1.5            # 50+ 年历史加成
rarity_bonus = 1.25        # 街机基板稀有度

total_multiplier = 3.0 * 1.5 * 1.25 = 5.625x

# Epoch 奖励
base_reward = 1.5 RTC  # 每 epoch 总奖励
active_miners = 10     # 假设活跃矿工数

share = base_reward / active_miners = 0.15 RTC
reward = share * total_multiplier = 0.15 * 5.625 = 0.84375 RTC
```

## 性能优化

### 6502 模拟器优化

1. **指令查找表**
   - 预编译指令解码表
   - O(1) 指令分发

2. **内存访问优化**
   - 直接数组访问 RAM
   - 回调仅用于硬件寄存器

3. **周期精确模拟**
   - 每条指令精确周期计数
   - 支持时序敏感代码

### 网络优化

1. **批量提交**
   - 多个 epoch 一起提交 (可选)
   - 减少网络往返

2. **连接复用**
   - HTTP keep-alive
   - 减少握手开销

3. **离线模式**
   - 本地缓存 attestation
   - 网络恢复后批量提交

## 安全考虑

### 防作弊机制

1. **硬件指纹绑定**
   - 每个硬件 ID 只能绑定一个钱包
   - 防止 Sybil 攻击

2. **时序验证**
   - 节点验证 attestation 时间戳
   - 防止重放攻击

3. **反模拟检查**
   - 检测 VM/模拟器特征
   - 但允许受信任的模拟器 (本项目)

### 钱包安全

1. **私钥管理**
   - 私钥永不离开宿主机
   - 6502 模拟器只处理公钥操作

2. **签名验证**
   - 所有 attestation 必须签名
   - 节点验证签名有效性

## 扩展性

### 未来改进

1. **完整矢量显示模拟**
   - 使用 pygame 或 WebGL
   - 实时显示 Tempest 游戏画面

2. **声音模拟**
   - Pokey 芯片精确模拟
   - 播放 Tempest 音效

3. **多人游戏支持**
   - 多个 Tempest 矿工联网
   - 协作挖矿

4. **实体硬件支持**
   - FPGA 实现 6502
   - 真实 Tempest PCB 运行矿工

## 参考资料

- [6502 指令集](https://www.masswerk.at/6502/)
- [Tempest Code Project](https://web.archive.org/web/20170704084629/http://ionpool.net/arcade/tempest_code_project/tempest_code_project.html)
- [RustChain Whitepaper](https://rustchain.org)
- [Pokey 芯片文档](https://www.atariarchive.org/)
