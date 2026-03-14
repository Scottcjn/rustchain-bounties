# Galaga 矿工移植指南

## 📋 概述

本指南详细介绍如何将 RustChain 矿工移植到 Galaga 街机 (1981) 平台。由于原始硬件限制，我们采用 **Badge-Only** 方案。

---

## 🎯 移植策略

### 为什么选择 Badge-Only？

原始 Galaga 硬件存在以下不可逾越的限制：

| 限制 | 原始硬件 | 矿工需求 | 差距 |
|------|---------|---------|------|
| **RAM** | 6 KB | ~100 KB (最小) | ❌ 16x 不足 |
| **网络** | 无 | WiFi/Ethernet | ❌ 无硬件 |
| **加密** | 无硬件加速 | SHA-256, HTTP | ❌ 无法实现 |
| **存储** | ROM 固化 | 可写存储 | ❌ 只读 |
| **时钟** | 3.072 MHz | 需要精确时序 | ⚠️ 可用但慢 |

**结论**: 必须使用现代硬件模拟 Galaga 美学和行为。

---

## 🛠️ Badge 硬件设计

### 核心组件

```
┌─────────────────────────────────────────────────┐
│              Galaga Badge Miner                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐     ┌─────────────────────┐   │
│  │  ESP32-S3   │────▶│  2.8" IPS Display   │   │
│  │  240 MHz    │     │  240×320 pixels     │   │
│  │  512 KB RAM │     │  CRT effect filter  │   │
│  │  8 MB Flash │     └─────────────────────┘   │
│  │  WiFi/BT    │                                │
│  └──────┬──────┘     ┌─────────────────────┐   │
│         │            │  Control Panel      │   │
│         ├───────────▶│  - 4-way Joystick   │   │
│         │            │  - Fire Button      │   │
│         │            │  - Start Button     │   │
│         │            │  - Credit Button    │   │
│         │            └─────────────────────┘   │
│         │                                      │
│         │            ┌─────────────────────┐   │
│         └───────────▶│  2000 mAh LiPo      │   │
│                      │  USB-C Charging     │   │
│                      └─────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 组件清单

| 组件 | 型号 | 数量 | 单价 | 小计 |
|------|------|------|------|------|
| **主控板** | ESP32-S3-WROOM-1 | 1 | $8 | $8 |
| **显示屏** | 2.8" IPS (240×320) | 1 | $15 | $15 |
| **摇杆** | 4 向微动摇杆 | 1 | $5 | $5 |
| **按钮** | 12mm 微动开关 | 4 | $0.50 | $2 |
| **电池** | 2000 mAh LiPo | 1 | $10 | $10 |
| **充电模块** | TP4056 USB-C | 1 | $2 | $2 |
| **PCB** | 定制或洞洞板 | 1 | $5 | $5 |
| **外壳** | 3D 打印 | 1 | $10 | $10 |
| **其他** | 螺丝、导线等 | - | - | $5 |
| **总计** | | | | **$62** |

---

## 💻 软件开发

### 1. 固件架构

```
rustchain-galaga-firmware/
├── src/
│   ├── main.c              # 主入口
│   ├── galaga_ui.c         # Galaga 风格 UI
│   ├── rustchain_client.c  # RustChain 客户端
│   ├── hardware_fp.c       # 硬件指纹
│   ├── wifi_manager.c      # WiFi 管理
│   └── power_mgmt.c        # 电源管理
├── include/
│   ├── galaga.h
│   ├── rustchain.h
│   └── config.h
├── lib/
│   ├── lvgl/               # GUI 库
│   └── cJSON/              # JSON 解析
└── platformio.ini          # PlatformIO 配置
```

### 2. PlatformIO 配置

```ini
; platformio.ini
[env:esp32s3]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino

lib_deps =
    lvgl/lvgl@^8.3.0
    bblanchon/ArduinoJson@^6.21.0
    knolleary/PubSubClient@^2.8

build_flags =
    -D GALAGA_MINER
    -D VERSION=\"1.0.0\"
    -D WALLET_ADDRESS=\"RTC4325af95d26d59c3ef025963656d22af638bb96b\"

monitor_speed = 115200
upload_speed = 921600
```

### 3. 硬件指纹实现

```c
// hardware_fp.c
#include <Arduino.h>
#include <sha256.h>

typedef struct {
    uint32_t chip_id[2];
    uint32_t flash_id;
    uint32_t timing_samples[32];
    float temp_samples[8];
    uint8_t hash[32];
} GalagaFingerprint;

void collect_z80_timing(uint32_t* samples, int count) {
    // 模拟 Z80 @ 3.072 MHz 时序
    for (int i = 0; i < count; i++) {
        uint32_t start = ESP.getCycleCount();
        
        // 执行"Z80 指令" (空循环模拟)
        for (int j = 0; j < 3072; j++) {
            __asm__ __volatile__("nop");
        }
        
        uint32_t elapsed = ESP.getCycleCount() - start;
        samples[i] = elapsed;
    }
}

void collect_temperature(float* samples, int count) {
    // ESP32 内部温度传感器
    for (int i = 0; i < count; i++) {
        samples[i] = temperatureRead();
        delay(100);
    }
}

void generate_fingerprint(GalagaFingerprint* fp) {
    // 获取芯片 ID
    esp_read_chip_id(fp->chip_id);
    
    // 获取 Flash ID
    fp->flash_id = spi_flash_get_chip_size();
    
    // 收集时序样本
    collect_z80_timing(fp->timing_samples, 32);
    
    // 收集温度样本
    collect_temperature(fp->temp_samples, 8);
    
    // 生成哈希
    SHA256_CTX ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, fp->chip_id, sizeof(fp->chip_id));
    sha256_update(&ctx, fp->timing_samples, sizeof(fp->timing_samples));
    sha256_update(&ctx, fp->temp_samples, sizeof(fp->temp_samples));
    sha256_final(&ctx, fp->hash);
}
```

### 4. RustChain 客户端

```c
// rustchain_client.c
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define NODE_URL "http://50.28.86.131:8088"
#define ATTEST_INTERVAL 600000  // 10 minutes

typedef struct {
    char wallet[48];
    char device_arch[32];
    char device_family[32];
    uint32_t cpu_speed;
    uint32_t total_ram_kb;
    char display_type[32];
    char hardware_id[65];
    int vintage_year;
    float antiquity_multiplier;
    uint32_t timestamp;
} Attestation;

int submit_attestation(Attestation* att) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi not connected");
        return -1;
    }
    
    HTTPClient http;
    http.begin(NODE_URL "/attest");
    http.addHeader("Content-Type", "application/json");
    
    // 构建 JSON
    StaticJsonDocument<512> doc;
    doc["wallet_id"] = att->wallet;
    doc["device_arch"] = att->device_arch;
    doc["device_family"] = att->device_family;
    doc["cpu_speed"] = att->cpu_speed;
    doc["total_ram_kb"] = att->total_ram_kb;
    doc["display_type"] = att->display_type;
    doc["hardware_id"] = att->hardware_id;
    doc["vintage_year"] = att->vintage_year;
    doc["antiquity_multiplier"] = att->antiquity_multiplier;
    doc["timestamp"] = att->timestamp;
    
    String json;
    serializeJson(doc, json);
    
    // POST 请求
    int httpCode = http.POST(json);
    
    if (httpCode > 0) {
        String response = http.getString();
        Serial.printf("Response: %s\n", response.c_str());
        
        // 解析响应
        DynamicJsonDocument respDoc(256);
        deserializeJson(respDoc, response);
        
        const char* status = respDoc["status"];
        if (strcmp(status, "success") == 0) {
            float reward = respDoc["reward"];
            Serial.printf("Reward: %.4f RTC\n", reward);
            return 1;
        }
    }
    
    http.end();
    return 0;
}
```

### 5. Galaga UI 实现

```c
// galaga_ui.c
#include <lvgl.h>

static lv_obj_t* screen;
static lv_obj_t* fleet_label;
static lv_obj_t* status_label;
static lv_obj_t* epoch_label;
static lv_obj_t* earned_label;
static lv_obj_t* wallet_label;

// Galaga 外星精灵 ASCII
const char* alien_sprites[] = {
    "  👾  ",
    " 👾👾 ",
    "👾👾👾",
};

void init_galaga_ui() {
    screen = lv_obj_create(NULL);
    
    // 标题
    lv_obj_t* title = lv_label_create(screen);
    lv_label_set_text(title, "⭐ RUSTCHAIN GALAGA ⭐");
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 10);
    
    // 外星舰队
    fleet_label = lv_label_create(screen);
    lv_label_set_text(fleet_label, alien_sprites[0]);
    lv_obj_align(fleet_label, LV_ALIGN_CENTER, 0, -20);
    
    // 状态栏
    status_label = lv_label_create(screen);
    lv_label_set_text(status_label, "STATUS: INIT");
    lv_obj_align(status_label, LV_ALIGN_BOTTOM_LEFT, 10, -50);
    
    epoch_label = lv_label_create(screen);
    lv_label_set_text(epoch_label, "EPOCH: --:--:--");
    lv_obj_align(epoch_label, LV_ALIGN_BOTTOM_LEFT, 10, -35);
    
    earned_label = lv_label_create(screen);
    lv_label_set_text(earned_label, "EARNED: 0.0000 RTC");
    lv_obj_align(earned_label, LV_ALIGN_BOTTOM_LEFT, 10, -20);
    
    wallet_label = lv_label_create(screen);
    lv_label_set_text(wallet_label, "WALLET: RTC...");
    lv_obj_align(wallet_label, LV_ALIGN_BOTTOM_LEFT, 10, -5);
}

void update_galaga_fleet(int frame) {
    // 蜜蜂编队动画
    float offset = sin(frame * 0.1) * 10;
    int sprite_idx = frame % 3;
    
    char buf[64];
    snprintf(buf, sizeof(buf), "%s\n%s\n%s",
             alien_sprites[sprite_idx],
             alien_sprites[(sprite_idx + 1) % 3],
             alien_sprites[(sprite_idx + 2) % 3]);
    
    lv_label_set_text(fleet_label, buf);
    lv_obj_set_x(fleet_label, offset);
}

void update_status(const char* status, const char* epoch, float earned) {
    char buf[64];
    
    snprintf(buf, sizeof(buf), "STATUS: %s", status);
    lv_label_set_text(status_label, buf);
    
    snprintf(buf, sizeof(buf), "EPOCH: %s", epoch);
    lv_label_set_text(epoch_label, buf);
    
    snprintf(buf, sizeof(buf), "EARNED: %.4f RTC", earned);
    lv_label_set_text(earned_label, buf);
}
```

---

## 🔋 电源管理

### 功耗分析

| 模式 | 电流 | 持续时间 | 日均耗电 |
|------|------|---------|---------|
| **活跃 (Attest)** | 150 mA | 10 分钟/epoch | 360 mAh |
| **空闲 (动画)** | 80 mA | 9 小时/天 | 720 mAh |
| **深度睡眠** | 10 µA | 15 小时/天 | 0.15 mAh |
| **总计** | | | ~1080 mAh/天 |

**电池续航**: 2000 mAh / 1080 mAh ≈ **1.85 天**

### 优化策略

1. **降低显示亮度**: 减少 30% 功耗
2. **减少动画**: 仅在 attestation 期间播放
3. **延长睡眠**: epoch 之间进入深度睡眠
4. **关闭 WiFi**: 仅在提交时开启

优化后续航可达 **3-4 天**。

---

## 📡 网络连接

### WiFi 配置

```c
// WiFi 管理器
#include <WiFi.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

void connect_wifi() {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    
    int timeout = 30;
    while (WiFi.status() != WL_CONNECTED && timeout > 0) {
        delay(500);
        Serial.print(".");
        timeout--;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected!");
        Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\nWiFi connection failed!");
    }
}

void disconnect_wifi() {
    WiFi.disconnect();
    Serial.println("WiFi disconnected");
}
```

### 离线模式

如果 WiFi 不可用，矿工可以：

1. **本地存储证明**: 保存到 Flash
2. **批量提交**: 网络恢复后批量上传
3. **QR 码导出**: 显示证明 QR 码供手机扫描

---

## 🎨 外壳设计

### 3D 打印规格

```
尺寸：120mm × 80mm × 25mm (与 Galaga 控制台比例一致)
材料：PLA 或 ABS
颜色：黑色 (主体) + 红色 (装饰)
壁厚：2mm
填充：20%
```

### 设计要点

1. **屏幕开口**: 2.8" IPS 精确开孔
2. **按钮布局**: 复制 Galaga 原始布局
3. **散热孔**: ESP32 上方开孔
4. **USB-C 开口**: 侧面充电口
5. **电池仓**: 底部可拆卸

---

## 📝 测试清单

### 功能测试

- [ ] WiFi 连接稳定
- [ ] 硬件指纹生成正确
- [ ] Attestation 提交成功
- [ ] 钱包生成和备份
- [ ] 显示正常 (无花屏)
- [ ] 按钮响应灵敏
- [ ] 电池充电正常
- [ ] 功耗符合预期

### 压力测试

- [ ] 连续运行 24 小时
- [ ] 高温环境测试 (40°C)
- [ ] WiFi 断开重连
- [ ] 电池耗尽恢复
- [ ] Flash 读写耐久性

---

## 🚀 部署步骤

1. **组装硬件**
   - 焊接 PCB
   - 安装显示屏
   - 连接按钮
   - 装入外壳

2. **烧录固件**
   ```bash
   pio run --target upload
   ```

3. **配置 WiFi**
   - 首次启动进入配置模式
   - 通过串口或 Web 界面配置

4. **备份钱包**
   - 记录生成的钱包地址
   - 保存到安全位置

5. **开始挖矿**
   - 连接到电源
   - 监控首次 attestation

---

## 📊 预期收益

| 时间 | 基础收益 | ×2.0 乘数 | 累计 |
|------|---------|----------|------|
| **1 天** | 0.216 RTC | 0.432 RTC | 0.432 RTC |
| **1 周** | 1.512 RTC | 3.024 RTC | 3.024 RTC |
| **1 月** | 6.48 RTC | 12.96 RTC | 12.96 RTC |
| **1 年** | 78.84 RTC | 157.68 RTC | 157.68 RTC |

**Bounty**: 200 RTC (一次性)  
**参考汇率**: 1 RTC = $0.10 USD

---

## 📚 参考资料

- [ESP32-S3 技术手册](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)
- [LVGL 文档](https://docs.lvgl.io/)
- [PlatformIO ESP32 开发](https://docs.platformio.org/en/latest/platforms/espressif32.html)
- [RustChain API 文档](https://github.com/Scottcjn/RustChain)

---

<div align="center">

**👾 移植愉快！愿你的 Z80 永远不宕机！ 👾**

</div>
