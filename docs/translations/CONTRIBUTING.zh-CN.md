# 贡献指南 - RustChain 赏金项目

感谢你对 RustChain 赏金项目的关注！本指南说明了如何参与赏金计划、认领任务、提交证明并赚取 RTC 代币。

## 快速开始

1. **Fork** 本仓库
2. **Clone** 你的 Fork 到本地
3. **创建分支** (`git checkout -b feature/my-contribution`)
4. **进行修改** 并测试
5. **提交** 并附上清晰的提交信息
6. **推送** 到你的 Fork 并创建 **Pull Request**

## 赚取 RTC 代币

所有被合并的贡献都能获得 RTC 代币！赏金等级如下：

| 等级 | 奖励 | 示例 |
| ---- | ------ | -------- |
| 微型 | 1-10 RTC | 修复拼写、小型文档、简单测试 |
| 标准 | 20-50 RTC | 新功能、重构、新接口 |
| 重要 | 75-100 RTC | 安全修复、共识改进 |
| 关键 | 100-150 RTC | 漏洞修复、协议升级 |

浏览 [开放赏金](https://github.com/Scottcjn/rustchain-bounties/issues) 查看具体 RTC 奖励的任务。

## 赏金工作流程

### 寻找赏金
1. 前往 [RustChain 赏金仓库的 Issues 页面](https://github.com/Scottcjn/rustchain-bounties/issues)
2. 查找带有赏金标签的 Issue（如 `[DOC]`、`[FEAT]`、`[BUG]`）
3. 查看 Issue 描述中的 RTC 奖励信息
4. **重要**：认领任何赏金前，请阅读 [反刷单规则 (#452)](https://github.com/Scottcjn/rustchain-bounties/issues/452)

### 认领赏金
1. **检查是否已被认领**：阅读 Issue 评论，确认是否有人已认领
2. **认领格式**：在 Issue 中评论：
   ```
   **认领此赏金。**

   [简要描述你的方案]

   预计完成时间：[时间]
   -你的GitHub用户名
   ```
3. **等待确认**：如果无人认领，你可以开始工作
4. **开始工作**：Fork 仓库并开始实现

### 钱包格式
- **使用钱包名称，而非地址**：`your-wallet-name`（如 `maojianian25-png`）
- **不要在评论中包含加密货币地址**
- 钱包名称用于在账本中追踪 RTC 收益

### 证明要求
需要完成证明的赏金：
1. **截图**：清晰的全屏截图，展示功能正常运行
2. **代码片段**：已实现代码的相关部分
3. **测试结果**：测试命令的输出
4. **视频演示**（可选）：适用于复杂的 UI/UX 功能

### 提交流程
1. 在 Fork 的仓库中**完成工作**
2. **创建 Pull Request** 到主仓库
3. **关联 Issue**：在 PR 描述中包含 `Closes #<issue_number>`
4. **提供证明**：在 PR 评论中附上截图或其他要求的证明
5. **等待审核**：维护者将在 48-72 小时内审核

### 审核通过后
1. **PR 被合并**：审核通过后，维护者将合并你的 PR
2. **RTC 分发**：RTC 代币将分发到你的钱包名称
3. **记录在案**：你的贡献将记录在 [BOUNTY_LEDGER.md](BOUNTY_LEDGER.md) 中

## 行为准则

- 尊重所有贡献者
- 不要刷单或重复提交
- 提供真实、有意义的贡献
- 遵守 [行为准则](CODE_OF_CONDUCT.md)

## 安全报告

如果你发现安全漏洞，请**不要**公开报告。请通过 GitHub 的[私人漏洞报告](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)功能报告。

## 获取帮助

- [Discord](https://discord.gg/VqVVS2CW9Q)
- [GitHub Issues](https://github.com/Scottcjn/rustchain-bounties/issues)

感谢你的贡献！
