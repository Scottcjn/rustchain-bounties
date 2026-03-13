# 🎬 第 1 集：RustChain 入门指南

**时长**: 5-8 分钟  
**难度**: 初学者  
**目标**: 让开发者了解 RustChain 并开始挖矿

---

## 📝 完整脚本

### 开场 (0:00 - 0:30)

**[画面]: RustChain Logo 动画 + 背景音乐**

**旁白**:
> 大家好！欢迎来到 RustChain 教程系列第一集。
> 
> 你是否想过，你的旧电脑也能挖加密货币？
> 
> RustChain 是一个革命性的 Proof-of-Antiquity 区块链，它奖励的是**最老**的硬件，而不是最快的硬件。
> 
> 在这集里，我会教你如何开始挖矿，赚取 RTC 代币。

---

### 什么是 RustChain？(0:30 - 2:30)

**[画面]: 对比图表 - PoW vs PoA**

**旁白**:
> 传统的 Proof-of-Work，比如比特币，奖励的是计算力最强的矿机。
> 
> 这导致了能源浪费和硬件军备竞赛。
> 
> RustChain 完全不同。它的 Proof-of-Antiquity 机制，奖励的是**历史悠久**的硬件。
> 
> **[画面]: 硬件 multiplier 表格**
> 
> 看这个表格：
> - PowerPC G4（1999-2005 年）：2.5 倍奖励
> - PowerPC G5（2003-2006 年）：2.0 倍奖励
> - Apple Silicon（2020+）：1.2 倍奖励
> - 现代 x86_64：1.0 倍基准
> 
> **[画面]: 老式 Mac G4 照片]
> 
> 这意味着，如果你有一台 20 年前的老 Mac，它的挖矿收益比最新电脑还要高！
> 
> 核心理念：**历经数十年考验的真实复古硬件，值得被奖励。**

---

### 快速开始 - 安装 RustChain (2:30 - 5:00)

**[画面]: 终端屏幕录制]

**旁白**:
> 好，让我们开始安装 RustChain。
> 
> 我使用的是 macOS，如果你也是 macOS 用户，我们需要先安装 Homebrew。
> 
> **[画面]: 终端命令]
> 
> 打开终端，输入：
> 
> ```bash
> # 安装 Homebrew（如果还没有）
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
> ```
> 
> **[画面]: Homebrew 安装过程]
> 
> 安装完成后，添加 RustChain 的 tap：
> 
> ```bash
> brew tap Scottcjn/homebrew-tap
> ```
> 
> **[画面]: tap 添加成功]
> 
> 然后安装 RustChain：
> 
> ```bash
> brew install rustchain
> ```
> 
> **[画面]: 安装进度条]
> 
> 安装完成后，设置你的钱包 ID：
> 
> ```bash
> export RUSTCHAIN_WALLET=my-first-wallet
> ```
> 
> **[画面]: 环境变量设置]
> 
> 最后，启动挖矿：
> 
> ```bash
> rustchain-start
> ```
> 
> **[画面]: 挖矿启动，显示硬件信息]
> 
> 看！RustChain 正在检测你的硬件，计算 multiplier，然后开始挖矿！

---

### 验证收益 (5:00 - 6:30)

**[画面]: 浏览器打开区块浏览器]

**旁白**:
> 挖矿启动后，如何查看你的收益呢？
> 
> 有两种方法：
> 
> **方法 1**: 使用 API
> 
> **[画面]: 终端命令]
> 
> ```bash
> curl -sk "https://rustchain.org/wallet/balance?miner_id=my-first-wallet"
> ```
> 
> **[画面]: JSON 响应，显示余额]
> 
> 返回 JSON 格式，显示你的 RTC 余额。
> 
> **方法 2**: 使用区块浏览器
> 
> **[画面]: 浏览器导航到 rustchain.org/explorer]
> 
> 打开浏览器，访问 rustchain.org/explorer
> 
> 在搜索框输入你的钱包 ID：my-first-wallet
> 
> **[画面]: 搜索结果显示余额和交易历史]
> 
> 看！这里显示你的余额、挖矿历史和所有交易记录。
> 
> **[画面]: 健康检查]
> 
> 你还可以检查节点状态：
> 
> ```bash
> curl -sk https://rustchain.org/health
> ```
> 
> 返回 `{"ok": true}` 表示一切正常！

---

### 结尾和预告 (6:30 - 7:00)

**[画面]: 回到主讲人/Logo]

**旁白**:
> 恭喜你！你已经成功开始了 RustChain 挖矿！
> 
> 现在你的旧电脑正在为你赚取 RTC 代币。
> 
> **[画面]: 下一集预告]
> 
> 在下一集里，我会教你如何：
> - 使用 RustChain API
> - 构建转账应用
> - 用 Python 代码与区块链交互
> 
> 这些都是开发者的必备技能！
> 
> **[画面]: 资源链接]
> 
> 本集的资源链接：
> - RustChain GitHub: github.com/Scottcjn/Rustchain
> - 文档：rustchain.org
> - Discord 社区：discord.gg/VqVVS2CW9Q
> 
> 如果你觉得有帮助，请点赞、订阅，并分享给你的朋友！
> 
> 我们下一集见！

**[画面]: Logo 动画 + 结束音乐**

---

## 💻 演示代码

### 1. 安装脚本

```bash
#!/bin/bash
# install-rustchain.sh

echo "🍺 Installing RustChain..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Add RustChain tap
echo "Adding RustChain tap..."
brew tap Scottcjn/homebrew-tap

# Install RustChain
echo "Installing RustChain..."
brew install rustchain

echo "✅ RustChain installed successfully!"
echo ""
echo "Next steps:"
echo "1. Set your wallet: export RUSTCHAIN_WALLET=my-wallet"
echo "2. Start mining: rustchain-start"
echo "3. Check balance: curl -sk 'https://rustchain.org/wallet/balance?miner_id=my-wallet'"
```

### 2. 快速启动脚本

```bash
#!/bin/bash
# start-mining.sh

# Set wallet (or use default)
WALLET=${RUSTCHAIN_WALLET:-"miner-$(hostname)"}

echo "🚀 Starting RustChain Mining..."
echo "Wallet: $WALLET"
echo ""

# Export wallet
export RUSTCHAIN_WALLET=$WALLET

# Start mining
rustchain-start

echo ""
echo "Mining started! Press Ctrl+C to stop."
```

### 3. 余额检查脚本

```bash
#!/bin/bash
# check-balance.sh

WALLET=${1:-$RUSTCHAIN_WALLET}

if [ -z "$WALLET" ]; then
    echo "❌ Error: No wallet specified"
    echo "Usage: $0 [wallet_id]"
    echo "Or set RUSTCHAIN_WALLET environment variable"
    exit 1
fi

echo "💰 Checking balance for: $WALLET"
echo ""

# Get balance
RESPONSE=$(curl -sk "https://rustchain.org/wallet/balance?miner_id=$WALLET")

# Parse and display
if command -v jq &> /dev/null; then
    echo "$RESPONSE" | jq .
else
    echo "$RESPONSE"
fi

echo ""
echo "View in explorer: https://rustchain.org/explorer?miner=$WALLET"
```

### 4. 监控脚本

```bash
#!/bin/bash
# monitor-mining.sh

WALLET=${RUSTCHAIN_WALLET:-"default"}
INTERVAL=${1:-60}  # Default 60 seconds

echo "📊 RustChain Mining Monitor"
echo "Wallet: $WALLET"
echo "Interval: ${INTERVAL}s"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Get balance
    BALANCE=$(curl -sk "https://rustchain.org/wallet/balance?miner_id=$WALLET" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        # Extract amount_rtc (requires jq)
        if command -v jq &> /dev/null; then
            AMOUNT=$(echo "$BALANCE" | jq -r '.amount_rtc')
            echo "[$TIMESTAMP] Balance: $AMOUNT RTC"
        else
            echo "[$TIMESTAMP] Balance: $BALANCE"
        fi
    else
        echo "[$TIMESTAMP] Error: Could not fetch balance"
    fi
    
    sleep $INTERVAL
done
```

---

## 🎨 视觉设计

### 开场动画
- RustChain Logo 旋转出现
- 背景：区块链网络动画
- 音乐：轻快科技感

### 转场效果
- 章节之间使用滑动转场
- 代码演示使用终端录制
- 图表使用动画展示

### 配色方案
- 主色：RustChain 品牌色（橙色/棕色，呼应"Rust"）
- 代码背景：深色主题（#1e1e1e）
- 文字：白色/浅灰色

### 字幕样式
- 字体：思源黑体 / Noto Sans SC
- 大小：24px
- 颜色：白色，黑色描边
- 位置：底部居中

---

## 📋 录制清单

### 录制前准备
- [ ] 清理桌面，关闭无关应用
- [ ] 测试麦克风音质
- [ ] 调整终端字体大小（至少 16px）
- [ ] 设置终端主题（推荐：One Dark / Dracula）
- [ ] 准备演示用的钱包 ID

### 录制中注意
- [ ] 语速适中，清晰发音
- [ ] 命令输入不要太快
- [ ] 等待命令执行完成
- [ ] 出错时暂停，后期剪辑

### 录制后检查
- [ ] 音频质量（无噪音、无爆音）
- [ ] 视频清晰度（1080p）
- [ ] 代码可读性
- [ ] 时长控制（5-8 分钟）

---

## 🎵 背景音乐推荐

### 开场/结尾
- 风格：Upbeat Electronic / Tech House
- 音量：-20dB（低于旁白）
- 推荐：YouTube Audio Library 免版权音乐

### 演示部分
- 风格：Ambient / Lo-fi
- 音量：-25dB（几乎听不见）
- 目的：填补沉默间隙

---

## 📝 视频描述模板

```markdown
# RustChain 教程 #1: 快速入门指南

欢迎来到 RustChain 教程系列第一集！在这集里，你将学会：
✅ 什么是 RustChain 和 Proof-of-Antiquity
✅ 如何安装和配置 RustChain
✅ 开始挖矿赚取 RTC 代币
✅ 查看你的挖矿收益

⏱️ 时间戳:
0:00 - 开场介绍
0:30 - 什么是 RustChain？
2:30 - 安装 RustChain
5:00 - 验证收益
6:30 - 下一集预告

🔗 资源链接:
- RustChain GitHub: https://github.com/Scottcjn/Rustchain
- 官方文档：https://rustchain.org
- 区块浏览器：https://rustchain.org/explorer
- Discord 社区：https://discord.gg/VqVVS2CW9Q

💻 代码示例:
https://github.com/Scottcjn/rustchain-bounties/issues/57

📺 下一集:
RustChain API 开发实战 - 教你用 Python 代码与区块链交互！

#RustChain #区块链 #加密货币 #挖矿 #RTC #教程 #开发
```

---

**脚本完成时间**: 2026-03-13  
**状态**: ✅ 准备录制
