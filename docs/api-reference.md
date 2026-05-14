# RustChain API Reference

> **Base URL:** `https://50.28.86.131`
> **注意：** 服务端使用自签名证书，所有请求需跳过 TLS 验证（curl 加 `-k`，Python 加 `verify=False`）。

---

## 目录

- [健康检查](#健康检查)
- [系统统计](#系统统计)
- [Epoch 信息](#epoch-信息)
- [查询余额](#查询余额)
- [获取证明挑战](#获取证明挑战)
- [提交证明](#提交证明)
- [Epoch 注册](#epoch-注册)
- [通用错误码](#通用错误码)

---

## 健康检查

检查节点是否在线运行。

```
GET /health
```

### 示例

**curl**

```bash
curl -k https://50.28.86.131/health
```

**Python**

```python
import requests

resp = requests.get("https://50.28.86.131/health", verify=False)
print(resp.json())
```

### 响应

```json
{
  "status": "ok",
  "uptime_seconds": 86400,
  "version": "0.1.0"
}
```

---

## 系统统计

返回整个网络的统计信息。

```
GET /api/stats
```

### 示例

**curl**

```bash
curl -k https://50.28.86.131/api/stats
```

**Python**

```python
resp = requests.get("https://50.28.86.131/api/stats", verify=False)
stats = resp.json()
print(f"当前 Epoch: {stats['current_epoch']}")
print(f"活跃矿工: {stats['active_miners']}")
```

### 响应

```json
{
  "current_epoch": 42,
  "active_miners": 128,
  "total_supply": "21000000",
  "circulating_supply": "8450000",
  "block_height": 31050,
  "network_hashrate": "1.2 TH/s"
}
```

---

## Epoch 信息

获取当前 Epoch 详细信息，包括起止时间和注册矿工数。

```
GET /epoch
```

### 示例

**curl**

```bash
curl -k https://50.28.86.131/epoch
```

**Python**

```python
resp = requests.get("https://50.28.86.131/epoch", verify=False)
epoch = resp.json()
print(f"Epoch #{epoch['epoch_number']} 结束于 {epoch['end_time']}")
```

### 响应

```json
{
  "epoch_number": 42,
  "start_time": "2026-05-13T00:00:00Z",
  "end_time": "2026-05-20T00:00:00Z",
  "enrolled_miners": 95,
  "status": "active"
}
```

---

## 查询余额

根据矿工公钥查询 RTC 挖矿余额。

```
GET /balance/{miner_pk}
```

### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `miner_pk` | string | 矿工公钥（Base58 编码） |

### 示例

**curl**

```bash
curl -k https://50.28.86.131/balance/RTCM1n3Y...YOUR_PUBLIC_KEY
```

**Python**

```python
miner_pk = "RTCM1n3Y...YOUR_PUBLIC_KEY"
resp = requests.get(f"https://50.28.86.131/balance/{miner_pk}", verify=False)
balance = resp.json()
print(f"可提余额: {balance['available']} RTC")
```

### 响应

```json
{
  "miner_pk": "RTCM1n3Y...",
  "available": "125.50",
  "pending": "12.00",
  "total_earned": "137.50",
  "unit": "RTC"
}
```

---

## 获取证明挑战

向网络请求一个硬件证明挑战。矿工需在真实硬件上执行挑战并提交结果。

```
POST /attest/challenge
```

### 请求体

```json
{
  "miner_pk": "RTCM1n3Y...YOUR_PUBLIC_KEY",
  "hardware_type": "PowerPC",
  "hardware_model": "PowerMac G5"
}
```

### 示例

**curl**

```bash
curl -k -X POST https://50.28.86.131/attest/challenge \
  -H "Content-Type: application/json" \
  -d '{"miner_pk":"RTCM1n3Y...KEY","hardware_type":"PowerPC","hardware_model":"PowerMac G5"}'
```

**Python**

```python
payload = {
    "miner_pk": "RTCM1n3Y...YOUR_PUBLIC_KEY",
    "hardware_type": "PowerPC",
    "hardware_model": "PowerMac G5"
}
resp = requests.post("https://50.28.86.131/attest/challenge", json=payload, verify=False)
challenge = resp.json()
print(f"挑战 ID: {challenge['challenge_id']}")
print(f"有效期: {challenge['expires_in']}秒")
```

### 响应

```json
{
  "challenge_id": "ch_abc123",
  "nonce": "0xdeadbeef",
  "algorithm": "sha256",
  "difficulty": 4,
  "expires_in": 300
}
```

---

## 提交证明

将硬件证明结果提交给网络验证。

```
POST /attest/submit
```

### 请求体

```json
{
  "challenge_id": "ch_abc123",
  "miner_pk": "RTCM1n3Y...YOUR_PUBLIC_KEY",
  "proof": "0x...computed_proof_hex",
  "signature": "0x...signature_hex"
}
```

### 示例

**curl**

```bash
curl -k -X POST https://50.28.86.131/attest/submit \
  -H "Content-Type: application/json" \
  -d '{"challenge_id":"ch_abc123","miner_pk":"RTCM1n3Y...KEY","proof":"0x...","signature":"0x..."}'
```

**Python**

```python
payload = {
    "challenge_id": "ch_abc123",
    "miner_pk": "RTCM1n3Y...YOUR_PUBLIC_KEY",
    "proof": "0x...computed_proof_hex",
    "signature": "0x...signature_hex"
}
resp = requests.post("https://50.28.86.131/attest/submit", json=payload, verify=False)
result = resp.json()
print(f"验证状态: {result['status']}")
```

### 响应

```json
{
  "status": "accepted",
  "reward": "0.5",
  "epoch": 42,
  "message": "Proof accepted, reward credited"
}
```

---

## Epoch 注册

为当前 Epoch 注册矿工身份。每个 Epoch 需重新注册。

```
POST /epoch/enroll
```

### 请求体

```json
{
  "miner_pk": "RTCM1n3Y...YOUR_PUBLIC_KEY",
  "hardware_type": "SPARC",
  "hardware_model": "Sun Ultra 45"
}
```

### 示例

**curl**

```bash
curl -k -X POST https://50.28.86.131/epoch/enroll \
  -H "Content-Type: application/json" \
  -d '{"miner_pk":"RTCM1n3Y...KEY","hardware_type":"SPARC","hardware_model":"Sun Ultra 45"}'
```

**Python**

```python
payload = {
    "miner_pk": "RTCM1n3Y...YOUR_PUBLIC_KEY",
    "hardware_type": "SPARC",
    "hardware_model": "Sun Ultra 45"
}
resp = requests.post("https://50.28.86.131/epoch/enroll", json=payload, verify=False)
print(resp.json())
```

### 响应

```json
{
  "status": "enrolled",
  "epoch": 42,
  "slot_index": 73,
  "message": "Successfully enrolled for epoch 42"
}
```

---

## 通用错误码

| HTTP 状态码 | 含义 | 说明 |
|-------------|------|------|
| 200 | 成功 | 请求处理成功 |
| 400 | 请求错误 | 参数缺失或格式错误 |
| 401 | 未授权 | 公钥无效或未注册 |
| 404 | 未找到 | 端点或资源不存在 |
| 409 | 冲突 | 已注册或挑战已过期 |
| 429 | 请求过多 | 触发频率限制 |
| 500 | 服务器错误 | 节点内部错误 |

### 错误响应格式

```json
{
  "error": "challenge_expired",
  "message": "The challenge has expired. Please request a new one.",
  "code": 409
}
```

---

## 支持

- GitHub: [https://github.com/Scottcjn/Rustchain](https://github.com/Scottcjn/Rustchain)
- 共识协议: RIP-200 (Proof of Antiquity)
