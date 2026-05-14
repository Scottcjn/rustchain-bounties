# 教程 01：从零开始 — RustChain 环境搭建

> **难度：** 🟢 入门 | **预计时间：** 30 分钟 | **作者钱包：** zp6

---

## 概述

本教程将带你从零搭建 RustChain 开发环境，包括 Rust 工具链安装、RustChain 节点编译和本地测试网络启动。

---

## 前置条件

| 要求 | 说明 |
|------|------|
| 操作系统 | Windows 10/11、macOS 12+、Ubuntu 22.04+ |
| 内存 | ≥ 8 GB RAM |
| 磁盘 | ≥ 20 GB 可用空间 |
| 网络 | 稳定的互联网连接 |

---

## 步骤 1：安装 Rust 工具链

```bash
# 安装 rustup（Rust 版本管理器）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 选择默认安装（选项 1）
# 安装完成后加载环境
source $HOME/.cargo/env

# 验证安装
rustc --version    # 需要 ≥ 1.75.0
cargo --version
```

> **Windows 用户：** 下载 [rustup-init.exe](https://rustup.rs/) 并运行，选择默认安装即可。

---

## 步骤 2：安装系统依赖

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y git build-essential pkg-config libssl-dev clang cmake
```

### macOS

```bash
xcode-select --install
brew install openssl cmake
```

### Windows

```powershell
# 安装 Visual Studio Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# 或通过 chocolatey
choco install visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools"
```

---

## 步骤 3：克隆并编译 RustChain

```bash
# 克隆仓库
git clone https://github.com/rustchain/rustchain.git
cd rustchain

# 编译节点（debug 模式，首次编译约 10-15 分钟）
cargo build

# 编译 release 版本（用于性能测试）
cargo build --release
```

<!-- 📸 截图占位符：cargo build 成功输出，显示 "Finished dev [unoptimized + debuginfo]" -->
> 📸 **截图：** 编译成功后的终端输出

---

## 步骤 4：配置节点

```bash
# 生成默认配置文件
./target/debug/rustchain-node init --chain local

# 查看生成的配置
ls -la ~/.rustchain/
# config.toml
# genesis.json
# keystore/
```

编辑 `~/.rustchain/config.toml` 根据需要调整参数：

```toml
[network]
port = 30333
bootnodes = []

[rpc]
enabled = true
port = 9933
cors = ["*"]

[authoring]
mining_enabled = true
```

<!-- 📸 截图占位符：配置文件内容 -->
> 📸 **截图：** config.toml 配置示例

---

## 步骤 5：启动本地测试网

```bash
# 启动单节点开发网络
./target/debug/rustchain-node \
  --dev \
  --rpc-cors all \
  --base-path /tmp/rustchain-dev

# 你应该看到类似输出：
# 🎉 RustChain node started
# 📦 Chain specification: Development
# 👤 Role: AUTHORITY
# 💻 Operating as validator...
```

<!-- 📸 截图占位符：节点启动成功，显示区块开始生产 -->
> 📸 **截图：** 节点启动并开始出块

---

## 步骤 6：验证节点运行

```bash
# 查询节点健康状态
curl -s -H "Content-Type: application/json" \
  -d '{"id":1,"jsonrpc":"2.0","method":"system_health","params":[]}' \
  http://localhost:9933 | jq

# 预期输出：
# {
#   "jsonrpc": "2.0",
#   "result": {
#     "health": "ok",
#     "peers": 0,
#     "isSyncing": false
#   }
# }
```

---

## 常见问题 (FAQ)

### Q: 编译时报 `linker 'cc' not found`
**A:** 需要安装 C 编译器。Ubuntu 运行 `sudo apt install build-essential`，macOS 运行 `xcode-select --install`。

### Q: 编译时间太长怎么办？
**A:** 可以使用 `cargo build` 的增量编译特性。首次编译后，后续修改只会重新编译变更部分。也可以考虑开启 sccache：

```bash
cargo install sccache
export RUSTC_WRAPPER=sccache
```

### Q: Windows 上编译报 OpenSSL 错误
**A:** 设置环境变量指向 OpenSSL 安装路径：

```powershell
$env:OPENSSL_DIR = "C:\Program Files\OpenSSL-Win64"
```

### Q: 端口 9933 被占用
**A:** 修改 `config.toml` 中的 RPC 端口，或启动时使用 `--rpc-port 9944`。

### Q: 如何重置链数据？
**A:** 删除数据目录后重新初始化：

```bash
rm -rf /tmp/rustchain-dev
./target/debug/rustchain-node init --chain local
```

---

## 下一步

🎉 恭喜！你已经成功搭建了 RustChain 开发环境。

接下来，请继续学习：
- **[教程 02：第一笔交易](./02-first-transaction.md)** — 学习如何发送和接收 RustChain 交易

---

*本教程由 [zp6](https://github.com/zp6) 贡献至 RustChain 社区。*
