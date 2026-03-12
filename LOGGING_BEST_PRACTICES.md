# RustChain Logging Best Practices

> **Bounty:** #1680 - 3 RTC  
> **Status:** Complete  
> **Author:** AI Contributor

---

## Table of Contents

1. [Overview](#overview)
2. [Log Levels](#log-levels)
3. [Log Format](#log-format)
4. [Log Rotation](#log-rotation)
5. [Log Analysis](#log-analysis)
6. [Implementation Examples](#implementation-examples)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Proper logging is critical for RustChain nodes and miners. Good logs enable:

- **Debugging**: Quick identification of issues
- **Monitoring**: Real-time health assessment
- **Auditing**: Security and compliance tracking
- **Performance Analysis**: Bottleneck identification

This guide covers logging standards for all RustChain components.

---

## Log Levels

RustChain uses standard syslog severity levels:

| Level | Numeric | When to Use | Example |
|-------|---------|-------------|---------|
| `ERROR` | 3 | Operation failed, requires attention | API endpoint crashed, database connection lost |
| `WARN` | 4 | Unexpected but handled situation | High latency detected, retry attempted |
| `INFO` | 6 | Normal operational messages | Node started, attestation submitted, block validated |
| `DEBUG` | 7 | Detailed diagnostic info | Request payload, query execution time |
| `TRACE` | 8 | Very fine-grained events | Function entry/exit, variable values |

### Level Guidelines

```python
# ERROR - User action needed
logger.error(f"Wallet transfer failed: insufficient balance. Required: {amount}, Available: {balance}")

# WARN - Degraded but functional
logger.warning(f"Node response time {latency_ms}ms exceeds threshold {threshold_ms}ms")

# INFO - State changes
logger.info(f"Attestation submitted for epoch {epoch_id}. Hardware score: {score}")

# DEBUG - Operational details
logger.debug(f"API request: POST /wallet/transfer payload={redact_sensitive(data)}")

# TRACE - Internal flow
logger.trace(f"Entering validate_signature() with key_id={key_id}")
```

### Production Recommendations

| Environment | Recommended Level | Rationale |
|-------------|------------------|-----------|
| Production | `INFO` | Balance between visibility and performance |
| Staging | `DEBUG` | Catch issues before production |
| Development | `TRACE` | Maximum visibility for debugging |
| Troubleshooting | `DEBUG` (temporary) | Enable temporarily to diagnose specific issues |

---

## Log Format

### Structured Logging (JSON)

All RustChain logs MUST use structured JSON format for machine parseability:

```json
{
  "timestamp": "2026-03-12T12:34:56.789Z",
  "level": "INFO",
  "service": "rustchain-node",
  "component": "attestation",
  "message": "Attestation submitted successfully",
  "context": {
    "epoch_id": 15234,
    "miner_id": "miner_abc123",
    "hardware_score": 87.5,
    "node_url": "50.28.86.131:8099"
  },
  "trace_id": "req_7f8a9b2c3d4e5f6g",
  "host": "node-prod-01",
  "version": "1.2.3"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | UTC timestamp with milliseconds |
| `level` | String | Log severity (ERROR, WARN, INFO, DEBUG, TRACE) |
| `service` | String | Service name (rustchain-node, rustchain-miner, etc.) |
| `message` | String | Human-readable description |
| `trace_id` | String | Request/correlation ID for tracing |

### Optional Context Fields

| Field | When to Include |
|-------|-----------------|
| `epoch_id` | Attestation, mining operations |
| `miner_id` | Miner-specific operations |
| `wallet_address` | Balance, transfer operations (redact partial) |
| `error_code` | Error-level logs |
| `stack_trace` | Exception errors |
| `duration_ms` | Performance-sensitive operations |
| `request_id` | API requests |

### Python Implementation

```python
import json
import logging
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "rustchain-miner",
            "component": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, 'trace_id', None),
            "host": socket.gethostname(),
        }
        
        # Add context if present
        if hasattr(record, 'context'):
            log_entry["context"] = record.context
        
        # Add stack trace for errors
        if record.exc_info:
            log_entry["stack_trace"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

# Usage
logger = logging.getLogger('rustchain.attestation')
handler = logging.FileHandler('rustchain.log')
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Log with context
logger.info(
    "Attestation submitted",
    extra={
        'trace_id': 'req_abc123',
        'context': {
            'epoch_id': 15234,
            'hardware_score': 87.5
        }
    }
)
```

---

## Log Rotation

### Why Rotation Matters

- Prevents disk space exhaustion
- Enables log archival and retention policies
- Improves log search performance

### Configuration (Linux/systemd)

#### Option 1: logrotate

Create `/etc/logrotate.d/rustchain`:

```bash
/var/log/rustchain/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 rustchain rustchain
    postrotate
        systemctl kill -s HUP rustchain-node.service
    endscript
}
```

| Directive | Purpose |
|-----------|---------|
| `daily` | Rotate every day |
| `rotate 14` | Keep 14 days of logs |
| `compress` | Gzip old logs |
| `delaycompress` | Compress on next rotation (allows tailing) |
| `postrotate` | Reload service to use new file |

#### Option 2: Python Logging Handlers

```python
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Size-based rotation (100MB per file, keep 10 files)
size_handler = RotatingFileHandler(
    'rustchain.log',
    maxBytes=100*1024*1024,  # 100MB
    backupCount=10
)

# Time-based rotation (daily, keep 30 days)
time_handler = TimedRotatingFileHandler(
    'rustchain.log',
    when='D',
    interval=1,
    backupCount=30
)
```

### Docker Logging

For Docker deployments, use Docker's built-in rotation:

```yaml
# docker-compose.yml
services:
  rustchain-node:
    image: rustchain/node:latest
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"
```

### Retention Policy

| Log Type | Retention | Rationale |
|----------|-----------|-----------|
| ERROR | 90 days | Compliance, incident investigation |
| WARN | 30 days | Trend analysis |
| INFO | 14 days | Operational monitoring |
| DEBUG/TRACE | 7 days (or less) | Debugging, high volume |

---

## Log Analysis

### Real-Time Monitoring

#### Grep Patterns for Common Issues

```bash
# Critical errors in last hour
grep '"level": "ERROR"' rustchain.log | grep "$(date -d '1 hour ago' +%Y-%m-%dT%H)"

# High latency warnings
grep '"latency_ms"' rustchain.log | jq -r 'select(.context.latency_ms > 1000) | .message'

# Failed attestations
grep -E '"attestation.*failed|failed.*attestation' rustchain.log

# Wallet-related errors
grep '"component": "wallet"' rustchain.log | grep '"level": "ERROR"'
```

#### Live Tail with Filtering

```bash
# Watch errors in real-time
tail -f rustchain.log | jq -r 'select(.level == "ERROR") | "\(.timestamp) [\(.component)] \(.message)"'

# Monitor specific miner
tail -f rustchain.log | jq -r 'select(.context.miner_id == "miner_abc123") | .message'
```

### Aggregation Tools

#### Option 1: ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# logstash.conf
input {
  file {
    path => "/var/log/rustchain/*.log"
    start_position => "beginning"
    codec => json
  }
}

filter {
  date {
    match => ["timestamp", "ISO8601"]
  }
  
  if [level] == "ERROR" {
    mutate {
      add_tag => ["critical"]
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "rustchain-logs-%{+YYYY.MM.dd}"
  }
}
```

#### Option 2: Grafana Loki (Lightweight)

```yaml
# promtail config
scrape_configs:
  - job_name: rustchain
    static_configs:
      - targets:
          - localhost
        labels:
          job: rustchain
          __path__: /var/log/rustchain/*.log
```

#### Option 3: Simple Python Analyzer

```python
#!/usr/bin/env python3
"""Analyze RustChain logs for common patterns."""

import json
from collections import Counter
from datetime import datetime

def analyze_logs(log_file):
    errors = []
    latency_samples = []
    attestation_count = 0
    
    with open(log_file, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                
                # Count errors
                if entry['level'] == 'ERROR':
                    errors.append(entry)
                
                # Collect latency
                if 'context' in entry and 'latency_ms' in entry['context']:
                    latency_samples.append(entry['context']['latency_ms'])
                
                # Count attestations
                if 'attestation' in entry.get('message', '').lower():
                    attestation_count += 1
                    
            except json.JSONDecodeError:
                continue
    
    # Report
    print(f"=== RustChain Log Analysis ===")
    print(f"Total Errors: {len(errors)}")
    print(f"Attestations: {attestation_count}")
    
    if latency_samples:
        avg_latency = sum(latency_samples) / len(latency_samples)
        max_latency = max(latency_samples)
        print(f"Avg Latency: {avg_latency:.2f}ms")
        print(f"Max Latency: {max_latency}ms")
    
    # Top error messages
    if errors:
        error_counts = Counter(e['message'] for e in errors)
        print("\nTop Errors:")
        for msg, count in error_counts.most_common(5):
            print(f"  [{count}x] {msg}")

if __name__ == '__main__':
    analyze_logs('rustchain.log')
```

### Alerting Rules

Set up alerts for these conditions:

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Error rate | > 10 errors/min | Page on-call |
| Failed attestations | > 3 in 5 min | Investigate node connectivity |
| High latency | > 2000ms avg | Check network, node health |
| Disk space | Log partition > 80% | Rotate/archive logs |
| Service restart | Any restart | Review error logs before restart |

Example Prometheus alert rule:

```yaml
# prometheus_alerts.yml
groups:
  - name: rustchain
    rules:
      - alert: HighErrorRate
        expr: rate(rustchain_logs_total{level="ERROR"}[5m]) > 0.166
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate in RustChain"
          description: "Error rate is {{ $value }} errors/sec"
```

---

## Implementation Examples

### Miner Logging

```python
import logging
from contextlib import contextmanager

logger = logging.getLogger('rustchain.miner')

class Miner:
    def __init__(self, wallet_name, node_url):
        self.wallet_name = wallet_name
        self.node_url = node_url
        logger.info(
            "Miner initialized",
            extra={
                'context': {
                    'wallet_name': wallet_name,
                    'node_url': self._redact_url(node_url)
                }
            }
        )
    
    def submit_attestation(self, epoch_id, hardware_data):
        try:
            logger.debug(
                f"Preparing attestation for epoch {epoch_id}",
                extra={'context': {'epoch_id': epoch_id}}
            )
            
            response = self._send_attestation(hardware_data)
            
            logger.info(
                "Attestation submitted successfully",
                extra={
                    'context': {
                        'epoch_id': epoch_id,
                        'hardware_score': response.score,
                        'response_time_ms': response.latency
                    }
                }
            )
            return response
            
        except ConnectionError as e:
            logger.error(
                f"Failed to submit attestation: connection lost",
                extra={
                    'context': {
                        'epoch_id': epoch_id,
                        'node_url': self._redact_url(self.node_url),
                        'error_code': 'CONNECTION_FAILED'
                    },
                    'exc_info': True
                }
            )
            raise
    
    def _redact_url(self, url):
        """Redact sensitive parts of URL for logging."""
        return url.split('@')[-1] if '@' in url else url

@contextmanager
def log_operation(operation_name, **context):
    """Context manager for logging operation duration."""
    start = datetime.now()
    logger.debug(f"Starting {operation_name}", extra={'context': context})
    try:
        yield
        duration = (datetime.now() - start).total_seconds() * 1000
        logger.info(
            f"{operation_name} completed",
            extra={'context': {**context, 'duration_ms': duration}}
        )
    except Exception as e:
        duration = (datetime.now() - start).total_seconds() * 1000
        logger.error(
            f"{operation_name} failed: {str(e)}",
            extra={'context': {**context, 'duration_ms': duration}, 'exc_info': True}
        )
        raise

# Usage
with log_operation("balance_check", wallet=wallet_name):
    balance = get_balance(wallet_name)
```

### Node API Logging

```python
from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid

app = FastAPI()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                'trace_id': request_id,
                'context': {
                    'method': request.method,
                    'path': request.url.path,
                    'client_ip': request.client.host
                }
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Request completed: {response.status_code}",
            extra={
                'trace_id': request_id,
                'context': {
                    'status_code': response.status_code,
                    'duration_ms': round(duration_ms, 2)
                }
            }
        )
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = request_id
        return response

app.add_middleware(LoggingMiddleware)

@app.post("/wallet/transfer")
async def transfer_wallet(request: TransferRequest):
    logger.debug(
        "Transfer request received",
        extra={
            'context': {
                'from_wallet': redact_wallet(request.from_address),
                'to_wallet': redact_wallet(request.to_address),
                'amount': request.amount
            }
        }
    )
    # ... implementation
```

---

## Troubleshooting

### Common Issues

#### 1. Logs Not Appearing

**Symptoms:** Application running but no logs written

**Checks:**
```bash
# Verify log directory permissions
ls -la /var/log/rustchain/

# Check if process can write
sudo -u rustchain touch /var/log/rustchain/test.log

# Verify log level
grep -i "log.*level" config.yaml
```

**Fix:**
```bash
# Fix permissions
sudo chown -R rustchain:rustchain /var/log/rustchain
sudo chmod 755 /var/log/rustchain

# Restart service
sudo systemctl restart rustchain-node
```

#### 2. Disk Space Exhausted

**Symptoms:** No new logs, disk full alert

**Checks:**
```bash
# Check log sizes
du -sh /var/log/rustchain/*

# Find largest log files
find /var/log -name "*.log" -exec du -h {} \; | sort -rh | head -10
```

**Fix:**
```bash
# Manual rotation
sudo logrotate -f /etc/logrotate.d/rustchain

# Clear old logs (keep last 7 days)
find /var/log/rustchain -name "*.log.*.gz" -mtime +7 -delete

# Verify logrotate is working
sudo logrotate -d /etc/logrotate.d/rustchain
```

#### 3. Performance Impact from Logging

**Symptoms:** High CPU, slow responses when logging enabled

**Checks:**
```bash
# Check log volume
wc -l /var/log/rustchain/*.log

# Monitor write rate
iostat -x 1 | grep -E "Device|sda"
```

**Fix:**
```bash
# Reduce log level temporarily
# Edit config: log_level: WARN

# Sample high-volume debug logs
# Only log every Nth debug message

# Async logging (if supported)
# Use QueueHandler + QueueListener pattern
```

#### 4. Missing Context in Logs

**Symptoms:** Logs present but hard to debug

**Fix:**
```python
# Before (bad)
logger.info("Transfer failed")

# After (good)
logger.info(
    "Transfer failed: insufficient balance",
    extra={
        'context': {
            'from_wallet': redact(wallet_from),
            'to_wallet': redact(wallet_to),
            'required_amount': amount,
            'available_balance': balance,
            'shortfall': amount - balance
        }
    }
)
```

### Debug Checklist

When investigating issues:

- [ ] Check ERROR logs first
- [ ] Look for patterns (time, component, operation type)
- [ ] Correlate with metrics (CPU, memory, network)
- [ ] Review logs before/after the incident window
- [ ] Check for service restarts
- [ ] Verify log timestamps are synchronized (NTP)
- [ ] Search for related trace_ids across services

---

## Appendix: Quick Reference

### Environment Variables

```bash
# Log level
export RUSTCHAIN_LOG_LEVEL=INFO

# Log file location
export RUSTCHAIN_LOG_FILE=/var/log/rustchain/node.log

# Enable JSON formatting
export RUSTCHAIN_LOG_FORMAT=json

# Log rotation size (MB)
export RUSTCHAIN_LOG_MAX_SIZE=100

# Number of rotated files to keep
export RUSTCHAIN_LOG_BACKUP_COUNT=14
```

### Systemd Service with Logging

```ini
# /etc/systemd/system/rustchain-node.service
[Unit]
Description=RustChain Node
After=network.target

[Service]
Type=simple
User=rustchain
Group=rustchain
WorkingDirectory=/opt/rustchain
ExecStart=/opt/rustchain/venv/bin/python -m rustchain.node
Environment=LOG_LEVEL=INFO
Environment=LOG_FILE=/var/log/rustchain/node.log
Restart=always
StandardOutput=journal
StandardError=journal

# Log rotation signal
ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
```

### One-Liner Health Check

```bash
# Check for errors in last 1000 lines
tail -1000 /var/log/rustchain/node.log | jq -r 'select(.level == "ERROR") | "\(.timestamp): \(.message)"' | head -20
```

---

## Contributing

Found an issue or have suggestions? Open a PR to this guide.

**License:** Same as RustChain project  
**Version:** 1.0.0  
**Last Updated:** 2026-03-12
