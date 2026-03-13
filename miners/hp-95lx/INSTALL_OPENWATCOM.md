# 安装 Open Watcom 编译器

**HP 95LX Miner 需要 Open Watcom C 编译器来构建 DOS 程序。**

---

## 快速安装指南

### 方法 1: 官方 GitHub 下载 (推荐)

1. **访问 releases 页面**:
   ```
   https://github.com/open-watcom/open-watcom-v2/releases
   ```

2. **下载 Windows 版本**:
   - 查找 `ow-snapshot-win*.exe` 或 `ow*_win.zip`
   - 最新 Current-build 版本

3. **安装**:
   ```
   运行 installer (如果是 .exe)
   或解压 zip 文件到 C:\WATCOM
   ```

4. **设置环境变量**:
   ```batch
   setx WATCOM "C:\WATCOM"
   setx PATH "%PATH%;C:\WATCOM\binw"
   ```

5. **验证安装**:
   ```batch
   wcl -v
   ```
   应该显示版本信息。

### 方法 2: 使用 Chocolatey (如果已安装)

```batch
choco install open-watcom
```

### 方法 3: 手动下载

如果上述方法都不可用，可以:

1. 访问: https://openwatcom.org/
2. 下载适合 Windows 的版本
3. 解压到 `C:\WATCOM`

---

## 环境变量配置

### 临时设置 (当前会话)

```batch
set WATCOM=C:\WATCOM
set PATH=%WATCOM%\binw;%PATH%
```

### 永久设置 (系统环境变量)

1. 右键 "此电脑" → "属性"
2. "高级系统设置" → "环境变量"
3. 在 "系统变量" 中添加:
   - 变量名: `WATCOM`
   - 变量值: `C:\WATCOM`
4. 编辑 `Path` 变量，添加: `C:\WATCOM\binw`

---

## 验证安装

### 检查编译器

```batch
wcl -v
```

**预期输出**:
```
Open Watcom Version 2.0 ...
```

### 测试编译

```batch
cd miners\hp-95lx
build.bat
```

---

## 常见问题

### Q: "WATCOM environment variable not set"

**A**: 设置环境变量:
```batch
set WATCOM=C:\WATCOM
```

### Q: "wcl.exe not found"

**A**: 检查 PATH 是否包含 `%WATCOM%\binw`:
```batch
echo %PATH%
```

### Q: 编译错误 "undefined symbol"

**A**: 确保所有源文件都在 build.bat 中列出。

### Q: 内存模型错误

**A**: HP 95LX 使用 tiny 内存模型 (`-mt`), 确保 build.bat 使用正确参数。

---

## 构建 HP 95LX Miner

安装完成后:

```batch
cd C:\Users\48973\.openclaw-autoclaw\workspace\miners\hp-95lx
build.bat
```

**输出**: `bin\miner.com`

---

## 下一步

1. ✅ 安装 Open Watcom
2. ✅ 运行 `build.bat`
3. ⏳ 在 HP 95LX 模拟器测试
4. ⏳ 在真实硬件测试 (可选)

---

## 资源链接

- Open Watcom GitHub: https://github.com/open-watcom/open-watcom-v2
- Open Watcom 官网: https://openwatcom.org/
- HP 95LX 模拟器: https://github.com/jeff-1amstump/jupiter
- Bounty #417: https://github.com/rustchain/rustchain/issues/417

---

**需要帮助？** 检查 PHASE3_COMPLETE.md 获取详细信息。
