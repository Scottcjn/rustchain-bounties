# RustChain 备份和恢复指南

本指南说明如何备份和恢复 RustChain 矿工数据、钱包配置和系统设置。

## 目录

- [备份什么](#备份什么)
- [备份流程](#备份流程)
- [恢复流程](#恢复流程)
- [自动化备份脚本](#自动化备份脚本)
- [故障排除](#故障排除)

---

## 备份什么

RustChain 的关键数据存储在以下位置：

### 1. 矿工数据目录
```
~/.rustchain/
├── rustchain_miner.py      # 矿工程序
├── fingerprint_checks.py   # 硬件指纹检查
├── venv/                   # Python 虚拟环境
├── start.sh                # 启动脚本
└── miner.log               # 矿工日志（运行后生成）
```

### 2. 系统服务配置

**Linux (systemd):**
```
~/.config/systemd/user/rustchain-miner.service
```

**macOS (launchd):**
```
~/Library/LaunchAgents/com.rustchain.miner.plist
```

### 3. 钱包/矿工 ID

钱包名称（miner_id）在安装时设置，用于：
- 接收挖矿奖励
- 身份验证
- 余额查询

**重要：** 钱包名称是您在安装时指定的字符串（例如：`my-miner-wallet` 或 `miner-desktop-1234`）。

---

## 备份流程

### 步骤 1：停止矿工服务

在备份之前，先停止正在运行的矿工服务。

**Linux:**
```bash
systemctl --user stop rustchain-miner
```

**macOS:**
```bash
launchctl stop com.rustchain.miner
```

### 步骤 2：备份矿工数据目录

```bash
# 创建备份目录
mkdir -p ~/rustchain-backup/$(date +%Y%m%d)

# 备份整个 .rustchain 目录
cp -r ~/.rustchain ~/rustchain-backup/$(date +%Y%m%d)/rustchain-data
```

### 步骤 3：备份服务配置

**Linux:**
```bash
cp ~/.config/systemd/user/rustchain-miner.service \
   ~/rustchain-backup/$(date +%Y%m%d)/
```

**macOS:**
```bash
cp ~/Library/LaunchAgents/com.rustchain.miner.plist \
   ~/rustchain-backup/$(date +%Y%m%d)/
```

### 步骤 4：记录钱包信息

```bash
# 记录钱包名称（替换为您的实际钱包名）
echo "your-wallet-name" > ~/rustchain-backup/$(date +%Y%m%d)/wallet-name.txt

# 可选：查询并保存当前余额
curl -sk "https://rustchain.org/wallet/balance?miner_id=your-wallet-name" \
   > ~/rustchain-backup/$(date +%Y%m%d)/wallet-balance.json
```

### 步骤 5：验证备份

```bash
# 检查备份文件是否存在
ls -la ~/rustchain-backup/$(date +%Y%m%d)/

# 验证备份大小（应该大于 10MB，包含 venv）
du -sh ~/rustchain-backup/$(date +%Y%m%d)/rustchain-data
```

### 步骤 6：重新启动矿工服务

**Linux:**
```bash
systemctl --user start rustchain-miner
systemctl --user status rustchain-miner
```

**macOS:**
```bash
launchctl start com.rustchain.miner
launchctl list | grep rustchain
```

---

## 恢复流程

### 场景 1：同一台机器恢复

#### 步骤 1：停止现有服务（如果运行中）

```bash
# Linux
systemctl --user stop rustchain-miner

# macOS
launchctl stop com.rustchain.miner
```

#### 步骤 2：恢复矿工数据

```bash
# 备份当前数据（以防万一）
mv ~/.rustchain ~/.rustchain.old.$(date +%s) 2>/dev/null || true

# 恢复备份
cp -r ~/rustchain-backup/20260312/rustchain-data ~/.rustchain
```

#### 步骤 3：恢复服务配置

**Linux:**
```bash
mkdir -p ~/.config/systemd/user/
cp ~/rustchain-backup/20260312/rustchain-miner.service \
   ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable rustchain-miner
```

**macOS:**
```bash
mkdir -p ~/Library/LaunchAgents/
cp ~/rustchain-backup/20260312/com.rustchain.miner.plist \
   ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.rustchain.miner.plist
```

#### 步骤 4：启动服务并验证

```bash
# Linux
systemctl --user start rustchain-miner
systemctl --user status rustchain-miner
journalctl --user -u rustchain-miner -f

# macOS
launchctl start com.rustchain.miner
launchctl list | grep rustchain
tail -f ~/.rustchain/miner.log
```

#### 步骤 5：验证矿工状态

```bash
# 检查节点健康
curl -sk https://rustchain.org/health | jq .

# 检查矿工是否在线
curl -sk https://rustchain.org/api/miners | jq .

# 查询钱包余额
curl -sk "https://rustchain.org/wallet/balance?miner_id=your-wallet-name" | jq .
```

---

### 场景 2：迁移到新机器

#### 在新机器上：

#### 步骤 1：安装基础依赖

```bash
# 确保 Python 3.8+ 已安装
python3 --version

# 安装必要工具
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y python3 python3-venv curl

# macOS (需要 Homebrew)
brew install python3 curl
```

#### 步骤 2：传输备份文件

```bash
# 使用 scp、rsync 或 USB 驱动器传输
# 示例：使用 scp
scp -r ~/rustchain-backup/20260312 user@new-machine:~/rustchain-backup/
```

#### 步骤 3：恢复数据

```bash
# 创建目录结构
mkdir -p ~/.rustchain
mkdir -p ~/.config/systemd/user/  # Linux
# 或
mkdir -p ~/Library/LaunchAgents/  # macOS

# 恢复矿工数据
cp -r ~/rustchain-backup/20260312/rustchain-data/* ~/.rustchain/

# 恢复服务配置（根据平台选择）
# Linux
cp ~/rustchain-backup/20260312/rustchain-miner.service \
   ~/.config/systemd/user/

# macOS
cp ~/rustchain-backup/20260312/com.rustchain.miner.plist \
   ~/Library/LaunchAgents/
```

#### 步骤 4：重新配置服务（如需要）

如果硬件发生变化，可能需要重新安装矿工：

```bash
# 使用相同的钱包名称重新安装
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | \
   bash -s -- --wallet your-wallet-name
```

#### 步骤 5：启动并验证

```bash
# Linux
systemctl --user daemon-reload
systemctl --user enable rustchain-miner --now
systemctl --user status rustchain-miner

# macOS
launchctl load ~/Library/LaunchAgents/com.rustchain.miner.plist
launchctl start com.rustchain.miner

# 验证
curl -sk https://rustchain.org/health | jq .
curl -sk "https://rustchain.org/wallet/balance?miner_id=your-wallet-name" | jq .
```

---

## 自动化备份脚本

### 备份脚本

创建 `~/rustchain-backup.sh`：

```bash
#!/bin/bash
# RustChain 自动备份脚本

set -e

BACKUP_DIR="$HOME/rustchain-backup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"

echo "🔧 RustChain 备份开始..."

# 创建备份目录
mkdir -p "$BACKUP_PATH"

# 停止服务
echo "⏹️  停止矿工服务..."
if command -v systemctl &>/dev/null; then
    systemctl --user stop rustchain-miner 2>/dev/null || true
elif command -v launchctl &>/dev/null; then
    launchctl stop com.rustchain.miner 2>/dev/null || true
fi

# 备份数据
echo "💾 备份矿工数据..."
cp -r ~/.rustchain "$BACKUP_PATH/rustchain-data"

# 备份配置
if [ -f "$HOME/.config/systemd/user/rustchain-miner.service" ]; then
    cp "$HOME/.config/systemd/user/rustchain-miner.service" "$BACKUP_PATH/"
fi

if [ -f "$HOME/Library/LaunchAgents/com.rustchain.miner.plist" ]; then
    cp "$HOME/Library/LaunchAgents/com.rustchain.miner.plist" "$BACKUP_PATH/"
fi

# 记录钱包信息（需要手动填写）
echo "⚠️  请手动记录您的钱包名称到：$BACKUP_PATH/wallet-name.txt"

# 清理旧备份（保留最近 5 个）
cd "$BACKUP_DIR"
ls -t | tail -n +6 | xargs -r rm -rf

# 重启服务
echo "▶️  重启矿工服务..."
if command -v systemctl &>/dev/null; then
    systemctl --user start rustchain-miner 2>/dev/null || true
elif command -v launchctl &>/dev/null; then
    launchctl start com.rustchain.miner 2>/dev/null || true
fi

echo "✅ 备份完成：$BACKUP_PATH"
echo "📦 备份大小：$(du -sh "$BACKUP_PATH" | cut -f1)"
```

使用：
```bash
chmod +x ~/rustchain-backup.sh
~/rustchain-backup.sh
```

### 定时备份（Cron）

```bash
# 编辑 crontab
crontab -e

# 添加每周备份（每周日 2:00 AM）
0 2 * * 0 /home/youruser/rustchain-backup.sh >> /home/youruser/rustchain-backup.log 2>&1
```

---

## 故障排除

### 问题 1：恢复后矿工不启动

**检查服务状态：**
```bash
# Linux
systemctl --user status rustchain-miner
journalctl --user -u rustchain-miner -n 50

# macOS
launchctl list | grep rustchain
tail -f ~/.rustchain/miner.log
```

**常见原因：**
- Python 虚拟环境路径不正确
- 服务配置文件中的路径需要更新
- 权限问题

**解决方案：**
```bash
# 重新设置虚拟环境
cd ~/.rustchain
rm -rf venv
python3 -m venv venv
./venv/bin/pip install requests -q
```

### 问题 2：钱包余额显示为 0

**检查：**
```bash
# 确认钱包名称正确
cat ~/rustchain-backup/*/wallet-name.txt

# 查询矿工列表
curl -sk https://rustchain.org/api/miners | jq .

# 确认矿工在线
curl -sk https://rustchain.org/health | jq .
```

**可能原因：**
- 钱包名称不匹配
- 矿工尚未完成奖励周期
- 网络延迟

### 问题 3：服务配置加载失败

**Linux systemd:**
```bash
# 重新加载配置
systemctl --user daemon-reload
systemctl --user enable rustchain-miner

# 检查服务文件
cat ~/.config/systemd/user/rustchain-miner.service
```

**macOS launchd:**
```bash
# 验证 plist 文件
plutil -lint ~/Library/LaunchAgents/com.rustchain.miner.plist

# 重新加载
launchctl unload ~/Library/LaunchAgents/com.rustchain.miner.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.rustchain.miner.plist
```

### 问题 4：硬件变更后的恢复

如果更换了硬件（主板、CPU 等），硬件指纹会改变，需要：

1. **使用相同钱包名称重新安装：**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | \
   bash -s -- --wallet your-wallet-name
```

2. **重新进行硬件认证：**
```bash
# 等待矿工自动完成认证
# 查看日志确认
tail -f ~/.rustchain/miner.log
```

3. **验证新硬件的挖矿状态：**
```bash
curl -sk https://rustchain.org/api/miners | jq .
```

---

## 最佳实践

### 备份频率建议

| 场景 | 频率 |
|------|------|
| 日常运行 | 每周一次 |
| 升级前 | 必须备份 |
| 硬件变更前 | 必须备份 |
| 系统重装前 | 必须备份 |

### 备份存储建议

1. **本地备份**：快速恢复
2. **外部存储**：USB 驱动器、外部硬盘
3. **云存储**：加密后上传到云盘
4. **多份拷贝**：至少 2 份不同位置

### 安全注意事项

- ⚠️ **永远不要分享钱包名称给不可信的来源**
- ⚠️ **备份文件加密存储**（包含敏感配置）
- ⚠️ **定期测试恢复流程**（确保备份有效）
- ⚠️ **记录钱包名称在安全位置**（离线存储）

### 加密备份（可选）

```bash
# 使用 GPG 加密备份
gpg -c ~/rustchain-backup/20260312.tar.gz
# 输入密码保护

# 恢复时解密
gpg -d ~/rustchain-backup/20260312.tar.gz.gpg | tar -xz
```

---

## 快速参考命令

```bash
# 检查矿工状态
curl -sk https://rustchain.org/health | jq .

# 查看在线矿工
curl -sk https://rustchain.org/api/miners | jq .

# 查询钱包余额
curl -sk "https://rustchain.org/wallet/balance?miner_id=WALLET_NAME" | jq .

# 停止矿工（Linux）
systemctl --user stop rustchain-miner

# 启动矿工（Linux）
systemctl --user start rustchain-miner

# 查看日志（Linux）
journalctl --user -u rustchain-miner -f

# 查看日志（macOS）
tail -f ~/.rustchain/miner.log
```

---

## 获取帮助

如遇到问题：

1. 检查 [FAQ_TROUBLESHOOTING.md](https://github.com/Scottcjn/Rustchain/blob/main/docs/FAQ_TROUBLESHOOTING.md)
2. 查看矿工日志
3. 在 GitHub 提交 Issue 或参与 Bounty 讨论
4. 加入 Discord 社区：https://discord.gg/VqVVS2CW9Q

---

**文档版本：** 1.0  
**最后更新：** 2026-03-12  
**适用版本：** RustChain Miner v1.1.0+
