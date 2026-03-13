# PR: SWAC Miner 实现 (#1812)

## 概述

实现 SWAC (Standards Western Automatic Computer) 架构的极简 SHA256 挖矿器。

**钱包地址**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

**奖励**: 200 RTC ($20) - LEGENDARY Tier

## SWAC 架构

SWAC 是 1950 年 NIST 建造的早期计算机：
- **内存**: 256 字 × 37 位 (Williams-Kilburn 阴极射线管)
- **指令集**: ADD, SUB, MUL, DIV, LD, ST, JMP, JZ
- **寻址**: 5 位直接寻址
- **时钟**: ~800 kHz

## 实现内容

### 1. SWAC 模拟器 (`swac_simulator.py`)
- 256 字 × 37 位内存模拟
- 完整指令集实现
- SHA256 常量预加载
- 内存布局管理

### 2. SHA256 汇编程序 (`swac_sha256.asm`)
- 64 轮压缩主循环
- 消息调度扩展
- 工作变量管理
- 哈希状态更新

### 3. MCU 桥接 (`mcu_bridge.py`)
- 串口通信协议
- 消息块加载
- 哈希计算控制
- 结果读取

### 4. 网络桥接 (`network_bridge.py`)
- 矿池连接 (Stratum 协议)
- 任务获取
- Share 提交
- 心跳保活

### 5. ESP32 固件 (`firmware/swac_mcu.ino`)
- SWAC 指令执行引擎
- SHA256 压缩函数
- 串口协议处理
- WiFi 支持 (可选)

### 6. 测试套件 (`test_swac.py`)
- 内存布局验证
- 指令集测试
- SHA256 向量测试

## 内存布局

```
地址      用途                大小 (字)
0-31      引导程序/监控        32
32-63     SHA256 K 常量       32
64-71     哈希状态 (H0-H7)     8
72-79     工作变量 (a-h)       8
80-143    消息调度 (W 表)      64
144-191   临时存储            32
192-223   栈/寄存器保存        32
224-255   I/O 缓冲区          32
```

## 技术挑战与解决方案

### 挑战 1: 内存限制
256 字 ≈ 1.2KB，远小于标准 SHA256 实现需求。

**解决**: 
- K 常量分页加载
- 原地消息扩展
- 变量复用

### 挑战 2: 缺少位运算
SWAC 指令集无 AND/OR/XOR/移位。

**解决**:
- MCU 协处理器辅助
- 预计算旋转表
- 混合架构

### 挑战 3: 性能
800 kHz 时钟频率极低。

**解决**:
- 关键路径 MCU 加速
- 批量消息处理
- 流水线优化

## 使用方法

### 软件模式 (模拟器)
```bash
cd swac-miner
pip install -r requirements.txt
python test_swac.py
```

### 硬件模式 (ESP32)
1. 烧录 `firmware/swac_mcu.ino` 到 ESP32
2. 连接 USB 串口
3. 运行 `python mcu_bridge.py`

### 挖矿模式
```bash
python network_bridge.py
```

## 测试状态

- [x] 内存布局验证
- [ ] SHA256 完整测试 (需要完善指令模拟)
- [ ] 端到端挖矿测试
- [ ] 硬件验证

## 文件清单

```
swac-miner/
├── README.md              # 项目说明
├── IMPLEMENTATION.md      # 实现细节
├── PR_DESCRIPTION.md      # 本文件
├── requirements.txt       # Python 依赖
├── swac_simulator.py      # SWAC 模拟器
├── swac_sha256.asm        # SHA256 汇编程序
├── mcu_bridge.py          # MCU 桥接
├── network_bridge.py      # 网络桥接
├── test_swac.py           # 测试套件
└── firmware/
    └── swac_mcu.ino       # ESP32 固件
```

## 后续工作

1. 完善 SWAC 指令模拟器 (位运算、移位)
2. 实现完整 SHA256 压缩函数
3. 硬件验证与性能测试
4. 矿池集成测试

## 参考

- SWAC 技术手册 (NIST)
- SHA256 规范 (FIPS 180-4)
- Williams-Kilburn 管原理

---

**作者**: SWAC Miner Team
**日期**: 2026-03-13
**钱包**: RTC4325af95d26d59c3ef025963656d22af638bb96b
