# LinkedIn Scraper - RustChain Integration

🦞 LinkedIn 数据抓取工具 - RustChain Bounty 项目

## 功能

- ✅ 抓取 LinkedIn 个人资料
- ✅ 抓取公司数据
- ✅ 搜索功能演示
- ✅ 支持免费代理（Bright Data, Oxylabs, Smartproxy）
- ✅ 支持本地 IP 直接访问（简化版）

## 快速开始

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 proof 脚本
python3 linkedin_scraper.py
```

### 部署到 Railway

1. 创建 Railway 项目
2. 连接 GitHub 仓库
3. 配置环境变量（可选）:
   - `PROXY_URL`: 代理地址（如果使用代理）
4. 自动部署

## Proof 输出

运行脚本后生成 `proof_output.json`:

```json
{
  "timestamp": "2026-03-14 17:36:29",
  "profiles": [10 个个人资料],
  "companies": [3 个公司数据],
  "search_demo": [5 个搜索结果]
}
```

## 环境变量

```bash
# .env 文件
PROXY_URL=http://your-proxy.com:port
USE_PROXY=false  # true/false
```

## Bounty 提交

- **钱包地址**: `6eUdVwsPArTxwVqEARYGCh4S2qwW2zCs7jSEDRpxydnv`
- **任务类型**: LinkedIn 数据抓取演示
- **完成状态**: ✅ 已完成 proof 脚本

## 注意事项

⚠️ LinkedIn 有严格的反爬机制，建议:
- 使用代理避免 IP 被封
- 控制请求频率
- 遵守 LinkedIn 服务条款
- 仅用于学习和研究目的

## License

MIT
