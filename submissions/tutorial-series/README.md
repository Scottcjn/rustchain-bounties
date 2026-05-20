# RustChain 教程系列 📚

> 从零到一的 RustChain 开发完整指南

![Difficulty](https://img.shields.io/badge/Difficulty-Beginner_to_Advanced-green)
![Tutorials](https://img.shields.io/badge/Tutorials-5-blue)
![Language](https://img.shields.io/badge/Language-中文-orange)

---

## 📖 教程列表

| # | 教程 | 难度 | 时间 | 内容 |
|---|------|------|------|------|
| 01 | [从零开始](./01-getting-started.md) | 🟢 入门 | 30 min | 环境搭建、节点编译、本地测试网启动 |
| 02 | [第一笔交易](./02-first-transaction.md) | 🟢 入门 | 20 min | 钱包创建、转账、交易查询 |
| 03 | [挖矿指南](./03-mining-guide.md) | 🟡 中等 | 45 min | NPoS 共识、验证者/提名者、质押挖矿 |
| 04 | [智能合约开发](./04-smart-contracts.md) | 🟡 中等 | 60 min | ERC-20 合约、编译部署、合约交互 |
| 05 | [高级主题](./05-advanced-topics.md) | 🔴 进阶 | 90 min | 跨合约调用、Runtime 模块、Gas 优化、安全 |

---

## 🗺️ 学习路径

```
01 从零开始 ──▶ 02 第一笔交易 ──▶ 03 挖矿指南
                                         │
                                         ▼
                                  04 智能合约开发 ──▶ 05 高级主题
```

**建议按顺序学习**，每个教程都以前一个为基础。

---

## ⚡ 快速开始

```bash
# 1. 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. 克隆 RustChain
git clone https://github.com/rustchain/rustchain.git
cd rustchain

# 3. 编译并启动
cargo build
./target/debug/rustchain-node --dev

# 4. 打开教程 01 开始学习！
```

---

## 📋 每个教程包含

- ✅ **前置条件** — 开始前需要准备什么
- 📝 **分步骤指引** — 详细的操作说明和完整代码
- 📸 **截图占位符** — 关键步骤的可视化指引
- ❓ **常见问题 FAQ** — 遇到问题？先看这里
- ➡️ **下一步** — 学完后的推荐路径

---

## 🛠️ 技术栈

- **语言：** Rust
- **合约编译目标：** WebAssembly (wasm32-unknown-unknown)
- **共识机制：** NPoS (Nominated Proof-of-Stake)
- **运行时：** Substrate-based

---

## 🤝 贡献

欢迎贡献！请遵循以下规范：

1. 每个教程一个 Markdown 文件
2. 包含前置条件、步骤、FAQ、下一步
3. 代码示例必须可运行
4. 使用截图占位符标注需要配图的位置

---

## 📄 许可

本教程系列采用 MIT 许可证开源。

---

*Contributed by [zp6](https://github.com/zp6)*
