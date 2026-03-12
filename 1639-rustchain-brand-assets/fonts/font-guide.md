# RustChain Font Guide - 字体指南

## 字体系统概述

RustChain 使用三套字体系统来传达品牌的科技感、复古未来主义和可读性。

---

## 1. 主字体 (Headers & Logo)

### Orbitron
**用途**: Logo、主标题、重要数字、品牌展示

**特点**: 
- 几何无衬线字体
- 强烈的科技感
- 适合未来主义设计

**获取**: 
- Google Fonts: https://fonts.google.com/specimen/Orbitron
- License: Open Font License (免费商用)

**使用示例**:
```css
h1, .logo-text {
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
}
```

### Rajdhani (备选)
**用途**: 副标题、章节标题

**特点**:
- 方正的几何造型
- 科技感强但比 Orbitron 柔和
- 良好的可读性

**获取**: 
- Google Fonts: https://fonts.google.com/specimen/Rajdhani

---

## 2. 正文字体 (Body Text)

### Inter (推荐)
**用途**: 正文、UI 文本、文档内容

**特点**:
- 高可读性
- 现代简洁
- 优秀的屏幕显示效果
- 多语言支持

**获取**: 
- Google Fonts: https://fonts.google.com/specimen/Inter
- License: Open Font License (免费商用)

**使用示例**:
```css
body, p, .text-content {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: #C0C0C0;
}
```

### Roboto (备选)
**用途**: 备选正文字体

**获取**: 
- Google Fonts: https://fonts.google.com/specimen/Roboto

---

## 3. 代码字体 (Monospace)

### JetBrains Mono (推荐)
**用途**: 代码块、终端显示、技术文档

**特点**:
- 专为编程设计
- 连字支持 (ligatures)
- 优秀的字符区分度

**获取**: 
- JetBrains: https://www.jetbrains.com/lp/mono/
- License: Open Font License (免费商用)

**使用示例**:
```css
code, pre, .terminal {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
}
```

### Fira Code (备选)
**用途**: 代码显示

**获取**: 
- GitHub: https://github.com/tonsky/FiraCode

### Consolas (系统备选)
**用途**: Windows 系统默认代码字体

---

## 4. 字体层级系统

### Web 使用

```css
/* 引入字体 */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* 字体变量 */
:root {
  --font-display: 'Orbitron', sans-serif;
  --font-heading: 'Rajdhani', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

/* 标题层级 */
h1 {
  font-family: var(--font-display);
  font-size: 2.5rem;      /* 40px */
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: 2px;
}

h2 {
  font-family: var(--font-display);
  font-size: 2rem;        /* 32px */
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: 1.5px;
}

h3 {
  font-family: var(--font-heading);
  font-size: 1.5rem;      /* 24px */
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 1px;
}

h4 {
  font-family: var(--font-heading);
  font-size: 1.25rem;     /* 20px */
  font-weight: 600;
  line-height: 1.4;
}

/* 正文 */
body {
  font-family: var(--font-body);
  font-size: 1rem;        /* 16px */
  line-height: 1.6;
  font-weight: 400;
}

small {
  font-size: 0.875rem;    /* 14px */
}

/* 代码 */
code {
  font-family: var(--font-mono);
  font-size: 0.9em;
}

pre {
  font-family: var(--font-mono);
  font-size: 14px;
  line-height: 1.5;
}
```

### 响应式字体大小

```css
/* 移动端优化 */
@media (max-width: 768px) {
  h1 {
    font-size: 2rem;      /* 32px */
  }
  
  h2 {
    font-size: 1.75rem;   /* 28px */
  }
  
  h3 {
    font-size: 1.25rem;   /* 20px */
  }
  
  body {
    font-size: 0.9375rem; /* 15px */
  }
}
```

---

## 5. 字体使用场景

### Logo 和 Branding
```
字体：Orbitron Bold
字重：700
字距：2px
大小写：全大写
颜色：#C0C0C0 (银色) 或 #FFFFFF (白色)
```

### 网站标题
```
字体：Orbitron / Rajdhani
字重：600-700
颜色：#FFFFFF (主标题) 或 #C0C0C0 (副标题)
```

### 文档和文章
```
字体：Inter
字重：400 (正文), 600 (小标题)
行高：1.6
颜色：#C0C0C0 (正文) 或 #808080 (次要文字)
```

### 代码和技术内容
```
字体：JetBrains Mono
字重：400
行高：1.5
背景：#1A1A2E (深色背景)
文字：#C0C0C0
```

---

## 6. 字体安装指南

### Windows

1. **下载字体文件** (.ttf 或 .otf)
2. **右键点击字体文件** → "为所有用户安装"
3. **重启应用程序** 以应用新字体

### macOS

1. **下载字体文件**
2. **双击字体文件** 打开 Font Book
3. **点击"安装字体"**
4. **重启应用程序**

### Linux (Ubuntu/Debian)

```bash
# 创建字体目录
mkdir -p ~/.fonts

# 复制字体文件
cp *.ttf ~/.fonts/

# 更新字体缓存
fc-cache -fv

# 验证字体安装
fc-list | grep -i "orbitron\|inter\|jetbrains"
```

### Web 项目 (Google Fonts)

在 HTML `<head>` 中添加：

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
```

---

## 7. 字体最佳实践

### ✅ 推荐做法

1. **限制字体数量**: 每个项目最多使用 2-3 种字体
2. **保持层次清晰**: 标题、正文、代码使用不同字体
3. **注意可读性**: 正文字号不小于 14px
4. **行高适当**: 正文行高 1.5-1.8
5. **对比度充足**: 文字与背景对比度至少 4.5:1

### ❌ 避免做法

1. 使用过多字体样式
2. 正文字号过小 (<14px)
3. 花哨的装饰字体用于正文
4. 低对比度的文字颜色
5. 全大写长段落

---

## 8. 字体许可证

所有推荐字体均为 **Open Font License (OFL)**，允许：

- ✅ 个人和商业使用
- ✅ 修改和衍生
- ✅ 自由分发
- ❌ 单独出售字体文件

详细信息：https://scripts.sil.org/OFL

---

## 9. 字体测试

### 在线测试工具

- **Font Pair**: https://www.fontpair.co/ (测试字体搭配)
- **Type Scale**: https://type-scale.com/ (测试字体大小比例)
- **Google Fonts**: https://fonts.google.com/ (预览和测试)

### 本地测试

创建测试 HTML 文件：

```html
<!DOCTYPE html>
<html>
<head>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@400;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; background: #1A1A2E; color: #C0C0C0; padding: 40px; }
    h1 { font-family: 'Orbitron', sans-serif; color: #B7410E; }
    code { font-family: 'JetBrains Mono', monospace; background: #252542; padding: 4px 8px; }
  </style>
</head>
<body>
  <h1>RUSTCHAIN</h1>
  <p>Proof-of-Antiquity Blockchain</p>
  <p>代码示例：<code>const rtc = 183;</code></p>
</body>
</html>
```

---

## 10. 联系与支持

如有字体相关问题，请联系 RustChain 团队：

- **GitHub**: https://github.com/Scottcjn/RustChain
- **Discord**: https://discord.gg/VqVVS2CW9Q

---

**最后更新**: 2026-03-12  
**版本**: 1.0.0
