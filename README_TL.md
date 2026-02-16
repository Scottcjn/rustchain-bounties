<div align="center">

# 🧱 RustChain: Blockchain na Proof-of-Antiquity

[![Lisensya](https://img.shields.io/badge/Lisensya-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Konsensas-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)

**Ang unang blockchain na nagbibigay-gantimpala sa lumang hardware dahil sa tanda nito, hindi dahil sa bilis.**
</div>

---

## 🪙 wRTC sa Solana

Ang RustChain Token (RTC) ay magagamit bilang **wRTC** sa Solana gamit ang BoTTube Bridge:

| Rekursos | Link |
|----------|------|
| **Magpalit ng wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Talaan ng Presyo** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Tulay na RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Mabilisang Pagsisimula** | [wRTC Quickstart](docs/wrtc.md) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## ⚡ Mabilisang Pagsisimula

### Mag-install Gamit ang Isang Command (Inirerekomenda)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Ang installer ay:
- ✅ Awtomatikong magdedetekta ng platform
- ✅ Gagawa ng hiwalay na Python virtualenv
- ✅ Magdo-download ng angkop na miner para sa hardware
- ✅ Magse-setup ng auto-start sa pagbukas
- ✅ May opsyon para i-uninstall

---

## 💰 Multiplier Base sa Katandaan

Ang edad ng hardware ay nagtatakda ng kita sa pagmimina:

| Hardware | Panahon | Multiplier | Halimbawa ng Kita |
|----------|---------|------------|-------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **Intel Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Modern x86_64** | Ngayon | **1.0×** | 0.12 RTC/epoch |

---

## 🔧 Paano Gumagana ang Proof-of-Antiquity

### 1. Pagkakakilanlan ng Hardware (RIP-PoA)

Dapat patunayan ng mga minero na ang kanilang hardware ay totoo at hindi emulated:

- Clock-Skew & Oscillator Drift
- Cache Timing Fingerprint
- Thermal Drift Entropy
- Anti-Emulation Checks

### 2. 1 CPU = 1 Boto (RIP-200)

- Bawat natatanging hardware device ay may isang boto bawat epoch
- Ang premyo ay nahahati nang pantay-pantay, pinarami ng age multiplier

### 3. Mga Gantimpala sa Epoch

```
Tagal ng Epoch: 10 minuto (600 segundo)
Batayang Gantimpala: 1.5 RTC bawat epoch
Pamamahagi: Hatian × age multiplier
```

---

## 🤝 Pag-ambag

**Mga maaari mong gawin:**
- ⭐ **Bigyan ng bituin** ang repo na ito - tulungan ang iba na makita ito
- 🔗 **I-share ang link** - ipakita sa iba

```
Talaan ng mga Kontribyutor:
- @Scottcjn (Tagapag-akda)
- [Ibang mga Kontribyutor] (open-source)
```

---

<div align="center">
**Ginawa ni Scott (Scottcjn)**
</div>
