# RustChain 矿工设置指南

> **前提：** RustChain 使用 Proof-of-Antiquity 共识，需要**真实的老旧硬件**参与挖矿。虚拟机（VM、模拟器）不被支持。

---

## 目录

- [硬件要求](#硬件要求)
- [支持的硬件平台](#支持的硬件平台)
- [软件依赖](#软件依赖)
- [Linux 安装步骤](#linux-安装步骤)
- [Windows 安装步骤](#windows-安装步骤)
- [macOS 安装步骤](#macos-安装步骤)
- [配置矿工](#配置矿工)
- [启动挖矿](#启动挖矿)
- [验证挖矿状态](#验证挖矿状态)
- [常见问题](#常见问题)

---

## 硬件要求

| 组件 | 最低要求 | 推荐 |
|------|----------|------|
| CPU | PowerPC G4 / SPARC V9 / POWER8 | PowerPC G5 / SPARC T2 / POWER9 |
| 内存 | 512 MB | 2 GB+ |
| 存储 | 1 GB 可用空间 | 10 GB+ SSD |
| 网络 | 稳定的互联网连接 | 低延迟宽带 |

> ⚠️ **重要：** 虚拟机挖矿会被检测并拒绝。必须使用物理硬件。

## 支持的硬件平台

- **PowerPC** — PowerMac G4/G5, iBook G4, PowerBook G4
- **SPARC** — Sun Ultra 24/45, SPARC T2/T3 服务器
- **POWER** — IBM POWER8/POWER9 服务器
- **其他古董硬件** — 具体支持列表参见 GitHub 仓库

---

## 软件依赖

### 通用依赖

- **Rust** (1.70+) — [https://rustup.rs](https://rustup.rs)
- **OpenSSL** 开发库
- **Git**

### Linux 额外依赖

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install -y build-essential pkg-config libssl-dev git

# RHEL/CentOS
sudo yum groupinstall "Development Tools" && sudo yum install openssl-devel git
```

---

## Linux 安装步骤

### 1. 安装 Rust 工具链

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### 2. 克隆仓库

```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
```

### 3. 编译

```bash
cargo build --release
```

> 编译时间取决于硬件性能，老旧机器上可能需要 30-60 分钟。

### 4. 生成密钥对

```bash
./target/release/rustchain keygen --output miner.key
```

这会生成矿工公钥（miner_pk）和私钥，**务必安全保存私钥**。

### 5. 验证安装

```bash
./target/release/rustchain --version
```

---

## Windows 安装步骤

### 1. 安装前置软件

- 安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)（需要 C++ 工具链）
- 安装 [Rust](https://rustup.rs)（选择 x86_64-pc-windows-msvc 目标）
- 安装 [Git for Windows](https://git-scm.com)

### 2. 克隆并编译

```powershell
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
cargo build --release
```

### 3. 生成密钥对

```powershell
.\target\release\rustchain.exe keygen --output miner.key
```

### 4. 验证安装

```powershell
.\target\release\rustchain.exe --version
```

> **注意：** Windows 可用于管理节点，但实际挖矿需要将二进制部署到老旧硬件上运行。

---

## macOS 安装步骤

### 1. 安装 Xcode 命令行工具

```bash
xcode-select --install
```

### 2. 安装 Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### 3. 克隆并编译

```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
cargo build --release
```

### 4. 生成密钥对

```bash
./target/release/rustchain keygen --output miner.key
```

---

## 配置矿工

创建配置文件 `rustchain.toml`：

```toml
[network]
api_url = "https://50.28.86.131"
skip_tls_verify = true    # 自签名证书

[miner]
public_key = "RTCM1n3Y...YOUR_PUBLIC_KEY"
key_file = "miner.key"

[hardware]
type = "PowerPC"          # PowerPC / SPARC / POWER8
model = "PowerMac G5"

[mining]
auto_enroll = true        # 自动注册 Epoch
challenge_timeout = 280   # 挑战超时（秒）
max_retries = 3
```

---

## 启动挖矿

### 前台运行

```bash
./target/release/rustchain mine --config rustchain.toml
```

### 后台运行（Linux/macOS）

```bash
nohup ./target/release/rustchain mine --config rustchain.toml > miner.log 2>&1 &
```

### 使用 systemd（Linux 推荐生产方案）

创建 `/etc/systemd/system/rustchain-miner.service`：

```ini
[Unit]
Description=RustChain Miner
After=network.target

[Service]
Type=simple
User=miner
WorkingDirectory=/home/miner/Rustchain
ExecStart=/home/miner/Rustchain/target/release/rustchain mine --config rustchain.toml
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

启动并设置开机自启：

```bash
sudo systemctl enable rustchain-miner
sudo systemctl start rustchain-miner
sudo systemctl status rustchain-miner
```

---

## 验证挖矿状态

### 检查矿工是否在线

```bash
curl -k https://50.28.86.131/health
```

### 查询余额

```bash
curl -k https://50.28.86.131/balance/YOUR_PUBLIC_KEY
```

### 查看当前 Epoch

```bash
curl -k https://50.28.86.131/epoch
```

---

## 常见问题

### 编译太慢

老旧硬件上编译确实慢。可以尝试在交叉编译环境中构建二进制，然后传输到目标机器。

### TLS 连接失败

确保 `rustchain.toml` 中设置了 `skip_tls_verify = true`，因为节点使用自签名证书。

### 挖矿被拒绝

确认使用的是**物理硬件**，不是虚拟机。RustChain 会检测硬件特征，虚拟机提交的证明会被拒绝。

---

## 支持

- GitHub Issues: [https://github.com/Scottcjn/Rustchain/issues](https://github.com/Scottcjn/Rustchain/issues)
- 共识协议: RIP-200 (Proof of Antiquity)
