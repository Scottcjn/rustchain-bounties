# RustChain FAQ & 故障排除

> 使用 RustChain 过程中遇到问题？这里有你需要的答案。

---

## 目录

- [常见问题 (FAQ)](#常见问题-faq)
  - [基础概念](#基础概念)
  - [挖矿相关](#挖矿相关)
  - [代币与奖励](#代币与奖励)
- [故障排除](#故障排除)
  - [连接问题](#连接问题)
  - [编译问题](#编译问题)
  - [挖矿问题](#挖矿问题)
  - [API 错误](#api-错误)
- [获取帮助](#获取帮助)

---

## 常见问题 (FAQ)

### 基础概念

**Q: 什么是 RustChain？**

RustChain 是一条区块链网络，使用 Proof-of-Antiquity (PoA) 共识机制，让老旧硬件（如 PowerPC、SPARC、POWER8）参与挖矿并获得 RTC 代币奖励。

**Q: 什么是 Proof-of-Antiquity？**

PoA (RIP-200) 是 RustChain 独创的共识算法。与传统 PoW 追求算力不同，PoA 要求矿工证明自己拥有并在使用**真实的老旧物理硬件**。网络通过硬件指纹、挑战-响应和反虚拟化检测来验证。

**Q: 支持哪些硬件？**

| 架构 | 示例设备 | 支持状态 |
|------|----------|----------|
| PowerPC | PowerMac G4/G5, iBook G4 | ✅ 完全支持 |
| SPARC | Sun Ultra 24/45, SPARC T2 | ✅ 完全支持 |
| POWER | IBM POWER8/POWER9 | ✅ 完全支持 |
| x86 老旧硬件 | Pentium III/4 等 | 🔄 实验性支持 |
| ARM | 旧版 ARM 开发板 | 📋 计划中 |

**Q: 代币总量多少？**

RTC 总量 21,000,000 枚，与比特币类似有减半机制。

---

### 挖矿相关

**Q: 可以用虚拟机挖矿吗？**

**不可以。** RustChain 有多层反虚拟化检测：
- CPU 特征检测（CPUID、指令集差异）
- 时序侧信道分析
- I/O 行为模式匹配
- 内存拓扑检测

虚拟机提交的证明会被直接拒绝，多次尝试可能导致质押扣除。

**Q: 一台机器可以运行多个矿工吗？**

不建议。每个物理硬件对应一个矿工身份。如果机器有多颗 CPU（如多插槽服务器），可以为每个 CPU 注册独立矿工。

**Q: 挖矿对带宽有什么要求？**

很低。每次挖矿交互只有几 KB 数据，每分钟约 1-2 次请求。拨号网络都够用。

**Q: 需要一直在线吗？**

不需要 24/7 在线，但在线时间越长，获得的挑战越多，收益越高。建议至少保持每天数小时的在线时间。

**Q: 每个 Epoch 都需要注册吗？**

是的。每个 Epoch 开始时矿工需要通过 `POST /epoch/enroll` 重新注册。

---

### 代币与奖励

**Q: 奖励如何计算？**

奖励取决于多个因素：
- 硬件的**稀缺性**（越老的硬件加成越高）
- 成功提交证明的**次数**
- 当前 Epoch 的**总奖励池**
- 在线**时长**

**Q: 奖励什么时候到账？**

证明被接受后立即计入余额。在 Epoch Settlement 阶段进行最终确认。

**Q: 如何提取 RTC？**

通过 API 查询余额后，可发起提现交易到你的钱包地址。具体方式参见 [API Reference](./api-reference.md)。

---

## 故障排除

### 连接问题

#### 症状：无法连接到 API

```bash
curl -k https://50.28.86.131/health
# curl: (7) Failed to connect to 50.28.86.131
```

**排查步骤：**

1. **检查网络连通性**
   ```bash
   ping 50.28.86.131
   ```

2. **检查端口是否开放**
   ```bash
   telnet 50.28.86.131 443
   ```

3. **检查防火墙**
   ```bash
   # Linux
   sudo iptables -L -n | grep 443

   # Windows
   netsh advfirewall firewall show rule name=all | findstr 443
   ```

4. **检查代理设置**
   ```bash
   echo $HTTP_PROXY $HTTPS_PROXY
   ```
   如果有代理，尝试直连：
   ```bash
   curl -k --noproxy '*' https://50.28.86.131/health
   ```

#### 症状：TLS 证书错误

```
SSL: CERTIFICATE_VERIFY_FAILED
```

**解决方案：** RustChain 使用自签名证书，确保：
- curl 加 `-k` 参数
- Python 加 `verify=False`
- 配置文件设 `skip_tls_verify = true`

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

---

### 编译问题

#### 症状：Rust 编译失败

```
error: linker `cc` not found
```

**解决方案：** 安装 C 编译器：
```bash
# Debian/Ubuntu
sudo apt install build-essential

# macOS
xcode-select --install
```

#### 症状：OpenSSL 编译错误

```
error: failed to run custom build command for `openssl-sys`
```

**解决方案：**
```bash
# Debian/Ubuntu
sudo apt install libssl-dev pkg-config

# macOS
brew install openssl
export OPENSSL_DIR=$(brew --prefix openssl)

# Windows: 使用 vcpkg
vcpkg install openssl:x64-windows
```

#### 症状：内存不足（老旧硬件常见）

```
error: compiler ran out of memory
```

**解决方案：**
1. 增加交换空间：
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```
2. 限制并行编译：
   ```bash
   cargo build --release -j 1
   ```
3. 考虑在性能更好的机器上交叉编译。

---

### 挖矿问题

#### 症状：证明被拒绝

```
{"error": "invalid_proof", "message": "Hardware attestation failed"}
```

**可能原因及解决方案：**

| 原因 | 解决方案 |
|------|----------|
| 在虚拟机中运行 | 迁移到物理硬件 |
| 挑战已过期 | 重新获取挑战（300 秒有效期） |
| 硬件指纹不匹配 | 确认注册和提交使用的硬件一致 |
| 签名错误 | 检查私钥是否正确 |

#### 症状：挖矿收益为零

**排查步骤：**

1. 确认已注册当前 Epoch：
   ```bash
   curl -k https://50.28.86.131/epoch
   ```
2. 检查矿工是否正常提交证明
3. 查看日志中是否有错误：
   ```bash
   tail -100 miner.log | grep -i error
   ```

#### 症状：挑战超时

老旧硬件计算速度慢，可能无法在 300 秒内完成。

**解决方案：**
- 降低难度设置（如果配置支持）
- 使用性能稍好的硬件
- 减少后台进程，释放计算资源

---

### API 错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 400 | 请求格式错误 | 检查 JSON 格式和必填字段 |
| 401 | 未授权 | 检查矿工公钥是否有效 |
| 404 | 资源不存在 | 检查 URL 路径和参数 |
| 409 | 冲突 | 可能已注册或挑战已用 |
| 429 | 频率限制 | 降低请求频率，等待后重试 |
| 500 | 服务器内部错误 | 稍后重试，如持续请联系团队 |

---

## 获取帮助

- **GitHub Issues:** [https://github.com/Scottcjn/Rustchain/issues](https://github.com/Scottcjn/Rustchain/issues)
- **API Reference:** [api-reference.md](./api-reference.md)
- **矿工指南:** [miner-setup-guide.md](./miner-setup-guide.md)
- **架构概述:** [architecture-overview.md](./architecture-overview.md)

提交 Issue 时请附上：
1. 硬件型号和操作系统
2. RustChain 版本（`rustchain --version`）
3. 完整错误日志
4. 复现步骤
