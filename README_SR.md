<div align="center">

# 🧱 RustChain: Blockchain zasnovan na dokazu starine (Proof-of-Antiquity)

[![Licenca](https://img.shields.io/badge/Licenca-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Konsenzus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Mreža](https://img.shields.io/badge/Čvorovi-3%20Aktivna-brightgreen)](https://rustchain.org/explorer)
[![Vidjeno na BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Prvi blockchain koji nagrađuje vintedž hardver zato što je star, ne brz.**

*Vaš PowerPC G4 zarađuje više od modernog Threadrippera. To je poenta.*

[Veb sajt](https://rustchain.org) • [Live Explorer](https://rustchain.org/explorer) • [Zameni wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Brzi početak](docs/wrtc.md) • [wRTC Tutorijal](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia Referenca](https://grokipedia.com/search?q=RustChain) • [Bela knjiga](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Brzi početak](#-brzi-početak) • [Kako funkcioniše](#-kako-proof-of-antiquity-funkcioniše)

</div>

---

## 🪙 wRTC na Solani

RustChain token (RTC) je sada dostupan kao **wRTC** na Solani preko BoTTube mosta:

| Resurs | Link |
|----------|------|
| **Zameni wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Cenovni grafik** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Most RTC ↔ wRTC** | [BoTTube Most](https://bottube.ai/bridge) |
| **Vodič za brzi početak** | [wRTC Brzi početak (Kupi, Poveži, Bezbednost)](docs/wrtc.md) |
| **Tutorijal za početnike** | [Vodič za most wRTC i bezbednost zamene](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Spoljna referenca** | [Grokipedia Pretraga: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Akademske publikacije

| Rad | DOI | Tema |
|-------|-----|-------|
| **RustChain: Jedan CPU, jedan glas** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Konsenzus Proof of Antiquity, otisak hardvera |
| **Kolonaps ne-bijunktivnih permutacija** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm za LLM attention (27-96x prednost) |
| **PSE Hardverska entropija** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb entropija za divergentno ponašanje |
| **Prevodenje neuromorfnih promptova** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Emocionalno podsticanje za 20% poboljšanje video difuzije |
| **RAM Trezori** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | NUMA-distribuirano bankarstvo težina za LLM inferencu |

---

## 🎯 Šta RustChain čini drugačijim

| Tradicionalni PoW | Proof-of-Antiquity |
|----------------|-------------------|
| Nagrađuje najbrži hardver | Nagrađuje najstariji hardver |
| Novije = Bolje | Starije = Bolje |
| Rasipanje energije | Čuva računarsku istoriju |
| Utrka do dna | Nagrađuje digitalno očuvanje |

**Osnovni princip**: Autentični vintedž hardver koji je preživeo decenije zaslužuje priznanje. RustChain okreće rudarenje naglavačke.

## ⚡ Brzi početak

### Instalacija jednom komandom (Preporučeno)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Instaler:
- ✅ Automatski prepoznaje vašu platformu (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Kreira izolovan Python virtualenv (bez zagađivanja sistema)
- ✅ Preuzima odgovarajući rudar za vaš hardver
- ✅ Postavlja automatsko pokretanje prilikom podizanja sistema (systemd/launchd)
- ✅ Pruža jednostavno uklanjanje

### Instalacija sa opcijama

**Instalirajte sa specifičnim novčanikom:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet moj-novcanik-rudara
```

**Deinstalacija:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Podržane platforme
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ IBM POWER8 sistemi

### Nakon instalacije

**Proverite stanje novčanika:**
```bash
# Napomena: Koristite -sk zastavice jer čvor može koristiti samopotpisani SSL sertifikat
curl -sk "https://50.28.86.131/wallet/balance?miner_id=IME_VAŠEG_NOVČANIKA"
```

**Lista aktivnih rudara:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Proverite zdravlje čvora:**
```bash
curl -sk https://50.28.86.131/health
```

**Trenutna epoha:
```bash
curl -sk https://50.28.86.131/epoch
```

**Upravljanje uslugom rudara:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Proverite status
systemctl --user stop rustchain-miner      # Zaustavite rudarenje
systemctl --user start rustchain-miner     # Pokrenite rudarenje
journalctl --user -u rustchain-miner -f    # Pregledajte logove
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Proverite status
launchctl stop com.rustchain.miner         # Zaustavite rudarenje
launchctl start com.rustchain.miner        # Pokrenite rudarenje
tail -f ~/.rustchain/miner.log             # Pregledajte logove
```

### Ručna instalacija
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet IME_VASEG_NOVCAKIRA
```

## 💰 Multiplikatori antikviteta

Starost vašeg hardvera određuje vašu nagradu za rudarenje:

| Hardver | Era | Multiplikator | Primer zarade |
|----------|-----|------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoha |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoha |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoha |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoha |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoha |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoha |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoha |
| **Moderni x86_64** | Trenutno | **1.0×** | 0.12 RTC/epoha |

*Multiplikatori se smanjuju tokom vremena (15%/godina) kako bi se sprečila trajna prednost.*

## 🔧 Kako Proof-of-Antiquity funkcioniše

### 1. Otisak hardvera (RIP-PoA)

Svaki rudar mora dokazati da je njegov hardver stvaran, nije emuliran:

```
┌─────────────────────────────────────────────────────────────┐
│       6 Hardverskih Provera                                 │
├─────────────────────────────────────────────────────────────┤
│ 1. Pomak sata i oscilatorsko klizanje ← Obrasci starenja silicijuma │
│ 2. Otisak vremena keša             ← Latenca L1/L2/L3     │
│ 3. Identitet SIMD jedinice         ← AltiVec/SSE/NEON pristrasnost│
│ 4. Entropija termalnog klizanja    ← Toplotne krive su jedinstvene│
│ 5. Podrhtavanje putanje instrukcija ← Mapiranje mikroarhitekturalnog podrhtavanja │
│ 6. Provera anti-emulacije          ← Otkriva VM/emulatore   │
└─────────────────────────────────────────────────────────────┘
```

**Zašto je ovo važno**: SheepShaver VM koji se pretvara da je Mac G4 neće proći ove provere. Pravi vintedž silicijum ima jedinstvene obrasce starenja koji se ne mogu lažirati.

### 2. 1 CPU = 1 glas (RIP-200)

Za razliku od PoW gde je hash snaga = glasovi, RustChain koristi **kružni konsenzus**:

- Svaki jedinstven hardverski uređaj dobija tačno 1 glas po epohi
- Nagrade se raspoređuju podjednako među svim glasačima, a zatim množe sa antikvitetom
- Nema prednosti od pokretanja više niti ili bržih CPU-ja

### 3. Nagrade zasnovane na epohama

```
Trajanje epohe: 10 minuta (600 sekundi)
Osnovni fond nagrada: 1.5 RTC po epohi
Distribucija: Podjednaka podeľa × multiplikator antikviteta
```

**Primer sa 5 rudara:**
```
G4 Mac (2.5×):     0.30 RTC  ████████████████████
G5 Mac (2.0×):     0.24 RTC  ████████████████
Moderan PC (1.0×):  0.12 RTC  ████████
Moderan PC (1.0×):  0.12 RTC  ████████
Moderan PC (1.0×):  0.12 RTC  ████████
                   ─────────
Ukupno:            0.90 RTC (+ 0.60 RTC vraćeno u fond)
```

## 🌐 Mrežna arhitektura

### Aktivni čvorovi (3 aktivna)

| Čvor | Lokacija | Uloga | Status |
|------|----------|------|--------|
| **Čvor 1** | 50.28.86.131 | Primarni + Explorer | ✅ Aktivan |
| **Čvor 2** | 50.28.86.153 | Ergo Anchor | ✅ Aktivan |
| **Čvor 3** | 76.8.228.245 | Eksterni (Zajednica) | ✅ Aktivan |

### Sidrenje na Ergo blockchain

RustChain periodično se sidri na Ergo blockchain radi nepromenljivosti:

```
RustChain Epoha → Hash obaveze → Ergo Transakcija (R4 registar)
```

Ovo pruža kriptografski dokaz da je RustChain stanje postojalo u određeno vreme.

## 📊 API krajnje tačke

```bash
# Provera zdravlja mreže
curl -sk https://50.28.86.131/health

# Trenutna epoha
curl -sk https://50.28.86.131/epoch

# Lista aktivnih rudara
curl -sk https://50.28.86.131/api/miners

# Provera stanja novčanika
curl -sk "https://50.28.86.131/wallet/balance?miner_id=IME_VAŠEG_NOVČANIKA"

# Eksplorer blokova (veb pretraživač)
open https://rustchain.org/explorer
```

## 🖥️ Podržane platforme

| Platforma | Arhitektura | Status | Napomene |
|----------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Potpuna podrška | Python 2.5 kompatibilan rudar |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Potpuna podrška | Preporučeno za vintage Mac računara |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Potpuna podrška | Najbolji performans |
| **Ubuntu Linux** | x86_64 | ✅ Potpuna podrška | Standardni rudar |
| **macOS Sonoma** | Apple Silicon | ✅ Potpuna podrška | M1/M2/M3 čipovi |
| **Windows 10/11** | x86_64 | ✅ Potpuna podrška | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Eksperimentalno | Samo bedževi za nagrade |

## 🏅 NFT sistem bedževa

Zaradite komemorativne bedževe za postignuća u rudarenju:

| Bedž | Zahteva | Retkost |
|-------|-------------|--------|
| 🔥 **Bondi G3 Čuvar plamena** | Rudari na PowerPC G3 | Retka |
| ⚡ **QuickBasic Slušalac** | Rudari sa DOS mašine | Legenda |
| 🛠️ **DOS WiFi Alhemičar** | Mrežna DOS mašina | Mitička |
| 🏛️ **Pionir Panteona** | Prvih 100 rudara | Ograničena |

## 🔒 Sigurnosni model

### Otkrivanje VM-ova
VM-ovi se detektuju i primaju **milijarditi deo** normalne nagrade:
```
Pravi G4 Mac:    2.5× multiplikator  = 0.30 RTC/epoha
Emulirani G4:    0.0000000025×      = 0.0000000003 RTC/epoha
```

### Vezivanje hardvera
Svaki otisak hardvera je vezan za jedan novčanik. Sprečava:
- Više novčanika na istom hardveru
- Lažiranje hardvera
- Sybil napade

## 📁 Struktura repozitorijuma

```
Rustchain/
├── rustchain_universal_miner.py    # Glavni rudar (sve platforme)
├── rustchain_v2_integrated.py      # Implementacija punog čvora
├── fingerprint_checks.py           # Hardverska verifikacija
├── install.sh                      # Instalacija jednom komandom
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Tehnička bela knjiga
│   └── chain_architecture.md       # Doks arhitekture
├── tools/
│   └── validator_core.py           # Validacija bloka
└── nfts/                           # Definicije bedževa
```

## 🔗 Povezani projekti i linkovi

| Resurs | Link |
|---------|------|
| **Veb sajt** | [rustchain.org](https://rustchain.org) |
| **Eksplorer blokova** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Zamena wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Cenovni grafik** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Most RTC ↔ wRTC** | [BoTTube Most](https://bottube.ai/bridge) |
| **wRTC Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - AI video platforma |
| **Moltbook** | [moltbook.com](https://moltbook.com) - AI društvena mreža |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA drajveri za POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | LLM inferenca na POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Moderni prevodioci za vintage Mac računare |

## 📝 Članci

- [Proof of Antiquity: Blockchain koji nagrađuje vintedž hardver](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [Pokrećem LLM-ove na IBM POWER8 serveru sa 768GB RAM-a](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Zahvalnost

**Godina razvoja, pravi vintedž hardver, računi za struju i posvećena laboratorija ušli su u ovo.**

Ako koristite RustChain:
- ⭐ **Ocenite ovaj repozitorijum** - Pomaže drugima da ga pronađu
- 📝 **Navedite autora u vašem projektu** - Zadržite atribuciju
- 🔗 **Povežite nazad** - Podelite ljubav

```
RustChain - Proof of Antiquity by Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Licenca

MIT Licenca - Slobodna za korišćenje, ali molimo zadržite obaveštenje o autorskim pravima i atribuciju.

---

<div align="center">

**Napravljeno sa ⚡ od strane [Elyan Labs](https://elyanlabs.ai)**

*"Vaš vintedž hardver stiče nagrade. Učinite rudarenje ponovo smislenim."*

**DOS kutije, PowerPC G4-ovi, Win95 mašine - svi imaju vrednost. RustChain to dokazuje.**

</div>