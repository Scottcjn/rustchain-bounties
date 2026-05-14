# RustChain DevOps 指南

## 概述

本指南涵盖 RustChain 节点部署、CI/CD 流水线、监控告警和运维最佳实践。

---

## 1. 节点部署

### 1.1 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 8+ 核 |
| 内存 | 8 GB | 16+ GB |
| 存储 | 500 GB SSD | 1+ TB NVMe |
| 网络 | 50 Mbps | 100+ Mbps |
| OS | Ubuntu 20.04+ | Ubuntu 22.04 LTS |

### 1.2 Docker 部署（推荐）

```bash
# 拉取官方镜像
docker pull rustchain/node:latest

# 启动全节点
docker run -d \
  --name rustchain-node \
  -p 26656:26656 \
  -p 26657:26657 \
  -v ~/.rustchain:/root/.rustchain \
  rustchain/node:latest \
  rustchain start
```

### 1.3 验证者节点部署

```bash
# 初始化节点
rustchain init <moniker> --chain-id rustchain-1

# 创建钱包
rustchain keys add validator

# 获取代币（测试网从 faucet）
rustchain query bank balances <address>

# 创建验证者
rustchain tx staking create-validator \
  --amount 1000000urtc \
  --pubkey $(rustchain tendermint show-validator) \
  --moniker "<moniker>" \
  --chain-id rustchain-1 \
  --from validator
```

---

## 2. CI/CD 流水线

### 2.1 GitHub Actions 示例

```yaml
name: RustChain CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  CARGO_TERM_COLOR: always

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions-rust-lang/setup-rust-toolchain@v1
        with:
          toolchain: stable
      - name: Run tests
        run: cargo test --all-features
      - name: Run clippy
        run: cargo clippy -- -D warnings
      - name: Check formatting
        run: cargo fmt -- --check

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions-rust-lang/setup-rust-toolchain@v1
      - name: Build release
        run: cargo build --release
      - name: Build Docker image
        run: docker build -t rustchain/node:${{ github.sha }} .

  deploy-testnet:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to testnet
        run: |
          echo "Deploying to testnet..."
          # 滚动升级测试网节点
```

### 2.2 发布流程

1. **代码审查**：所有 PR 至少 1 人 review
2. **自动化测试**：单元测试 + 集成测试必须通过
3. **版本打 tag**：`vX.Y.Z` 语义化版本
4. **构建发布包**：交叉编译多平台二进制
5. **部署测试网**：先在测试网验证
6. **主网升级**：治理提案 → 投票 → 执行

---

## 3. 监控与告警

### 3.1 Prometheus + Grafana

#### 节点指标（Prometheus 配置）

```yaml
scrape_configs:
  - job_name: 'rustchain'
    static_configs:
      - targets: ['localhost:26660']
    metrics_path: /metrics
    scrape_interval: 15s
```

#### 关键监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| `block_height` | 当前区块高度 | 停止增长 > 60s |
| `block_time` | 出块时间 | > 10s |
| `peers_connected` | 连接的对等节点数 | < 3 |
| `mempool_size` | 内存池交易数 | > 10000 |
| `consensus_rounds` | 共识轮次 | > 3（频繁重投票）|
| `validator_missed_blocks` | 验证者漏块数 | > 10 |
| `cpu_usage` | CPU 使用率 | > 80% |
| `disk_usage_percent` | 磁盘使用率 | > 85% |

### 3.2 Grafana 仪表板

推荐创建以下面板：
- **网络概览**：区块高度、TPS、活跃验证者数
- **节点健康**：CPU、内存、磁盘、网络 I/O
- **共识状态**：提案数、投票情况、轮次统计
- **内存池**：交易数、Gas 使用、排队时间

### 3.3 告警配置

```yaml
# AlertManager 规则示例
groups:
  - name: rustchain
    rules:
      - alert: NodeStuck
        expr: rate(block_height[5m]) == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "节点停止出块"

      - alert: HighMissedBlocks
        expr: validator_missed_blocks > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "验证者漏块过多"

      - alert: DiskSpaceLow
        expr: disk_usage_percent > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "磁盘空间不足"
```

---

## 4. 日志管理

### 4.1 日志级别

```bash
# 设置日志级别
rustchain start --log-level info

# 按模块设置
rustchain start --log-level "rustchain=info,tendermint=debug"
```

### 4.2 结构化日志

RustChain 输出 JSON 格式日志，方便日志聚合：

```bash
# 使用 jq 过滤错误日志
rustchain start 2>&1 | jq 'select(.level=="error")'

# 使用 Loki + Grafana 聚合
```

### 4.3 日志轮转

```bash
# /etc/logrotate.d/rustchain
/var/log/rustchain/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
}
```

---

## 5. 备份与恢复

### 5.1 关键数据备份

```bash
#!/bin/bash
# backup.sh - 每日备份脚本
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/rustchain/$DATE"

# 备份节点密钥和配置
mkdir -p $BACKUP_DIR
cp -r ~/.rustchain/config $BACKUP_DIR/
cp -r ~/.rustchain/keyring $BACKUP_DIR/

# 备份数据快照
rustchain export --height $(rustchain status | jq .sync_info.latest_block_height)
mv ~/.rustchain/data/export.json $BACKUP_DIR/

# 压缩并上传
tar czf $BACKUP_DIR.tar.gz $BACKUP_DIR
# aws s3 cp $BACKUP_DIR.tar.gz s3://your-backup-bucket/
```

### 5.2 恢复流程

```bash
# 从快照恢复
rustchain unsafe-reset-all
rustchain start --snapshot-uri s3://your-snapshot-bucket/latest.tar.gz
```

---

## 6. 安全加固

### 6.1 防火墙规则

```bash
# 只开放必要端口
ufw allow 26656/tcp  # P2P
ufw allow 26657/tcp  # RPC（可限制 IP）
ufw deny 26660/tcp   # Prometheus 仅内网访问
ufw enable
```

### 6.2 密钥管理

- **不要将私钥存储在节点上**：使用硬件签名模块（HSM）或 KMS
- **密钥轮换**：定期更换节点密钥
- **多重签名**：大额操作使用 multisig

### 6.3 自动安全更新

```bash
# 启用自动安全更新
apt install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## 7. 节点升级

### 7.1 滚动升级流程

```bash
# 1. 编译新版本
cargo build --release

# 2. 停止节点
systemctl stop rustchain

# 3. 备份
cp -r ~/.rustchain ~/.rustchain.backup

# 4. 替换二进制
cp target/release/rustchain /usr/local/bin/

# 5. 启动
systemctl start rustchain

# 6. 验证
rustchain status
journalctl -u rustchain -f
```

### 7.2 协议升级

- 通过治理提案发起升级
- 达成共识后，所有节点在指定高度切换
- 使用 `cosmovisor` 自动管理升级：

```bash
# 安装 cosmovisor
go install github.com/cosmos/cosmos-sdk/cosmovisor/cmd/cosmovisor@latest

# 配置自动升级
export DAEMON_NAME=rustchain
export DAEMON_HOME=~/.rustchain
cosmovisor run start
```

---

## 8. 故障排查

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| 节点不同步 | 区块高度落后 | 检查网络连接、重启节点 |
| 内存不足 | OOM killed | 增加内存或减少缓存 |
| 磁盘满 | 写入失败 | 清理旧数据、扩容 |
| 共识超时 | 频繁 round | 检查网络延迟、验证者在线数 |
| 交易失败 | Gas 不足 | 调整 Gas 限制和价格 |

---

## 9. 最佳实践清单

- [x] 使用 Docker 或 systemd 管理节点进程
- [x] 配置 Prometheus + Grafana 监控
- [x] 设置日志轮转和归档
- [x] 定期备份密钥和配置
- [x] 启用防火墙，只开放必要端口
- [x] 使用 CI/CD 自动化构建和测试
- [x] 监控验证者漏块和签名情况
- [x] 保持节点软件最新版本
- [x] 准备灾难恢复计划
- [x] 文档化所有运维操作
