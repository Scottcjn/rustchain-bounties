# Fossil Record Visualizer - #2311

**Bounty**: 75 RTC
**Status**: 开发中
**开始时间**: 2026-03-22 10:25

---

## 📋 需求分析

### 目标
构建一个交互式可视化时间线，展示从 genesis 以来所有矿工的所有 attestation，按架构分层显示。

### 核心功能
1. **数据获取**: 从 RustChain 数据库拉取完整 attestation 历史
2. **可视化渲染**: 交互式时间线/地层图
3. **分层显示**: 
   - X 轴：时间（epochs）
   - Y 轴：按架构堆叠（最老在下）
   - 颜色：架构家族
   - 宽度：该架构活跃矿工数量
   - Hover：矿工 ID、设备、RTC 收益、fingerprint 质量
4. ** epoch 标记**: 显示 epoch settlement 标记（垂直线）
5. **新架构标记**: 显示新架构首次出现时间

### 架构层颜色
| 架构 | 颜色 |
|------|------|
| 68K | 深琥珀色 |
| G3/G4 | 暖铜色 |
| G5 | 青铜色 |
| SPARC | 深红色 |
| MIPS | 玉色 |
| POWER8 | 深蓝色 |
| Apple Silicon | 银色 |
| Modern x86 | 浅灰色 |

### 技术栈
- **可视化**: D3.js 或 Observable Plot
- **数据**: SQLite 导出或 API
- **部署**: rustchain.org/fossils

---

## 📁 项目结构

```
fossil-visualizer/
├── index.html          # 主页面
├── style.css           # 样式
├── script.js           # 可视化逻辑
├── data/
│   └── attestations.json  # 数据文件
├── tests/
│   └── test.js         # 测试文件
└── README.md           # 本文档
```

---

## ✅ 开发清单

- [ ] 1. 数据获取模块
- [ ] 2. 数据处理模块
- [ ] 3. 可视化渲染（D3.js）
- [ ] 4. 交互功能（hover、click）
- [ ] 5. 样式美化
- [ ] 6. 单元测试（100% 覆盖）
- [ ] 7. Code Review（自我审查）
- [ ] 8. 部署测试
- [ ] 9. 提交 PR

---

## 🎯 质量要求

- ✅ 100% 测试覆盖
- ✅ Code Review 通过
- ✅ 代码注释完整
- ✅ 错误处理完整
- ✅ 性能优化
- ✅ 响应式设计

---

**专注开发，一次只做这一个任务！**
