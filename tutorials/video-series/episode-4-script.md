# 🎬 第 4 集：RustChain Python SDK 实战

**时长**: 8-10 分钟  
**难度**: 中级  
**前置**: 第 2 集（API 开发实战）  
**目标**: 掌握 RustChain Python SDK，构建自动化应用

---

## 📝 完整脚本

### 开场回顾 (0:00 - 0:45)

**[画面]: 第 2 集 API 演示片段回放**

**旁白**:
> 欢迎回到 RustChain 教程系列！
> 
> 在上一集里，我们学会了：
> - RustChain REST API 基础
> - 如何查询余额和 epoch 信息
> - 构造和签名转账交易
> 
> **[画面]: 本集标题出现]
> 
> 这一集，我们将更进一步！
> 
> 我会教你使用 RustChain Python SDK：
> - 安装和配置 SDK
> - 用 Python 代码发送转账
> - 构建自动化挖矿监控应用
> 
> 让我们开始吧！

---

### 安装 Python SDK (0:45 - 2:00)

**[画面]: 终端屏幕录制]

**旁白**:
> 首先，安装 RustChain Python SDK。
> 
> **[画面]: pip 安装命令]
> 
> 打开终端，输入：
> 
> ```bash
> pip install rustchain-py
> ```
> 
> **[画面]: 安装进度]
> 
> 安装完成后，让我们验证一下：
> 
> ```bash
> python -c "import rustchain_py; print(rustchain_py.__version__)"
> ```
> 
> **[画面]: 版本号输出]
> 
> 好！SDK 已经准备好了。
> 
> 你也可以从 GitHub 获取源码：
> 
> ```bash
> git clone https://github.com/Scottcjn/Rustchain.git
> cd Rustchain/rustchain-py
> pip install -e .
> ```
> 
> **[画面]: GitHub 仓库页面]
> 
> 这样你就可以修改和调试 SDK 代码了。

---

### SDK 基础用法 (2:00 - 4:30)

**[画面]: Python 代码编辑器]

**旁白**:
> 现在，让我们看看 SDK 的基础用法。
> 
> **[画面]: 代码演示]
> 
> 创建一个新文件 `sdk_basics.py`：
> 
> ```python
> from rustchain_py import RustChainClient
> 
> # 初始化客户端
> client = RustChainClient(
>     base_url="https://rustchain.org",
>     wallet_id="my-wallet"
> )
> 
> # 检查连接
> health = client.health()
> print(f"节点状态：{health}")
> 
> # 查询余额
> balance = client.get_balance("my-wallet")
> print(f"余额：{balance['amount_rtc']} RTC")
> 
> # 查询 epoch 信息
> epoch = client.get_epoch()
> print(f"当前 epoch: {epoch['epoch']}, 高度：{epoch['height']}")
> ```
> 
> **[画面]: 运行代码]
> 
> 运行它：
> 
> ```bash
> python sdk_basics.py
> ```
> 
> **[画面]: 输出结果]
> 
> 看！我们成功连接到了 RustChain 节点，并获取了余额信息。
> 
> 这比直接用 curl 方便多了！

---

### 发送转账 (4:30 - 6:30)

**[画面]: 代码演示]

**旁白**:
> 现在来看最重要的功能：发送转账。
> 
> **[画面]: 转账代码]
> 
> 创建 `send_transfer.py`：
> 
> ```python
> from rustchain_py import RustChainClient
> import json
> 
> # 初始化客户端
> client = RustChainClient(
>     base_url="https://rustchain.org",
>     wallet_id="sender-wallet",
>     private_key="your-private-key"  # 实际使用时从环境变量读取
> )
> 
> # 发送转账
> response = client.transfer(
>     to="recipient-wallet",
>     amount=1000000,  # 单位：satoshis
>     fee=1000
> )
> 
> print(json.dumps(response, indent=2))
> 
> # 验证交易
> tx_id = response.get('tx_id')
> if tx_id:
>     print(f"✅ 交易成功！TX ID: {tx_id}")
>     print(f"查看交易：https://rustchain.org/explorer?tx={tx_id}")
> else:
>     print("❌ 交易失败")
> ```
> 
> **[画面]: 安全提示]
> 
> ⚠️ **安全警告**：
> 
> 永远不要把私钥硬编码在代码里！
> 
> 正确做法是使用环境变量：
> 
> ```python
> import os
> private_key = os.getenv('RUSTCHAIN_PRIVATE_KEY')
> ```
> 
> 或者使用密钥管理工具。

---

### 构建监控应用 (6:30 - 8:30)

**[画面]: 完整应用代码]

**旁白**:
> 最后，让我们构建一个实用的监控应用。
> 
> 这个应用会：
> - 定期检查钱包余额
> - 记录挖矿收益
> - 发送通知（可选）
> 
> **[画面]: 监控代码]
> 
> 创建 `mining_monitor.py`：
> 
> ```python
> from rustchain_py import RustChainClient
> import time
> from datetime import datetime
> import json
> 
> class MiningMonitor:
>     def __init__(self, wallet_id):
>         self.client = RustChainClient(
>             base_url="https://rustchain.org",
>             wallet_id=wallet_id
>         )
>         self.wallet_id = wallet_id
>         self.history = []
>     
>     def check_balance(self):
>         """查询当前余额"""
>         balance = self.client.get_balance(self.wallet_id)
>         return balance.get('amount_rtc', 0)
>     
>     def log_balance(self):
>         """记录余额到历史"""
>         timestamp = datetime.now().isoformat()
>         balance = self.check_balance()
>         
>         record = {
>             'timestamp': timestamp,
>             'balance': balance
>         }
>         
>         self.history.append(record)
>         
>         # 计算收益
>         if len(self.history) > 1:
>             prev_balance = self.history[-2]['balance']
>             earnings = balance - prev_balance
>             record['earnings'] = earnings
>             
>             print(f"[{timestamp}] 余额：{balance} RTC, 收益：{earnings} RTC")
>         else:
>             print(f"[{timestamp}] 余额：{balance} RTC")
>         
>         return record
>     
>     def save_history(self, filename='mining_history.json'):
>         """保存历史到文件"""
>         with open(filename, 'w') as f:
>             json.dump(self.history, f, indent=2)
>         print(f"✅ 历史记录已保存到 {filename}")
>     
>     def start_monitoring(self, interval=300):
>         """开始监控（默认每 5 分钟）"""
>         print(f"🚀 开始监控钱包：{self.wallet_id}")
>         print(f"检查间隔：{interval}秒")
>         print("按 Ctrl+C 停止\n")
>         
>         try:
>             while True:
>                 self.log_balance()
>                 time.sleep(interval)
>         except KeyboardInterrupt:
>             print("\n\n⏹️  停止监控")
>             self.save_history()
>             print(f"共记录 {len(self.history)} 条数据")
> 
> # 使用示例
> if __name__ == "__main__":
>     import os
>     
>     wallet = os.getenv('RUSTCHAIN_WALLET', 'default-wallet')
>     interval = int(os.getenv('CHECK_INTERVAL', '300'))
>     
>     monitor = MiningMonitor(wallet)
>     monitor.start_monitoring(interval)
> ```
> 
> **[画面]: 运行监控]
> 
> 运行它：
> 
> ```bash
> export RUSTCHAIN_WALLET=my-wallet
> python mining_monitor.py
> ```
> 
> **[画面]: 实时监控输出]
> 
> 看！它正在实时监控你的挖矿收益！

---

### 结尾和预告 (8:30 - 9:00)

**[画面]: 回到主讲人/Logo]

**旁白**:
> 恭喜你！你已经掌握了 RustChain Python SDK！
> 
> 现在你可以：
> - 用 Python 代码与 RustChain 交互
> - 发送自动化转账
> - 构建监控和数据分析应用
> 
> **[画面]: 下一集预告]
> 
> 在下一集（也是最后一集）里，我会教你：
> - 使用 JavaScript SDK
> - 构建网页钱包应用
> - 集成到前端项目
> 
> 对于前端开发者来说，这是必备技能！
> 
> **[画面]: 资源链接]
> 
> 本集的资源链接：
> - Python SDK: github.com/Scottcjn/Rustchain/rustchain-py
> - 示例代码：本集 GitHub Issue
> - 文档：rustchain.org/docs/sdk/python
> 
> 如果你觉得有帮助，请点赞、订阅，并分享给你的朋友！
> 
> 我们下一集见！

**[画面]: Logo 动画 + 结束音乐**

---

## 💻 演示代码

### 1. SDK 安装和测试

```python
# test_sdk.py
from rustchain_py import RustChainClient

def test_connection():
    """测试 SDK 连接"""
    client = RustChainClient(base_url="https://rustchain.org")
    
    # Health check
    health = client.health()
    assert health.get('ok') == True, "节点不健康"
    print(f"✅ 节点健康：version={health.get('version')}")
    
    # Get epoch
    epoch = client.get_epoch()
    print(f"✅ 当前 epoch: {epoch.get('epoch')}, 高度：{epoch.get('height')}")
    
    print("\n✅ SDK 测试通过！")

if __name__ == "__main__":
    test_connection()
```

### 2. 批量转账工具

```python
# batch_transfer.py
from rustchain_py import RustChainClient
import json
import os

def batch_transfer(recipients_file, private_key=None):
    """
    批量转账工具
    
    recipients_file: JSON 文件，格式如下：
    [
        {"to": "wallet1", "amount": 1000000},
        {"to": "wallet2", "amount": 2000000},
        ...
    ]
    """
    # 从环境变量获取私钥
    if private_key is None:
        private_key = os.getenv('RUSTCHAIN_PRIVATE_KEY')
    
    if not private_key:
        print("❌ 错误：未提供私钥")
        print("请设置 RUSTCHAIN_PRIVATE_KEY 环境变量")
        return
    
    # 初始化客户端
    client = RustChainClient(
        base_url="https://rustchain.org",
        wallet_id=os.getenv('RUSTCHAIN_WALLET'),
        private_key=private_key
    )
    
    # 读取 recipients
    with open(recipients_file, 'r') as f:
        recipients = json.load(f)
    
    print(f"📤 开始批量转账，共 {len(recipients)} 笔交易\n")
    
    results = []
    for i, recipient in enumerate(recipients, 1):
        print(f"[{i}/{len(recipients)}] 转账给 {recipient['to']}: {recipient['amount']} RTC")
        
        try:
            response = client.transfer(
                to=recipient['to'],
                amount=recipient['amount'],
                fee=1000
            )
            
            if response.get('tx_id'):
                print(f"  ✅ 成功！TX: {response['tx_id']}")
                results.append({
                    'to': recipient['to'],
                    'amount': recipient['amount'],
                    'status': 'success',
                    'tx_id': response['tx_id']
                })
            else:
                print(f"  ❌ 失败：{response.get('error', 'Unknown error')}")
                results.append({
                    'to': recipient['to'],
                    'amount': recipient['amount'],
                    'status': 'failed',
                    'error': response.get('error')
                })
        except Exception as e:
            print(f"  ❌ 异常：{str(e)}")
            results.append({
                'to': recipient['to'],
                'amount': recipient['amount'],
                'status': 'error',
                'error': str(e)
            })
    
    # 保存结果
    with open('batch_transfer_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ 批量转账完成！结果已保存到 batch_transfer_results.json")
    
    # 统计
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"成功：{success_count}/{len(recipients)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法：python batch_transfer.py <recipients.json>")
        sys.exit(1)
    
    batch_transfer(sys.argv[1])
```

### 3. 收益分析工具

```python
# analyze_earnings.py
from rustchain_py import RustChainClient
import json
from datetime import datetime, timedelta

def analyze_earnings(wallet_id, days=7):
    """分析过去 N 天的挖矿收益"""
    client = RustChainClient(
        base_url="https://rustchain.org",
        wallet_id=wallet_id
    )
    
    print(f"📊 分析钱包 {wallet_id} 过去 {days} 天的收益\n")
    
    # 获取当前余额
    current_balance = client.get_balance(wallet_id).get('amount_rtc', 0)
    print(f"当前余额：{current_balance} RTC")
    
    # 注意：这里假设有一个历史 API，实际可能需要本地记录
    # 实际使用时，需要从本地 mining_history.json 读取
    
    try:
        with open('mining_history.json', 'r') as f:
            history = json.load(f)
        
        # 过滤最近 N 天的数据
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            r for r in history 
            if datetime.fromisoformat(r['timestamp']) > cutoff
        ]
        
        if len(recent) < 2:
            print("❌ 数据不足，无法分析")
            return
        
        # 计算收益
        first_balance = recent[0]['balance']
        last_balance = recent[-1]['balance']
        total_earnings = last_balance - first_balance
        
        # 计算平均每日收益
        days_span = (
            datetime.fromisoformat(recent[-1]['timestamp']) - 
            datetime.fromisoformat(recent[0]['timestamp'])
        ).days or 1
        
        daily_avg = total_earnings / days_span
        
        print(f"\n📈 收益统计:")
        print(f"  起始余额：{first_balance} RTC")
        print(f"  结束余额：{last_balance} RTC")
        print(f"  总收益：{total_earnings} RTC")
        print(f"  平均每日：{daily_avg:.2f} RTC/天")
        
        # 计算预计月度收益
        monthly_proj = daily_avg * 30
        print(f"  预计月度：{monthly_proj:.2f} RTC/月")
        
    except FileNotFoundError:
        print("❌ 未找到历史记录文件 mining_history.json")
        print("请先运行 mining_monitor.py 收集数据")

if __name__ == "__main__":
    import os
    import sys
    
    wallet = sys.argv[1] if len(sys.argv) > 1 else os.getenv('RUSTCHAIN_WALLET')
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    
    if not wallet:
        print("❌ 错误：未指定钱包 ID")
        print("用法：python analyze_earnings.py <wallet_id> [days]")
        sys.exit(1)
    
    analyze_earnings(wallet, days)
```

---

## 🎨 视觉设计

### 代码展示
- 使用深色主题（One Dark Pro）
- 字体：JetBrains Mono, 16px
- 语法高亮：Python 蓝色/黄色主题

### 动画效果
- 代码逐行高亮显示
- 运行结果使用终端录制
- 图表使用 matplotlib 实时生成

### 转场
- 章节间使用代码雨效果
- 重要概念使用放大强调

---

## 📋 录制清单

### 录制前准备
- [ ] 安装 rustchain-py SDK
- [ ] 准备测试钱包（不要使用主网私钥！）
- [ ] 清理代码编辑器，关闭无关标签
- [ ] 测试所有示例代码

### 录制中注意
- [ ] 代码输入速度适中
- [ ] 解释每行代码的作用
- [ ] 强调安全注意事项
- [ ] 展示错误处理和调试

### 录制后检查
- [ ] 代码清晰可读
- [ ] 音频无噪音
- [ ] 时长控制在 8-10 分钟
- [ ] 添加字幕和关键点标注

---

## 📝 视频描述模板

```markdown
# RustChain 教程 #4: Python SDK 实战

学会使用 RustChain Python SDK 构建自动化应用！

在这集里，你将学会：
✅ 安装和配置 RustChain Python SDK
✅ 用 Python 代码发送转账
✅ 构建挖矿监控应用
✅ 批量转账工具开发
✅ 收益数据分析

⏱️ 时间戳:
0:00 - 开场回顾
0:45 - 安装 Python SDK
2:00 - SDK 基础用法
4:30 - 发送转账
6:30 - 构建监控应用
8:30 - 下一集预告

🔗 资源链接:
- Python SDK: https://github.com/Scottcjn/Rustchain/tree/main/rustchain-py
- 示例代码: [本集 GitHub Issue 链接]
- 文档：https://rustchain.org/docs/sdk/python

📺 上一集:
RustChain API 开发实战 - REST API 基础

📺 下一集 (最终集):
JavaScript SDK 实战 - 构建网页钱包应用！

#RustChain #Python #SDK #区块链开发 #RTC #教程
```

---

**脚本完成时间**: 2026-03-13 15:40  
**状态**: ✅ 准备录制
