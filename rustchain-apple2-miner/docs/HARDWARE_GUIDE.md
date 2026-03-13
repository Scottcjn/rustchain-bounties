# Apple II 硬件采购指南

## 目标配置

为了完成 RustChain Apple II 矿工移植，你需要以下硬件:

## 必需组件

### 1. Apple II 主机

**推荐型号**: Apple IIe Enhanced

| 型号 | 优点 | 缺点 | 价格范围 |
|------|------|------|----------|
| **Apple IIe Enhanced** | 128KB RAM, 易获得，扩展性好 | 需要检查电容 | $150-250 |
| Apple IIe | 64KB RAM, 便宜 | RAM 可能不足 | $100-180 |
| Apple IIgs | 1MB+ RAM, 65816 CPU (16-bit) | 较贵，配件少 | $300-500 |
| Apple II+ | 48KB RAM, 经典 | RAM 严重不足 | $100-150 |
| Apple II (原始) | 最经典 | 仅 4KB RAM, 不实用 | $200-400 |

**购买建议**:
- eBay 搜索："Apple IIe enhanced"
- 检查卖家是否提供通电测试视频
- 优先选择已更换电容的机器
- 确认包含电源和线缆

### 2. Uthernet II 以太网卡

**唯一选择**: Uthernet II (W5100 芯片)

| 供应商 | 价格 | 备注 |
|--------|------|------|
| a2retrosystems.com | ~$80 | 官方供应商 |
| eBay (二手) | ~$60-100 | 偶尔出现 |

**功能**:
- 10/100 Mbps 以太网
- W5100 硬件 TCP/IP 栈
- 兼容所有 Apple II 型号 (需要 5V 槽)
- 支持 Contiki OS 和 IP65 库

**注意**: 确保是 Uthernet **II** (第二代)，不是原始 Uthernet

### 3. 存储方案

**选项 A: CFFA3000 (推荐)**
- CompactFlash 转 Apple II
- 容量：支持到 128GB CF 卡
- 价格：~$120
- 优点：快速，可靠，易传输文件

**选项 B: MicroDrive/Turbo**
- CF 卡转软驱接口
- 容量：支持到 8GB CF 卡
- 价格：~$80
- 优点：不需要扩展槽

**选项 C: 软盘 (传统)**
- 3.5" 软盘 (IIe) 或 5.25" 软盘 (II/II+)
- 容量：140KB-800KB
- 价格：$20-50 (USB 软驱用于传输)
- 缺点：慢，不可靠，容量小

**选项 D: SD 卡接口**
- various homebrew 方案
- 价格：$40-80
- 需要 DIY 焊接

**购买建议**: CFFA3000 + 8GB CF 卡 (~$130 总计)

### 4. 网络线缆

- 标准以太网线 (Cat5/Cat5e/Cat6)
- 长度：根据需求
- 价格：$5-10

### 5. 显示器

**选项**:
- VGA 转 Apple II 适配器 + 现代显示器 (~$30)
- 复古 CRT 显示器 (eBay ~$50-100)
- 捕获卡用于视频输出 (~$20)

## 可选组件

### 6. 超级串行卡 (Super Serial Card)

- 用于调试和串口通信
- 价格：$40-80 (eBay)
- 非必需，但方便开发

### 7. 语言卡 (Language Card)

- 扩展 RAM 到 64KB+
- IIe Enhanced 已内置
- 老型号需要单独购买
- 价格：$30-60

### 8. 80 列卡

- 扩展显示到 80 列
- IIe Enhanced 已内置
- 价格：$30-50

## 完整配置价格估算

### 最小配置 (能运行)
```
Apple IIe (64KB)        $150
Uthernet II             $80
3.5" 软盘 + USB 软驱      $40
以太网线                $10
------------------------
总计：~$280
```

### 推荐配置 (开发友好)
```
Apple IIe Enhanced      $200
Uthernet II             $80
CFFA3000 + 8GB CF       $130
VGA 适配器              $30
以太网线                $10
------------------------
总计：~$450
```

### 豪华配置 (IIgs)
```
Apple IIgs              $400
Uthernet II             $80
CFFA3000 + 16GB CF      $130
VGA 适配器              $30
以太网线                $10
------------------------
总计：~$650
```

## 采购渠道

### eBay
- 搜索："Apple IIe", "Uthernet II", "CFFA3000"
- 筛选：美国境内 (减少运输风险)
- 检查：卖家评分 >98%, 提供测试视频

### 专业供应商
- **a2retrosystems.com** - Uthernet II 官方
- **reactivemicro.com** - Apple II 配件
- **whittakerdistributors.com** - 复古电脑配件

### 社区
- Apple II Facebook 群组
- 6502.org 论坛
- Reddit r/apple2

## 收货检查清单

### Apple II 主机
- [ ] 外观无明显损坏
- [ ] 键盘按键完整
- [ ] 电源风扇运转
- [ ] 通电自检通过 (显示 "APPLE ][" 或类似)
- [ ] 所有插槽无腐蚀

### Uthernet II
- [ ] PCB 无损坏
- [ ] 芯片无烧毁痕迹
- [ ] 接口无锈蚀
- [ ] 附带驱动磁盘 (如果有)

### CFFA3000
- [ ] CF 卡槽完好
- [ ] 接口针脚无弯曲
- [ ] 固件版本 (检查标签)

## 设置步骤

### 1. 基础测试
1. 连接显示器和电源
2. 开机，确认显示正常
3. 测试键盘所有按键
4. 运行 BASIC: `PRINT "HELLO"`

### 2. 安装 Uthernet II
1. 关机，拔掉电源
2. 打开机箱
3. 插入 Uthernet II 到 Slot 3 (或空闲槽)
4. 关闭机箱，开机
5. 确认识别 (运行诊断程序)

### 3. 安装 CFFA3000
1. 格式化 CF 卡 (FAT32)
2. 写入 ProDOS 镜像
3. 插入 CFFA3000
4. 开机，确认识别为磁盘驱动器

### 4. 网络连接
1. 连接以太网线
2. 配置网络 (DHCP 或静态 IP)
3. 测试 ping (如果有工具)
4. 测试 HTTP (运行浏览器或测试程序)

## 开发环境设置 (现代 PC)

### Windows
```powershell
# 安装 WSL2 (可选)
wsl --install

# 下载 cc65
git clone https://github.com/cc65/cc65
cd cc65
make
make install

# 下载 AppleWin 模拟器
# https://github.com/AppleWin/AppleWin/releases
```

### macOS
```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 cc65
brew install cc65

# 下载 KeG II 模拟器
# https://www.kc.net/keg/
```

### Linux
```bash
# Ubuntu/Debian
sudo apt-get install cc65

# Arch
sudo pacman -S cc65

# 模拟器
sudo apt-get install mame
```

## 故障排除

### 常见问题

**Q: Apple II 不通电**
- 检查电源线
- 检查保险丝
- 电源可能需更换 (~$50)

**Q: 显示雪花/不稳定**
- 检查视频线
- 调整显示器
- 可能是视频芯片问题

**Q: Uthernet II 不识别**
- 重新插拔卡
- 尝试不同槽位
- 检查驱动磁盘

**Q: 网络不通**
- 检查网线
- 检查路由器 DHCP
- 尝试静态 IP

## 预算与回报

### 投资
- 硬件：$300-650 (一次性)
- 时间：2-4 周开发

### 回报
- Bounty: 150 RTC (~$15 当前)
- 持续挖矿：4.0x 乘数 (最高等级)
- 历史意义：第一台 Apple II RustChain 矿工
- 学习价值：6502 汇编，复古计算

### ROI 计算
假设 4.0x 乘数，每天挖矿收益约为现代 CPU 的 4 倍 (按代币计)。
虽然绝对值不高，但历史意义和收藏价值远超金钱回报。

## 下一步

1. ✅ 阅读本指南
2. ⏳ 在 eBay 寻找 Apple IIe
3. ⏳ 订购 Uthernet II (a2retrosystems.com)
4. ⏳ 订购 CFFA3000
5. ⏳ 等待硬件到达期间：
   - 安装 cc65
   - 设置模拟器
   - 开始软件开发
6. ⏳ 硬件到达后：
   - 测试所有组件
   - 安装网络卡
   - 部署矿工
   - 拍摄证明照片/视频

---

**1977 年的电脑，2026 年的加密货币。让我们创造历史！** 🍎⛏️

*最后更新*: 2026-03-13
