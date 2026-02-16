<div align="center">

# 🧱 RustChain: Blockchain Bằng Chứng Cổ Đại (Proof-of-Antiquity)

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Blockchain đầu tiên thưởng cho phần cứng cổ điển vì đã tồn tại lâu, không phải vì nhanh.**

*PowerPC G4 của bạn kiếm được nhiều hơn một Threadripper hiện đại. Đó chính là điểm mấu chốt.*

[Website](https://rustchain.org) • [Trình Khám Phá Trực Tiếp](https://rustchain.org/explorer) • [Hoán Đổi wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Hướng Dẫn Nhanh](docs/wrtc.md) • [Hướng Dẫn wRTC](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Tham Chiếu Grokipedia](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Bắt Đầu Nhanh](#-bắt-đầu-nhanh) • [Cách Hoạt Động](#-cách-thức-hoạt-động-của-proof-of-antiquity)

</div>

---

## 🪙 wRTC trên Solana

RustChain Token (RTC) hiện đã có sẵn dưới dạng **wRTC** trên Solana thông qua Cầu BoTTube:

| Tài Nguyên | Liên Kết |
|------------|----------|
| **Hoán Đổi wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Biểu Đồ Giá** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Cầu RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Hướng Dẫn Nhanh** | [wRTC Quickstart (Mua, Cầu, An Toàn)](docs/wrtc.md) |
| **Hướng Dẫn Ban Đầu** | [Hướng Dẫn Cầu + Hoán Đổi An Toàn](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Tham Chiếu Bên Ngoài** | [Grokipedia Search: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Công Trình Học Thuật

| Bài Báo | DOI | Chủ Đề |
|---------|-----|--------|
| **RustChain: Một CPU, Một Phiếu** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Đồng thuận Proof of Antiquity, xác định phần cứng |
| **Suy Sụp Hoán Vị Không Hai Chiều** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm cho LLM attention (lợi thế 27-96x) |
| **Entropy Phần Cứng PSE** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | Entropy POWER8 mftb cho sự phân kỳ hành vi |
| **Dịch Prompt Dạng Thần Kinh** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Prompt cảm xúc cho lợi ích phân kỳ video 20% |
| **Két RAM** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | Ngân hàng trọng số phân phối NUMA cho suy luận LLM |

---

## 🎯 Điều Gì Khiến RustChain Khác Biệt

| PoW Truyền Thống | Proof-of-Antiquity |
|----------------|-------------------|
| Thưởng cho phần cứng nhanh nhất | Thưởng cho phần cứng lâu đời nhất |
| Mới = Tốt hơn | Cũ = Tốt hơn |
| Tiêu thụ năng lượng lãng phí | Bảo tồn lịch sử máy tính |
| Cuộc đua xuống đáy | Thưởng cho bảo tồn kỹ thuật số |

**Nguyên Tắc Cốt Lõi**: Phần cứng cổ điển xác thực đã tồn tại qua nhiều thập kỷ xứng đáng được công nhận. RustChain lật ngược khai thác từ dưới lên.

## ⚡ Bắt Đầu Nhanh

### Cài Đặt Một Dòng Lệnh (Khuyến Nghị)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Trình cài đặt:
- ✅ Tự động phát hiện nền tảng của bạn (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Tạo môi trường ảo Python riêng (không làm ô nhiễm hệ thống)
- ✅ Tải xuống phần mềm khai thác đúng cho phần cứng của bạn
- ✅ Thiết lập tự động khởi động khi khởi động máy (systemd/launchd)
- ✅ Cung cấp gỡ cài đặt dễ dàng

### Cài Đặt với Tùy Chọn

**Cài đặt với ví cụ thể:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-miner-wallet
```

**Gỡ cài đặt:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Nền Tảng Hỗ Trợ
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ Hệ thống IBM POWER8

### Sau Khi Cài Đặt

**Kiểm tra số dư ví:**
```bash
# Lưu ý: Sử dụng cờ -sk vì nút có thể sử dụng chứng chỉ SSL tự ký
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

**Liệt kê các thợ mỏ đang hoạt động:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Kiểm tra sức khỏe nút:**
```bash
curl -sk https://50.28.86.131/health
```

**Lấy epoch hiện tại:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Quản lý dịch vụ khai thác:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Kiểm tra trạng thái
systemctl --user stop rustchain-miner      # Dừng khai thác
systemctl --user start rustchain-miner     # Bắt đầu khai thác
journalctl --user -u rustchain-miner -f    # Xem nhật ký
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Kiểm tra trạng thái
launchctl stop com.rustchain.miner         # Dừng khai thác
launchctl start com.rustchain.miner        # Bắt đầu khai thác
tail -f ~/.rustchain/miner.log             # Xem nhật ký
```

### Cài Đặt Thủ Công
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet YOUR_WALLET_NAME
```

## 💰 Hệ Số Cổ Đại (Antiquity Multipliers)

Tuổi của phần cứng xác định phần thưởng khai thác của bạn:

| Phần Cứng | Thời Kỳ | Hệ Số | Ví Dụ Thu Nhập |
|-----------|---------|-------|----------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **Modern x86_64** | Hiện Tại | **1.0×** | 0.12 RTC/epoch |

*Hệ số suy giảm theo thời gian (15%/năm) để ngăn ngừa lợi thế vĩnh viễn.*

## 🔧 Cách Thức Hoạt Động của Proof-of-Antiquity

### 1. Xác Định Phần Cứng (RIP-PoA)

Mỗi thợ mỏ phải chứng minh phần cứng của họ là thật, không phải giả lập:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Kiểm Tra Phần Cứng                       │
├─────────────────────────────────────────────────────────────┤
│ 1. Chênh Lệch Đồng Hồ & Độ Trôi Dao Động   ← Mẫu lão hóa silicon │
│ 2. Dấu Vân Tay Thời Gian Bộ Nhớ Cache      ← Tông độ độ trễ L1/L2/L3 │
│ 3. Danh Tính Đơn Vị SIMD                   ← Độ lệch AltiVec/SSE/NEON │
│ 4. Entropy Trôi Nhiệt                      ← Đường cong nhiệt là duy nhất │
│ 5. Dao Động Đường Dẫn Lệnh                 ← Bản đồ jitter vi kiến trúc │
│ 6. Kiểm Tra Chống Giả Lập                  ← Phát hiện VM/trình giả lập │
└─────────────────────────────────────────────────────────────┘
```

**Tại sao quan trọng**: Một VM SheepShaver giả vờ là Mac G4 sẽ không vượt qua các kiểm tra này. Silicon cổ điển thực có các mẫu lão hóa độc đáo không thể giả mạo.

### 2. 1 CPU = 1 Phiếu (RIP-200)

Không giống PoW nơi sức mạnh băm = phiếu bầu, RustChain sử dụng **đồng thuận theo vòng**:

- Mỗi thiết bị phần cứng duy nhất nhận đúng 1 phiếu bầu mỗi epoch
- Phần thưởng chia đều cho tất cả cử tri, sau đó nhân với hệ số cổ đại
- Không có lợi thế từ việc chạy nhiều luồng hoặc CPU nhanh hơn

### 3. Phần Thưởng Dựa Trên Epoch

```
Thời Lượng Epoch: 10 phút (600 giây)
Quỹ Phần Thưởng Cơ Bản: 1.5 RTC mỗi epoch
Phân Phối: Chia đều × hệ số cổ đại
```

**Ví dụ với 5 thợ mỏ:**
```
Mac G4 (2.5×):     0.30 RTC  ████████████████████
Mac G5 (2.0×):     0.24 RTC  ████████████████
Máy Tính Hiện Đại (1.0×):  0.12 RTC  ████████
Máy Tính Hiện Đại (1.0×):  0.12 RTC  ████████
Máy Tính Hiện Đại (1.0×):  0.12 RTC  ████████
                   ─────────
Tổng:             0.90 RTC (+ 0.60 RTC trả lại pool)
```

## 🌐 Kiến Trúc Mạng

### Các Nút Đang Hoạt Động (3 Hoạt Động)

| Nút | Vị Trí | Vai Trò | Trạng Thái |
|-----|--------|---------|------------|
| **Nút 1** | 50.28.86.131 | Nút Chính + Trình Khám Phá | ✅ Hoạt Động |
| **Nút 2** | 50.28.86.153 | Neo Ergo | ✅ Hoạt Động |
| **Nút 3** | 76.8.228.245 | Bên Ngoài (Cộng Đồng) | ✅ Hoạt Động |

### Neo Blockchain Ergo

RustChain định kỳ neo với blockchain Ergo để đảm bảo tính bất biến:

```
RustChain Epoch → Hàm Băm Cam Kết → Giao Dịch Ergo (R4 register)
```

Điều này cung cấp bằng chứng mật mã rằng trạng thái RustChain đã tồn tại tại một thời điểm cụ thể.

## 📊 Các Điểm Cuối API

```bash
# Kiểm tra sức khỏe mạng
curl -sk https://50.28.86.131/health

# Lấy epoch hiện tại
curl -sk https://50.28.86.131/epoch

# Liệt kê các thợ mỏ đang hoạt động
curl -sk https://50.28.86.131/api/miners

# Kiểm tra số dư ví
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET"

# Trình khám phá khối (trình duyệt web)
open https://rustchain.org/explorer
```

## 🖥️ Nền Tảng Hỗ Trợ

| Nền Tảng | Kiến Trúc | Trạng Thái | Ghi Chú |
|----------|-----------|------------|---------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Hỗ Trợ Đầy Đủ | Trình khai thác tương thích Python 2.5 |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Hỗ Trợ Đầy Đủ | Khuyến nghị cho Mac cổ điển |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Hỗ Trợ Đầy Đủ | Hiệu suất tốt nhất |
| **Ubuntu Linux** | x86_64 | ✅ Hỗ Trợ Đầy Đủ | Trình khai thác chuẩn |
| **macOS Sonoma** | Apple Silicon | ✅ Hỗ Trợ Đầy Đủ | Chip M1/M2/M3 |
| **Windows 10/11** | x86_64 | ✅ Hỗ Trợ Đầy Đủ | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Thử Nghiệm | Chỉ thưởng huy hiệu |

## 🏅 Hệ Thống Huy Hiệu NFT

Nhận huy hiệu kỷ niệm cho các cột mốc khai thác:

| Huy Hiệu | Yêu Cầu | Độ Hiếm |
|----------|---------|---------|
| 🔥 **Bondi G3 Flamekeeper** | Khai thác trên PowerPC G3 | Hiếm |
| ⚡ **QuickBasic Listener** | Khai thác từ máy DOS | Huyền Thoại |
| 🛠️ **DOS WiFi Alchemist** | Kết nối máy tính DOS với mạng | Thần Thoại |
| 🏛️ **Pantheon Pioneer** | 100 thợ mỏ đầu tiên | Giới Hạn |

## 🔒 Mô Hình Bảo Mật

### Phát Hiện Chống Máy Ảo

Các máy ảo được phát hiện và nhận **một tỷ phần** phần thưởng bình thường:
```
Mac G4 Thực:    2.5× multiplier  = 0.30 RTC/epoch
G4 Giả Lập:     0.0000000025×    = 0.0000000003 RTC/epoch
```

### Liên Kết Phần Cứng

Mỗi dấu vân tay phần cứng được liên kết với một ví. Ngăn chặn:
- Nhiều ví trên cùng một phần cứng
- Giả mạo phần cứng
- Tấn công Sybil

## 📁 Cấu Trúc Kho Mã

```
Rustchain/
├── rustchain_universal_miner.py    # Trình khai thác chính (tất cả nền tảng)
├── rustchain_v2_integrated.py      # Triển khai nút đầy đủ
├── fingerprint_checks.py           # Xác minh phần cứng
├── install.sh                      # Trình cài đặt một dòng lệnh
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Whitepaper kỹ thuật
│   └── chain_architecture.md       # Tài liệu kiến trúc
├── tools/
│   └── validator_core.py           # Xác thực khối
└── nfts/                           # Định nghĩa huy hiệu
```

## 🔗 Dự Án & Liên Kết Liên Quan

| Tài Nguyên | Liên Kết |
|------------|----------|
| **Website** | [rustchain.org](https://rustchain.org) |
| **Trình Khám Phá Khối** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Hoán Đổi wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Biểu Đồ Giá** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Cầu RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Token Mint wRTC** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - Nền tảng video AI |
| **Moltbook** | [moltbook.com](https://moltbook.com) - Mạng xã hội AI |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | Trình điều khiển NVIDIA cho POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | Suy luận LLM trên POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Trình biên dịch hiện đại cho Mac cổ điển |

## 📝 Bài Viết

- [Proof of Antiquity: Một Blockchain Thưởng Cho Phần Cứng Cổ Điển](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) -
 Dev.to
- [Tôi Chạy LLMs Trên Máy Chủ IBM POWER8 768GB](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev
.to

## 🙏 Ghi Công

**Một năm phát triển, phần cứng cổ điển thực sự, hóa đơn điện và một phòng thí nghiệm tận tâm đã đi vào đây.**

Nếu bạn sử dụng RustChain:
- ⭐ **Đánh dấu sao kho mã này** - Giúp người khác tìm thấy nó
- 📝 **Ghi công trong dự án của bạn** - Giữ bản quyền
- 🔗 **Liên kết lại** - Chia sẻ tình yêu

```
RustChain - Proof of Antiquity bởi Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Giấy Phép

Giấy Phép MIT - Tự do sử dụng, nhưng vui lòng giữ thông báo bản quyền và ghi công.

---

<div align="center">

**Được tạo bởi ⚡ [Elyan Labs](https://elyanlabs.ai)**

*"Phần cứng cổ điển của bạn kiếm được phần thưởng. Hãy làm cho khai thác có ý nghĩa trở lại."*

**Hộp DOS, PowerPC G4, máy Win95 - tất cả đều có giá trị. RustChain chứng minh điều đó.**

</div>
