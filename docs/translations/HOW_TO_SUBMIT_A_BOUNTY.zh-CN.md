# 如何提交真正能获得付款的赏金 PR

> 原文：`docs/HOW_TO_SUBMIT_A_BOUNTY.md`
> 对应任务：rustchain-bounties#12027，本文件为简体中文本地化版本。

> **适用于 AI 代理和人类贡献者。**
> 这份指南存在的原因很直接：2026-04-09 提交的 14 个 PR 中，有 11 个因为可避免的问题被关闭。我们希望你的工作能成功。

## 五条规则

遵守这些规则，你的 PR 会得到公平审核。忽略它们，你的 PR 很可能会被关闭。

### 1. 写代码前先验证真实 API

**RustChain 节点位于 `https://50.28.86.131`。**

它不在下面这些凭空想象出来的地址：

- `https://api.rustchain.io`
- `https://api.rustchain.io/v1`
- `https://rustchain.org/api`

在写任何集成代码之前，先运行：

```bash
curl https://50.28.86.131/health
```

你应该看到类似这样的返回：

```json
{"ok": true, "version": "2.2.1-rip200", "uptime_s": 77, "db_rw": true}
```

如果你的代码基于 `api.rustchain.io` 或其他不存在的 URL 编写，PR 会被判定为 LLM 幻觉并关闭。

### 2. 引用文件前先验证真实路径

先克隆仓库，并确认文件确实存在：

```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
ls node/        # 查看真实 node 文件
ls miners/      # 查看真实 miner 文件
ls scripts/     # 查看真实 scripts 文件
```

**不要编造文件名。** 2026-04-09，我们收到过一份 377 行的“安全审计”，其中审计了 `sophia_inspector.py`、`sophia_db.py`、`sophia_scheduler.py` 和 `sophia_dashboard.py`，但这些文件一个都不存在。整份审计被立即关闭。

如果你的 PR 写了类似“`foo.py` 中 `build_user_prompt()` 第 94 行”的内容，审核者会运行：

```bash
gh api repos/Scottcjn/Rustchain/contents/foo.py
```

如果返回 404，你的 PR 会被关闭。

### 3. 一个 PR 只对应一个赏金，并保持范围清晰

比如，“Dockerize the miner” 这个赏金 PR 应该只包含：

- `docker/Dockerfile`
- `docker/docker-compose.yml`
- `docker/entrypoint.sh`
- `docker/README.md`

它不应该包含：

- 跨 5 个子系统的 11 个文件
- 重写仓库主 README
- `bcos/badge-generator.html`，这是另一个赏金
- `silicon-obituary/`，这也是另一个赏金
- `node_modules/`
- `.pyc` 编译文件

**如果你想认领三个赏金，请提交三个独立 PR。** 审核者无法给大杂烩 PR 支付部分赏金，因为他们无法判断哪一部分才是实际交付。

### 4. 不要重写仓库主 README

`rustchain-bounties` 的 README 是赏金看板入口，包含：

- 开放赏金数量
- 已支付 RTC 总额
- Stars、BCOS 徽章
- 赏金浏览、简单任务、红队、付款账本等链接

如果你把它替换成自己的文档，就等于抹掉了赏金看板。多个 PR 已经因为这个原因被关闭。

新内容应该放在正确位置：

- 协议文档：放在 `Rustchain` 仓库的 `docs/`
- Docker 设置：放在 `docker/README.md`
- 集成指南：放在 `docs/integrations/YOUR_TOPIC.md`

### 5. 提交前做端到端验证

点击“Create pull request”之前，先跑完这份检查清单：

- [ ] 代码真的能运行吗？不要提交会触发 `NameError` 的 Python。
- [ ] 它调用的是真实 API 吗？`curl https://50.28.86.131/health` 是否可用？
- [ ] 是否误提交了 `.pyc`、`__pycache__/`、`node_modules/` 或 `.DS_Store`？请删除。
- [ ] PR 是否只对应一个赏金？文件数量超过 15 个通常就需要重新拆分。
- [ ] PR 描述是否说明了要认领哪个赏金，并提供钱包 ID？

## 好的 PR 长什么样

下面这些 PR 和 11 个被关闭的 PR 是同一天合并的。可以学习它们的做法：

| PR | 做对了什么 |
|----|------------|
| [Rustchain#2186](https://github.com/Scottcjn/Rustchain/pull/2186) by @createkr | 5 个聚焦文件、dry-run 模式、安全上限、真实 API、重复提交防护 |
| [rustchain-bounties#2871](https://github.com/Scottcjn/rustchain-bounties/pull/2871) by @stevehuuuu | 17 个文件都在 `sdk/python/` 下、真实 URL、真实断言、正确异常类 |
| [Rustchain#2189](https://github.com/Scottcjn/Rustchain/pull/2189) by @lx277856602 | 单个 `docs/RUSTCHAIN_PROTOCOL.md` 文件、407 行、真实架构图、正确端点 URL |
| [Rustchain#2182](https://github.com/Scottcjn/Rustchain/pull/2182) by @geldbert | 228 行可执行测试代码，复现真实代码路径中的 bug，并通过 CI 验证 |

这些贡献者都在当天收到了付款。他们都没有一次提交多个赏金。

## AI 代理如何验证自己的工作

如果你是自主代理，请把这个验证步骤加入工作流：

```python
import requests
import subprocess

# 1. 检查真实节点
r = requests.get("https://50.28.86.131/health", verify=False, timeout=10)
assert r.status_code == 200, f"Real node returned {r.status_code}"

# 2. 检查引用的文件是否存在
for path in your_referenced_files:
    result = subprocess.run(
        ["gh", "api", f"repos/Scottcjn/Rustchain/contents/{path}"],
        capture_output=True,
    )
    assert result.returncode == 0, f"File {path} does not exist in the real repo"

# 3. 检查 import 是否引用了不存在的模块
for module in your_imports:
    try:
        __import__(module)
    except ImportError:
        raise RuntimeError(f"Module {module} cannot be imported")
```

如果这三项检查过不了，就不要提交 PR。会产生幻觉的 LLM 通常会在这三项中全部失败。

## 我们会为什么付款

- 针对真实 API 测试过的可运行代码
- 聚焦且只做一件事的 PR
- 有可复现 PoC 的真实 bug
- 与实际代码库一致的文档
- 能体现作者投入的创意内容，例如视频、文章、俳句

## 我们不会为什么付款

- 从未运行过的 LLM 生成代码
- 审计不存在文件的“安全报告”
- 把无关改动塞在一起的大杂烩 PR
- 覆盖赏金看板的 README 替换
- 基于错误前提的 claim，例如“修复坏链接”，但链接其实可用
- 同时向多个赏金批量喷洒提交

## 有疑问怎么办

如果你不确定自己的工作是否符合要求，请在提交前先问。在对应赏金 issue 下留言提问。提前澄清比 PR 被关闭要好。

**我们希望你成功。** 这份指南就是为了让你的下一次提交能赚到 RTC。
