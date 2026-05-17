# RustChain DevOps 指南

## 概述

本指南涵盖 RustChain 矿工节点部署、CI/CD 流水线、监控告警和运维最佳实践。RustChain 使用 RIP-200 Proof-of-Antiquity (PoAn) 共识协议，基于硬件认证挖矿。

- **端点**: https://rustchain.org
- **项目结构**: Python 为主（pyproject.toml, tests/），Rust 钱包（rustchain-wallet 子目录）
- **挖矿奖励**: 1.5 RTC/epoch

---

## 1. 矿工节点部署

### 1.1 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 8+ 核 |
| 内存 | 8 GB | 16+ GB |
| 存储 | 500 GB SSD | 1+ TB NVMe |
| 网络 | 50 Mbps | 100+ Mbps |
| OS | Ubuntu 20.04+ | Ubuntu 22.04 LTS |

### 1.2 Docker 部署（推荐）

RustChain 矿工通过本地源码构建 Docker 镜像，**没有预构建镜像**：

```bash
# 从源码构建矿工镜像
docker build -f Dockerfile.miner -t rustchain-miner .

# 使用 docker-compose 启动
docker-compose up -d
```

> **注意**：不存在 `rustchain/node:latest` 等预构建镜像。所有镜像必须从仓库源码本地构建。

### 1.3 docker-compose.yml 示例

```yaml
version: "3.8"
services:
  miner:
    build:
      context: .
      dockerfile: Dockerfile.miner
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    environment:
      - RUSTCHAIN_ENDPOINT=https://rustchain.org
```

### 1.4 矿工注册与硬件认证

```bash
# 检查节点健康状态
curl -sk https://rustchain.org/health

# 查看当前矿工列表
curl -sk https://rustchain.org/api/miners

# 查询钱包余额
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_MINER_ID"
```

---

## 2. CI/CD 流水线

### 2.1 GitHub Actions 示例

RustChain 项目以 Python 为主，Rust 钱包在 `rustchain-wallet` 子目录：

```yaml
name: RustChain CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  python-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run pytest
        run: pytest tests/ -v

  rust-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: rustchain-wallet
    steps:
      - uses: actions/checkout@v4
      - uses: actions-rust-lang/setup-rust-toolchain@v1
        with:
          toolchain: stable
      - name: Run Rust tests
        run: cargo test
      - name: Run clippy
        run: cargo clippy -- -D warnings
      - name: Check formatting
        run: cargo fmt -- --check

  docker-build:
    needs: [python-test, rust-test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -f Dockerfile.miner -t rustchain-miner:${{ github.sha }} .
```

### 2.2 关键 CI 要点

- **Python 测试为主**：`pytest tests/` 覆盖核心逻辑
- **Rust 测试**：`working-directory: rustchain-wallet`，在该子目录下运行 `cargo test`
- **没有根目录 Cargo.toml**：Rust 代码仅存在于 `rustchain-wallet/` 子目录
- **Docker 构建**：使用 `Dockerfile.miner` 本地构建

### 2.3 发布流程

1. **代码审查**：所有 PR 至少 1 人 review
2. **自动化测试**：pytest + cargo test 必须通过
3. **版本打 tag**：`vX.Y.Z` 语义化版本
4. **构建矿工镜像**：`docker build -f Dockerfile.miner`
5. **部署测试网**：先在测试网验证
6. **主网发布**：矿工升级节点软件

---

## 3. 监控与告警

### 3.1 健康检查端点

```bash
# 节点健康检查
curl -s https://rustchain.org/health
# Expected: {"ok": true, "version": "2.2.1-rip200", ...}

# 矿工状态
curl -s https://rustchain.org/api/miners
```

### 3.2 Prometheus 指标

```yaml
scrape_configs:
  - job_name: 'rustchain-miner'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: /metrics
    scrape_interval: 15s
```

#### 关键监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| `rustchain_health_status` | 节点健康状态 | != 1 |
| `rustchain_epoch_rewards` | Epoch 奖励发放 | 未按预期发放 |
| `rustchain_miners_active` | 活跃矿工数 | < 预期值 |
| `rustchain_block_height` | 当前区块高度 | 停止增长 > 60s |
| `cpu_usage` | CPU 使用率 | > 80% |
| `disk_usage_percent` | 磁盘使用率 | > 85% |

### 3.3 Grafana 仪表板

推荐创建以下面板：
- **网络概览**：区块高度、活跃矿工数、epoch 奖励
- **节点健康**：CPU、内存、磁盘、网络 I/O、`/health` 状态
- **矿工状态**：在线矿工、硬件认证状态、epoch 参与
- **钱包**：余额变化、交易历史

### 3.4 告警配置

```yaml
# AlertManager 规则示例
groups:
  - name: rustchain
    rules:
      - alert: MinerDown
        expr: rustchain_health_status != 1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "矿工节点不健康"

      - alert: DiskSpaceLow
        expr: disk_usage_percent > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "磁盘空间不足"

      - alert: NoEpochRewards
        expr: rate(rustchain_epoch_rewards[30m]) == 0
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "超过30分钟未收到epoch奖励"
```

---

## 4. 日志管理

### 4.1 日志级别

```bash
# 设置日志级别（环境变量）
export RUSTCHAIN_LOG_LEVEL=info

# Docker 中通过环境变量
RUSTCHAIN_LOG_LEVEL=debug docker-compose up
```

### 4.2 结构化日志

RustChain 输出 JSON 格式日志，方便日志聚合：

```bash
# 使用 jq 过滤错误日志
docker logs rustchain-miner 2>&1 | jq 'select(.level=="error")'
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

# 备份钱包和配置
mkdir -p $BACKUP_DIR
cp -r ./data/config $BACKUP_DIR/
cp -r ./data/wallet $BACKUP_DIR/

# 压缩并上传
tar czf $BACKUP_DIR.tar.gz $BACKUP_DIR
```

### 5.2 恢复流程

```bash
# 停止矿工
docker-compose down

# 恢复数据
tar xzf /backup/rustchain/latest.tar.gz -C ./data/

# 重启
docker-compose up -d

# 验证
curl -sk https://rustchain.org/health
```

---

## 6. 安全加固

### 6.1 防火墙规则

```bash
# 只开放必要端口
ufw allow 8080/tcp  # 矿工 API
ufw allow 443/tcp   # HTTPS
ufw deny 8080/tcp   # 如不需要外部访问 API
ufw enable
```

### 6.2 密钥管理

- **不要将私钥存储在节点上**：使用硬件签名模块（HSM）或 KMS
- **密钥轮换**：定期更换节点密钥
- **钱包安全**：Rust 钱包（rustchain-wallet）密钥妥善保管

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
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建 Docker 镜像
docker build -f Dockerfile.miner -t rustchain-miner .

# 3. 重启矿工
docker-compose down
docker-compose up -d

# 4. 验证
curl -sk https://rustchain.org/health
curl -sk https://rustchain.org/api/miners
```

---

## 8. 故障排查

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| 矿工离线 | /health 返回异常 | 检查 Docker 日志、重启容器 |
| 不同步 | 区块高度落后 | 检查网络连接、确认端点可达 |
| 内存不足 | OOM killed | 增加内存或减少缓存 |
| 磁盘满 | 写入失败 | 清理旧数据、扩容 |
| Epoch 无奖励 | 余额不变 | 检查硬件认证状态、确认矿工活跃 |
| 钱包连接失败 | API 超时 | 检查 https://rustchain.org 可达性 |

---

## 9. 最佳实践清单

- [x] 使用 Docker + docker-compose 管理矿工进程
- [x] 本地构建镜像（Dockerfile.miner），不依赖预构建镜像
- [x] 配置 Prometheus + Grafana 监控
- [x] 定期检查 /health 和 /api/miners 端点
- [x] 设置日志轮转和归档
- [x] 定期备份钱包和配置
- [x] 启用防火墙，只开放必要端口
- [x] 使用 CI/CD 自动化测试（pytest + cargo test）
- [x] 保持节点软件最新版本
- [x] 准备灾难恢复计划
- [x] 文档化所有运维操作
