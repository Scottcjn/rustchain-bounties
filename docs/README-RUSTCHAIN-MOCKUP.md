# RustChain Mobile App Mockup - RustChain 移动应用界面原型

## 📱 项目概述

这是 RustChain 移动应用的高保真 HTML/CSS 界面原型设计，展示了钱包、挖矿、治理等核心功能界面。

## 🎨 设计文件

本项目包含 4 个主要界面原型：

### 1. 首页 (rustchain-mobile-mockup.html)
**功能特性：**
- 账户总余额展示（RTC 代币）
- 快捷操作按钮（发送、接收、兑换、质押）
- 挖矿状态实时显示
- 治理提案列表
- 底部导航栏

**设计亮点：**
- 渐变色彩方案
- 卡片式布局
- 实时挖矿状态指示器
- 提案进度条

### 2. 钱包界面 (rustchain-wallet-screen.html)
**功能特性：**
- 多代币支持（RTC, wRTC-Solana, wRTC-Base）
- 代币余额和 USD 估值
- 交易历史记录
- QR 码扫描功能
- 代币类型筛选标签

**设计亮点：**
- 代币图标渐变设计
- 交易类型颜色区分
- 清晰的金额展示

### 3. 挖矿界面 (rustchain-mining-screen.html)
**功能特性：**
- 实时挖矿状态
- 今日收益显示
- 挖矿控制按钮（开始、暂停、停止、设置）
- 硬件信息展示（设备类型、CPU、内存、系统）
- Antiquity 倍数显示
- 收益趋势图表

**设计亮点：**
- 动态脉冲动画
- 硬件信息卡片
- 柱状图收益趋势
- 控制按钮网格布局

### 4. 治理界面 (rustchain-governance-screen.html)
**功能特性：**
- 投票权展示（含硬件倍数计算）
- 提案列表（进行中、已结束、我的）
- 提案详情（标题、描述、投票进度）
- 投票按钮
- 创建提案功能

**设计亮点：**
- 投票权详细信息
- 提案状态标签
- 进度条可视化
- 赞成/反对票数对比

## 🎯 核心功能模块

### 钱包功能 💼
- 多链代币管理（RustChain 主网、Solana、Base）
- 发送/接收代币
- 跨链兑换（桥接）
- 交易历史查询
- QR 码扫描

### 挖矿功能 ⛏️
- 一键启动/停止挖矿
- 实时收益监控
- 硬件设备管理
- Antiquity 倍数计算
- 收益趋势分析

### 治理功能 🗳️
- 提案浏览和搜索
- 链上投票
- 提案创建
- 投票权计算（基于持币量和硬件倍数）
- 投票历史追踪

## 🎨 设计规范

### 色彩方案
```css
/* 主色调 */
Primary Gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Pink Gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)
Green Gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)
Blue Gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)
```

### 字体
- 系统字体栈：-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
- 标题：700 粗度
- 正文：400 粗度
- 辅助文字：11-12px

### 间距系统
- 卡片边距：20px
- 元素间距：15px
- 内边距：10-25px

### 圆角规范
- 手机框架：40px
- 屏幕圆角：30px
- 卡片圆角：20px
- 按钮圆角：15px
- 小元素圆角：12px

## 📐 设备规格

原型基于 iPhone X/11/12 Pro 规格设计：
- 屏幕尺寸：375 x 812 px
- 状态栏高度：44px
- 底部导航高度：80px
- 边框宽度：12px

## 🚀 使用方法

### 查看原型
直接在浏览器中打开 HTML 文件：

```bash
# Windows
start rustchain-mobile-mockup.html
start rustchain-wallet-screen.html
start rustchain-mining-screen.html
start rustchain-governance-screen.html

# macOS
open rustchain-mobile-mockup.html
open rustchain-wallet-screen.html
open rustchain-mining-screen.html
open rustchain-governance-screen.html

# Linux
xdg-open rustchain-mobile-mockup.html
xdg-open rustchain-wallet-screen.html
xdg-open rustchain-mining-screen.html
xdg-open rustchain-governance-screen.html
```

### 交互说明
- 所有按钮都设计了 hover 效果
- 底部导航栏可切换（视觉展示）
- 挖矿状态有动画效果（脉冲）
- 收益图表使用 CSS 高度模拟

## 🎯 技术特点

### 纯 HTML/CSS
- 无需 JavaScript
- 无需外部依赖
- 无需构建工具
- 即开即用

### 响应式设计
- 基于 viewport 单位
- 适配不同屏幕尺寸
- 保持设计比例

### CSS 特性
- Flexbox 布局
- CSS Grid 布局
- 渐变背景
- 阴影效果
- 动画效果
- 过渡效果

## 📊 界面预览

### 首页
```
┌─────────────────────────┐
│  9:41              📶🔋 │
├─────────────────────────┤
│ 🦀 RustChain            │
│ 欢迎回来，矿工          │
├─────────────────────────┤
│ ╔═══════════════════╗   │
│ ║ 总余额            ║   │
│ ║ 2,847.50 RTC      ║   │
│ ║ ≈ $284.75 USD     ║   │
│ ╚═══════════════════╝   │
│                         │
│ [➤]  [⬇]  [⇄]  [📊]    │
│ 发送 接收 兑换 质押      │
│                         │
│ ⛏️ 挖矿状态             │
│ ╔═══════════════════╗   │
│ ║ ● 正在挖矿        ║   │
│ ║ 3.2 RTC/天 2.8x   ║   │
│ ╚═══════════════════╝   │
│                         │
│ 🗳️ 治理提案             │
│ ╔═══════════════════╗   │
│ ║ #1695 大使计划    ║   │
│ ║ ████████░░ 67%    ║   │
│ ╚═══════════════════╝   │
├─────────────────────────┤
│ 🏠   💼   ⛏️   🗳️   ⚙️  │
│首页  钱包  挖矿  治理 设置│
└─────────────────────────┘
```

## 🎨 设计原则

1. **简洁直观**：用户一眼就能看到核心信息
2. **一致性**：统一的色彩、间距、圆角规范
3. **视觉层次**：通过大小、颜色、阴影区分重要性
4. **反馈及时**：动画和状态变化提供即时反馈
5. **易于访问**：清晰的对比度和可读性

## 📱 适配建议

### iOS
- 使用 Safe Area 适配刘海屏
- 支持深色模式
- 遵循 Human Interface Guidelines

### Android
- 适配不同屏幕比例
- 支持 Material Design
- 考虑不同厂商 ROM

## 🔮 未来扩展

### 待开发界面
- [ ] 设置界面
- [ ] 转账确认界面
- [ ] 收款二维码界面
- [ ] 提案详情界面
- [ ] 挖矿设置界面
- [ ] 交易详情界面
- [ ] 跨链桥接界面
- [ ] 质押详情界面

### 交互增强
- [ ] 添加 JavaScript 交互
- [ ] 页面切换动画
- [ ] 数据刷新动画
- [ ] 下拉刷新
- [ ] 上拉加载

### 功能完善
- [ ] 真实 API 对接
- [ ] 钱包连接
- [ ] 实时数据更新
- [ ] 推送通知
- [ ] 生物识别

## 📝 版权说明

本设计原型为 RustChain 社区创作，遵循开源协议。

## 👥 贡献者

- 设计：RustChain AI Agent
- 日期：2026-03-12

## 🔗 相关链接

- [RustChain 官网](https://rustchain.org)
- [GitHub 仓库](https://github.com/Scottcjn/Rustchain)
- [Bounty Issue](https://github.com/Scottcjn/rustchain-bounties/issues/1698)

---

**注意：** 此为界面原型展示，实际功能需要后端 API 支持和智能合约集成。
