# Bounty Claim Guide - RustChain Pong Port

## 申领指南 (Claim Instructions)

**项目**: RustChain Pong 移植 #473  
**等级**: LEGENDARY Tier  
**奖励**: 200 RTC (~$20 USD)  
**钱包地址**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## 步骤 1: 准备提交材料

### 必需文件

确保以下文件都已创建并包含在提交中：

- [x] `README.md` - 项目概述
- [x] `HARDWARE_RESEARCH.md` - 硬件架构研究
- [x] `BADGE_ONLY_DESIGN.md` - 设计方案
- [x] `PR_TEMPLATE.md` - PR 描述模板
- [x] `pong_miner_simulator.py` - Python 模拟器
- [x] `CLAIM_BOUNTY.md` - 本文件

### 可选文件

- [ ] `assets/` - 图片和图表
- [ ] `tests/` - 测试脚本
- [ ] `requirements.txt` - Python 依赖

---

## 步骤 2: 创建 GitHub PR

### 2.1 Fork 仓库

```bash
# 访问 RustChain miners 仓库
# 点击 "Fork" 按钮创建你的副本
```

### 2.2 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/rustchain-miners.git
cd rustchain-miners
```

### 2.3 创建分支

```bash
git checkout -b feature/pong-miner-port-473
```

### 2.4 添加项目文件

```bash
# 创建 pong 目录
mkdir -p miners/pong

# 复制所有文件
cp -r /path/to/pong-miner/* miners/pong/

# 添加到 git
git add miners/pong/
```

### 2.5 提交更改

```bash
git commit -m "feat: Add Pong (1972) miner port - LEGENDARY Tier #473

- Complete hardware research on Atari Pong architecture
- Badge Only implementation design
- Python simulator demonstrating the concept
- Comprehensive documentation
- Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b"
```

### 2.6 推送到 GitHub

```bash
git push origin feature/pong-miner-port-473
```

### 2.7 创建 Pull Request

1. 访问你的 fork 仓库
2. 点击 "Pull requests" → "New pull request"
3. 选择分支：`feature/pong-miner-port-473`
4. 使用 `PR_TEMPLATE.md` 中的内容作为 PR 描述
5. 确保包含钱包地址
6. 点击 "Create pull request"

---

## 步骤 3: PR 描述模板

复制以下内容到 PR 描述：

```markdown
# Pull Request: Port Miner to Atari Pong (1972)

**Issue**: #473  
**Tier**: LEGENDARY  
**Reward**: 200 RTC (~$20 USD)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## Description

This PR implements a conceptual port of the RustChain miner to **Atari Pong (1972)**, the world's first commercially successful arcade video game.

### Key Features

- ✅ Complete hardware research on Pong's TTL-based architecture
- ✅ Badge Only implementation (due to no CPU/RAM limitations)
- ✅ Working Python simulator
- ✅ Comprehensive documentation

### Files Added

- `miners/pong/README.md`
- `miners/pong/HARDWARE_RESEARCH.md`
- `miners/pong/BADGE_ONLY_DESIGN.md`
- `miners/pong/pong_miner_simulator.py`
- `miners/pong/CLAIM_BOUNTY.md`

## Testing

```bash
cd miners/pong
python pong_miner_simulator.py
```

## Bounty Claim

**Wallet Address**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

Thank you for reviewing! 🕹️⛏️
```

---

## 步骤 4: 等待审核

### 审核时间

- **通常**: 1-7 天
- **最长**: 30 天

### 可能的审核意见

#### ✅ 批准

```
Approved! Great work on the historical research and creative approach.
The Badge Only solution is clever given the hardware limitations.
```

**下一步**: 等待奖励发放

#### 🔧 需要修改

```
Thanks for the submission! A few minor changes needed:
1. Add more details to the hardware research
2. Include test results from the simulator
3. Verify wallet address format
```

**下一步**: 根据反馈修改并重新提交

#### ❌ 拒绝

```
Unfortunately, this doesn't meet the requirements because...
```

**下一步**: 询问具体原因，考虑申诉或重新设计

---

## 步骤 5: 接收奖励

### 奖励发放

一旦 PR 被合并：

1. **自动发放**: 某些项目使用自动奖励系统
2. **手动发放**: 需要团队手动发送 RTC

### 确认接收

```bash
# 检查你的钱包余额
rustchain-cli balance RTC4325af95d26d59c3ef025963656d22af638bb96b
```

### 预期金额

- **基础奖励**: 200 RTC
- **美元价值**: ~$20 USD (根据当前汇率)

---

## 常见问题 (FAQ)

### Q: 我的 PR 多久会被审核？

**A**: 通常 1-7 天。如果超过 30 天没有回复，可以礼貌地 ping 项目维护者。

### Q: 如果 PR 被拒绝怎么办？

**A**: 
1. 询问具体拒绝原因
2. 根据反馈修改
3. 重新提交
4. 如果认为决定不公，可以友好地申诉

### Q: 我可以修改钱包地址吗？

**A**: 一旦提交，最好不要修改。如果需要修改，请在 PR 评论中说明。

### Q: 奖励何时发放？

**A**: 通常在 PR 合并后 1-14 天内。某些项目使用批量发放。

### Q: 我可以提交多个矿工移植吗？

**A**: 可以！每个符合条件的移植都可以获得奖励。

---

## 联系支持

如果有问题：

1. **GitHub Issues**: 在项目仓库创建 issue
2. **Discord/Telegram**: 加入社区群组
3. **Email**: 查看项目联系方式

---

## 成功提交清单

在提交前确认：

- [ ] 所有必需文件都已创建
- [ ] 钱包地址正确无误
- [ ] PR 描述完整
- [ ] 模拟器可以运行
- [ ] 文档没有拼写错误
- [ ] 使用了正确的分支命名
- [ ] 提交信息清晰

---

## 示例时间线

```
Day 0:  提交 PR
Day 2:  审核者提出问题
Day 3:  回复并修改
Day 5:  PR 被批准
Day 7:  PR 被合并
Day 14: 奖励发放到钱包
```

---

## 庆祝你的成就！🎉

恭喜你完成了历史上最不可能的矿工移植之一！

- 你研究了 50 年前的硬件
- 你创造性地解决了不可能的挑战
- 你为社区贡献了有趣的教育内容
- 你获得了 LEGENDARY Tier 奖励

**享受你的 200 RTC！** 🍾

---

*最后更新：2026-03-14*  
*RustChain Pong Port Project #473*
