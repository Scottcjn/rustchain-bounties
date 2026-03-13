# 🎬 第 2 集：RustChain API 开发实战

**时长**: 8-10 分钟  
**难度**: 中级  
**前置**: 第 1 集（入门指南）  
**目标**: 掌握 RustChain API，构建转账应用

---

## 📝 完整脚本

### 开场回顾 (0:00 - 0:45)

**[画面]: 第 1 集精彩片段回放**

**旁白**:
> 欢迎回到 RustChain 教程系列！
> 
> 在上一集里，我们学会了：
> - 什么是 Proof-of-Antiquity
> - 如何安装 RustChain
> - 开始挖矿赚取 RTC
> 
> **[画面]: 本集标题出现]
> 
> 这一集，我们将进入开发者的世界！
> 
> 我会教你如何：
> - 使用 RustChain API
> - 构造和签名交易
> - 用 Python 代码发送 RTC 转账
> 
> 让我们开始吧！

---

### API 基础 (0:45 - 2:30)

**[画面]: API 端点列表]

**旁白**:
> RustChain 提供了一套简洁的 REST API。
> 
> 主要端点有：
> 
> **[画面]: 代码演示]
> 
> **1. Health Check** - 检查节点状态
> 
> ```bash
> curl -sk https://rustchain.org/health
> ```
> 
> 返回：`{"ok": true, "version": "2.2.1", "uptime": 200000}`
> 
> **2. Epoch 信息** - 当前区块高度
> 
> ```bash
> curl -sk https://rustchain.org/epoch
> ```
> 
> 返回：`{"epoch": 95, "slot": 12345, "height": 67890}`
> 
> **3. 查询余额** - 查看钱包余额
> 
> ```bash
> curl -sk "https://rustchain.org/wallet/balance?miner_id=my-wallet"
> ```
> 
> 返回：`{"amount_rtc": 155.0, "miner_id": "my-wallet"}`
> 
> **[画面]: Postman 演示]
> 
> 你可以用 Postman 或 curl 测试这些 API。
> 
> 注意：RustChain 使用自签名证书，所以要加 `-k` 参数跳过验证。

---

### 转账 API 详解 (2:30 - 4:30)

**[画面]: 转账流程图]

**旁白**:
> 现在来看最重要的部分：转账 API。
> 
> RustChain 的转账需要**签名**，确保交易安全。
> 
> **[画面]: 请求结构]
> 
> 端点：`POST /wallet/transfer/signed`
> 
> 请求体包含：
> 
> ```json
> {
>   "from": "sender_wallet",
>   "to": "recipient_wallet",
>   "amount": 1000000,
>   "fee": 1000,
>   "timestamp": 1234567890,
>   "signature": "signed_with_private_key"
> }
> ```
> 
> **[画面]: Python 签名代码]
> 
> 签名过程：
> 
> ```python
> import hashlib
> import hmac
> import base64
> 
> def sign_transaction(from_wallet, to_wallet, amount, fee, private_key):
>     # 构造交易数据
>     tx_data = f"{from_wallet}:{to_wallet}:{amount}:{fee}"
>     
>     # 使用 HMAC-SHA256 签名
>     signature = hmac.new(
>         private_key.encode(),
>         tx_data.encode(),
>         hashlib.sha256
>     ).digest()
>     
>     return base64.b64encode(signature).decode()
> 
> # 使用示例
> sig = sign_transaction(
>     "sender", "recipient", 1000000, 1000,
>     "my-secret-private-key"
> )
> print(f"签名：{sig}")
> ```

---

### Python 实战：发送转账 (4:30 - 7:00)

**[画面]: 完整 Python 代码]

**旁白**:
> 现在让我们用 Python 实现一个完整的转账工具。
> 
> **[画面]: 代码编辑器]
> 
> 创建 `transfer_rtc.py`：
> 
> ```python
> import requests
> import hashlib
> import hmac
> import base64
> import time
> import json
> 
> class RustChainAPI:
>     def __init__(self, base_url="https://rustchain.org"):
>         self.base_url = base_url
>     
>     def health(self):
>         """检查节点健康"""
>         response = requests.get(f"{self.base_url}/health", verify=False)
>         return response.json()
>     
>     def get_balance(self, miner_id):
>         """查询余额"""
>         response = requests.get(
>             f"{self.base_url}/wallet/balance?miner_id={miner_id}",
>             verify=False
>         )
>         return response.json()
>     
>     def sign_transaction(self, from_wallet, to_wallet, amount, fee, private_key):
>         """签名交易"""
>         tx_data = f"{from_wallet}:{to_wallet}:{amount}:{fee}"
>         signature = hmac.new(
>             private_key.encode(),
>             tx_data.encode(),
>             hashlib.sha256
>         ).digest()
>         return base64.b64encode(signature).decode()
>     
>     def transfer(self, from_wallet, to_wallet, amount, fee, private_key):
>         """发送转账"""
>         timestamp = int(time.time())
>         signature = self.sign_transaction(
>             from_wallet, to_wallet, amount, fee, private_key
>         )
>         
>         payload = {
>             "from": from_wallet,
>             "to": to_wallet,
>             "amount": amount,
>             "fee": fee,
>             "timestamp": timestamp,
>             "signature": signature
>         }
>         
>         response = requests.post(
>             f"{self.base_url}/wallet/transfer/signed",
>             json=payload,
>             verify=False
>         )
>         
>         return response.json()
> 
> # 使用示例
> if __name__ == "__main__":
>     api = RustChainAPI()
>     
>     # 检查节点状态
>     print("节点状态:", api.health())
>     
>     # 查询余额
>     balance = api.get_balance("my-wallet")
>     print(f"余额：{balance['amount_rtc']} RTC")
>     
>     # 发送转账（示例，不要实际运行！）
>     # result = api.transfer(
>     #     from_wallet="my-wallet",
>     #     to_wallet="recipient-wallet",
>     #     amount=1000000,  # 1 RTC
>     #     fee=1000,
>     #     private_key="your-private-key"
>     # )
>     # print(f"交易结果：{result}")
> ```
> 
> **[画面]: 运行代码]
> 
> 运行它：
> 
> ```bash
> python transfer_rtc.py
> ```
> 
> **[画面]: 输出结果]
> 
> 看！我们成功查询了余额。
> 
> ⚠️ **安全提示**：
> - 永远不要在代码中硬编码私钥
> - 使用环境变量或密钥管理工具
> - 测试时使用测试网钱包

---

### 批量查询工具 (7:00 - 8:30)

**[画面]: 批量查询代码]

**旁白**:
> 最后，让我们构建一个实用的批量查询工具。
> 
> 这个工具可以：
> - 一次性查询多个钱包余额
> - 导出到 CSV 格式
> - 计算总余额
> 
> **[画面]: 代码演示]
> 
> 创建 `batch_balance.py`：
> 
> ```python
> import requests
> import csv
> 
> def check_balances(wallets, base_url="https://rustchain.org"):
>     """批量查询钱包余额"""
>     results = []
>     
>     for wallet in wallets:
>         try:
>             response = requests.get(
>                 f"{base_url}/wallet/balance?miner_id={wallet}",
>                 verify=False
>             )
>             data = response.json()
>             
>             results.append({
>                 'wallet': wallet,
>                 'balance': data.get('amount_rtc', 0),
>                 'status': 'success'
>             })
>         except Exception as e:
>             results.append({
>                 'wallet': wallet,
>                 'balance': 0,
>                 'status': f'error: {str(e)}'
>             })
>     
>     return results
> 
> def export_to_csv(results, filename='balances.csv'):
>     """导出到 CSV"""
>     with open(filename, 'w', newline='') as f:
>         writer = csv.DictWriter(f, fieldnames=['wallet', 'balance', 'status'])
>         writer.writeheader()
>         writer.writerows(results)
>     print(f"✅ 已导出到 {filename}")
> 
> # 使用示例
> if __name__ == "__main__":
>     wallets = [
>         "wallet-1",
>         "wallet-2",
>         "wallet-3"
>     ]
>     
>     print("🔍 批量查询余额...\n")
>     results = check_balances(wallets)
>     
>     total = 0
>     for r in results:
>         print(f"{r['wallet']}: {r['balance']} RTC ({r['status']})")
>         total += r['balance']
>     
>     print(f"\n💰 总余额：{total} RTC")
>     
>     # 导出 CSV
>     export_to_csv(results)
> ```

---

### 结尾和预告 (8:30 - 9:00)

**[画面]: 回到主讲人/Logo]

**旁白**:
> 恭喜你！你已经掌握了 RustChain API 开发！
> 
> 现在你可以：
> - 查询节点状态和余额
> - 构造和签名交易
> - 用 Python 发送转账
> - 批量查询多个钱包
> 
> **[画面]: 下一集预告]
> 
> 在下一集里，我会介绍 BoTTube 平台：
> - AI 驱动的视频平台
> - 上传和管理视频
> - SDK 集成
> 
> 这是 RustChain 生态系统的重要组成部分！
> 
> **[画面]: 资源链接]
> 
> 本集的资源链接：
> - API 文档：rustchain.org/docs/api
> - 示例代码：本集 GitHub Issue
> - Python SDK：github.com/Scottcjn/Rustchain/rustchain-py
> 
> 如果你觉得有帮助，请点赞、订阅，并分享给你的朋友！
> 
> 我们下一集见！

**[画面]: Logo 动画 + 结束音乐**

---

## 💻 演示代码

### 1. API 封装类

```python
# rustchain_api.py
import requests
from typing import Dict, Optional

class RustChainAPI:
    """RustChain REST API 封装"""
    
    def __init__(self, base_url: str = "https://rustchain.org"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False  # 自签名证书
    
    def health(self) -> Dict:
        """检查节点健康状态"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def get_epoch(self) -> Dict:
        """获取当前 epoch 信息"""
        response = self.session.get(f"{self.base_url}/epoch")
        return response.json()
    
    def get_balance(self, miner_id: str) -> Dict:
        """查询钱包余额"""
        response = self.session.get(
            f"{self.base_url}/wallet/balance",
            params={"miner_id": miner_id}
        )
        return response.json()
    
    def get_transaction(self, tx_id: str) -> Dict:
        """查询交易详情"""
        response = self.session.get(
            f"{self.base_url}/transaction/{tx_id}"
        )
        return response.json()
    
    def get_transactions(self, miner_id: str, limit: int = 10) -> list:
        """获取交易历史"""
        response = self.session.get(
            f"{self.base_url}/wallet/transactions",
            params={"miner_id": miner_id, "limit": limit}
        )
        return response.json()
```

### 2. 命令行工具

```python
# rustchain_cli.py
import argparse
import sys
from rustchain_api import RustChainAPI

def main():
    parser = argparse.ArgumentParser(description='RustChain CLI 工具')
    parser.add_argument('--url', default='https://rustchain.org',
                       help='RustChain 节点 URL')
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # Health 命令
    health_parser = subparsers.add_parser('health', help='检查节点健康')
    
    # Balance 命令
    balance_parser = subparsers.add_parser('balance', help='查询余额')
    balance_parser.add_argument('wallet', help='钱包 ID')
    
    # Epoch 命令
    epoch_parser = subparsers.add_parser('epoch', help='获取 epoch 信息')
    
    args = parser.parse_args()
    
    api = RustChainAPI(args.url)
    
    if args.command == 'health':
        result = api.health()
        print(f"节点状态：{'✅ 健康' if result.get('ok') else '❌ 异常'}")
        print(f"版本：{result.get('version')}")
        print(f"运行时间：{result.get('uptime')} 秒")
    
    elif args.command == 'balance':
        result = api.get_balance(args.wallet)
        print(f"钱包：{args.wallet}")
        print(f"余额：{result.get('amount_rtc')} RTC")
    
    elif args.command == 'epoch':
        result = api.get_epoch()
        print(f"Epoch: {result.get('epoch')}")
        print(f"Slot: {result.get('slot')}")
        print(f"高度：{result.get('height')}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
```

---

## 🎨 视觉设计

### API 演示
- 使用 Postman 界面展示 API 调用
- 代码使用深色主题
- JSON 响应使用语法高亮

### 流程图
- 转账流程使用动画展示
- 签名过程逐步演示
- 数据流向清晰标注

### 配色方案
- API 端点：蓝色背景
- 代码：深色主题
- 响应：绿色（成功）/红色（错误）

---

## 📋 录制清单

### 录制前准备
- [ ] 准备测试钱包
- [ ] 安装 Python 和依赖（requests）
- [ ] 测试所有 API 端点
- [ ] 准备 Postman Collection

### 录制中注意
- [ ] 代码输入清晰
- [ ] 解释每个 API 参数
- [ ] 强调安全注意事项
- [ ] 展示错误处理

### 录制后检查
- [ ] API 调用演示清晰
- [ ] 代码可读性好
- [ ] 时长控制在 8-10 分钟
- [ ] 添加字幕和标注

---

## 📝 视频描述模板

```markdown
# RustChain 教程 #2: API 开发实战

掌握 RustChain REST API，构建区块链应用！

在这集里，你将学会：
✅ RustChain API 端点介绍
✅ 查询余额和 epoch 信息
✅ 构造和签名交易
✅ Python 代码实现转账
✅ 批量查询工具开发

⏱️ 时间戳:
0:00 - 开场回顾
0:45 - API 基础
2:30 - 转账 API 详解
4:30 - Python 实战
7:00 - 批量查询工具
8:30 - 下一集预告

🔗 资源链接:
- API 文档：https://rustchain.org/docs/api
- 示例代码：[GitHub Issue 链接]
- Python SDK: https://github.com/Scottcjn/Rustchain/rustchain-py

📺 上一集:
RustChain 入门指南 - 快速开始挖矿

📺 下一集:
BoTTube 平台介绍 - AI 驱动的视频平台

#RustChain #API #Python #区块链开发 #RTC #教程
```

---

**脚本完成时间**: 2026-03-13  
**状态**: ✅ 准备录制
