# BoTTube Parasocial Hooks - Issue #2286

**价值**: 25 RTC
**状态**: 开发中
**认领时间**: 2026-03-29 15:28
**预计完成**: 2026-03-30 15:28（24 小时内）

---

## 📋 需求分析

### 核心功能
1. **Viewer/Commenter Tracking** - 追踪每个 agent 的观众
2. **Regular Viewer Identification** - 识别常客（评论 3+ 视频）
3. **Newcomer Detection** - 识别新观众
4. **Shoutout UI Component** - 在视频中展示感谢

### 技术方案
- 后端：Node.js/Python API
- 前端：React 组件
- 数据库：SQLite/PostgreSQL

---

## 🚀 开发计划

### Phase 1: 数据库设计（2 小时）
- [ ] 设计 viewer_tracks 表
- [ ] 设计 agent_stats 表
- [ ] 创建迁移脚本

### Phase 2: 后端 API（4 小时）
- [ ] GET /api/agent/:id/viewers - 获取观众列表
- [ ] GET /api/agent/:id/regulars - 获取常客列表
- [ ] GET /api/agent/:id/newcomers - 获取新观众
- [ ] POST /api/agent/:id/shoutout - 触发 shoutout

### Phase 3: 前端组件（4 小时）
- [ ] ShoutoutBanner 组件
- [ ] RegularViewerList 组件
- [ ] NewcomerWelcome 组件
- [ ] 集成到 BoTTube watch page

### Phase 4: 测试（3 小时）
- [ ] 单元测试（≥10 个）
- [ ] 集成测试
- [ ] E2E 测试

### Phase 5: 文档（1 小时）
- [ ] API 文档
- [ ] 使用示例
- [ ] README 更新

---

## 📁 文件结构

```
bottube-parasocial-2286/
├── backend/
│   ├── api.py
│   ├── database.py
│   └── tests/
├── frontend/
│   ├── components/
│   │   ├── ShoutoutBanner.tsx
│   │   ├── RegularViewerList.tsx
│   │   └── NewcomerWelcome.tsx
│   └── tests/
├── migrations/
│   └── 001_add_parasocial_tracking.sql
├── tests/
│   ├── test_api.py
│   ├── test_components.tsx
│   └── test_e2e.py
├── README.md
└── package.json
```

---

## ✅ 检查清单

### 提交前
- [ ] 所有功能完成
- [ ] ≥10 个测试用例通过
- [ ] 代码审查通过
- [ ] 文档完善
- [ ] 检查脚本通过

### 收款信息
**RTC**: RTCb72a1accd46b9ba9f22dbd4b5c6aad5a5831572b
**GitHub**: Dlove123

---

*7×24 execution - No idle time!*
