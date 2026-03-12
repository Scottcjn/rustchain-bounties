# RustChain 负载均衡部署指南

## 概述

本指南介绍如何为 RustChain 网络部署负载均衡器，实现流量分配、高可用性和水平扩展。

**奖励：** 3 RTC  
**Issue：** #1671

---

## 目录

1. [架构概述](#架构概述)
2. [负载均衡方案选择](#负载均衡方案选择)
3. [NGINX 部署方案](#nginx 部署方案)
4. [HAProxy 部署方案](#haproxy 部署方案)
5. [流量分配策略](#流量分配策略)
6. [健康检查配置](#健康检查配置)
7. [监控与日志](#监控与日志)
8. [故障排除](#故障排除)

---

## 架构概述

### RustChain 网络拓扑

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │  (NGINX/HAProxy)│
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
    │  Node 1     │   │  Node 2     │   │  Node 3     │
    │  Primary    │   │  Secondary  │   │  Community  │
    │  :443       │   │  :443       │   │  :443       │
    └─────────────┘   └─────────────┘   └─────────────┘
```

### 当前节点列表

| 节点 | IP 地址 | 角色 | 状态 |
|------|---------|------|------|
| Node 1 | 50.28.86.131 | Primary + Explorer | ✅ Active |
| Node 2 | 50.28.86.153 | Ergo Anchor | ✅ Active |
| Node 3 | 76.8.228.245 | External (Community) | ✅ Active |

### 需要负载均衡的端点

```bash
# 健康检查
GET /health

#  epoch 信息
GET /epoch

# 矿工列表
GET /api/miners

# 钱包余额
GET /wallet/balance?miner_id={wallet}

# 区块浏览器
GET /explorer

# 治理端点
POST /governance/propose
POST /governance/vote
GET /governance/proposals
```

---

## 负载均衡方案选择

### 方案对比

| 特性 | NGINX | HAProxy | Traefik |
|------|-------|---------|---------|
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 配置简易性 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 健康检查 | ✅ | ✅ | ✅ 自动 |
| SSL 终止 | ✅ | ✅ | ✅ 自动 |
| WebSocket 支持 | ✅ | ✅ | ✅ |
| 动态配置 | ❌ | ❌ | ✅ |
| 社区支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**推荐：** 
- **生产环境：** NGINX（性能最佳，稳定性高）
- **简单部署：** HAProxy（配置简洁，专注负载均衡）
- **容器环境：** Traefik（自动服务发现）

---

## NGINX 部署方案

### 1. 安装 NGINX

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

#### CentOS/RHEL

```bash
sudo yum install epel-release -y
sudo yum install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

#### macOS (Homebrew)

```bash
brew install nginx
brew services start nginx
```

### 2. 配置负载均衡

创建配置文件 `/etc/nginx/conf.d/rustchain-lb.conf`：

```nginx
upstream rustchain_nodes {
    least_conn;  # 最少连接数算法
    
    # 后端节点配置
    server 50.28.86.131:443 weight=5 max_fails=3 fail_timeout=30s;  # Primary
    server 50.28.86.153:443 weight=3 max_fails=3 fail_timeout=30s;  # Ergo Anchor
    server 76.8.228.245:443 weight=2 max_fails=3 fail_timeout=30s;  # Community
}

server {
    listen 80;
    listen [::]:80;
    server_name rustchain.example.com;  # 替换为你的域名
    
    # HTTP 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name rustchain.example.com;
    
    # SSL 证书配置（使用 Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/rustchain.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rustchain.example.com/privkey.pem;
    
    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    
    # 日志配置
    access_log /var/log/nginx/rustchain_access.log;
    error_log /var/log/nginx/rustchain_error.log;
    
    # 健康检查端点（不负载均衡，直接返回 OK）
    location /nginx-health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # API 端点负载均衡
    location /health {
        proxy_pass https://rustchain_nodes;
        proxy_ssl_verify off;  # RustChain 使用自签名证书
        proxy_ssl_server_name on;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
    
    location /epoch {
        proxy_pass https://rustchain_nodes;
        proxy_ssl_verify off;
        proxy_ssl_server_name on;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_pragma;
        proxy_no_cache $http_pragma;
    }
    
    location /api/ {
        proxy_pass https://rustchain_nodes;
        proxy_ssl_verify off;
        proxy_ssl_server_name on;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 速率限制（可选）
        limit_req zone=api_limit burst=20 nodelay;
    }
    
    location /wallet/ {
        proxy_pass https://rustchain_nodes;
        proxy_ssl_verify off;
        proxy_ssl_server_name on;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /explorer {
        proxy_pass https://rustchain_nodes;
        proxy_ssl_verify off;
        proxy_ssl_server_name on;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /governance/ {
        proxy_pass https://rustchain_nodes;
        proxy_ssl_verify off;
        proxy_ssl_server_name on;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 治理端点需要更长的超时
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 默认位置
    location / {
        proxy_pass https://rustchain_nodes;
        proxy_ssl_verify off;
        proxy_ssl_server_name on;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# 速率限制区域配置
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

### 3. 配置主动健康检查（NGINX Plus）

如果使用 NGINX Plus，可以配置主动健康检查：

```nginx
upstream rustchain_nodes {
    least_conn;
    
    server 50.28.86.131:443;
    server 50.28.86.153:443;
    server 76.8.228.245:443;
    
    # 主动健康检查
    health_check interval=10s fails=3 passes=2 uri=/health match=healthy_response;
}

match healthy_response {
    status 200;
    body ~ "healthy";
}
```

### 4. 测试配置

```bash
# 测试配置文件语法
sudo nginx -t

# 重新加载配置
sudo nginx -s reload

# 检查状态
sudo systemctl status nginx
```

### 5. 验证负载均衡

```bash
# 多次请求查看不同节点响应
for i in {1..10}; do
    curl -sk https://rustchain.example.com/health | jq -r '.node_id // "unknown"'
done

# 检查负载均衡器自身健康
curl -s http://localhost/nginx-health
```

---

## HAProxy 部署方案

### 1. 安装 HAProxy

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install haproxy -y
sudo systemctl enable haproxy
sudo systemctl start haproxy
```

#### CentOS/RHEL

```bash
sudo yum install haproxy -y
sudo systemctl enable haproxy
sudo systemctl start haproxy
```

### 2. 配置 HAProxy

编辑 `/etc/haproxy/haproxy.cfg`：

```haproxy
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

    # SSL 配置
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
    ssl-default-server-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    ssl-default-server-options ssl-min-ver TLSv1.2 no-tls-tickets

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    option  forwardfor
    option  http-server-close
    timeout connect 5s
    timeout client  30s
    timeout server  30s
    timeout http-request 10s
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

# 统计页面
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
    stats admin if LOCALHOST

# HTTPS 前端
frontend https_front
    bind *:443 ssl crt /etc/letsencrypt/live/rustchain.example.com/combined.pem
    http-request set-header X-Forwarded-Proto https
    
    # ACL 定义
    acl is_health path_beg /health
    acl is_api path_beg /api/
    acl is_wallet path_beg /wallet/
    acl is_explorer path_beg /explorer
    acl is_governance path_beg /governance/
    
    # 路由到不同后端
    use_backend rustchain_health if is_health
    use_backend rustchain_api if is_api
    use_backend rustchain_wallet if is_wallet
    use_backend rustchain_explorer if is_explorer
    use_backend rustchain_governance if is_governance
    default_backend rustchain_main

# HTTP 重定向到 HTTPS
frontend http_front
    bind *:80
    http-request redirect scheme https unless { ssl_fc }

# 主后端
backend rustchain_main
    balance leastconn
    option httpchk GET /health
    http-check expect status 200
    
    # 后端节点（使用 verify none 因为 RustChain 使用自签名证书）
    server node1 50.28.86.131:443 weight 5 check ssl verify none inter 5s fall 3 rise 2
    server node2 50.28.86.153:443 weight 3 check ssl verify none inter 5s fall 3 rise 2
    server node3 76.8.228.245:443 weight 2 check ssl verify none inter 5s fall 3 rise 2

# 健康检查专用后端
backend rustchain_health
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    
    server node1 50.28.86.131:443 check ssl verify none inter 5s fall 3 rise 2
    server node2 50.28.86.153:443 check ssl verify none inter 5s fall 3 rise 2
    server node3 76.8.228.245:443 check ssl verify none inter 5s fall 3 rise 2

# API 后端（带速率限制）
backend rustchain_api
    balance leastconn
    option httpchk GET /health
    http-check expect status 200
    
    server node1 50.28.86.131:443 weight 5 check ssl verify none inter 5s fall 3 rise 2
    server node2 50.28.86.153:443 weight 3 check ssl verify none inter 5s fall 3 rise 2
    server node3 76.8.228.245:443 weight 2 check ssl verify none inter 5s fall 3 rise 2

# 钱包后端
backend rustchain_wallet
    balance source  # 基于源 IP 保持会话
    option httpchk GET /health
    http-check expect status 200
    
    server node1 50.28.86.131:443 check ssl verify none inter 5s fall 3 rise 2
    server node2 50.28.86.153:443 check ssl verify none inter 5s fall 3 rise 2
    server node3 76.8.228.245:443 check ssl verify none inter 5s fall 3 rise 2

# 区块浏览器后端
backend rustchain_explorer
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    
    server node1 50.28.86.131:443 check ssl verify none inter 5s fall 3 rise 2
    server node2 50.28.86.153:443 check ssl verify none inter 5s fall 3 rise 2
    server node3 76.8.228.245:443 check ssl verify none inter 5s fall 3 rise 2

# 治理后端（更长超时）
backend rustchain_governance
    balance leastconn
    timeout server 60s
    option httpchk GET /health
    http-check expect status 200
    
    server node1 50.28.86.131:443 weight 5 check ssl verify none inter 5s fall 3 rise 2
    server node2 50.28.86.153:443 weight 3 check ssl verify none inter 5s fall 3 rise 2
    server node3 76.8.228.245:443 weight 2 check ssl verify none inter 5s fall 3 rise 2
```

### 3. 测试和启动

```bash
# 检查配置
sudo haproxy -c -f /etc/haproxy/haproxy.cfg

# 重启 HAProxy
sudo systemctl restart haproxy

# 查看状态
sudo systemctl status haproxy

# 查看日志
sudo tail -f /var/log/haproxy.log
```

### 4. 访问统计页面

```bash
# 访问 HAProxy 统计页面（需要认证可添加）
curl http://localhost:8404/stats
```

---

## 流量分配策略

### 1. 负载均衡算法

#### 轮询（Round Robin）
```nginx
# NGINX
upstream rustchain_nodes {
    rr;  # 默认
    server 50.28.86.131:443;
    server 50.28.86.153:443;
    server 76.8.228.245:443;
}
```

```haproxy
# HAProxy
backend rustchain_main
    balance roundrobin
```

#### 最少连接（Least Connections）
```nginx
# NGINX
upstream rustchain_nodes {
    least_conn;
    server 50.28.86.131:443;
    server 50.28.86.153:443;
    server 76.8.228.245:443;
}
```

```haproxy
# HAProxy
backend rustchain_main
    balance leastconn
```

#### IP 哈希（会话保持）
```nginx
# NGINX
upstream rustchain_nodes {
    ip_hash;
    server 50.28.86.131:443;
    server 50.28.86.153:443;
    server 76.8.228.245:443;
}
```

```haproxy
# HAProxy
backend rustchain_wallet
    balance source
```

#### 加权分配
```nginx
# NGINX - 根据节点性能分配权重
upstream rustchain_nodes {
    least_conn;
    server 50.28.86.131:443 weight=5;  # Primary 节点，50% 流量
    server 50.28.86.153:443 weight=3;  # Ergo Anchor，30% 流量
    server 76.8.228.245:443 weight=2;  # Community，20% 流量
}
```

### 2. 基于路径的路由

```nginx
# NGINX 示例
location /api/miners {
    proxy_pass https://rustchain_nodes;
    # API 请求
}

location /explorer {
    proxy_pass https://rustchain_nodes;
    # 浏览器请求，可能需要 WebSocket
}
```

### 3. 基于地理位置的路由（高级）

使用 GeoIP 模块：

```nginx
# 需要 NGINX Plus 或编译 GeoIP 模块
geoip_country /usr/share/GeoIP/GeoIP.dat;

map $geoip_country_code $rustchain_node {
    CN      50.28.86.131;  # 亚洲用户到 Node 1
    US      50.28.86.153;  # 美洲用户到 Node 2
    EU      76.8.228.245;  # 欧洲用户到 Node 3
    default 50.28.86.131;
}
```

---

## 健康检查配置

### 1. NGINX 健康检查

#### 被动健康检查（开源版）

```nginx
upstream rustchain_nodes {
    least_conn;
    
    # max_fails: 失败次数阈值
    # fail_timeout: 失败后的隔离时间
    server 50.28.86.131:443 max_fails=3 fail_timeout=30s;
    server 50.28.86.153:443 max_fails=3 fail_timeout=30s;
    server 76.8.228.245:443 max_fails=3 fail_timeout=30s;
}
```

#### 主动健康检查（NGINX Plus）

```nginx
upstream rustchain_nodes {
    least_conn;
    
    server 50.28.86.131:443;
    server 50.28.86.153:443;
    server 76.8.228.245:443;
    
    # 主动健康检查配置
    health_check interval=10s fails=3 passes=2 uri=/health match=healthy_response;
}

match healthy_response {
    status 200;
    body ~ "healthy";
}
```

### 2. HAProxy 健康检查

```haproxy
backend rustchain_main
    # 健康检查间隔 5 秒
    # 连续 3 次失败标记为 down
    # 连续 2 次成功标记为 up
    option httpchk GET /health
    http-check expect status 200
    
    server node1 50.28.86.131:443 check ssl verify none inter 5s fall 3 rise 2
    server node2 50.28.86.153:443 check ssl verify none inter 5s fall 3 rise 2
    server node3 76.8.228.245:443 check ssl verify none inter 5s fall 3 rise 2
```

### 3. 自定义健康检查脚本

创建 `/usr/local/bin/rustchain-health-check.sh`：

```bash
#!/bin/bash

NODE_URL=$1
TIMEOUT=5

# 检查健康端点
response=$(curl -sk --max-time $TIMEOUT "${NODE_URL}/health" 2>/dev/null)

if [ $? -eq 0 ]; then
    # 验证响应内容
    if echo "$response" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
        exit 0  # 健康
    fi
fi

exit 1  # 不健康
```

```bash
chmod +x /usr/local/bin/rustchain-health-check.sh
```

---

## 监控与日志

### 1. NGINX 日志分析

#### 访问日志格式

```nginx
# 在 http 块中添加
log_format rustchain '$remote_addr - $remote_user [$time_local] '
                     '"$request" $status $body_bytes_sent '
                     '"$http_referer" "$http_user_agent" '
                     'rt=$request_time uct="$upstream_connect_time" '
                     'uht="$upstream_header_time" urt="$upstream_response_time"';

access_log /var/log/nginx/rustchain_access.log rustchain;
```

#### 实时监控

```bash
# 实时查看访问日志
tail -f /var/log/nginx/rustchain_access.log

# 统计状态码
awk '{print $9}' /var/log/nginx/rustchain_access.log | sort | uniq -c

# 查看最慢的请求
awk '($NF > 1) {print $7, $NF}' /var/log/nginx/rustchain_access.log | sort -k2 -rn | head -20
```

### 2. HAProxy 统计

#### 启用统计页面

```haproxy
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
    stats admin if LOCALHOST
```

访问 `http://your-lb-ip:8404/stats` 查看实时统计。

#### 使用 Socket 监控

```bash
# 连接到 HAProxy socket
echo "show stat" | sudo socat stdio /run/haproxy/admin.sock

# 显示服务器状态
echo "show servers state" | sudo socat stdio /run/haproxy/admin.sock
```

### 3. Prometheus + Grafana 监控

#### NGINX Exporter

```bash
# 安装 nginx-prometheus-exporter
docker run -d \
  --name nginx-exporter \
  -p 9113:9113 \
  nginx/nginx-prometheus-exporter:latest \
  -nginx.scrape-uri="http://localhost/stub_status"
```

#### HAProxy Exporter

```bash
docker run -d \
  --name haproxy-exporter \
  -p 9101:9101 \
  prom/haproxy-exporter:latest \
  --haproxy.scrape-uri="http://localhost:8404/stats;csv"
```

#### Grafana 仪表板

导入以下仪表板：
- NGINX: Dashboard ID 12708
- HAProxy: Dashboard ID 2428

### 4. 告警配置

创建 Prometheus 告警规则 `/etc/prometheus/rules/rustchain.yml`：

```yaml
groups:
  - name: rustchain
    rules:
      - alert: RustChainNodeDown
        expr: haproxy_server_up{backend="rustchain_main"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "RustChain 节点 {{ $labels.server }} 宕机"
          description: "节点 {{ $labels.server }} 已经宕机超过 1 分钟"
      
      - alert: RustChainHighErrorRate
        expr: rate(haproxy_server_http_responses_total{code="5xx"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RustChain 错误率过高"
          description: "5xx 错误率超过 10%"
      
      - alert: RustChainHighLatency
        expr: histogram_quantile(0.95, rate(haproxy_server_http_response_time_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RustChain 延迟过高"
          description: "95 分位延迟超过 1 秒"
```

---

## 故障排除

### 1. 常见问题

#### SSL 证书验证失败

**问题：** 后端使用自签名证书

**解决：**
```nginx
# NGINX
proxy_ssl_verify off;
proxy_ssl_server_name on;
```

```haproxy
# HAProxy
server node1 50.28.86.131:443 ssl verify none
```

#### 后端节点全部不可用

**问题：** 健康检查过于严格

**解决：** 调整健康检查参数
```haproxy
# 增加容错
server node1 50.28.86.131:443 check inter 10s fall 5 rise 3
```

#### WebSocket 连接断开

**问题：** 未正确配置 WebSocket 升级

**解决：**
```nginx
location /explorer {
    proxy_pass https://rustchain_nodes;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400s;  # 长时间连接
}
```

### 2. 调试命令

```bash
# 测试 NGINX 配置
sudo nginx -t

# 测试 HAProxy 配置
sudo haproxy -c -f /etc/haproxy/haproxy.cfg

# 检查后端节点连通性
curl -sk https://50.28.86.131/health | jq .
curl -sk https://50.28.86.153/health | jq .
curl -sk https://76.8.228.245/health | jq .

# 测试负载均衡
for i in {1..10}; do
    curl -sk https://rustchain.example.com/health
done

# 查看 NGINX 错误日志
sudo tail -f /var/log/nginx/rustchain_error.log

# 查看 HAProxy 日志
sudo tail -f /var/log/haproxy.log

# 检查连接数
sudo netstat -an | grep :443 | wc -l

# 查看 HAProxy 统计
echo "show stat" | sudo socat stdio /run/haproxy/admin.sock | cut -d',' -f1,2,18
```

### 3. 性能调优

#### NGINX 优化

```nginx
# 增加 worker 进程
worker_processes auto;

events {
    worker_connections 4096;
    multi_accept on;
    use epoll;
}

http {
    # 开启 sendfile
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    
    # 保持连接
    keepalive_timeout 65;
    keepalive_requests 100;
    
    # 代理缓冲
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
    
    # 连接池
    upstream rustchain_nodes {
        least_conn;
        server 50.28.86.131:443;
        server 50.28.86.153:443;
        server 76.8.228.245:443;
        
        # 保持连接到后端
        keepalive 32;
    }
}
```

#### HAProxy 优化

```haproxy
global
    # 增加最大连接数
    maxconn 4096
    
    # 调整缓冲区
    tune.bufsize 16384
    tune.maxrewrite 1024

defaults
    # 优化超时设置
    timeout connect 3s
    timeout client 30s
    timeout server 30s
    
    # 启用 HTTP 保持连接
    option http-keep-alive
    option persistent
    timeout http-keep-alive 10s
```

---

## 部署检查清单

### 部署前

- [ ] 确认所有后端节点正常运行
- [ ] 测试每个节点的健康端点
- [ ] 准备 SSL 证书（Let's Encrypt 或自有 CA）
- [ ] 规划域名和 DNS 配置

### 部署中

- [ ] 安装负载均衡软件（NGINX/HAProxy）
- [ ] 配置负载均衡参数
- [ ] 配置健康检查
- [ ] 配置 SSL/TLS
- [ ] 测试配置语法
- [ ] 启动服务

### 部署后

- [ ] 验证负载均衡功能
- [ ] 测试故障转移
- [ ] 配置监控和告警
- [ ] 设置日志轮转
- [ ] 文档化配置
- [ ] 制定应急预案

---

## 最佳实践

### 1. 安全

- 使用强加密套件（TLS 1.2+）
- 启用速率限制防止 DDoS
- 配置防火墙仅开放必要端口
- 定期更新负载均衡软件
- 启用访问日志审计

### 2. 性能

- 根据实际流量调整 worker 进程数
- 启用连接保持（keepalive）
- 配置适当的缓冲区和超时
- 使用最少连接算法
- 实施缓存策略（如果适用）

### 3. 可用性

- 至少部署 2 个负载均衡器（主备）
- 配置健康检查自动故障转移
- 设置合理的超时和重试
- 实施灰度发布策略
- 定期演练故障场景

### 4. 监控

- 实时监控节点健康状态
- 跟踪请求延迟和错误率
- 设置告警阈值
- 保留足够的日志历史
- 定期审查性能指标

---

## 参考资源

- [NGINX 官方文档](https://nginx.org/en/docs/)
- [HAProxy 官方文档](https://www.haproxy.org/documentation/)
- [RustChain API 文档](https://github.com/Scottcjn/RustChain/blob/main/docs/API.md)
- [Let's Encrypt SSL 证书](https://letsencrypt.org/)
- [Prometheus 监控](https://prometheus.io/)

---

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2026-03-12 | 初始版本，包含 NGINX 和 HAProxy 部署方案 |

---

**作者：** 牛 2（Subagent）  
**审核状态：** 待审核  
**PR 链接：** 待提交
