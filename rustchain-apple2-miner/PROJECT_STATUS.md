# RustChain Apple II Miner - 项目状态

**最后更新**: 2026-03-13  
**Issue**: [#436](https://github.com/Scottcjn/rustchain-bounties/issues/436)  
**钱包**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## 项目概述

将 RustChain 矿工移植到 Apple II (MOS 6502 @ 1MHz)，争取 150 RTC bounty 和 4.0x 最高挖矿乘数。

## 当前状态

### ✅ 已完成

1. **项目调研**
   - ✅ 阅读 issue #436 详情
   - ✅ 研究 DOS 矿工源码 (rustchain-dos-miner)
   - ✅ 分析技术挑战和可行性

2. **项目结构创建**
   - ✅ 创建仓库目录结构
   - ✅ 创建 README.md
   - ✅ 创建 IMPLEMENTATION_PLAN.md
   - ✅ 创建 HARDWARE_GUIDE.md

3. **代码框架**
   - ✅ 创建头文件 (include/rustchain.h)
   - ✅ 创建主程序 (src/main.c)
   - ✅ 创建熵收集模块 (src/entropy.c)
   - ✅ 创建钱包模块 (src/wallet.c)
   - ✅ 创建网络模块占位符 (src/network.c)
   - ✅ 创建汇编例程 (asm/hardware.s)
   - ✅ 创建 Makefile
   - ✅ 创建 cc65 配置文件

### ⏳ 进行中

- 等待硬件采购 (Apple IIe + Uthernet II)
- 软件开发 (模拟器环境)

### ⏸️ 待开始

1. **网络栈实现** (50 RTC)
   - Uthernet II 驱动
   - TCP/IP 栈集成 (IP65 或 Contiki)
   - HTTP 客户端实现
   - DNS 解析

2. **矿工核心完善** (50 RTC)
   - 完整熵收集
   - 钱包持久化
   - JSON 构建
   - HTTP POST 实现

3. **硬件指纹** (25 RTC)
   - Floating bus 检测
   - 视频时序分析
   - 反模拟器检测
   - 真实硬件验证

4. **测试与证明** (25 RTC)
   - 模拟器测试
   - 真实硬件部署
   - 照片/视频拍摄
   - PR 提交

## 技术设计

### 架构选择

**方案**: Contiki OS + CC65 + IP65

理由:
- Contiki 已有 Apple II 支持
- IP65 轻量级 TCP/IP 栈
- CC65 成熟的 C 编译器
- 平衡开发难度和性能

### 内存布局

```
$0000-$00FF   Zero Page (256 bytes)
$0100-$01FF   Stack (256 bytes)
$0200-$07FF   Free RAM
$0800-$9FFF   Program + Data (~38KB available)
$A000-$BFFF   DOS/ProDOS
$C000-$CFFF   I/O Space
$D000-$FFFF   ROM
```

### 关键组件

| 组件 | 状态 | 备注 |
|------|------|------|
| 熵收集 | 🟡 框架完成 | 需真实硬件测试 |
| 钱包生成 | 🟡 框架完成 | 需测试 |
| 网络驱动 | 🔴 未实现 | 等待 Uthernet II |
| HTTP 客户端 | 🔴 未实现 | 依赖网络驱动 |
| JSON 构建 | 🟡 设计完成 | 手动构建 |
| 硬件指纹 | 🟡 部分实现 | 需真实硬件测试 |

## 时间线

### 阶段 1: 环境搭建 (Week 1-2)

- [x] 项目规划
- [x] 代码框架
- [ ] 安装 cc65 工具链
- [ ] 设置模拟器
- [ ] 编译测试程序
- [ ] 采购硬件 (并行)

### 阶段 2: 网络栈 (Week 3-4)

- [ ] Uthernet II 驱动
- [ ] IP65 集成
- [ ] HTTP GET 测试
- [ ] HTTP POST 实现
- [ ] DNS 解析 (可选)

### 阶段 3: 矿工核心 (Week 5-6)

- [ ] 完整熵收集循环
- [ ] 钱包保存/加载
- [ ] JSON 构建优化
- [ ] 证明提交循环
- [ ] 错误处理

### 阶段 4: 硬件指纹 (Week 7)

- [ ] Floating bus 检测
- [ ] 视频时序分析
- [ ] 键盘 timing 分析
- [ ] 反模拟器逻辑
- [ ] 真实硬件验证

### 阶段 5: 测试与提交 (Week 8)

- [ ] 模拟器完整测试
- [ ] 真实硬件部署
- [ ] 照片/视频拍摄
- [ ] 文档完善
- [ ] GitHub PR 提交
- [ ] Bounty 申领

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 硬件采购延迟 | 中 | 高 | 先用模拟器开发 |
| 内存不足 | 中 | 中 | 使用 bank switching 或 IIgs |
| 网络栈太重 | 中 | 高 | 直接 W5100 编程 |
| SHA256 太慢 | 高 | 中 | 简化哈希，服务器宽松验证 |
| Uthernet II 缺货 | 低 | 高 | 考虑二手或替代方案 |

## 预算

| 项目 | 估算 | 状态 |
|------|------|------|
| Apple IIe Enhanced | $200 | ⏳ 待采购 |
| Uthernet II | $80 | ⏳ 待采购 |
| CFFA3000 + CF 卡 | $130 | ⏳ 待采购 |
| 线缆/配件 | $40 | ⏳ 待采购 |
| **总计** | **$450** | |

## 文件清单

```
rustchain-apple2-miner/
├── README.md                    ✅ 完成
├── IMPLEMENTATION_PLAN.md       ✅ 完成
├── PROJECT_STATUS.md            ✅ 本文件
├── Makefile                     ✅ 完成
├── include/
│   └── rustchain.h              ✅ 完成
├── src/
│   ├── main.c                   ✅ 完成
│   ├── entropy.c                ✅ 完成
│   ├── wallet.c                 ✅ 完成
│   └── network.c                ✅ 占位符
├── asm/
│   └── hardware.s               ✅ 完成
├── config/
│   └── cc65.cfg                 ✅ 完成
├── disk/                        📁 空 (待构建)
└── docs/
    └── HARDWARE_GUIDE.md        ✅ 完成
```

## 下一步行动

### 立即 (今天)

1. ✅ 完成项目框架
2. ✅ 创建详细文档
3. ⏳ 提交到 GitHub (创建仓库)
4. ⏳ 在 issue #436 评论认领任务

### 本周

1. ⏳ 安装 cc65 工具链
2. ⏳ 设置 Apple II 模拟器
3. ⏳ 编译并测试基础程序
4. ⏳ 开始 eBay 寻找 Apple IIe

### 下周

1. ⏳ 订购 Uthernet II
2. ⏳ 实现网络栈框架
3. ⏳ 实现 HTTP 客户端
4. ⏳ 等待硬件到达

## 参考资源

### 文档
- [Issue #436](https://github.com/Scottcjn/rustchain-bounties/issues/436)
- [DOS 矿工源码](https://github.com/Scottcjn/rustchain-dos-miner)
- [CC65 文档](https://cc65.github.io/doc/)
- [Apple II 技术手册](https://archive.org/details/Apple_IIe_Technical_Reference_Manual)

### 社区
- [6502.org](http://www.6502.org/)
- [Apple II 论坛](https://apple2.org.za/)
- [Reddit r/apple2](https://reddit.com/r/apple2)

### 供应商
- [Uthernet II](https://a2retrosystems.com/products.htm)
- [CFFA3000](https://www.reactivemicro.com/)

## 联系与协作

欢迎贡献！特别是:
- 6502 汇编优化
- Apple II 硬件测试
- 网络栈实现
- 文档改进

GitHub: (待创建仓库)  
Discord: (待添加)

---

**1977 meets 2026. Let's make history!** 🍎⛏️
