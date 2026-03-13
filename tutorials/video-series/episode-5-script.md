# 🎬 第 5 集：JavaScript SDK 与网页钱包

**时长**: 8-10 分钟  
**难度**: 中级  
**前置**: 第 2 集（API 开发实战）  
**目标**: 掌握 RustChain JavaScript SDK，构建网页钱包应用

---

## 📝 完整脚本

### 开场回顾 (0:00 - 0:45)

**[画面]: 前几集精彩片段快速回放**

**旁白**:
> 欢迎来到 RustChain 教程系列的最终集！
> 
> 在过去的四集里，我们学会了：
> - RustChain 挖矿入门
> - REST API 开发
> - BoTTube 平台介绍
> - Python SDK 实战
> 
> **[画面]: 本集标题出现]
> 
> 这一集，我们进入前端开发！
> 
> 我会教你使用 RustChain JavaScript SDK：
> - 在浏览器中使用 SDK
> - 构建网页钱包应用
> - 集成到 React/Vue 项目
> 
> 让我们完成这个系列！

---

### 安装 JavaScript SDK (0:45 - 2:00)

**[画面]: 终端屏幕录制]

**旁白**:
> 首先，安装 RustChain JavaScript SDK。
> 
> **[画面]: npm 安装命令]
> 
> 打开终端，输入：
> 
> ```bash
> npm install rustchain-js-sdk
> ```
> 
> **[画面]: 安装进度]
> 
> 或者使用 yarn：
> 
> ```bash
> yarn add rustchain-js-sdk
> ```
> 
> **[画面]: package.json 依赖]
> 
> 安装完成后，你的 package.json 会添加：
> 
> ```json
> {
>   "dependencies": {
>     "rustchain-js-sdk": "^1.0.0"
>   }
> }
> ```
> 
> 你也可以直接在浏览器中使用 CDN：
> 
> ```html
> <script src="https://cdn.jsdelivr.net/npm/rustchain-js-sdk@1.0.0/dist/rustchain.min.js"></script>
> ```

---

### SDK 基础用法 (2:00 - 4:00)

**[画面]: 代码编辑器]

**旁白**:
> 现在，让我们看看 SDK 的基础用法。
> 
> **[画面]: Node.js 示例]
> 
> 创建 `sdk-basics.js`：
> 
> ```javascript
> const RustChain = require('rustchain-js-sdk');
> 
> // 初始化客户端
> const client = new RustChain.Client({
>   baseURL: 'https://rustchain.org',
>   walletId: 'my-wallet'
> });
> 
> // 检查连接
> async function testConnection() {
>   try {
>     const health = await client.health();
>     console.log('节点状态:', health);
>     
>     const balance = await client.getBalance('my-wallet');
>     console.log('余额:', balance.amount_rtc, 'RTC');
>     
>     const epoch = await client.getEpoch();
>     console.log('当前 epoch:', epoch.epoch, '高度:', epoch.height);
>   } catch (error) {
>     console.error('错误:', error.message);
>   }
> }
> 
> testConnection();
> ```
> 
> **[画面]: 运行代码]
> 
> 运行它：
> 
> ```bash
> node sdk-basics.js
> ```
> 
> **[画面]: 输出结果]
> 
> 好！现在让我们看看如何在浏览器中使用。

---

### 构建网页钱包 (4:00 - 7:00)

**[画面]: HTML 文件]

**旁白**:
> 现在，让我们构建一个完整的网页钱包应用。
> 
> 这个应用会：
> - 显示钱包余额
> - 发送转账
> - 查看交易历史
> 
> **[画面]: 完整 HTML 代码]
> 
> 创建 `wallet.html`：
> 
> ```html
> <!DOCTYPE html>
> <html lang="zh-CN">
> <head>
>   <meta charset="UTF-8">
>   <meta name="viewport" content="width=device-width, initial-scale=1.0">
>   <title>RustChain 网页钱包</title>
>   <script src="https://cdn.jsdelivr.net/npm/rustchain-js-sdk@1.0.0/dist/rustchain.min.js"></script>
>   <style>
>     body {
>       font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
>       max-width: 600px;
>       margin: 40px auto;
>       padding: 20px;
>       background: #f5f5f5;
>     }
>     .card {
>       background: white;
>       border-radius: 8px;
>       padding: 24px;
>       margin-bottom: 20px;
>       box-shadow: 0 2px 8px rgba(0,0,0,0.1);
>     }
>     h1 { color: #d97706; }
>     h2 { color: #374151; font-size: 18px; }
>     .balance {
>       font-size: 36px;
>       font-weight: bold;
>       color: #059669;
>     }
>     input {
>       width: 100%;
>       padding: 12px;
>       margin: 8px 0;
>       border: 1px solid #d1d5db;
>       border-radius: 6px;
>       font-size: 16px;
>     }
>     button {
>       width: 100%;
>       padding: 12px;
>       background: #d97706;
>       color: white;
>       border: none;
>       border-radius: 6px;
>       font-size: 16px;
>       cursor: pointer;
>       margin-top: 12px;
>     }
>     button:hover { background: #b45309; }
>     button:disabled {
>       background: #9ca3af;
>       cursor: not-allowed;
>     }
>     .status {
>       padding: 12px;
>       border-radius: 6px;
>       margin-top: 12px;
>     }
>     .success { background: #d1fae5; color: #065f46; }
>     .error { background: #fee2e2; color: #991b1b; }
>     .tx-list {
>       list-style: none;
>       padding: 0;
>     }
>     .tx-item {
>       padding: 12px;
>       border-bottom: 1px solid #e5e7eb;
>     }
>     .tx-item:last-child { border-bottom: none; }
>   </style>
> </head>
> <body>
>   <h1>🦀 RustChain 钱包</h1>
>   
>   <!-- 余额卡片 -->
>   <div class="card">
>     <h2>💰 余额</h2>
>     <div class="balance" id="balance">--</div>
>     <button onclick="refreshBalance()">刷新</button>
>   </div>
>   
>   <!-- 转账卡片 -->
>   <div class="card">
>     <h2>📤 发送转账</h2>
>     <input type="text" id="recipient" placeholder="收款钱包 ID">
>     <input type="number" id="amount" placeholder="金额 (RTC)">
>     <input type="number" id="fee" placeholder="手续费 (默认 0.001)" value="0.001" step="0.000001">
>     <button onclick="sendTransfer()" id="sendBtn">发送</button>
>     <div id="status"></div>
>   </div>
>   
>   <!-- 交易历史 -->
>   <div class="card">
>     <h2>📜 交易历史</h2>
>     <ul class="tx-list" id="txList">
>       <li>加载中...</li>
>     </ul>
>   </div>
> 
>   <script>
>     // 初始化客户端
>     const client = new RustChain.Client({
>       baseURL: 'https://rustchain.org',
>       walletId: localStorage.getItem('walletId') || 'guest'
>     });
>     
>     // 刷新余额
>     async function refreshBalance() {
>       try {
>         const balance = await client.getBalance(client.walletId);
>         document.getElementById('balance').textContent = 
>           (balance.amount_rtc / 1000000).toFixed(6) + ' RTC';
>       } catch (error) {
>         console.error('获取余额失败:', error);
>       }
>     }
>     
>     // 发送转账
>     async function sendTransfer() {
>       const recipient = document.getElementById('recipient').value;
>       const amount = parseFloat(document.getElementById('amount').value);
>       const fee = parseFloat(document.getElementById('fee').value) || 0.001;
>       
>       if (!recipient || !amount) {
>         showStatus('请填写收款地址和金额', 'error');
>         return;
>       }
>       
>       const btn = document.getElementById('sendBtn');
>       btn.disabled = true;
>       btn.textContent = '发送中...';
>       
>       try {
>         // 转换为 satoshis
>         const amountSat = Math.floor(amount * 1000000);
>         const feeSat = Math.floor(fee * 1000000);
>         
>         const result = await client.transfer({
>           to: recipient,
>           amount: amountSat,
>           fee: feeSat
>         });
>         
>         if (result.tx_id) {
>           showStatus(
>             `✅ 转账成功！<br>TX: ${result.tx_id}<br>` +
>             `<a href="https://rustchain.org/explorer?tx=${result.tx_id}" target="_blank">查看交易</a>`,
>             'success'
>           );
>           refreshBalance();
>           loadTransactions();
>         } else {
>           showStatus('❌ 转账失败：' + (result.error || '未知错误'), 'error');
>         }
>       } catch (error) {
>         showStatus('❌ 错误：' + error.message, 'error');
>       } finally {
>         btn.disabled = false;
>         btn.textContent = '发送';
>       }
>     }
>     
>     // 显示状态
>     function showStatus(message, type) {
>       const status = document.getElementById('status');
>       status.innerHTML = message;
>       status.className = 'status ' + type;
>       setTimeout(() => {
>         status.innerHTML = '';
>         status.className = 'status';
>       }, 5000);
>     }
>     
>     // 加载交易历史
>     async function loadTransactions() {
>       try {
>         const txs = await client.getTransactions(client.walletId);
>         const list = document.getElementById('txList');
>         
>         if (txs.length === 0) {
>           list.innerHTML = '<li>暂无交易</li>';
>           return;
>         }
>         
>         list.innerHTML = txs.slice(0, 10).map(tx => `
>           <li class="tx-item">
>             <strong>${tx.type === 'send' ? '📤' : '📥'}</strong>
>             ${tx.type === 'send' ? '发送给' : '接收自'}: ${tx.counterparty}<br>
>             <span style="color: ${tx.type === 'send' ? '#dc2626' : '#059669'}">
>               ${tx.type === 'send' ? '-' : '+'}${(tx.amount / 1000000).toFixed(6)} RTC
>             </span><br>
>             <small style="color: #6b7280">${new Date(tx.timestamp).toLocaleString()}</small>
>           </li>
>         `).join('');
>       } catch (error) {
>         console.error('加载交易失败:', error);
>       }
>     }
>     
>     // 初始化
>     refreshBalance();
>     loadTransactions();
>     
>     // 每 30 秒刷新
>     setInterval(refreshBalance, 30000);
>   </script>
> </body>
> </html>
> ```
> 
> **[画面]: 浏览器演示]
> 
> 在浏览器中打开这个文件，你就有了一个功能完整的网页钱包！

---

### React 集成示例 (7:00 - 8:30)

**[画面]: React 组件代码]

**旁白**:
> 如果你使用 React，可以这样集成：
> 
> ```jsx
> // WalletCard.jsx
> import React, { useState, useEffect } from 'react';
> import RustChain from 'rustchain-js-sdk';
> 
> const client = new RustChain.Client({
>   baseURL: 'https://rustchain.org'
> });
> 
> export function WalletCard({ walletId }) {
>   const [balance, setBalance] = useState(null);
>   const [loading, setLoading] = useState(true);
>   
>   useEffect(() => {
>     async function fetchBalance() {
>       try {
>         const data = await client.getBalance(walletId);
>         setBalance(data.amount_rtc / 1000000);
>       } catch (error) {
>         console.error('Failed to fetch balance:', error);
>       } finally {
>         setLoading(false);
>       }
>     }
>     
>     fetchBalance();
>     const interval = setInterval(fetchBalance, 30000);
>     return () => clearInterval(interval);
>   }, [walletId]);
>   
>   if (loading) return <div>加载中...</div>;
>   
>   return (
>     <div className="wallet-card">
>       <h2>💰 余额</h2>
>       <div className="balance">{balance?.toFixed(6)} RTC</div>
>     </div>
>   );
> }
> ```
> 
> **[画面]: Vue 组件示例]
> 
> Vue 用户也可以类似集成。SDK 支持所有主流框架！

---

### 系列总结 (8:30 - 9:30)

**[画面]: 五集内容回顾 montage]

**旁白**:
> 恭喜你完成了整个 RustChain 教程系列！
> 
> 让我们一起回顾：
> 
> **[画面]: 第 1 集封面]
> **第 1 集**: RustChain 入门指南
> - 什么是 Proof-of-Antiquity
> - 安装和开始挖矿
> 
> **[画面]: 第 2 集封面]
> **第 2 集**: API 开发实战
> - REST API 基础
> - 构造和签名交易
> 
> **[画面]: 第 3 集封面]
> **第 3 集**: BoTTube 平台介绍
> - AI 驱动的视频平台
> - SDK 和 API 集成
> 
> **[画面]: 第 4 集封面]
> **第 4 集**: Python SDK 实战
> - 自动化应用开发
> - 监控和数据分析
> 
> **[画面]: 第 5 集封面]
> **第 5 集**: JavaScript SDK 与网页钱包
> - 浏览器集成
> - 前端应用开发
> 
> **[画面]: 资源汇总]
> 
> 所有资源都在这里：
> - GitHub: github.com/Scottcjn/Rustchain
> - 文档：rustchain.org/docs
> - Discord: discord.gg/VqVVS2CW9Q
> - BoTTube: bottube.ai
> 
> 感谢你的观看！
> 
> 现在你已经掌握了 RustChain 开发的所有技能。
> 
> 开始构建你的应用吧！

**[画面]: Logo 动画 + 结束音乐 + 所有社交媒体链接**

---

## 💻 演示代码

### 1. React 完整钱包组件

```jsx
// CompleteWallet.jsx
import React, { useState, useEffect } from 'react';
import RustChain from 'rustchain-js-sdk';

const client = new RustChain.Client({
  baseURL: 'https://rustchain.org'
});

export function CompleteWallet() {
  const [walletId, setWalletId] = useState('');
  const [balance, setBalance] = useState(null);
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [transactions, setTransactions] = useState([]);
  
  useEffect(() => {
    if (walletId) {
      client.walletId = walletId;
      refreshBalance();
      loadTransactions();
    }
  }, [walletId]);
  
  const refreshBalance = async () => {
    try {
      const data = await client.getBalance(walletId);
      setBalance(data.amount_rtc / 1000000);
    } catch (error) {
      console.error('Failed to fetch balance:', error);
    }
  };
  
  const loadTransactions = async () => {
    try {
      const txs = await client.getTransactions(walletId);
      setTransactions(txs.slice(0, 10));
    } catch (error) {
      console.error('Failed to load transactions:', error);
    }
  };
  
  const handleTransfer = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    
    try {
      const result = await client.transfer({
        to: recipient,
        amount: Math.floor(parseFloat(amount) * 1000000),
        fee: 1000
      });
      
      if (result.tx_id) {
        setStatus({
          type: 'success',
          message: `Transfer successful! TX: ${result.tx_id}`
        });
        setRecipient('');
        setAmount('');
        refreshBalance();
        loadTransactions();
      } else {
        setStatus({
          type: 'error',
          message: `Transfer failed: ${result.error}`
        });
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: `Error: ${error.message}`
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="wallet-container">
      <h1>🦀 RustChain Wallet</h1>
      
      <div className="card">
        <label>Wallet ID</label>
        <input
          type="text"
          value={walletId}
          onChange={(e) => setWalletId(e.target.value)}
          placeholder="Enter your wallet ID"
        />
      </div>
      
      {walletId && (
        <>
          <div className="card">
            <h2>Balance</h2>
            <div className="balance">
              {balance !== null ? `${balance.toFixed(6)} RTC` : 'Loading...'}
            </div>
            <button onClick={refreshBalance}>Refresh</button>
          </div>
          
          <div className="card">
            <h2>Send Transfer</h2>
            <form onSubmit={handleTransfer}>
              <input
                type="text"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                placeholder="Recipient wallet ID"
                required
              />
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Amount (RTC)"
                step="0.000001"
                min="0"
                required
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
            
            {status && (
              <div className={`status ${status.type}`}>
                {status.message}
              </div>
            )}
          </div>
          
          <div className="card">
            <h2>Transaction History</h2>
            <ul className="tx-list">
              {transactions.map((tx, i) => (
                <li key={i} className="tx-item">
                  <span>{tx.type === 'send' ? '📤' : '📥'}</span>
                  <span>{tx.type === 'send' ? 'To' : 'From'}: {tx.counterparty}</span>
                  <span className={tx.type === 'send' ? 'negative' : 'positive'}>
                    {tx.type === 'send' ? '-' : '+'}{(tx.amount / 1000000).toFixed(6)} RTC
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
```

### 2. TypeScript 类型定义

```typescript
// rustchain-js-sdk.d.ts
declare module 'rustchain-js-sdk' {
  export interface ClientOptions {
    baseURL: string;
    walletId?: string;
    privateKey?: string;
  }
  
  export interface HealthResponse {
    ok: boolean;
    version: string;
    uptime: number;
  }
  
  export interface EpochResponse {
    epoch: number;
    slot: number;
    height: number;
  }
  
  export interface BalanceResponse {
    amount_rtc: number;
    miner_id: string;
  }
  
  export interface TransferRequest {
    to: string;
    amount: number; // in satoshis
    fee?: number;
  }
  
  export interface TransferResponse {
    tx_id?: string;
    error?: string;
  }
  
  export interface Transaction {
    tx_id: string;
    type: 'send' | 'receive';
    counterparty: string;
    amount: number;
    fee: number;
    timestamp: string;
    confirmed: boolean;
  }
  
  export class Client {
    constructor(options: ClientOptions);
    
    walletId: string;
    
    health(): Promise<HealthResponse>;
    getEpoch(): Promise<EpochResponse>;
    getBalance(walletId: string): Promise<BalanceResponse>;
    transfer(request: TransferRequest): Promise<TransferResponse>;
    getTransactions(walletId: string, limit?: number): Promise<Transaction[]>;
    getTransaction(txId: string): Promise<Transaction>;
  }
  
  export default RustChain;
}
```

---

## 🎨 视觉设计

### 网页钱包 UI
- 简洁现代设计
- 移动端响应式
- 清晰的状态反馈

### 代码展示
- 使用 VS Code 深色主题
- JavaScript/React 语法高亮
- 实时浏览器预览

### 动画
- 页面切换使用淡入淡出
- 按钮点击有反馈动画
- 加载状态显示进度

---

## 📋 录制清单

### 录制前准备
- [ ] 准备完整的网页钱包 demo
- [ ] 测试所有功能
- [ ] 准备 React 示例项目
- [ ] 设置本地开发环境

### 录制中注意
- [ ] 展示完整的开发流程
- [ ] 解释关键代码逻辑
- [ ] 演示浏览器调试
- [ ] 强调安全最佳实践

### 录制后检查
- [ ] 代码清晰可读
- [ ] UI 演示流畅
- [ ] 时长控制在 8-10 分钟
- [ ] 添加系列回顾和总结

---

## 📝 视频描述模板

```markdown
# RustChain 教程 #5: JavaScript SDK 与网页钱包（系列最终集）

RustChain 教程系列的最终集！学会使用 JavaScript SDK 构建网页钱包应用！

在这集里，你将学会：
✅ 安装 RustChain JavaScript SDK
✅ 在浏览器中使用 SDK
✅ 构建完整的网页钱包
✅ 集成到 React/Vue 项目
✅ 系列总结和下一步学习路径

⏱️ 时间戳:
0:00 - 开场回顾
0:45 - 安装 JavaScript SDK
2:00 - SDK 基础用法
4:00 - 构建网页钱包
7:00 - React 集成示例
8:30 - 系列总结

🔗 资源链接:
- JavaScript SDK: https://github.com/Scottcjn/Rustchain/tree/main/js-sdk
- 完整示例代码：[GitHub Issue 链接]
- 文档：https://rustchain.org/docs/sdk/javascript
- React 示例：[CodeSandbox 链接]

📺 系列回顾:
第 1 集：RustChain 入门指南
第 2 集：API 开发实战
第 3 集：BoTTube 平台介绍
第 4 集：Python SDK 实战
第 5 集：JavaScript SDK 与网页钱包（本集）

🎯 下一步:
- 加入 Discord 社区：discord.gg/VqVVS2CW9Q
- 参与 Bounty 计划：github.com/Scottcjn/rustchain-bounties
- 开始构建你的应用！

感谢观看整个系列！🎉

#RustChain #JavaScript #React #网页开发 #区块链 #RTC #教程
```

---

**脚本完成时间**: 2026-03-13 15:45  
**状态**: ✅ 5/5 脚本全部完成！
