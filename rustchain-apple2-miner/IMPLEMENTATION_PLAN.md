# RustChain Apple II Miner - 移植计划

## 任务概述

**Issue**: [#436](https://github.com/Scottcjn/rustchain-bounties/issues/436)  
**奖励**: 150 RTC (4.0x 乘数 - 最高等级)  
**钱包**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## 硬件规格

| 组件 | 规格 |
|------|------|
| CPU | MOS 6502 @ 1.023 MHz (NTSC) |
| RAM | 48-128 KB (IIe 标准 64KB, IIgs 可达 1MB+) |
| 地址空间 | 64 KB |
| 数据宽度 | 8-bit |
| FPU | 无 |
| MMU | 无 (基础 6502) |

## 技术挑战

1. **极端资源限制**: 64KB 地址空间必须容纳 OS + 网络栈 + 矿工
2. **无硬件乘法**: 6502 只有加法/减法，乘除需要软件实现
3. **无 FPU**: 所有运算必须是整数
4. **网络**: 需要 Uthernet II (W5100 芯片) 或 Contiki OS
5. **SHA256**: 在 1MHz 6502 上极慢 (~30 秒/次)

## 推荐方案

### 方案 A: Contiki OS + CC65 (推荐入门)

**优点**:
- Contiki 已有 Apple II 支持
- 内置 uIP TCP/IP 栈
- 可使用 C 语言开发 (CC65 编译器)
- 社区资源丰富

**缺点**:
- Contiki 占用较大 (~30KB)
- 剩余空间紧张

**硬件需求**:
- Apple IIe (64KB RAM 最小)
- Uthernet II 以太网卡
- 存储：ProDOS 分区或 CF 卡

### 方案 B: ProDOS + IP65 + 汇编 (最轻量)

**优点**:
- 最小占用 (~10KB)
- 完全控制硬件
- 最快执行速度

**缺点**:
- 6502 汇编开发难度大
- 需要手动实现所有功能

### 方案 C: Apple IIgs + Marinetti (最强性能)

**优点**:
- 65816 CPU (16-bit, 2.8 MHz)
- 1MB+ RAM
- Marinetti TCP/IP 栈成熟
- 可用 ORCA/C 开发

**缺点**:
- IIgs 硬件较贵
- 部分"纯粹主义者"可能认为这是作弊 (但官方允许)

## 实现步骤

### 阶段 1: 网络环境搭建 (50 RTC)

#### 1.1 硬件准备
- [ ] 获取 Apple IIe 或 IIgs (eBay ~$200)
- [ ] 获取 Uthernet II 网卡 (~$80 from a2retrosystems.com)
- [ ] 准备存储介质 (CF 卡或 3.5" 软盘)
- [ ] 准备开发环境 (现代 PC + cc65 工具链)

#### 1.2 软件开发环境
```bash
# 安装 cc65 编译器
git clone https://github.com/cc65/cc65
cd cc65
make
sudo make install

# 安装 Apple II 模拟器 (开发测试用)
# Windows: AppleWin
# macOS: KeG IIgs
# Linux: MAME
```

#### 1.3 网络栈选择

**选项 1: Contiki OS**
```c
// Contiki 已有 Apple II 端口
// https://github.com/contiki-os/contiki
// 支持 Uthernet II
```

**选项 2: IP65 库**
```c
// https://github.com/cc65/ip65
// 轻量级 TCP/IP 栈
// 支持 W5100 芯片直接编程
```

**选项 3: 直接 W5100 编程**
```
Uthernet II 使用 W5100 芯片，内置 TCP/IP 栈
只需通过 6502 I/O 操作 W5100 寄存器
最简单但最底层的方法
```

#### 1.4 网络测试程序
```c
// 测试 HTTP GET 请求
#include <stdio.h>
#include <tcp.h>

void test_network(void) {
    // 连接到测试服务器
    // 发送 HTTP GET
    // 验证响应
}
```

### 阶段 2: 矿工客户端实现 (50 RTC)

#### 2.1 核心结构

参考 DOS 矿工结构，适配 6502:

```c
// 熵结构 (简化版以适应 6502)
typedef struct {
    unsigned char bios_date[8];    // Apple II ROM 日期
    unsigned char cpu_speed;       // 6502 速度标志
    unsigned int timer_samples[16]; // 定时器采样 (减少数量)
    unsigned char ram_size;        // RAM 大小
    unsigned char hash[32];        // 熵哈希
} Apple2Entropy;

// 钱包配置
typedef struct {
    char wallet_id[48];    // RTC + 40 hex
    char miner_id[16];     // APPLE2-XXXX
    unsigned long created;
} WalletConfig;
```

#### 2.2 硬件熵收集

```assembly
; 6502 汇编 - 收集定时器熵
CollectTimerEntropy:
    LDA #$00
    STA $C070    ; 清除键盘 strobe
    LDY #0
Loop:
    LDA $C060    ; 读取定时器 (伪代码)
    STA timer_samples,Y
    INY
    CPY #32
    BNE Loop
    RTS
```

**Apple II 独特熵源**:
- ROM 版本/日期 (0xD000-0xFFFF)
- 键盘读取时序 ($C000-$C0FF)
- 软盘驱动器步进时序
- 视频生成时序 (与 DRAM 刷新耦合)
- "Floating bus" 行为

#### 2.3 钱包生成

```c
// 简化版哈希 (6502 无法承受完整 SHA256)
void generate_wallet_hash(Apple2Entropy *e, char *wallet) {
    // 使用简单但有效的混合函数
    // 输出格式：RTC + 40 hex 字符
}
```

#### 2.4 HTTP 客户端

```c
// 构建 HTTP POST 请求
void build_attestation_request(char *buffer, WalletConfig *wallet) {
    sprintf(buffer,
        "POST /attest/submit HTTP/1.0\r\n"
        "Host: rustchain.org\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: 256\r\n"
        "\r\n"
        "{\"miner\":\"%s\",\"miner_id\":\"%s\",...}",
        wallet->wallet_id,
        wallet->miner_id
    );
}
```

#### 2.5 JSON 构建

6502 没有 JSON 库，手动构建:

```c
// 手动构建 JSON (避免解析库开销)
void build_json_attestation(char *buf, size_t len) {
    char *p = buf;
    p += sprintf(p, "{");
    p += sprintf(p, "\"miner\":\"%s\",", g_wallet.wallet_id);
    p += sprintf(p, "\"device\":{");
    p += sprintf(p, "\"arch\":\"6502\",");
    p += sprintf(p, "\"family\":\"apple2\"");
    p += sprintf(p, "}");
    p += sprintf(p, "}");
}
```

### 阶段 3: 硬件指纹 (25 RTC)

#### 3.1 Apple II 独特特征

```c
// 检测真实硬件 vs 模拟器
int detect_emulation(void) {
    // 1. 测试 floating bus 行为
    // 2. 测量视频时序
    // 3. 测试 DRAM 刷新模式
    // 4. 软盘驱动器步进时序
    // 返回：0=模拟器，1=真实硬件
}
```

**关键检测点**:

1. **Floating Bus**: Apple II 的未驱动总线会"浮动"到特定值，每块主板不同
2. **视频时序**: 6502 的视频生成与 DRAM 刷新耦合，产生独特时序
3. **键盘时序**: $C000 区域的键盘读取有模拟特性
4. **软盘步进**: 机械步进电机 timing 每驱动器不同

#### 3.2 反模拟器检测

```assembly
; 检测 AppleWin/MAME 的 timing 差异
DetectRealHardware:
    ; 读取视频计数器
    ; 测量精确 cycles
    ; 比较预期值 (真实硬件有微小偏差)
    ; 模拟器通常太"完美"
```

### 阶段 4: 测试与证明 (25 RTC)

#### 4.1 测试清单

- [ ] 在模拟器上开发测试
- [ ] 在真实 Apple II 硬件上验证
- [ ] 网络连通性测试
- [ ] 钱包生成测试
- [ ] 证明真实硬件 (照片/视频)

#### 4.2 交付物

1. **源代码**: GitHub 仓库
2. **磁盘镜像**: .dsk 或 .po 格式
3. **构建脚本**: Makefile + cc65 配置
4. **文档**: README + 使用说明
5. **证明**: 
   - Apple II 运行照片
   - 网络卡连接照片
   - 矿工在 rustchain.org/api/miners 中的截图

## 文件结构

```
rustchain-apple2-miner/
├── README.md              # 项目说明
├── LICENSE                # Apache 2.0
├── Makefile               # 构建脚本
├── src/
│   ├── main.c             # 主程序入口
│   ├── entropy.c          # 熵收集
│   ├── entropy.s          # 关键汇编优化
│   ├── wallet.c           # 钱包生成
│   ├── network.c          # 网络通信
│   ├── http.c             # HTTP 客户端
│   ├── json.c             # JSON 构建
│   └── fingerprint.c      # 硬件指纹
├── include/
│   └── rustchain.h        # 头文件
├── config/
│   └── cc65.cfg           # cc65 链接器配置
├── disk/
│   └── miner.dsk          # 磁盘镜像
└── docs/
    ├── hardware.md        # 硬件指南
    ├── build.md           # 构建说明
    └── proof/             # 证明材料
```

## 开发时间表

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| 环境搭建 | 1-2 天 | 开发环境 + 网络测试 |
| 网络栈集成 | 2-3 天 | HTTP 客户端工作 |
| 矿工核心 | 3-5 天 | 熵收集 + 钱包生成 |
| 硬件指纹 | 2-3 天 | 反模拟器检测 |
| 真实硬件测试 | 3-5 天 | 照片/视频证明 |
| 文档 + PR | 1-2 天 | 完整提交 |

**总计**: 12-20 天 (取决于硬件获取速度)

## 预算估算

| 项目 | 成本 |
|------|------|
| Apple IIe | $150-250 (eBay) |
| Uthernet II | $80 (a2retrosystems) |
| CF 卡/存储 | $20 |
| 线缆/适配器 | $30 |
| **总计** | **~$300** |

**ROI**: 150 RTC ≈ $15 (当前) + 4.0x 持续挖矿奖励

## 风险与缓解

| 风险 | 概率 | 缓解措施 |
|------|------|----------|
| 硬件获取困难 | 中 | 使用 IIgs 模拟器先开发，硬件后补 |
| 网络栈太重 | 中 | 使用直接 W5100 编程，最小化占用 |
| SHA256 太慢 | 高 | 使用简化哈希，服务器端验证 |
| 内存不足 | 中 | 使用 IIgs (1MB RAM) 或 bank switching |

## 下一步行动

1. ✅ 阅读 issue #436 详情
2. ✅ 研究 DOS 矿工源码
3. ⏳ 创建详细技术设计文档
4. ⏳ 设置 cc65 开发环境
5. ⏳ 编写网络测试程序
6. ⏳ 采购硬件 (Apple II + Uthernet II)
7. ⏳ 实现矿工核心功能
8. ⏳ 测试并提交 PR

## 参考资源

- [Uthernet II](https://a2retrosystems.com/products.htm)
- [CC65 编译器](https://cc65.github.io/)
- [Contiki OS](https://github.com/contiki-os/contiki)
- [IP65 库](https://github.com/cc65/ip65)
- [Apple II 技术手册](https://archive.org/details/Apple_IIe_Technical_Reference_Manual)
- [6502.org 社区](http://www.6502.org/)
- [SHA256 for 6502](https://github.com/omarandlorraine/sha256-6502)
- [Marinetti (IIgs TCP/IP)](http://www.interlacedsciences.com/products.html)

---

**创建时间**: 2026-03-13  
**钱包**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
