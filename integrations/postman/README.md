# RustChain API Postman Collection

## 概述

这是 RustChain Proof-of-Antiquity Blockchain 的完整 Postman API 集合，覆盖了所有公开 API 端点。

**奖励：** 3 RTC  
**Issue:** [#1617](https://github.com/Scottcjn/rustchain-bounties/issues/1617)

## 端点分类

### 1. Health & Status（健康检查）
- `GET /health` - 节点健康状态检查

### 2. Epoch & Network（ epoch 和网络信息）
- `GET /epoch` - 当前 epoch 信息

### 3. Miners（矿工）
- `GET /api/miners` - 活跃矿工列表

### 4. Wallet（钱包）
- `GET /wallet/balance?miner_id={id}` - 查询钱包余额

### 5. Governance（治理）
- `GET /governance/proposals` - 列出治理提案
- `POST /governance/propose` - 创建新提案
- `GET /governance/proposal/{id}` - 获取提案详情
- `POST /governance/vote` - 提交投票
- `GET /governance/ui` - 治理 UI 页面

### 6. Premium API (x402)（高级 API）
- `GET /api/premium/videos` - 批量视频导出（BoTTube）
- `GET /api/premium/analytics/` - 深度代理分析（BoTTube）
- `GET /api/premium/reputation` - 完整声誉导出（Beacon Atlas）
- `GET /wallet/swap-info` - USDC/wRTC 交换指导

### 7. Explorer（浏览器）
- `GET /explorer` - 区块浏览器 UI

## 使用方法

### 导入 Postman

1. 打开 Postman
2. 点击 **Import**
3. 选择 `rustchain-postman-collection.json`
4. 集合将出现在你的工作区

### 环境变量

集合使用以下变量：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `baseUrl` | `https://rustchain.org` | RustChain API 基础 URL |
| `minerId` | `test` | 矿工 ID/钱包名称 |
| `proposalId` | `1` | 治理提案 ID |

### 测试 API

1. 导入集合后，展开各个文件夹
2. 点击任意请求发送
3. 查看响应结果

## 已验证的端点

以下端点已通过测试并包含示例响应：

- ✅ `GET /health` - 返回节点状态、版本、运行时间
- ✅ `GET /epoch` - 返回 epoch 编号、slot、矿工数量、RTC 总供应量
- ✅ `GET /api/miners` - 返回活跃矿工列表及硬件信息
- ✅ `GET /wallet/balance?miner_id=test` - 返回钱包余额

## 注意事项

1. **SSL 证书**: RustChain 节点可能使用自签名 SSL 证书，在某些客户端中需要禁用证书验证
2. **Governance 端点**: 部分治理端点可能返回 404（如果没有活跃提案）
3. **Premium API**: x402 高级 API 端点目前免费使用（证明流程阶段）

## 技术细节

- **认证**: 无需认证（公开 API）
- **格式**: 所有响应均为 JSON 格式（除 UI 页面外）
- **速率限制**: 未文档化，建议合理请求

## 贡献

此集合由社区贡献，用于 RustChain 赏金计划 #1617。

---

**创建时间:** 2026-03-12  
**版本:** 1.0.0  
**Postman Schema:** v2.1.0
