# RustChain 监控和告警指南

本指南介绍如何为 RustChain 区块链网络设置完整的监控系统，包括节点监控、矿工监控、告警规则配置和仪表板搭建。

## 目录

1. [监控架构概述](#监控架构概述)
2. [监控工具选择](#监控工具选择)
3. [设置 Prometheus 监控](#设置-prometheus-监控)
4. [配置 Grafana 仪表板](#配置-grafana-仪表板)
5. [告警规则配置](#告警规则配置)
6. [通知渠道集成](#通知渠道集成)
7. [监控最佳实践](#监控最佳实践)

---

## 监控架构概述

### RustChain 核心监控指标

| 类别 | 指标 | 说明 |
|------|------|------|
| 节点健康 | `node_health_status` | 节点运行状态 (1=正常，0=异常) |
| 节点健康 | `node_uptime_seconds` | 节点运行时间 |
| 节点健康 | `node_peers_count` | 连接的对等节点数量 |
| 区块同步 | `current_epoch` | 当前纪元编号 |
| 区块同步 | `block_height` | 当前区块高度 |
| 区块同步 | `sync_status` | 同步状态 (1=同步中，0=已同步) |
| 矿工监控 | `active_miners_count` | 活跃矿工数量 |
| 矿工监控 | `miner_hashrate` | 矿工算力 |
| 矿工监控 | `miner_rewards_earned` | 矿工累计奖励 |
| 系统资源 | `cpu_usage_percent` | CPU 使用率 |
| 系统资源 | `memory_usage_percent` | 内存使用率 |
| 系统资源 | `disk_usage_percent` | 磁盘使用率 |
| 网络性能 | `request_latency_ms` | API 请求延迟 |
| 网络性能 | `requests_per_second` | 每秒请求数 |
| 网络性能 | `error_rate_percent` | 错误率 |

---

## 监控工具选择

### 推荐技术栈

```
┌─────────────────────────────────────────────────────────┐
│                    Grafana (仪表板)                      │
├─────────────────────────────────────────────────────────┤
│                    Alertmanager (告警)                   │
├─────────────────────────────────────────────────────────┤
│                    Prometheus (指标收集)                 │
├─────────────────────────────────────────────────────────┤
│  Node Exporter │  RustChain Exporter  │  Blackbox      │
│  (系统指标)    │  (区块链指标)        │  (网络探测)     │
└─────────────────────────────────────────────────────────┘
```

### 替代方案

- **轻量级**: VictoriaMetrics + Grafana Cloud
- **云原生**: AWS CloudWatch / GCP Monitoring
- **简单场景**: Uptime Kuma + Telegram 通知

---

## 设置 Prometheus 监控

### 1. 安装 Prometheus

```bash
# 使用 Docker Compose 部署
mkdir -p ~/rustchain-monitoring
cd ~/rustchain-monitoring

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points="^/(sys|proc|dev|host|etc)($$|/)"'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=rustchain2026
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
EOF
```

### 2. 配置 Prometheus

```bash
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - "alert_rules.yml"

scrape_configs:
  # Prometheus 自身监控
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # 节点系统指标
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # RustChain 节点监控
  - job_name: 'rustchain-node'
    static_configs:
      - targets: ['rustchain.org:443']
    metrics_path: '/metrics'
    scheme: https

  # RustChain API 端点监控
  - job_name: 'rustchain-api'
    metrics_path: '/probe'
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://rustchain.org/health
        - https://rustchain.org/epoch
        - https://rustchain.org/api/miners
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

  # 钱包余额监控 (需要自定义 exporter)
  - job_name: 'rustchain-wallets'
    static_configs:
      - targets: ['wallet-exporter:9101']
EOF
```

### 3. 创建 RustChain 自定义 Exporter

```python
#!/usr/bin/env python3
"""
RustChain Prometheus Exporter
监控 RustChain 网络状态、矿工信息和钱包余额
"""

import requests
import time
from prometheus_client import start_http_server, Gauge, Counter, Info
import sys

# 定义指标
node_health = Gauge('rustchain_node_health', 'Node health status (1=healthy, 0=unhealthy)')
current_epoch = Gauge('rustchain_current_epoch', 'Current epoch number')
active_miners = Gauge('rustchain_active_miners', 'Number of active miners')
wallet_balance = Gauge('rustchain_wallet_balance', 'Wallet balance in RTC', ['wallet_name'])
request_latency = Gauge('rustchain_api_latency_seconds', 'API request latency', ['endpoint'])
request_errors = Counter('rustchain_api_errors_total', 'Total API request errors', ['endpoint'])

RUSTCHAIN_BASE_URL = "https://rustchain.org"

def get_node_health():
    """获取节点健康状态"""
    try:
        start = time.time()
        response = requests.get(f"{RUSTCHAIN_BASE_URL}/health", timeout=10, verify=False)
        latency = time.time() - start
        
        if response.status_code == 200:
            node_health.set(1)
            request_latency.labels(endpoint='health').set(latency)
            return True
        else:
            node_health.set(0)
            request_errors.labels(endpoint='health').inc()
            return False
    except Exception as e:
        node_health.set(0)
        request_errors.labels(endpoint='health').inc()
        print(f"Health check failed: {e}", file=sys.stderr)
        return False

def get_epoch_info():
    """获取当前纪元信息"""
    try:
        start = time.time()
        response = requests.get(f"{RUSTCHAIN_BASE_URL}/epoch", timeout=10, verify=False)
        latency = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            current_epoch.set(data.get('epoch', 0))
            request_latency.labels(endpoint='epoch').set(latency)
        else:
            request_errors.labels(endpoint='epoch').inc()
    except Exception as e:
        request_errors.labels(endpoint='epoch').inc()
        print(f"Epoch fetch failed: {e}", file=sys.stderr)

def get_miner_count():
    """获取活跃矿工数量"""
    try:
        start = time.time()
        response = requests.get(f"{RUSTCHAIN_BASE_URL}/api/miners", timeout=10, verify=False)
        latency = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            miners = data.get('miners', [])
            active_miners.set(len(miners))
            request_latency.labels(endpoint='miners').set(latency)
        else:
            request_errors.labels(endpoint='miners').inc()
    except Exception as e:
        request_errors.labels(endpoint='miners').inc()
        print(f"Miner fetch failed: {e}", file=sys.stderr)

def get_wallet_balance(wallet_name):
    """获取钱包余额"""
    try:
        response = requests.get(
            f"{RUSTCHAIN_BASE_URL}/wallet/balance?miner_id={wallet_name}",
            timeout=10,
            verify=False
        )
        if response.status_code == 200:
            data = response.json()
            balance = data.get('balance', 0)
            wallet_balance.labels(wallet_name=wallet_name).set(balance)
    except Exception as e:
        print(f"Wallet balance fetch failed for {wallet_name}: {e}", file=sys.stderr)

def collect_metrics():
    """收集所有指标"""
    get_node_health()
    get_epoch_info()
    get_miner_count()
    
    # 监控配置的钱包
    wallets = ['my-miner-wallet', 'treasury', 'rewards-pool']
    for wallet in wallets:
        get_wallet_balance(wallet)

if __name__ == '__main__':
    # 启动 HTTP 服务器暴露指标
    start_http_server(9101)
    print("RustChain Exporter started on port 9101")
    
    while True:
        collect_metrics()
        time.sleep(60)  # 每分钟收集一次
```

### 4. 启动监控服务

```bash
# 启动所有服务
docker-compose up -d

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f prometheus
```

---

## 配置 Grafana 仪表板

### 1. 添加 Prometheus 数据源

访问 `http://localhost:3000`，使用 admin/rustchain2026 登录。

**添加数据源步骤:**

1. 点击 Configuration → Data Sources
2. 点击 "Add data source"
3. 选择 Prometheus
4. 设置 URL: `http://prometheus:9090`
5. 点击 "Save & Test"

### 2. 导入仪表板

#### 仪表板 1: RustChain 网络概览

```json
{
  "dashboard": {
    "title": "RustChain Network Overview",
    "panels": [
      {
        "title": "Node Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "rustchain_node_health",
            "legendFormat": "Health"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"value": null, "color": "red"},
                {"value": 1, "color": "green"}
              ]
            }
          }
        }
      },
      {
        "title": "Current Epoch",
        "type": "stat",
        "targets": [
          {
            "expr": "rustchain_current_epoch",
            "legendFormat": "Epoch {{epoch}}"
          }
        ]
      },
      {
        "title": "Active Miners",
        "type": "stat",
        "targets": [
          {
            "expr": "rustchain_active_miners",
            "legendFormat": "Miners"
          }
        ]
      },
      {
        "title": "API Request Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "rustchain_api_latency_seconds",
            "legendFormat": "{{endpoint}}"
          }
        ]
      }
    ]
  }
}
```

#### 仪表板 2: 系统资源监控

使用 Grafana 内置的 "Node Exporter Full" 仪表板 (ID: 1860)

#### 仪表板 3: 钱包余额追踪

```json
{
  "dashboard": {
    "title": "RustChain Wallet Balances",
    "panels": [
      {
        "title": "Wallet Balance Trend",
        "type": "graph",
        "targets": [
          {
            "expr": "rustchain_wallet_balance",
            "legendFormat": "{{wallet_name}}"
          }
        ]
      },
      {
        "title": "Total Balance",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rustchain_wallet_balance)",
            "legendFormat": "Total RTC"
          }
        ]
      }
    ]
  }
}
```

### 3. 导入现有仪表板

```bash
# 使用 grafana-cli 导入
docker exec grafana grafana-cli --pluginsDir /var/lib/grafana/plugins plugins install grafana-piechart-panel

# 通过 API 导入仪表板
curl -X POST \
  -H "Content-Type: application/json" \
  -d @dashboard-network-overview.json \
  http://admin:rustchain2026@localhost:3000/api/dashboards/db
```

---

## 告警规则配置

### 1. 创建告警规则文件

```yaml
# alert_rules.yml
groups:
  - name: rustchain_alerts
    interval: 30s
    rules:
      # 节点宕机告警
      - alert: RustChainNodeDown
        expr: rustchain_node_health == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "RustChain 节点宕机"
          description: "RustChain 节点已宕机超过 2 分钟，当前状态：{{ $value }}"

      # 纪元停止更新告警
      - alert: RustChainEpochStalled
        expr: changes(rustchain_current_epoch[15m]) == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RustChain 纪元停止更新"
          description: "当前纪元 {{ $value }} 已超过 15 分钟未更新"

      # 矿工数量骤降告警
      - alert: RustChainMinerDrop
        expr: delta(rustchain_active_miners[10m]) < -10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RustChain 矿工数量骤降"
          description: "10 分钟内矿工数量减少 {{ $value }} 个"

      # API 延迟过高告警
      - alert: RustChainAPILatencyHigh
        expr: rustchain_api_latency_seconds > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RustChain API 延迟过高"
          description: "端点 {{ $labels.endpoint }} 延迟 {{ $value }}s 超过阈值 5s"

      # API 错误率过高告警
      - alert: RustChainAPIErrorsHigh
        expr: rate(rustchain_api_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "RustChain API 错误率过高"
          description: "端点 {{ $labels.endpoint }} 错误率 {{ $value }}/s"

      # 磁盘空间不足告警
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "磁盘空间不足"
          description: "磁盘 {{ $labels.mountpoint }} 剩余空间仅 {{ $value }}%"

      # 内存使用率过高告警
      - alert: MemoryUsageHigh
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "内存使用率 {{ $value }}% 超过阈值 85%"

      # CPU 使用率过高告警
      - alert: CPUUsageHigh
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率过高"
          description: "CPU 使用率 {{ $value }}% 超过阈值 80%"
```

### 2. 配置 Alertmanager

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager@example.com'
  smtp_auth_password: 'your-password'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default-receiver'
  routes:
    - match:
        severity: critical
      receiver: 'critical-receiver'
      continue: true
    - match:
        severity: warning
      receiver: 'warning-receiver'

receivers:
  - name: 'default-receiver'
    email_configs:
      - to: 'admin@example.com'
        send_resolved: true

  - name: 'critical-receiver'
    email_configs:
      - to: 'oncall@example.com'
        send_resolved: true
        html: |
          <h2>🚨 紧急告警</h2>
          <p><strong>告警:</strong> {{ .CommonAnnotations.summary }}</p>
          <p><strong>描述:</strong> {{ .CommonAnnotations.description }}</p>
          <p><strong>时间:</strong> {{ .StartsAt }}</p>

  - name: 'warning-receiver'
    email_configs:
      - to: 'team@example.com'
        send_resolved: true

# Webhook 集成 (可选 - 钉钉/飞书/Telegram)
# webhook_configs:
#   - url: 'http://webhook-server:5001/alert'
#     send_resolved: true
```

### 3. 集成通知渠道

#### 飞书 webhook 集成

```python
# feishu_webhook.py
from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import base64
import time

app = Flask(__name__)

FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_KEY"
FEISHU_SECRET = "YOUR_SECRET"  # 飞书机器人加签密钥

def generate_sign(timestamp, secret):
    """生成飞书签名"""
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign

@app.route('/alert', methods=['POST'])
def handle_alert():
    data = request.json
    
    alerts = data.get('alerts', [])
    timestamp = str(int(time.time()))
    sign = generate_sign(timestamp, FEISHU_SECRET)
    
    for alert in alerts:
        status = "🔴 触发" if alert['status'] == 'firing' else "🟢 恢复"
        severity = alert['labels'].get('severity', 'unknown')
        
        color = "red" if severity == 'critical' else "orange"
        
        message = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"{status} RustChain 告警"
                    },
                    "template": color
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**告警名称**: {alert['labels']['alertname']}\n**严重级别**: {severity}\n**摘要**: {alert['annotations']['summary']}\n**描述**: {alert['annotations']['description']}"
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**开始时间**: {alert['startsAt']}"
                        }
                    }
                ]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Sign-Timestamp": timestamp,
            "X-Sign-Signature": sign
        }
        
        requests.post(FEISHU_WEBHOOK_URL, json=message, headers=headers)
    
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

#### Telegram 通知集成

```yaml
# alertmanager.yml 添加 Telegram 配置
receivers:
  - name: 'telegram-receiver'
    telegram_configs:
      - bot_token: 'YOUR_BOT_TOKEN'
        chat_id: 'YOUR_CHAT_ID'
        send_resolved: true
        message: |
          🚨 *告警通知*
          
          *告警:* {{ .CommonAnnotations.summary }}
          *级别:* {{ .CommonLabels.severity }}
          *描述:* {{ .CommonAnnotations.description }}
          *时间:* {{ .StartsAt }}
          
          {{ range .Alerts }}
          ---
          *实例:* {{ .Labels.instance }}
          {{ end }}
```

---

## 监控最佳实践

### 1. 监控分层策略

```
┌────────────────────────────────────────────┐
│ 业务层监控                                  │
│ - 钱包余额异常                              │
│ - 奖励发放失败                              │
│ - 治理提案状态                              │
├────────────────────────────────────────────┤
│ 应用层监控                                  │
│ - API 可用性                                │
│ - 节点同步状态                              │
│ - 矿工活跃度                                │
├────────────────────────────────────────────┤
│ 系统层监控                                  │
│ - CPU/内存/磁盘                             │
│ - 网络带宽                                  │
│ - 进程状态                                  │
└────────────────────────────────────────────┘
```

### 2. 告警分级标准

| 级别 | 响应时间 | 通知渠道 | 示例 |
|------|----------|----------|------|
| Critical | 5 分钟内 | 电话 + 短信 + IM | 节点宕机、数据丢失 |
| Warning | 30 分钟内 | IM + 邮件 | 资源使用率高、延迟增加 |
| Info | 工作日处理 | 邮件 | 配置变更、定期报告 |

### 3. 告警疲劳预防

- **设置合理的阈值**: 基于历史数据 P95/P99 分位数
- **使用告警抑制**: 避免级联告警
- **定期审查告警**: 每月审查并优化告警规则
- **设置静默期**: 维护期间暂停告警

### 4. 监控仪表板设计原则

- **5 秒原则**: 5 秒内理解系统状态
- **分层展示**: 概览 → 详情 → 诊断
- **颜色一致**: 绿色正常、黄色警告、红色异常
- **趋势展示**: 显示历史趋势而非单点值

### 5. 定期演练

```bash
# 测试告警规则
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alerts": [{
      "status": "firing",
      "labels": {
        "alertname": "TestAlert",
        "severity": "warning"
      },
      "annotations": {
        "summary": "测试告警",
        "description": "这是一条测试告警"
      },
      "startsAt": "'$(date -Iseconds)'",
      "endsAt": "'$(date -Iseconds -d '+5 minutes')'"
    }]
  }'
```

---

## 快速部署脚本

```bash
#!/bin/bash
# deploy-monitoring.sh - 一键部署 RustChain 监控系统

set -e

echo "🚀 开始部署 RustChain 监控系统..."

# 创建目录
mkdir -p ~/rustchain-monitoring/{prometheus,grafana,alertmanager}
cd ~/rustchain-monitoring

# 下载配置文件
echo "📥 下载配置文件..."
curl -o prometheus/prometheus.yml https://raw.githubusercontent.com/rustchain-monitoring/main/prometheus.yml
curl -o alertmanager/alertmanager.yml https://raw.githubusercontent.com/rustchain-monitoring/main/alertmanager.yml

# 启动服务
echo "🐳 启动 Docker 服务..."
docker-compose up -d

# 等待服务就绪
echo "⏳ 等待服务就绪..."
sleep 10

# 检查服务状态
echo "✅ 服务状态:"
docker-compose ps

echo ""
echo "📊 访问地址:"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3000 (admin/rustchain2026)"
echo "  - Alertmanager: http://localhost:9093"
echo ""
echo "🎉 部署完成!"
```

---

## 故障排查

### 常见问题

1. **Prometheus 无法抓取指标**
   ```bash
   # 检查目标状态
   curl http://localhost:9090/api/v1/targets
   
   # 查看 Prometheus 日志
   docker logs prometheus | grep error
   ```

2. **Grafana 无法连接数据源**
   - 确认 Prometheus 服务运行正常
   - 检查网络连通性：`docker network inspect monitoring_default`
   - 验证数据源 URL: `http://prometheus:9090`

3. **告警未触发**
   ```bash
   # 检查告警规则
   curl http://localhost:9090/api/v1/rules
   
   # 查看 Alertmanager 状态
   curl http://localhost:9093/api/v2/status
   
   # 查看待处理告警
   curl http://localhost:9093/api/v2/alerts
   ```

4. **Exporter 指标不更新**
   ```bash
   # 检查 Exporter 日志
   docker logs rustchain-exporter
   
   # 手动测试指标端点
   curl http://localhost:9101/metrics
   ```

---

## 参考资源

- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方文档](https://grafana.com/docs/)
- [Alertmanager 配置指南](https://prometheus.io/docs/alerting/latest/configuration/)
- [RustChain API 文档](https://rustchain.org/api/docs)
- [Prometheus 最佳实践](https://prometheus.io/docs/practices/)

---

*最后更新：2026-03-12*
*维护者：RustChain 社区*
