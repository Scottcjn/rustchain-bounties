<div align="center">

# 🧱 RustChain: Blockchain Proof-of-Antiquity

[![Lisensi](https://img.shields.io/badge/Lisensi-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Konsensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Jaringan](https://img.shields.io/badge/Node-3%20Aktif-brightgreen)](https://rustchain.org/explorer)
[![Terlihat di BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Blockchain pertama yang memberi penghargaan pada perangkat keras vintage karena sudah tua, bukan karena cepat.**

*PowerPC G4 Anda menghasilkan lebih banyak daripada Threadripper modern. Itulah intinya.*

[Website](https://rustchain.org) • [Explorer Langsung](https://rustchain.org/explorer) • [Tukar wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [Panduan Cepat wRTC](docs/wrtc.md) • [Tutorial wRTC](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Referensi Grokipedia](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Mulai Cepat](#-mulai-cepat) • [Cara Kerja](#-cara-kerja-proof-of-antiquity)

</div>

---

## 🪙 wRTC di Solana

Token RustChain (RTC) kini tersedia sebagai **wRTC** di Solana melalui BoTTube Bridge:

| Sumber Daya | Tautan |
|-------------|--------|
| **Tukar wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Grafik Harga** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Jembatan RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Panduan Mulai Cepat** | [Panduan wRTC (Beli, Jembatani, Keamanan)](docs/wrtc.md) |
| **Tutorial Onboarding** | [Panduan Jembatan wRTC + Keamanan Tukar](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Referensi Eksternal** | [Pencarian Grokipedia: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Mint Token** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Publikasi Akademik

| Makalah | DOI | Topik |
|---------|-----|-------|
| **RustChain: Satu CPU, Satu Suara** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Konsensus Proof of Antiquity, sidik jari perangkat keras |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm untuk perhatian LLM (keunggulan 27-96x) |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | Entropi POWER8 mftb untuk divergensi perilaku |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Prompt emosional untuk peningkatan diffusi video 20% |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | Perbankan bobot terdistribusi NUMA untuk inferensi LLM |

---

## 🎯 Apa yang Membuat RustChain Berbeda

| PoW Tradisional | Proof-of-Antiquity |
|----------------|-------------------|
| Memberi penghargaan pada perangkat keras tercepat | Memberi penghargaan pada perangkat keras tertua |
| Lebih baru = Lebih baik | Lebih tua = Lebih baik |
| Konsumsi energi yang boros | Melestarikan sejarah komputasi |
| Pertarungan ke bawah | Penghargaan pada pelestarian digital |

**Prinsip Inti**: Perangkat keras vintage otentik yang telah bertahan selama puluhan tahun layak mendapat pengakuan. RustChain membalikkan penambangan terbalik.

## ⚡ Mulai Cepat

### Instalasi Satu Baris (Direkomendasikan)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Penginstal akan:
- ✅ Mendeteksi platform Anda secara otomatis (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Membuat Python virtualenv yang terisolasi (tidak mencemari sistem)
- ✅ Mengunduh penambang yang tepat untuk perangkat keras Anda
- ✅ Mengatur auto-start saat boot (systemd/launchd)
- ✅ Menyediakan penghapusan yang mudah

### Instalasi dengan Opsi

**Instal dengan dompet tertentu:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet nama-dompet-saya
```

**Hapus Instalasi:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Platform yang Didukung
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ Sistem IBM POWER8

### Setelah Instalasi

**Periksa saldo dompet Anda:**
```bash
# Catatan: Menggunakan flag -sk karena node mungkin menggunakan sertifikat SSL self-signed
curl -sk "https://50.28.86.131/wallet/balance?miner_id=NAMA_DOMPET_ANDA"
```

**Daftar penambang aktif:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Periksa kesehatan node:**
```bash
curl -sk https://50.28.86.131/health
```

**Dapatkan epoch saat ini:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Kelola layanan penambang:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Periksa status
systemctl --user stop rustchain-miner        # Hentikan penambangan
systemctl --user start rustchain-miner       # Mulai penambangan
journalctl --user -u rustchain-miner -f      # Lihat log
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain             # Periksa status
launchctl stop com.rustchain.miner          # Hentikan penambangan
launchctl start com.rustchain.miner         # Mulai penambangan
tail -f ~/.rustchain/miner.log              # Lihat log
```

### Instalasi Manual
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet NAMA_DOMPET_ANDA
```

## 💰 Pengganda Antiquity

Usia perangkat keras Anda menentukan hadiah penambangan Anda:

| Perangkat Keras | Era | Pengganda | Contoh Penghasilan |
|-----------------|-----|-----------|-------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **x86_64 Modern** | Saat ini | **1.0×** | 0.12 RTC/epoch |

*Pengganda menurun dari waktu ke waktu (15%/tahun) untuk mencegah keuntungan permanen.*

## 🔧 Cara Kerja Proof-of-Antiquity

### 1. Sidik Jari Perangkat Keras (RIP-PoA)

Setiap penambang harus membuktikan perangkat keras mereka nyata, bukan tersimulasi:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Pemeriksaan Perangkat Keras             │
├─────────────────────────────────────────────────────────────┤
│ 1. Clock-Skew & Drift Osilator   ← Pola penuaan silikon   │
│ 2. Sidik Jari Waktu Cache        ← Nada latensi L1/L2/L3  │
│ 3. Identitas Unit SIMD             ← Bias AltiVec/SSE/NEON│
│ 4. Entropi Drift Termal            ← Kurva panas unik     │
│ 5. Instruction Path Jitter         ← Peta jitter mikroark │
│ 6. Pemeriksaan Anti-Emulasi        ← Deteksi VM/emulator  │
└─────────────────────────────────────────────────────────────┘
```

**Mengapa ini penting**: VM SheepShaver yang berpura-pura menjadi Mac G4 akan gagal dalam pemeriksaan ini. Silikon vintage nyata memiliki pola penuaan unik yang tidak dapat dipalsukan.

### 2. 1 CPU = 1 Suara (RIP-200)

Berbeda dengan PoW di mana kekuatan hash = suara, RustChain menggunakan **konsensus round-robin**:

- Setiap perangkat keras unik mendapat tepat 1 suara per epoch
- Hadiah dibagi sama rata di antara semua pemilih, kemudian dikalikan dengan antiquity
- Tidak ada keuntungan dari menjalankan beberapa thread atau CPU yang lebih cepat

### 3. Hadiah Berbasis Epoch

```
Durasi Epoch: 10 menit (600 detik)
Pool Hadiah Dasar: 1,5 RTC per epoch
Distribusi: Pembagian sama × pengganda antiquity
```

**Contoh dengan 5 penambang:**
```
Mac G4 (2.5×):     0.30 RTC  ████████████████████
Mac G5 (2.0×):     0.24 RTC  ████████████████
PC Modern (1.0×):  0.12 RTC  ████████
PC Modern (1.0×):  0.12 RTC  ████████
PC Modern (1.0×):  0.12 RTC  ████████
                   ─────────
Total:             0.90 RTC (+ 0.60 RTC dikembalikan ke pool)
```

## 🌐 Arsitektur Jaringan

### Node Langsung (3 Aktif)

| Node | Lokasi | Peran | Status |
|------|----------|-------|--------|
| **Node 1** | 50.28.86.131 | Primer + Explorer | ✅ Aktif |
| **Node 2** | 50.28.86.153 | Jangkar Ergo | ✅ Aktif |
| **Node 3** | 76.8.228.245 | Eksternal (Komunitas) | ✅ Aktif |

### Jangkar Blockchain Ergo

RustChain secara berkala menjangkar ke blockchain Ergo untuk keabadian:

```
Epoch RustChain → Hash Komitmen → Transaksi Ergo (register R4)
```

Ini memberikan bukti kriptografis bahwa keadaan RustChain ada pada waktu tertentu.

## 📊 Endpoint API

```bash
# Periksa kesehatan jaringan
curl -sk https://50.28.86.131/health

# Dapatkan epoch saat ini
curl -sk https://50.28.86.131/epoch

# Daftar penambang aktif
curl -sk https://50.28.86.131/api/miners

# Periksa saldo dompet
curl -sk "https://50.28.86.131/wallet/balance?miner_id=DOMPET_ANDA"

# Explorer blok (browser web)
open https://rustchain.org/explorer
```

## 🖥️ Platform yang Didukung

| Platform | Arsitektur | Status | Catatan |
|----------|------------|--------|---------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Dukungan Penuh | Penambang kompatibel Python 2.5 |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Dukungan Penuh | Direkomendasikan untuk Mac vintage |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Dukungan Penuh | Performa terbaik |
| **Ubuntu Linux** | x86_64 | ✅ Dukungan Penuh | Penambang standar |
| **macOS Sonoma** | Apple Silicon | ✅ Dukungan Penuh | Chip M1/M2/M3 |
| **Windows 10/11** | x86_64 | ✅ Dukungan Penuh | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Eksperimental | Hanya hadiah lencana |

## 🏅 Sistem Lencana NFT

Dapatkan lencana peringatan untuk tonggak penambangan:

| Lencana | Persyaratan | Kelangkaan |
|---------|-------------|------------|
| 🔥 **Bondi G3 Flamekeeper** | Menambang di PowerPC G3 | Langka |
| ⚡ **QuickBasic Listener** | Menambang dari mesin DOS | Legendaris |
| 🛠️ **DOS WiFi Alchemist** | Jaringkan mesin DOS | Mitos |
| 🏛️ **Pantheon Pioneer** | 100 penambang pertama | Terbatas |

## 🔒 Model Keamanan

### Deteksi Anti-VM
VM terdeteksi dan menerima **1 milyar** dari hadiah normal:
```
Mac G4 Nyata:    2.5× pengganda  = 0.30 RTC/epoch
G4 Tersimulasi:  0.0000000025×   = 0.0000000003 RTC/epoch
```

### Pengikatan Perangkat Keras
Setiap sidik jari perangkat keras diikat ke satu dompet. Mencegah:
- Beberapa dompet di perangkat keras yang sama
- Pemalsuan perangkat keras
- Serangan Sybil

## 📁 Struktur Repositori

```
Rustchain/
├── rustchain_universal_miner.py    # Penambang utama (semua platform)
├── rustchain_v2_integrated.py      # Implementasi node lengkap
├── fingerprint_checks.py           # Verifikasi perangkat keras
├── install.sh                      # Penginstal satu baris
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Whitepaper teknis
│   └── chain_architecture.md       # Dokumen arsitektur
├── tools/
│   └── validator_core.py           # Validasi blok
└── nfts/                           # Definisi lencana
```

## 🔗 Proyek Terkait & Tautan

| Sumber Daya | Tautan |
|-------------|--------|
| **Website** | [rustchain.org](https://rustchain.org) |
| **Block Explorer** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Tukar wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Grafik Harga** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Jembatan RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Mint Token wRTC** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - Platform video AI |
| **Moltbook** | [moltbook.com](https://moltbook.com) - Jaringan sosial AI |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | Driver NVIDIA untuk POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | Inferensi LLM di POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Kompiler modern untuk Mac vintage |

## 📝 Artikel

- [Proof of Antiquity: Blockchain yang Memberi Penghargaan pada Perangkat Keras Vintage](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [Saya Menjalankan LLM di Server IBM POWER8 768GB](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Atribusi

**Setahun pengembangan, perangkat keras vintage nyata, tagihan listrik, dan laboratorium khusus telah masuk ke dalam ini.**

Jika Anda menggunakan RustChain:
- ⭐ **Beri bintang repo ini** - Membantu orang lain menemukannya
- 📝 **Kredit di proyek Anda** - Simpan atribusi
- 🔗 **Tautan balik** - Bagikan cinta

```
RustChain - Proof of Antiquity oleh Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Lisensi

Lisensi MIT - Bebas digunakan, tetapi harap pertahankan pemberitahuan hak cipta dan atribusi.

---

<div align="center">

**Dibuat dengan ⚡ oleh [Elyan Labs](https://elyanlabs.ai)**

*"Perangkat keras vintage Anda menghasilkan hadiah. Jadikan penambangan bermakna lagi."*

**Kotak DOS, PowerPC G4, mesin Win95 - semuanya memiliki nilai. RustChain membuktikannya.**

</div>
