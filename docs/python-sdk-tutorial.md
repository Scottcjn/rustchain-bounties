# RustChain Python SDK 完整教程

> 官方 Python SDK — 异步区块链客户端，BIP39 钱包支持，完整 RPC 覆盖

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

---

## 目录

1. [安装指南](#1-安装指南)
2. [快速开始](#2-快速开始)
3. [完整 API 参考](#3-完整-api-参考)
   - [RustChainClient](#31-rustchainclient)
   - [RustChainWallet](#32-rustchainwallet)
   - [BoTTubeClient](#33-bottubeclient)
   - [异常类](#34-异常类)
4. [代码示例](#4-代码示例)
5. [CLI 工具](#5-cli-工具)
6. [错误处理](#6-错误处理)
7. [最佳实践](#7-最佳实践)

---

## 1. 安装指南

### 1.1 基础安装

```bash
pip install rustchain
```

### 1.2 从源码安装

```bash
git clone https://github.com/your-org/rustchain.git
cd rustchain/sdk/python
pip install -e .
```

### 1.3 开发依赖安装

```bash
pip install -e ".[dev]"
```

这会额外安装：
- `pytest>=7.0.0` — 测试框架
- `pytest-asyncio>=0.21.0` — 异步测试支持
- `cryptography>=41.0.0` — 真正的 Ed25519 签名

### 1.4 系统要求

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Python | >= 3.8 | 最低版本 |
| httpx | >= 0.25.0 | 异步 HTTP 客户端 |
| click | >= 8.0.0 | CLI 框架 |

**可选依赖：**
- `cryptography>=41.0.0` — 启用真正的 Ed25519 签名（未安装时使用 HMAC 回退方案）

### 1.5 验证安装

```python
import rustchain_sdk
print(rustchain_sdk.__version__)  # 1.0.0
```

或在命令行：

```bash
rustchain --version
```

---

## 2. 快速开始

### 2.1 连接节点

```python
import asyncio
from rustchain_sdk import RustChainClient

async def main():
    # 使用默认节点
    client = RustChainClient()
    
    # 或指定自定义节点
    # client = RustChainClient("https://your-node.example.com", timeout=60)
    
    async with client:
        health = await client.health()
        print(f"节点状态: {health}")

asyncio.run(main())
```

### 2.2 查询余额

```python
import asyncio
from rustchain_sdk import RustChainClient

async def main():
    async with RustChainClient() as client:
        balance = await client.get_balance("C4c7r9WPsnEe6CUfegMU9M7ReHD1pWg8qeSfTBoRcLbg")
        print(f"余额: {balance.get('balance', 0)} RTC")
        print(f"Nonce: {balance.get('nonce', 0)}")

asyncio.run(main())
```

### 2.3 查询 Epoch 信息

```python
import asyncio
from rustchain_sdk import RustChainClient

async def main():
    async with RustChainClient() as client:
        epoch = await client.get_epoch()
        print(f"当前 Epoch: {epoch}")

asyncio.run(main())
```

### 2.4 创建钱包并转账

```python
import asyncio
from rustchain_sdk import RustChainClient, RustChainWallet

async def main():
    # 创建新钱包
    wallet = RustChainWallet.create()
    print(f"地址: {wallet.address}")
    print(f"助记词: {' '.join(wallet.seed_phrase)}")
    
    # 转账
    async with RustChainClient() as client:
        result = await client.wallet_transfer_with_wallet(
            wallet=wallet,
            to_address="RTCrecipient_address_here",
            amount=1000,
            fee=0,
        )
        print(f"交易结果: {result}")

asyncio.run(main())
```

---

## 3. 完整 API 参考

### 3.1 RustChainClient

异步 HTTP 客户端，提供对 RustChain 网络 RPC API 的完整访问。

#### 构造函数

```python
RustChainClient(base_url="https://50.28.86.131", timeout=30.0)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | `str` | `"https://50.28.86.131"` | RustChain 节点 RPC 端点 URL |
| `timeout` | `float` | `30.0` | 请求超时时间（秒） |

支持异步上下文管理器（`async with`），会自动关闭连接。

#### TLS 证书

客户端会自动检测 `~/.rustchain/node_cert.pem`，若存在则使用该证书进行 TLS 验证，否则使用系统 CA 证书。

---

#### 健康与网络

##### `health()`

检查节点健康状态。

```python
result = await client.health()
```

**参数：** 无

**返回值：** `Dict[str, Any]` — 包含节点健康信息的字典，例如：
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": 12345
}
```

---

##### `get_epoch()`

获取当前 epoch 信息。

```python
result = await client.get_epoch()
```

**参数：** 无

**返回值：** `Dict[str, Any]` — 包含 epoch 编号、起止时间等信息：
```json
{
  "epoch_number": 42,
  "start_time": 1700000000,
  "end_time": 1700086400
}
```

---

##### `get_headers_tip()`

获取当前链头（headers tip）。

```python
result = await client.get_headers_tip()
```

**参数：** 无

**返回值：** `Dict[str, Any]` — 包含区块高度、哈希、时间戳等。

---

#### 矿工与认证

##### `get_miners()`

获取活跃矿工列表。

```python
miners = await client.get_miners()
```

**参数：** 无

**返回值：** `List[Dict[str, Any]]` — 矿工信息字典列表。

---

##### `get_attestation_status(miner_public_key)`

查询矿工的认证状态。

| 参数 | 类型 | 说明 |
|------|------|------|
| `miner_public_key` | `str` | 矿工公钥 |

**返回值：** `Dict[str, Any]` — 认证状态信息。

---

##### `attest_challenge(miner_public_key)`

为矿工请求认证挑战。

| 参数 | 类型 | 说明 |
|------|------|------|
| `miner_public_key` | `str` | 矿工公钥 |

**返回值：** `Dict[str, Any]` — 包含 `challenge` 字符串和过期时间。

---

##### `attest_submit(miner_public_key, challenge_response, signature)`

提交认证响应。

| 参数 | 类型 | 说明 |
|------|------|------|
| `miner_public_key` | `str` | 矿工公钥 |
| `challenge_response` | `str` | 挑战响应字符串 |
| `signature` | `str` | Ed25519 签名（hex 编码） |

**返回值：** `Dict[str, Any]` — 提交结果。

---

##### `get_bounty_multiplier()`

获取当前认证赏金倍率。

```python
result = await client.get_bounty_multiplier()
```

**参数：** 无

**返回值：** `Dict[str, Any]` — 赏金倍率信息。

---

#### 钱包与余额

##### `get_balance(wallet_address)`

根据钱包地址查询余额。

| 参数 | 类型 | 说明 |
|------|------|------|
| `wallet_address` | `str` | RTC 钱包地址 |

**返回值：** `Dict[str, Any]` — 包含 `balance`、`nonce` 等字段。

---

##### `get_wallet_balance(miner_id)`

根据矿工 ID 查询钱包余额。

| 参数 | 类型 | 说明 |
|------|------|------|
| `miner_id` | `str` | 矿工标识符 |

**返回值：** `Dict[str, Any]` — 钱包余额信息。

---

##### `get_wallet_history(wallet_address, limit=50)`

获取钱包交易历史。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `wallet_address` | `str` | — | 钱包地址 |
| `limit` | `int` | `50` | 返回交易数量上限 |

**返回值：** `Dict[str, Any]` — 包含 `transactions` 列表和元数据。

---

##### `wallet_transfer_with_wallet(wallet, to_address, amount, fee=0)`

使用钱包实例构建并提交签名转账。最常用的转账方法。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `wallet` | `RustChainWallet` | — | 发送方钱包实例 |
| `to_address` | `str` | — | 接收方地址 |
| `amount` | `int` | — | 转账金额（最小单位） |
| `fee` | `int` | `0` | 手续费 |

**返回值：** `Dict[str, Any]` — 包含 `tx_hash`、`status` 等。

---

#### 转账

##### `transfer_signed(from_address, to_address, amount, fee, signature, timestamp)`

提交已签名的转账交易（低级 API，通常用 `wallet_transfer_with_wallet` 代替）。

| 参数 | 类型 | 说明 |
|------|------|------|
| `from_address` | `str` | 发送方地址 |
| `to_address` | `str` | 接收方地址 |
| `amount` | `int` | 金额（最小单位） |
| `fee` | `int` | 手续费 |
| `signature` | `str` | Hex 编码的 Ed25519 签名 |
| `timestamp` | `int` | Unix 时间戳 |

**返回值：** `Dict[str, Any]` — 包含 `tx_hash`、`status` 等。

---

#### Beacon

##### `beacon_submit(envelope)`

提交 Beacon 信封。

| 参数 | 类型 | 说明 |
|------|------|------|
| `envelope` | `Dict` | Beacon 信封数据 |

**返回值：** `Dict[str, Any]` — 提交结果。

---

#### 治理

##### `governance_propose(proposer, proposal_type, description, payload)`

提交治理提案。

| 参数 | 类型 | 说明 |
|------|------|------|
| `proposer` | `str` | 提案人钱包地址 |
| `proposal_type` | `str` | 提案类型（如 `"param_change"`、`"treasury"`） |
| `description` | `str` | 人类可读的提案描述 |
| `payload` | `Dict` | 提案特定数据 |

**返回值：** `Dict[str, Any]` — 包含 `proposal_id`。

---

##### `governance_vote(voter, proposal_id, vote, signature)`

对治理提案投票。

| 参数 | 类型 | 说明 |
|------|------|------|
| `voter` | `str` | 投票人钱包地址 |
| `proposal_id` | `int` | 提案 ID |
| `vote` | `str` | 投票选择：`"yes"`、`"no"` 或 `"abstain"` |
| `signature` | `str` | 投票内容的 Ed25519 签名 |

**返回值：** `Dict[str, Any]` — 投票结果。

---

##### `list_governance_proposals(status=None)`

列出治理提案。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `status` | `str` | `None` | 过滤状态：`"active"`、`"passed"`、`"rejected"`、`"executed"` |

**返回值：** `List[Dict[str, Any]]` — 提案列表。

---

#### 浏览器

##### `explorer_blocks(limit=20)`

获取最近区块。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `limit` | `int` | `20` | 返回区块数量 |

**返回值：** `List[Dict[str, Any]]` — 区块列表。

---

##### `explorer_transactions(address=None, limit=20)`

获取交易记录。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `address` | `str` | `None` | 可选地址过滤 |
| `limit` | `int` | `20` | 返回交易数量 |

**返回值：** `List[Dict[str, Any]]` — 交易列表。

---

#### Epoch 奖励

##### `get_epoch_rewards(epoch_number)`

获取指定 epoch 的奖励分配。

| 参数 | 类型 | 说明 |
|------|------|------|
| `epoch_number` | `int` | Epoch 编号 |

**返回值：** `Dict[str, Any]` — 奖励分配信息。

---

### 3.2 RustChainWallet

BIP39 助记词 + Ed25519 签名的钱包管理。

#### 构造与创建

##### `RustChainWallet.create(strength=128)`

创建新钱包。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `strength` | `int` | `128` | 熵强度：`128` = 12 词，`256` = 24 词 |

**返回值：** `RustChainWallet` 实例

**抛出：** `ValueError` — 如果 `strength` 不是 128 或 256

---

##### `RustChainWallet.from_seed_phrase(words)`

从助记词恢复钱包。

| 参数 | 类型 | 说明 |
|------|------|------|
| `words` | `List[str]` | 12 或 24 个助记词 |

**返回值：** `RustChainWallet` 实例

**抛出：** `ValueError` — 如果词数不是 12 或 24

---

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `address` | `str` | RTC 钱包地址（如 `RTC1a2b3c...`） |
| `public_key_hex` | `str` | 公钥的 hex 字符串 |
| `seed_phrase` | `List[str]` | BIP39 助记词（务必保密！） |
| `private_key_hex` | `str` | 私钥的 hex 字符串（务必保密！） |

---

#### 方法

##### `sign(message)`

使用 Ed25519 签名消息。

| 参数 | 类型 | 说明 |
|------|------|------|
| `message` | `bytes` | 要签名的消息字节 |

**返回值：** `bytes` — 64 字节 Ed25519 签名

---

##### `sign_transfer(to_address, amount, fee=0)`

创建签名转账载荷。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `to_address` | `str` | — | 接收方地址 |
| `amount` | `int` | — | 金额（最小单位） |
| `fee` | `int` | `0` | 手续费 |

**返回值：** `Dict[str, Any]` — 包含 `from`、`to`、`amount`、`fee`、`timestamp`、`signature`

---

##### `export()`

导出钱包为 JSON 可序列化字典。

**返回值：** `Dict[str, Any]`
```json
{
  "version": 1,
  "address": "RTC...",
  "seed_phrase": ["word1", "word2", ...],
  "derivation_path": "m/44'/9000'/0'/0/0"
}
```

⚠️ **警告：** 导出包含助记词，务必安全存储！

---

##### `RustChainWallet.import_(data)`

从导出数据恢复钱包。

| 参数 | 类型 | 说明 |
|------|------|------|
| `data` | `Dict[str, Any]` | `export()` 导出的字典 |

**返回值：** `RustChainWallet` 实例

---

### 3.3 BoTTubeClient

BoTTube 视频平台 API 客户端（同步，基于 `urllib`）。

#### 构造函数

```python
BoTTubeClient(api_key=None, base_url="https://bottube.ai", verify_ssl=True, timeout=30, retry_count=3, retry_delay=1.0)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | `Optional[str]` | `None` | API 密钥（公开端点可省略） |
| `base_url` | `str` | `"https://bottube.ai"` | API 基础 URL |
| `verify_ssl` | `bool` | `True` | 启用 SSL 验证 |
| `timeout` | `int` | `30` | 请求超时（秒） |
| `retry_count` | `int` | `3` | 重试次数 |
| `retry_delay` | `float` | `1.0` | 重试间隔（秒） |

#### 方法总览

| 方法 | 说明 | 需要认证 |
|------|------|----------|
| `health()` | API 健康检查 | ❌ |
| `videos(agent, limit, cursor)` | 列出视频 | ❌ |
| `feed(cursor, limit)` | 获取视频流 | ❌ |
| `video(video_id)` | 获取单个视频详情 | ❌ |
| `upload(title, description, video_file, ...)` | 上传视频 | ✅ |
| `upload_metadata_only(title, description, ...)` | 验证上传元数据 | ✅ |
| `agent_profile(agent_id)` | 获取 Agent 资料 | ❌ |
| `analytics(video_id, agent_id)` | 获取分析数据 | ✅ |
| `feed_rss(limit, agent, cursor)` | RSS 2.0 格式 Feed | ❌ |
| `feed_atom(limit, agent, cursor)` | Atom 1.0 格式 Feed | ❌ |
| `feed_json(limit, agent, cursor)` | JSON Feed 1.1 格式 | ❌ |

---

### 3.4 异常类

所有异常继承自 `RustChainError`。

```
RustChainError (基类)
├── ConnectionError        — 节点连接失败
├── APIError               — API 返回错误（非 2xx）
├── AuthenticationError    — 认证/授权失败
├── ValidationError        — 输入验证失败
├── WalletError            — 钱包操作失败
├── AttestationError       — 认证流程失败
├── GovernanceError        — 治理操作失败
├── HealthError            — 健康检查失败
├── EpochError             — Epoch 操作失败
├── TransferError          — 转账失败
└── RPCError               — 通用 RPC 调用失败
```

`APIError` 额外属性：
- `status_code: Optional[int]` — HTTP 状态码
- `response_body: Optional[Dict]` — 响应体

`RPCError` 额外属性：
- `method: str` — RPC 方法名

---

## 4. 代码示例

### 示例 1：节点健康检查

```python
import asyncio
from rustchain_sdk import RustChainClient

async def check_node():
    async with RustChainClient() as client:
        health = await client.health()
        status = health.get("status", "unknown")
        if status == "ok":
            print(f"✅ 节点正常运行 (版本: {health.get('version', 'unknown')})")
        else:
            print(f"⚠️ 节点状态异常: {status}")

asyncio.run(check_node())
```

### 示例 2：查询多个钱包余额

```python
import asyncio
from rustchain_sdk import RustChainClient

ADDRESSES = [
    "C4c7r9WPsnEe6CUfegMU9M7ReHD1pWg8qeSfTBoRcLbg",
    "AnotherAddressHere",
]

async def check_balances():
    async with RustChainClient() as client:
        for addr in ADDRESSES:
            result = await client.get_balance(addr)
            balance = result.get("balance", 0)
            nonce = result.get("nonce", 0)
            print(f"{addr[:16]}... → 余额: {balance} RTC, Nonce: {nonce}")

asyncio.run(check_balances())
```

### 示例 3：创建并导出钱包

```python
from rustchain_sdk import RustChainWallet
import json

# 创建 12 词钱包（默认）
wallet = RustChainWallet.create()
print(f"地址: {wallet.address}")
print(f"公钥: {wallet.public_key_hex}")
print(f"助记词: {' '.join(wallet.seed_phrase)}")

# 导出并保存到文件
exported = wallet.export()
with open("wallet_backup.json", "w") as f:
    json.dump(exported, f, indent=2)

print("✅ 钱包已导出到 wallet_backup.json")
```

### 示例 4：从助记词恢复钱包

```python
import json
from rustchain_sdk import RustChainWallet

# 从备份文件恢复
with open("wallet_backup.json") as f:
    data = json.load(f)

wallet = RustChainWallet.import_(data)
print(f"恢复地址: {wallet.address}")

# 或直接从助记词列表恢复
words = ["abandon", "ability", "able", "about", "above", "absent",
         "absorb", "abstract", "absurd", "abuse", "access", "accident"]
wallet2 = RustChainWallet.from_seed_phrase(words)
print(f"从助记词恢复: {wallet2.address}")
```

### 示例 5：签名转账

```python
import asyncio
from rustchain_sdk import RustChainClient, RustChainWallet

async def send_rtc():
    # 从助记词恢复钱包
    wallet = RustChainWallet.from_seed_phrase(
        ["your", "seed", "words", "here", "..."]
    )
    
    async with RustChainClient() as client:
        # 检查余额
        balance = await client.get_balance(wallet.address)
        print(f"当前余额: {balance.get('balance', 0)} RTC")
        
        # 发送转账
        result = await client.wallet_transfer_with_wallet(
            wallet=wallet,
            to_address="RTCrecipient_address_here",
            amount=1000,
            fee=0,
        )
        print(f"交易哈希: {result.get('tx_hash', 'unknown')}")
        print(f"状态: {result.get('status', 'unknown')}")

asyncio.run(send_rtc())
```

### 示例 6：查询 Epoch 和奖励

```python
import asyncio
from rustchain_sdk import RustChainClient

async def epoch_info():
    async with RustChainClient() as client:
        # 当前 epoch
        epoch = await client.get_epoch()
        print(f"当前 Epoch: {epoch}")
        
        # 查询奖励
        epoch_num = epoch.get("epoch_number", 0)
        rewards = await client.get_epoch_rewards(epoch_num)
        print(f"Epoch {epoch_num} 奖励: {rewards}")

asyncio.run(epoch_info())
```

### 示例 7：矿工列表与认证

```python
import asyncio
from rustchain_sdk import RustChainClient

async def miner_ops():
    async with RustChainClient() as client:
        # 列出活跃矿工
        miners = await client.get_miners()
        print(f"活跃矿工数: {len(miners)}")
        for m in miners[:5]:
            print(f"  - {m}")
        
        # 查询第一个矿工的认证状态
        if miners:
            pubkey = miners[0].get("public_key", "")
            if pubkey:
                status = await client.get_attestation_status(pubkey)
                print(f"认证状态: {status}")
        
        # 查询赏金倍率
        bounty = await client.get_bounty_multiplier()
        print(f"当前赏金倍率: {bounty}")

asyncio.run(miner_ops())
```

### 示例 8：治理提案与投票

```python
import asyncio
from rustchain_sdk import RustChainClient, RustChainWallet

async def governance_demo():
    wallet = RustChainWallet.from_seed_phrase(
        ["your", "seed", "words", "here", "..."]
    )
    
    async with RustChainClient() as client:
        # 列出活跃提案
        proposals = await client.list_governance_proposals(status="active")
        print(f"活跃提案数: {len(proposals)}")
        
        # 提交新提案
        proposal = await client.governance_propose(
            proposer=wallet.address,
            proposal_type="param_change",
            description="Adjust block reward from 50 to 75 RTC",
            payload={"param": "block_reward", "new_value": 75},
        )
        print(f"新提案 ID: {proposal.get('proposal_id')}")
        
        # 对提案投票
        vote_payload = f"{wallet.address}:1:yes".encode()
        signature = wallet.sign(vote_payload).hex()
        
        vote_result = await client.governance_vote(
            voter=wallet.address,
            proposal_id=1,
            vote="yes",
            signature=signature,
        )
        print(f"投票结果: {vote_result}")

asyncio.run(governance_demo())
```

### 示例 9：区块链浏览器

```python
import asyncio
from rustchain_sdk import RustChainClient

async def explore():
    async with RustChainClient() as client:
        # 获取链头
        tip = await client.get_headers_tip()
        print(f"链头: {tip}")
        
        # 最近 5 个区块
        blocks = await client.explorer_blocks(limit=5)
        print(f"\n最近区块:")
        for block in blocks:
            print(f"  高度: {block.get('height')}, 哈希: {block.get('hash', '')[:16]}...")
        
        # 最近交易
        txs = await client.explorer_transactions(limit=5)
        print(f"\n最近交易:")
        for tx in txs:
            print(f"  {tx.get('from', '')[:12]}... → {tx.get('to', '')[:12]}... "
                  f"金额: {tx.get('amount', 0)}")

asyncio.run(explore())
```

### 示例 10：钱包交易历史

```python
import asyncio
from rustchain_sdk import RustChainClient

async def wallet_history():
    address = "C4c7r9WPsnEe6CUfegMU9M7ReHD1pWg8qeSfTBoRcLbg"
    
    async with RustChainClient() as client:
        result = await client.get_wallet_history(address, limit=10)
        transactions = result.get("transactions", [])
        
        print(f"钱包 {address[:16]}... 的最近交易:")
        for tx in transactions:
            direction = "📤 发送" if tx.get("from") == address else "📥 接收"
            amount = tx.get("amount", 0)
            print(f"  {direction} {amount} RTC")

asyncio.run(wallet_history())
```

### 示例 11：Beacon 信封提交

```python
import asyncio
from rustchain_sdk import RustChainClient

async def submit_beacon():
    envelope = {
        "type": "heartbeat",
        "payload": {"status": "alive", "timestamp": 1700000000},
        "signature": "hex_encoded_signature",
    }
    
    async with RustChainClient() as client:
        result = await client.beacon_submit(envelope)
        print(f"Beacon 提交结果: {result}")

asyncio.run(submit_beacon())
```

### 示例 12：BoTTube 视频平台操作

```python
from rustchain_sdk.bottube import BoTTubeClient, create_client

# 使用便捷函数创建客户端
client = create_client(api_key="your_api_key_here")

# 健康检查
health = client.health()
print(f"BoTTube 状态: {health}")

# 列出视频
videos = client.videos(limit=5)
for v in videos.get("videos", []):
    print(f"  🎬 {v.get('title', 'Untitled')}")

# 获取 Agent 资料
profile = client.agent_profile("my-agent")
print(f"Agent: {profile}")

# 获取分析数据
analytics = client.analytics(video_id="abc123")
print(f"播放量: {analytics.get('views', 0)}")

# RSS Feed
rss = client.feed_rss(limit=10)
print(f"RSS Feed 长度: {len(rss)} 字符")
```

---

## 5. CLI 工具

安装 SDK 后，`rustchain` 命令行工具自动可用。

### 5.1 钱包管理

```bash
# 创建新钱包（12 词）
rustchain wallet create

# 创建 24 词钱包
rustchain wallet create --words 24

# 输出 JSON 格式
rustchain wallet create --json

# 查询余额
rustchain wallet balance RTC1a2b3c4d5e6f...

# 指定节点
rustchain wallet balance RTC1a... --node https://your-node.com

# 发送 RTC
rustchain wallet send <from> <to> <amount> --seed "word1 word2 word3 ..."
```

### 5.2 节点与网络

```bash
# 节点状态
rustchain node status

# 当前 epoch
rustchain epoch info

# 矿工列表
rustchain miners list

# 认证矿工
rustchain attest <wallet_address> --seed "word1 word2 ..."
```

所有命令都支持 `--json` 标志以 JSON 格式输出，以及 `--node` 指定自定义节点。

---

## 6. 错误处理

### 6.1 基本错误捕获

```python
import asyncio
from rustchain_sdk import RustChainClient
from rustchain_sdk.exceptions import (
    RustChainError,
    ConnectionError,
    APIError,
    ValidationError,
)

async def safe_query():
    try:
        async with RustChainClient() as client:
            balance = await client.get_balance("RTCinvalid")
            print(balance)
    except ConnectionError as e:
        print(f"❌ 连接失败: {e}")
    except APIError as e:
        print(f"❌ API 错误 (HTTP {e.status_code}): {e}")
    except ValidationError as e:
        print(f"❌ 参数无效: {e}")
    except RustChainError as e:
        print(f"❌ RustChain 错误: {e}")

asyncio.run(safe_query())
```

### 6.2 钱包错误处理

```python
from rustchain_sdk import RustChainWallet
from rustchain_sdk.exceptions import WalletError

try:
    # 无效的词数
    wallet = RustChainWallet.create(strength=64)
except ValueError as e:
    print(f"创建失败: {e}")

try:
    # 助记词恢复
    wallet = RustChainWallet.from_seed_phrase(["invalid", "short"])
except ValueError as e:
    print(f"恢复失败: {e}")
```

### 6.3 转账错误处理

```python
import asyncio
from rustchain_sdk import RustChainClient, RustChainWallet
from rustchain_sdk.exceptions import APIError, ConnectionError

async def safe_transfer():
    wallet = RustChainWallet.create()
    
    try:
        async with RustChainClient() as client:
            result = await client.wallet_transfer_with_wallet(
                wallet, "RTCrecipient", 1000
            )
            print(f"✅ 成功: {result}")
    except ConnectionError:
        print("❌ 节点不可达，请检查网络或节点地址")
    except APIError as e:
        if e.status_code == 400:
            print("❌ 请求参数错误，请检查地址和金额")
        elif e.status_code == 401:
            print("❌ 认证失败")
        elif e.status_code == 409:
            print("❌ 余额不足或 nonce 冲突")
        else:
            print(f"❌ API 错误: {e}")

asyncio.run(safe_transfer())
```

### 6.4 重试模式

```python
import asyncio
from rustchain_sdk import RustChainClient
from rustchain_sdk.exceptions import ConnectionError, APIError

async def retry_request(max_retries=3, delay=2):
    """带重试的请求模式"""
    for attempt in range(max_retries):
        try:
            async with RustChainClient(timeout=10) as client:
                return await client.health()
        except ConnectionError as e:
            if attempt < max_retries - 1:
                print(f"连接失败，{delay}秒后重试 ({attempt + 1}/{max_retries})...")
                await asyncio.sleep(delay)
            else:
                raise

asyncio.run(retry_request())
```

---

## 7. 最佳实践

### 7.1 使用上下文管理器

始终使用 `async with` 来确保连接被正确关闭：

```python
# ✅ 推荐
async with RustChainClient() as client:
    result = await client.health()

# ❌ 不推荐（需要手动关闭）
client = RustChainClient()
result = await client.health()
await client.close()  # 容易忘记
```

### 7.2 助记词安全

```python
# ✅ 推荐：从环境变量读取助记词
import os
words = os.environ["RUSTCHAIN_SEED_PHRASE"].split()
wallet = RustChainWallet.from_seed_phrase(words)

# ❌ 危险：硬编码助记词
wallet = RustChainWallet.from_seed_phrase(["abandon", "ability", ...])  # 不要这样做！
```

### 7.3 安装 cryptography 库

为确保真正的 Ed25519 签名（而非 HMAC 回退），请安装 `cryptography`：

```bash
pip install rustchain[crypto]
# 或
pip install cryptography>=41.0.0
```

### 7.4 复用客户端实例

对于多次请求，复用同一客户端实例以利用连接池：

```python
# ✅ 推荐：复用客户端
async with RustChainClient() as client:
    health = await client.health()
    epoch = await client.get_epoch()
    balance = await client.get_balance("RTC...")
    # 所有请求共享同一 HTTP 连接池

# ❌ 不推荐：每次请求创建新客户端
for addr in addresses:
    async with RustChainClient() as client:
        await client.get_balance(addr)  # 每次都创建新连接
```

### 7.5 异常粒度

根据需要捕获不同层级的异常：

```python
# 精确捕获
try:
    await client.health()
except ConnectionError:
    # 处理连接问题
    pass
except APIError as e:
    # 处理 API 错误，可访问 e.status_code
    pass

# 或统一捕获
try:
    await client.health()
except RustChainError as e:
    # 所有 RustChain 错误的基类
    print(f"错误: {e}")
```

### 7.6 TLS 证书管理

如果节点使用自签名证书，将证书放到 `~/.rustchain/node_cert.pem`，SDK 会自动使用。

### 7.7 超时设置

根据网络情况调整超时：

```python
# 默认 30 秒
client = RustChainClient(timeout=30)

# 高延迟网络
client = RustChainClient(timeout=60)

# 快速失败
client = RustChainClient(timeout=5)
```

---

## 许可证

MIT License — kuanglaodi2-sudo (Atlas AI Agent)
