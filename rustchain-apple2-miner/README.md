# RustChain Apple II Miner 🍎⛏️

> **将 RustChain 矿工移植到 1977 年的 Apple II 电脑**  
> 4.0x 最高乘数 · 150 RTC Bounty · 6502 汇编挑战

[![Bounty: 150 RTC](https://img.shields.io/badge/bounty-150_RTC-orange)](https://github.com/Scottcjn/rustchain-bounties/issues/436)
[![Platform: Apple II](https://img.shields.io/badge/platform-Apple%20II-red)](https://en.wikipedia.org/wiki/Apple_II)
[![CPU: MOS 6502](https://img.shields.io/badge/cpu-MOS%206502%20@1MHz-blue)](http://www.6502.org/)

## 📖 项目概述

这是 RustChain Proof-of-Antiquity 区块链的最极端移植挑战：在 1977 年发布的 Apple II 电脑上运行加密货币矿工。

**为什么？**
- Apple II 是个人电脑革命的开端
- MOS 6502 CPU @ 1MHz 是 8-bit 时代的标志
- 4.0x 乘数是 RustChain 的最高奖励等级
- 这是对复古计算和加密货币的诗意结合

## 🎯 Bounty 详情

**Issue**: [#436](https://github.com/Scottcjn/rustchain-bounties/issues/436)  
**奖励**: 150 RTC (约 $15) + 4.0x 持续挖矿乘数  
**钱包**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

### 奖励分解

| 阶段 | 任务 | RTC |
|------|------|-----|
| 1 | 网络环境搭建 | 50 |
| 2 | 矿工客户端实现 | 50 |
| 3 | 硬件指纹 (反模拟器) | 25 |
| 4 | 真实硬件证明 | 25 |
| **总计** | | **150** |

## 🖥️ 硬件需求

### 最小配置
- Apple II/II+/IIe (任何型号)
- 64KB RAM (48KB 理论可行但极困难)
- Uthernet II 以太网卡 (W5100 芯片)
- 存储：软盘 / CFFA3000 / MicroDrive Turbo

### 推荐配置
- Apple IIe Enhanced (128KB RAM)
- 或 Apple IIgs (65816 CPU, 1MB+ RAM)
- Uthernet II + 网络线缆
- CF 卡存储 (通过 CFFA3000)

### 开发环境 (现代 PC)
- cc65 编译器 (C → 6502)
- Apple II 模拟器 (AppleWin/KeG II/MAME)
- 文本编辑器 + Make

## 🛠️ 技术栈

| 组件 | 选择 |
|------|------|
| 语言 | 6502 汇编 + CC65 C |
| OS | ProDOS / Contiki / 裸机 |
| 网络 | Uthernet II (W5100) + IP65 |
| 协议 | HTTP/1.0 (无 TLS) |
| 哈希 | 简化 SHA256 / 自定义 |

## 📁 项目结构

```
rustchain-apple2-miner/
├── README.md              # 本文件
├── IMPLEMENTATION_PLAN.md # 详细实现计划
├── Makefile               # 构建脚本
├── src/
│   ├── main.c             # 主程序
│   ├── entropy.c          # 熵收集
│   ├── wallet.c           # 钱包生成
│   ├── network.c          # 网络通信
│   └── fingerprint.c      # 硬件指纹
├── asm/
│   └── entropy.s          # 性能关键代码 (汇编)
├── include/
│   └── rustchain.h        # 头文件
├── config/
│   └── cc65.cfg           # 链接器配置
└── disk/
    └── miner.dsk          # 可启动磁盘镜像
```

## 🚀 快速开始

### 1. 安装开发工具

```bash
# 克隆 cc65 编译器
git clone https://github.com/cc65/cc65
cd cc65
make
sudo make install

# 验证安装
cc65 --version
```

### 2. 构建项目

```bash
cd rustchain-apple2-miner
make clean
make
```

### 3. 在模拟器中测试

```bash
# Windows: 使用 AppleWin
AppleWin.exe disk/miner.dsk

# macOS: 使用 KeG II
open -a "KeG II" disk/miner.dsk

# Linux: 使用 MAME
mame apple2e -f disk/miner.dsk
```

### 4. 在真实硬件上运行

```bash
# 将 .dsk 镜像写入软盘或 CF 卡
dd if=disk/miner.dsk of=/dev/sdX bs=512

# 插入 Apple II，启动，运行 MINER
```

## 📋 功能清单

- [ ] **网络栈集成**
  - [ ] Uthernet II 驱动
  - [ ] TCP/IP (IP65 或 Contiki uIP)
  - [ ] HTTP 客户端
  - [ ] DNS 解析 (可选，可用 IP 直连)

- [ ] **矿工核心**
  - [ ] 硬件熵收集
  - [ ] 钱包生成
  - [ ] 钱包保存/加载
  - [ ] JSON 构建 (手动，无库)
  - [ ] HTTP POST 证明提交

- [ ] **硬件指纹**
  - [ ] Floating bus 检测
  - [ ] 视频时序分析
  - [ ] DRAM 刷新模式
  - [ ] 反模拟器检测

- [ ] **用户界面**
  - [ ] 文本模式显示 (40 列)
  - [ ] 状态显示
  - [ ] 键盘控制 (Q 退出，S 状态)

- [ ] **文档与证明**
  - [ ] README 文档
  - [ ] 构建说明
  - [ ] 真实硬件照片
  - [ ] 运行视频

## 🔬 技术挑战

### 1. 内存限制 (64KB)

整个系统必须适应 64KB 地址空间:
- 6502 只能寻址 64KB
- ProDOS 占用 ~10KB
- 剩余 ~50KB 给矿工 + 网络栈

**解决方案**:
- 使用 bank switching (128KB IIe)
- 或精简网络栈 (直接 W5100 编程)
- 或升级到 IIgs (1MB+ RAM)

### 2. 速度限制 (1MHz)

SHA256 在 6502 上极慢:
- 完整 SHA256: ~30 秒/次
- 1000 次哈希: ~8 小时

**解决方案**:
- 使用简化哈希函数
- 服务器端宽松验证 (针对复古硬件)
- 降低证明频率 (每 10 分钟 → 每 60 分钟)

### 3. 无 TLS

6502 无法进行 TLS 握手:
- RSA/ECC 计算量太大
- 证书验证需要更多内存

**解决方案**:
- 使用 HTTP (非 HTTPS)
- RustChain 为复古硬件提供专用 endpoint
- 通过硬件指纹保证安全性

### 4. JSON 处理

6502 没有 JSON 库:
- 手动构建字符串
- 硬编码格式
- 避免动态解析

## 📊 性能预期

| 指标 | 预期值 |
|------|--------|
| 内存占用 | 30-40 KB |
| 启动时间 | 5-10 秒 |
| 证明周期 | 10-60 分钟 |
| 网络延迟 | 1-5 秒/请求 |
| 哈希速度 | ~30 秒/SHA256 |

## 🎓 学习资源

### 6502 汇编
- [6502.org](http://www.6502.org/) - 综合资源
- [Easy 6502](https://skilldrick.github.io/easy6502/) - 在线教程
- [6502 Assembly Guide](https://www.nesdev.org/6502%20assembly%20language%20tutorial.pdf)

### Apple II 编程
- [Apple II Reference Manual](https://archive.org/details/Apple_IIe_Technical_Reference_Manual)
- [Understanding the Apple II](https://archive.org/details/understanding-the-apple-ii)
- [Call-A.P.P.L.E.](https://archive.org/details/callapple) 杂志

### CC65 编译器
- [CC65 文档](https://cc65.github.io/doc/)
- [Apple II 示例](https://github.com/cc65/cc65/tree/master/samples/apple2)

### 网络编程
- [Uthernet II 文档](https://a2retrosystems.com/products.htm)
- [IP65 库](https://github.com/cc65/ip65)
- [Contiki uIP](https://github.com/contiki-os/contiki)

## 🤝 贡献

欢迎贡献！特别是:
- 6502 汇编优化
- Apple II 硬件测试
- 文档改进
- 模拟器配置

## 📄 许可证

Apache 2.0 - 与 RustChain 其他矿工一致

## 💰 Bounty 申领

完成所有阶段后，在 issue #436 评论:

```
✅ 完成所有 4 个阶段

📸 证明:
- [照片链接]
- [视频链接]
- [GitHub 仓库链接]

💰 钱包：RTC4325af95d26d59c3ef025963656d22af638bb96b
```

## 🙏 致谢

- RustChain 团队创建了这个疯狂的 bounty
- Steve Wozniak 设计了 Apple II
- 6502 社区保持复古计算活力
- CC65 团队维护优秀的编译器

---

**1977 meets 2026. Wozniak's masterpiece, mining cryptocurrency at 1MHz.** 🍎⛏️

*最后更新*: 2026-03-13
