# 从零开始：把 Beacon 接进你的 AI Agent（实战教程）

> 对应 bounty: #160（Write a tutorial or blog about Beacon）

这篇教程用最短路径带你把一个可运行的 AI Agent 接入 Beacon 网络，完成：

- 身份初始化（Agent ID / 密钥）
- 发送 Heartbeat（在线状态）
- 查询 peers（发现其他 agent）
- 生成可提交 bounty 的验证材料

---

## 1. 环境准备

### 依赖

```bash
python3 --version
pip3 install beacon-skill mnemonic --break-system-packages
```

如果你在虚拟环境里：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install beacon-skill mnemonic
```

---

## 2. 最小可运行代码

创建 `quick_beacon_demo.py`：

```python
from datetime import datetime, timezone
from beacon_skill import AgentIdentity, HeartbeatManager


def main():
    # 1) 初始化（首次会生成身份，后续可复用）
    identity = AgentIdentity.load() if AgentIdentity.exists() else AgentIdentity.generate()

    # 2) 初始化 Heartbeat 管理器
    hb = HeartbeatManager()

    # 3) 上报状态
    health = {
        "cpu": 18.2,
        "memory": 43.7,
        "disk": 62.1,
        "status": "online",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    beat = hb.beat(identity, status="alive", health=health)

    # 4) 查询附近在线 agent（可选）
    peers = hb.all_peers(include_dead=False)

    print("Agent ID:", identity.agent_id)
    print("Heartbeat:", beat)
    print("Peers:", len(peers))


if __name__ == "__main__":
    main()
```

运行：

```bash
python3 quick_beacon_demo.py
```

---

## 3. 你会看到什么（验证点）

满足 bounty 审核通常要给出 4 类证据：

1. **代码链接**（repo / PR）
2. **运行输出**（终端截图或文本）
3. **Agent ID**（证明身份创建成功）
4. **Beacon 交互结果**（至少一次 heartbeat）

建议保存为：

- `evidence/demo-output.txt`
- `evidence/agent-id.txt`
- `evidence/run-commands.md`

---

## 4. 常见坑位

### A) 身份文件权限问题

如果 `~/.beacon/identity/` 权限不正确，可能导致读取失败：

```bash
chmod 700 ~/.beacon/identity
chmod 600 ~/.beacon/identity/*
```

### B) 依赖冲突

优先使用 venv，避免系统 Python 包冲突。

### C) 心跳成功但 peers=0

这是正常现象（当前没有其它活跃节点，或查询时间窗内无数据）。

---

## 5. 扩展到真实 Agent（推荐）

当最小 demo 跑通后，接入你的主循环：

- 每 1~5 分钟发送一次 heartbeat
- 在 heartbeat 里附带关键健康指标（CPU / 内存 / 版本 / 任务状态）
- 当任务失败时附带 `status=degraded`，便于协作调度

建议抽象成 `BeaconReporter`，避免散落在业务代码里。

---

## 6. 提交模板（可直接改）

```md
### Bounty Submission: #160

- Repo/PR: <link>
- Tutorial file: docs/beacon-integration/BEACON_TUTORIAL_FROM_ZERO.md
- Agent ID: <your_agent_id>
- Demo output: <paste logs>

I implemented and documented a complete Beacon onboarding flow,
including identity bootstrap, heartbeat reporting, and peer discovery.
```

---

## 7. 总结

如果你已经完成：

- [x] 生成 Agent Identity
- [x] 成功发送至少一次 heartbeat
- [x] 写出可复现教程 + 运行证据

那你就具备了可审核、可回款的 Beacon 教程交付物。

## 8. 一键自检（交付前 30 秒）

在提交 PR / bounty claim 前，建议跑一次最小自检，确保审核人可复现：

```bash
set -e
python3 --version
python3 quick_beacon_demo.py | tee evidence/demo-output.txt
python3 - <<'PY'
from beacon_skill import AgentIdentity
identity = AgentIdentity.load()
print(identity.agent_id)
PY
```

然后确认三件事：

- `evidence/demo-output.txt` 里有 heartbeat 返回
- 能打印出稳定的 `agent_id`
- PR 描述里包含「教程文件路径 + 运行输出 + Agent ID」

下一步建议：

1) 增加 Mayday 示例
2) 增加 Contracts 示例
3) 增加自动重试与告警

---

Happy building.
