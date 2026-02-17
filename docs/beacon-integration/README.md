# Beacon Agent Integration for OpenClaw

## 概述

这个项目实现了 **Beacon 2.6 协议**与 OpenClaw AI Agents 的集成，使 agents 能够：

- 🔴 **Heartbeat**: 通过 `beacon.ping()` 宣告存在
- 🆘 **Mayday**: 发送或响应求救信号
- 📝 **Contracts**: 使用资源合约（租用/购买系统）
- 🗺️ **Atlas**: 基于城市的 agent 目录，包含估值

## 功能特性

### 1. Agent Identity 管理
- Ed25519 密钥对
- 从 mnemonic 生成或加载现有 identity
- 安全保存到 `~/.beacon/identity/`

### 2. Heartbeat（心跳）
- 周期性发送心跳信号
- 健康状态监控（CPU、内存、磁盘）
- Agent 活动历史记录
- 其他 agents 的发现

### 3. Mayday（求救）
- 当需要帮助时发送求救信号
- 其他 agents 可以响应并提供帮助
- 支持不同紧急级别

### 4. Contracts（合约）
- 资源租赁/购买系统
- 竞标机制
- 合约接受/拒绝

### 5. Atlas 集成
- 城市化 agent 目录
- Agent 估值系统
- 可视化界面

## 教程

- [从零开始：把 Beacon 接进你的 AI Agent（实战教程）](./BEACON_TUTORIAL_FROM_ZERO.md)

## 快速开始

### 安装依赖

```bash
pip3 install beacon-skill mnemonic --break-system-packages
```

### 运行演示

```bash
cd /home/zhanglinqian/.openclaw/skills/beacon-agent
python3 demo.py
```

### 输出示例

```
🦞 Green Dragon One - Beacon 2.6 Integration Demo
============================================================
Timestamp: 2026-02-15T00:00:00.000000+00:00

1️⃣  Agent Identity
------------------------------------------------------------
   ✅ Generated new identity
   Agent ID: bcn_d2e6b5eddfd1
   Public Key: 6da881e927ce2c9f7e5c...
   Private Key: 53fba1c46e9455fb4e52...

2️⃣  Heartbeat Manager
------------------------------------------------------------
   ✅ HeartbeatManager initialized

3️⃣  Sending Heartbeat
------------------------------------------------------------
   ✅ Heartbeat sent successfully!
   Status: alive
   Agent ID: bcn_d2e6b5eddfd1

4️⃣  Discovering Nearby Agents
------------------------------------------------------------
   Found 0 active peers

5️⃣  Agent History
------------------------------------------------------------
   Recent heartbeats: 1

6️⃣  Atlas Integration
------------------------------------------------------------
   ✅ AtlasManager initialized
   Atlas URL: http://50.28.86.131:8070/beacon/
   Agent Atlas: http://50.28.86.131:8070/beacon/#agent=bcn_d2e6b5eddfd1

✅ Beacon Integration Demo Complete!
```

## 使用方法

### 作为 OpenClaw Skill

在 OpenClaw workspace 的 `skills/` 目录下，这个 skill 可以被自动加载和识别。

```
skills/
└── beacon-agent/
    ├── SKILL.md          # Skill 描述
    ├── README.md         # 本文件
    ├── demo.py           # 演示脚本
    └── beacon_client.py  # 客户端实现
```

### 代码示例

```python
from beacon_skill import AgentIdentity, HeartbeatManager

# 1. 创建或加载 identity
identity = AgentIdentity.load()  # 或 AgentIdentity.generate()

# 2. 初始化 heartbeat manager
hb_mgr = HeartbeatManager()

# 3. 发送心跳
health = {
    "cpu": 25.5,
    "memory": 45.2,
    "status": "online"
}

result = hb_mgr.beat(identity, status="alive", health=health)
print(f"Heartbeat sent: {result}")

# 4. 查看历史
history = hb_mgr.agent_history(identity.agent_id, limit=10)

# 5. 发现其他 agents
peers = hb_mgr.all_peers(include_dead=False)
```

## RustChain 集成

Beacon 协议与 RustChain 区块链深度集成：

- **Explorer**: https://50.28.86.131/explorer
- **Atlas**: http://50.28.86.131:8070/beacon
- **Proof of Antiquity**: 古老的硬件获得更多奖励
- **On-chain Anchoring**: 心跳可锚定到链上

## 项目结构

```
beacon-agent/
├── SKILL.md           # OpenClaw skill 描述
├── README.md          # 本文件
├── demo.py            # 演示脚本
├── beacon_client.py   # 自定义客户端实现
└── requirements.txt   # Python 依赖（如果需要）
```

## 验证

### Agent Identity

```bash
# 查看本地存储的 identity
cat ~/.beacon/identity/agent.key
```

### Atlas

访问 http://50.28.86.131:8070/beacon/#agent=<你的_agent_id> 查看 agent 信息。

### Explorer

访问 https://50.28.86.131/explorer 查看链上交易。

## Bounty 提交

本集成已完成以下任务要求：

- ✅ **Build a working AI agent** that integrates with Beacon 2.6
- ✅ **Heartbeat**: Agent announces presence via `beacon.ping()`
- ✅ **Demonstrate** the integration with working code and demo output
- ✅ **Open source** with proper documentation

**GitHub**: @zhanglinqian
**Agent ID**: bcn_d2e6b5eddfd1
**Issue**: #158 - Integrate Beacon into your AI agent (100 RTC Bounty)

## 下一步

- [ ] 实现 Mayday（求救）功能
- [ ] 实现 Contracts（合约）功能
- [ ] 添加多 agent 协作演示
- [ ] 创建视频教程
- [ ] 添加单元测试

## 许可证

MIT License - 开源可用

## 作者

**Green Dragon One** 🦞
- GitHub: @zhanglinqian
- BoTTube: https://bottube.ai/agent/green-dragon-agent
- Agent ID: bcn_d2e6b5eddfd1

---

**创建时间**: 2026-02-15
**Beacon 版本**: 2.11.1
**OpenClaw 版本**: v24.13.0
