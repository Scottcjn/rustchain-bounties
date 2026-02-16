<div align="center">

# 🧱 RustChain: Antikite İspatı (Proof-of-Antiquity) Blockchain

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)

**Eskiden kalma donanımı yaşlı olduğu için ödüllendiren ilk blockchain.**

*Senin PowerPC G4'ün, modern bir Threadripper'dan daha fazla kazanır. Mesele budur.*

[Web Sitesi](https://rustchain.org) • [Canlı Explorer](https://rustchain.org/explorer) • [wRTC Takası](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [Hızlı Başlangıç](#-hızlı-başlangıç)

</div>

---

## 🪙 Solana'da wRTC

RustChain Token (RTC), BoTTube Bridge üzerinden Solana'da **wRTC** olarak mevcuttur:

| Kaynak | Bağlantı |
|--------|----------|
| **wRTC Takas** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Fiyat Grafiği** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **RTC ↔ wRTC Köprü** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 🎯 RustChain Nedir?

| Geleneksel PoW | Antikite İspatı (PoA) |
|---------------|----------------------|
| En hızlı donanımı ödüllendirir | En eski donanımı ödüllendirir |
| Yeni = Daha İyi | Eski = Daha İyi |
| İsraf enerji tüketimi | Hesaplama tarihini korur |

**Temel Prensip**: On yıllardır ayakta kalmış otantik vintage donanım, tanımayı hak eder.

## ⚡ Hızlı Başlangıç

### Tek Satır Kurulum (Tavsiye Edilen)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Kurulum otomatik olarak:
- Platformu tespit eder (Linux/macOS, x86_64/ARM/PowerPC)
- İzole Python virtualenv oluşturur
- Donanımınız için doğru madenci dosyasını indirir
- Açılışta otomatik başlatma ayarlar

### Desteklenen Platformlar
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ IBM POWER8 sistemleri

### Kurulum Sonrası

**Cüzdan bakiyesini kontrol etme:**
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=CÜZDAN_ADINIZ"
```

**Aktif madencileri listeleme:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Hizmet yönetimi (Linux):**
```bash
systemctl --user status rustchain-miner    # Durum kontrolü
systemctl --user stop rustchain-miner      # Madenciyi durdur
systemctl --user start rustchain-miner     # Madenciyi başlat
journalctl --user -u rustchain-miner -f    # Logları görüntüle
```

---

## 💰 Antikite Çarpanları

Donanımınızın yaşı, madencilik ödüllerinizi belirler:

| Donanım | Dönem | Çarpan | Örnek Kazanç |
|---------|-------|--------|--------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **Modern x86_64** | Güncel | **1.0×** | 0.12 RTC/epoch |

*Çarpanlar zamanla azalır (%15/yıl) - kalıcı avantajı önlemek için.*

---

## 🔧 Antikite İspatı (Proof-of-Antiquity) Nasıl Çalışır?

### 1. Donanım Parmak İzi (RIP-PoA)

Her madenci, donanımının gerçek olduğunu kanıtlamalıdır (emülatör değil):

1. **Saat Sapması ve Osilatör Kayması** - Silikon yaşlanma deseni
2. **Önbellek Zamanlama Parmak İzi** - L1/L2/L3 gecikme tonu
3. **SIMD Birim Kimliği** - AltiVec/SSE/NEON yanlılığı
4. **Isısal Kayma Entropisi** - Isı eğrileri benzersizdir
5. **Talimat Yolu Jitter'ı** - Mikromimari jitter haritası
6. **Anti-Emülasyon Kontrolleri** - VM/emülatör tespiti

### 2. 1 CPU = 1 Oy (RIP-200)

PoW'un aksine (hash gücü = oy), RustChain **yuvarlak-robin fikir birliği** kullanır:
- Her benzersiz donanım cihazı, epoch başına tam olarak 1 oy alır
- Ödüller tüm oylara eşit bölünür, ardından antikite çarpanı uygulanır
- Çoklu iş parçacığı veya daha hızlı CPU'dan avantaj yoktur

### 3. Epoch Bazlı Ödüller

```
Epoch Süresi: 10 dakika (600 saniye)
Temel Ödül Havuzu: Her epoch başına 1.5 RTC
Dağıtım: Eşit bölünme × antikite çarpanı
```

---

## 🌐 Ağ Mimarisi

### Canlı Düğümler (3 Aktif)

| Düğüm | Konum | Rol | Durum |
|-------|-------|-----|-------|
| **Node 1** | 50.28.86.131 | Birincil + Explorer | ✅ Aktif |
| **Node 2** | 50.28.86.153 | Ergo Anchor | ✅ Aktif |
| **Node 3** | 76.8.228.245 | Harici (Topluluk) | ✅ Aktif |

### Ergo Blockchain Bağlantısı

RustChain, değişmezlik için periyodik olarak Ergo blockchain'e bağlanır:
```
RustChain Epoch → Taahhüt Hash → Ergo İşlemi (R4 register)
```

---

## 🔒 Güvenlik Modeli

### Anti-VM Tespiti
VM'ler tespit edilir ve **normal ödüllerin 1 milyarda biri** alır:
```
Gerçek G4 Mac:    2.5× çarpan  = 0.30 RTC/epoch
Emüle edilmiş G4: 0.0000000025× = 0.0000000003 RTC/epoch
```

### Donanım Bağlama
Her donanım parmak izi tek bir cüzdana bağlanır. Önler:
- Aynı donanımda birden fazla cüzdan
- Donanım taklidi
- Sybil saldırıları

---

## 📝 Akademik Yayınlar

| Makale | DOI | Konu |
|--------|-----|------|
| **RustChain: One CPU, One Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | PoA fikir birliği, donanım parmak izi |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm LLM dikkat için |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb entropisi |

---

## 🤝 Katkıda Bulunma

RustChain'e katkıda bulunmak için:

1. **Repo'yu yıldızlayın** - Başkalarının bulmasına yardımcı olur
2. **Sorunları bildirin** - GitHub'da issue açın
3. **Pull request gönderin** - Geliştirmeler paylaşın
4. **Donanım test edin** - Vintage donanım raporları
5. **Topluluğa katılın** - Diğer madencilerle bağlantı kurun

**Kredi**: RustChain, Scott (Scottcjn) tarafından geliştirilmiştir.

---

<div align="center">

**Elyan Labs tarafından ⚡ ile yapıldı**

*"Vintage donanımınız ödül kazanır. Madenciliği tekrar anlamlı kılın."*

**DOS kutuları, PowerPC G4'ler, Win95 makineleri - hepsinin değeri var.**

</div>
