# RustChain Python SDK 教程

> 本教程帮助你使用 Python 快速与 RustChain 网络交互——查询余额、提交证明、管理 Epoch 注册。

---

## 目录

- [环境准备](#环境准备)
- [安装依赖](#安装依赖)
- [初始化客户端](#初始化客户端)
- [健康检查](#健康检查)
- [查询网络统计](#查询网络统计)
- [查询余额](#查询余额)
- [Epoch 管理](#epoch-管理)
- [挖矿流程](#挖矿流程)
- [完整示例：自动化矿工脚本](#完整示例自动化矿工脚本)
- [错误处理最佳实践](#错误处理最佳实践)

---

## 环境准备

- Python 3.8+
- pip 包管理器
- 网络访问 `https://50.28.86.131`

## 安装依赖

```bash
pip install requests
```

> RustChain 暂无官方 SDK，我们用 `requests` 直接调用 REST API。

---

## 初始化客户端

```python
import requests
import urllib3

# 禁用自签名证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://50.28.86.131"

def api_get(path: str):
    """发送 GET 请求"""
    resp = requests.get(f"{BASE_URL}{path}", verify=False, timeout=30)
    resp.raise_for_status()
    return resp.json()

def api_post(path: str, data: dict):
    """发送 POST 请求"""
    resp = requests.post(f"{BASE_URL}{path}", json=data, verify=False, timeout=30)
    resp.raise_for_status()
    return resp.json()
```

---

## 健康检查

```python
def check_health():
    """检查节点是否在线"""
    result = api_get("/health")
    print(f"状态: {result['status']}")
    print(f"运行时间: {result['uptime_seconds']}秒")
    return result

# 使用
check_health()
```

---

## 查询网络统计

```python
def get_stats():
    """获取网络统计"""
    stats = api_get("/api/stats")
    print(f"当前 Epoch: {stats['current_epoch']}")
    print(f"活跃矿工: {stats['active_miners']}")
    print(f"区块高度: {stats['block_height']}")
    print(f"网络算力: {stats['network_hashrate']}")
    return stats

# 使用
stats = get_stats()
```

---

## 查询余额

```python
def get_balance(miner_pk: str):
    """查询矿工 RTC 余额"""
    result = api_get(f"/balance/{miner_pk}")
    print(f"可用余额: {result['available']} RTC")
    print(f"待确认: {result['pending']} RTC")
    print(f"总收益: {result['total_earned']} RTC")
    return result

# 使用
balance = get_balance("RTCM1n3Y...YOUR_PUBLIC_KEY")
```

---

## Epoch 管理

### 查询当前 Epoch

```python
def get_current_epoch():
    """获取当前 Epoch 信息"""
    epoch = api_get("/epoch")
    print(f"Epoch #{epoch['epoch_number']}")
    print(f"注册矿工: {epoch['enrolled_miners']}")
    print(f"状态: {epoch['status']}")
    return epoch
```

### 注册 Epoch

```python
def enroll_epoch(miner_pk: str, hw_type: str, hw_model: str):
    """注册当前 Epoch"""
    result = api_post("/epoch/enroll", {
        "miner_pk": miner_pk,
        "hardware_type": hw_type,
        "hardware_model": hw_model
    })
    print(f"注册成功! Epoch {result['epoch']}, 槽位 {result['slot_index']}")
    return result

# 使用
enroll_epoch("RTCM1n3Y...KEY", "PowerPC", "PowerMac G5")
```

---

## 挖矿流程

挖矿分两步：获取挑战 → 提交证明。

### 步骤 1: 获取挑战

```python
def get_challenge(miner_pk: str, hw_type: str, hw_model: str):
    """请求硬件证明挑战"""
    result = api_post("/attest/challenge", {
        "miner_pk": miner_pk,
        "hardware_type": hw_type,
        "hardware_model": hw_model
    })
    print(f"挑战 ID: {result['challenge_id']}")
    print(f"难度: {result['difficulty']}")
    print(f"有效期: {result['expires_in']}秒")
    return result
```

### 步骤 2: 提交证明

```python
def submit_proof(challenge_id: str, miner_pk: str, proof: str, signature: str):
    """提交硬件证明"""
    result = api_post("/attest/submit", {
        "challenge_id": challenge_id,
        "miner_pk": miner_pk,
        "proof": proof,
        "signature": signature
    })
    print(f"状态: {result['status']}")
    if result.get("reward"):
        print(f"获得奖励: {result['reward']} RTC")
    return result
```

---

## 完整示例：自动化矿工脚本

```python
import time
import hashlib

MINER_PK = "RTCM1n3Y...YOUR_PUBLIC_KEY"
HW_TYPE = "PowerPC"
HW_MODEL = "PowerMac G5"

def compute_proof(challenge):
    """
    在真实硬件上计算证明。
    这里仅作演示，实际需要调用硬件特定的计算逻辑。
    """
    data = f"{challenge['nonce']}:{MINER_PK}:{challenge['challenge_id']}"
    proof = hashlib.sha256(data.encode()).hexdigest()
    return f"0x{proof}"

def mine_once():
    """执行一次完整的挖矿流程"""
    try:
        # 1. 获取挑战
        challenge = get_challenge(MINER_PK, HW_TYPE, HW_MODEL)

        # 2. 计算证明（需要在真实硬件上执行）
        proof = compute_proof(challenge)
        signature = "0x...your_signature"  # 用私钥签名

        # 3. 提交证明
        result = submit_proof(
            challenge["challenge_id"],
            MINER_PK,
            proof,
            signature
        )
        return result["status"] == "accepted"
    except requests.exceptions.HTTPError as e:
        print(f"请求失败: {e.response.status_code} - {e.response.text}")
        return False

def auto_mine(interval: int = 60):
    """自动挖矿循环"""
    print(f"开始自动挖矿，间隔 {interval} 秒...")
    while True:
        success = mine_once()
        status = "✓ 成功" if success else "✗ 失败"
        print(f"[{time.strftime('%H:%M:%S')}] {status}")
        time.sleep(interval)

if __name__ == "__main__":
    auto_mine(interval=60)
```

---

## 错误处理最佳实践

```python
import requests
from requests.exceptions import Timeout, ConnectionError

def safe_api_call(func, *args, retries=3, **kwargs):
    """带重试的安全 API 调用"""
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Timeout:
            print(f"请求超时，重试 {attempt + 1}/{retries}")
        except ConnectionError:
            print(f"连接失败，重试 {attempt + 1}/{retries}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("频率限制，等待 60 秒...")
                time.sleep(60)
            elif e.response.status_code >= 500:
                print(f"服务器错误，重试 {attempt + 1}/{retries}")
            else:
                raise  # 客户端错误不重试
        time.sleep(5 * (attempt + 1))  # 指数退避
    raise Exception(f"API 调用失败，已重试 {retries} 次")
```

---

## 下一步

- 阅读完整 [API Reference](./api-reference.md)
- 了解 [系统架构](./architecture-overview.md)
- 遇到问题查看 [FAQ](./faq-troubleshooting.md)

---

*GitHub: [https://github.com/Scottcjn/Rustchain](https://github.com/Scottcjn/Rustchain)*
