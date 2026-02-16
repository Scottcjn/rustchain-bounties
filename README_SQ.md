<div align="center">

# 🧱 RustChain: Blockchain me Prova e Vjetersise

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Prova%20e%20Vjet%C3%ABrsis%C3%AB-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Blockchain-i i parë që shpërblen harduerin e vjetër për moshën e tij, jo për shpejtësinë.**

*Një PowerPC G4 fiton më shumë se një Threadripper modern. Ky është qëllimi.*

[Faqja Kryesore](https://rustchain.org) • [Eksploruesi i Gjallë](https://rustchain.org/explorer) • [Shkëmbim wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [Udhëzues i Shpejtë wRTC](docs/wrtc.md) • [Tutorial wRTC](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Referenca Grokipedia](https://grokipedia.com/search?q=RustChain) • [Libër i Bardhë](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Udhëzim i Shpejtë](#-udh%E2%80%A2zim-i-shpejt%C3%AB) • [Si Funksionon](#-si-funksionon-prova-e-vjet%C3%ABrsis%C3%AB)

</div>

---

## 🪙 wRTC në Solana

Tokeni RustChain (RTC) tani është i disponueshëm si **wRTC** në Solana përmes Uresë BoTTube:

| Burimet | Lidhja |
|----------|------|
| **Shkëmbim wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Grafiku i Çmimeve** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Ura RTC ↔ wRTC** | [Ura BoTTube](https://bottube.ai/bridge) |
| **Udhëzues i Shpejtë** | [wRTC Udhëzues i Shpejtë (Blej, Ure, Siguri)](docs/wrtc.md) |
| **Tutorial për Fillestarë** | [Udhëzues i Sistemit wRTC](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Referenca e Jashtme** | [Kërkimi Grokipedia: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Botime Akademike

| Punimi | DOI | Tema |
|-------|-----|-------|
| **RustChain: Një CPU, Një Votë** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Konsensusi Prova e Vjetërsisë, identifikimi i harduerit |
| **Kolapsi i Permutacioneve Jo-Biunktive** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm për vëmendje LLM (avantazhi 27-96x) |
| **Entropia Hardware PSE** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | Entropia POWER8 mftb për divergjencë sjelljeje |
| **Përkthimi Neuromorfik i Prompteve** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Prompte emocionale për rritje të difuzionit të videos 20% |
| **Arkat e RAM-it** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | Bankimi i peshave të shpërndara për konkluzionin LLM |

---

## 🎯 Çfarë e Bën RustChain Të Ndryshëm

| Prova e Punës Tradicionale | Prova e Vjetersise |
|----------------|-------------------|
| Shpërblen harduerin më të shpejtë | Shpërblen harduerin më të vjetër |
| Më i ri = Më i mirë | Më i vjetër = Më i mirë |
| Konsum i mjerueshëm i energjisë | Ruan historinë e kompjuterizimit |
| Gara drejt fundit | Shpërblen ruajtjen dixhitale |

**Parimi kryesor**: Hardware i vjetër autentik që ka mbijetuar dekada meriton njohje. RustChain e kthen minierën përmbys.

## ⚡ Udhëzim i Shpejtë

### Instalim me Një Rresht (Rekomanduar)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Instaluesi:
- ✅ Zbulon automatikisht platformën tuaj (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Krijon një mjedis Python të izoluar (pa ndotje sistemi)
- ✅ Shkarkon minatorin e saktë për harduerin tuaj
- ✅ Konfiguron nisjen automatikisht në boot (systemd/launchd)
- ✅ Ofron çinstalim të lehtë

### Instalimi me Mundësi

**Instalo me një portofol specifik:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet portofoli-im-i-minatorit
```

**Çinstalo:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Platformat e Mbështetura
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ Sistemet IBM POWER8

### Pas Instalimit

**Kontrolloni bilancin e portofolit tuaj:**
```bash
# Shënim: Përdorim flamurin -sk sepse nyja mund të përdorë certifikatë SSL të vetënënshkruar
curl -sk "https://50.28.86.131/wallet/balance?miner_id=EMRI_I_PORTOFOLIT_TUJ"
```

**Listoni minatorët aktivë:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Kontrolloni shëndetin e nyjes:**
```bash
curl -sk https://50.28.86.131/health
```

**Merrni epokën aktuale:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Menaxhoni shërbimin e minatorit:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Kontrollo statusin
systemctl --user stop rustchain-miner      # Ndaloni minimin
systemctl --user start rustchain-miner     # Nisni minimin
journalctl --user -u rustchain-miner -f    # Shikoni log-et
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Kontrollo statusin
launchctl stop com.rustchain.miner         # Ndaloni minimin
launchctl start com.rustchain.miner        # Nisni minimin
tail -f ~/.rustchain/miner.log             # Shikoni log-et
```

### Instalim Manual
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet EMRI_I_PORTOFOLIT_TUJ
```

## 💰 Shumëzuesit e Vjetërsisë

Mosha e harduerit tuaj përcakton shpërblimin tuaj të minierave:

| Hardueri | Era | Shumëzuesi | Fitimet e Shembulli |
|----------|-----|------------|------------------|
| **PowerPC G4** | 1999-2005 | **2,5×** | 0,30 RTC/epokë |
| **PowerPC G5** | 2003-2006 | **2,0×** | 0,24 RTC/epokë |
| **PowerPC G3** | 1997-2003 | **1,8×** | 0,21 RTC/epokë |
| **IBM POWER8** | 2014 | **1,5×** | 0,18 RTC/epokë |
| **Pentium 4** | 2000-2008 | **1,5×** | 0,18 RTC/epokë |
| **Core 2 Duo** | 2006-2011 | **1,3×** | 0,16 RTC/epokë |
| **Apple Silicon** | 2020+ | **1,2×** | 0,14 RTC/epokë |
| **x86_64 Modern** | Aktual | **1,0×** | 0,12 RTC/epokë |

*Shumëzuesit zvogëlohen me kalimin e kohës (15%/vit) për të parandaluar avantazhin e përhershëm.*

## 🔧 Si Funksionon Prova e Vjetërsisë

### 1. Identifikimi i Harduerit (RIP-PoA)

Çdo minator duhet të provojë se hardueri i tij është i vërtetë, jo i emuluar:

```
┌─────────────────────────────────────────────────────────────┐
│               6 Kontrollime të Harduerit                    │
├─────────────────────────────────────────────────────────────┤
│ 1. Zhvendosja e Orës & Drifti i Oskilatorit  ← Modeli i plakjes së silikonit  │
│ 2. Shenja Kohore e Cache-it                  ← Ton i vonesës L1/L2/L3 │
│ 3. Identiteti i Njësisë SIMD                 ← Paragjykim AltiVec/SSE/NEON │
│ 4. Entropi Nga Lëvizja Termike              ← Lakoret e nxehtësisë janë unike │
│ 5. Luhatjet e Rrugës së Udhëzimeve           ← Harta e mikroarhitektes │
│ 6. Kontrollime Kundër Emulimit               ← Zbulon VM/emulatorë │
└─────────────────────────────────────────────────────────────┘
```

**Pse ka rëndësi**: Një VM SheepShaver që pretendohet të jetë Mac G4 do të dështojë në këto kontrollime. Silikoni i vjetër i vërtetë ka modele unike plakjeje që nuk mund të falsifikohen.

### 2. 1 CPU = 1 Votë (RIP-200)

Ndryshe nga Prova e Punës ku fuqia hash = vota, RustChain përdor **konsensus me radhë**:

- Çdo pajisje e veçantë hardueri merr saktësisht 1 votë për epokë
- Shpërblimet ndahen në mënyrë të barabartë mes të gjithë votuesve, pastaj shumëzohen me vjetërsinë
- Asnjë avantazh nga ekzekutimi i temave të shumta ose CPU më të shpejta

### 3. Shpërblime të Bazuar në Epokë

```
Kohëzgjatja e Epokës: 10 minuta (600 sekonda)
Pishina Bazë e Shpërblimeve: 1,5 RTC për epokë
Shpërndarja: Ndarje e barabartë × shumëzuesi i vjetërsisë
```

**Shembull me 5 minatorë:**
```
Mac G4 (2,5×):     0,30 RTC  ████████████████████
Mac G5 (2,0×):     0,24 RTC  ████████████████
PC Modern (1,0×):  0,12 RTC  ████████
PC Modern (1,0×):  0,12 RTC  ████████
PC Modern (1,0×):  0,12 RTC  ████████
                   ─────────
Totali:             0,90 RTC (+ 0,60 RTC kthehen në pishinë)
```

## 🌐 Arkitektura e Rrjetit

### Nyje në Punë (3 Aktiv)

| Nyja | Vendndodhja | Roli | Statusi |
|------|----------|------|--------|
| **Nyja 1** | 50.28.86.131 | Kryesore + Eksploruese | ✅ Aktiv |
| **Nyja 2** | 50.28.86.153 | Anker Ergo | ✅ Aktiv |
| **Nyja 3** | 76.8.228.245 | E Jashtme (Komuniteti) | ✅ Aktiv |

### Ankrimi në Blockchain-in Ergo

RustChain periodikisht ankrohet në blockchain-in Ergo për pandryshueshmëri:

```
Epoka e RustChain → Hash i Përkushtimit → Transaksion Ergo (Regjistri R4)
```

Kjo ofron provë kriptografike se gjendja e RustChain ekzistonte në një kohë të caktuar.

## 📊 API Endpoints

```bash
# Kontrollo shëndetin e rrjetit
curl -sk https://50.28.86.131/health

# Merr epokën aktuale
curl -sk https://50.28.86.131/epoch

# Listo minatorët aktivë
curl -sk https://50.28.86.131/api/miners

# Kontrollo bilancin e portofolit
curl -sk "https://50.28.86.131/wallet/balance?miner_id=PORTFOLI_YTEJ"

# Eksploruesi i blloqeve (shfletues web)
open https://rustchain.org/explorer
```

## 🖥️ Platformat e Mbështetura

| Platforma | Arkitektura | Statusi | Shënime |
|----------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Mbështetje e Plotë | Minier i përputhshëm me Python 2.5 |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Mbështetje e Plotë | Rekomanduar për Mac-et e vjetra |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Mbështetje e Plotë | Performanca më e mirë |
| **Ubuntu Linux** | x86_64 | ✅ Mbështetje e Plotë | Minier standard |
| **macOS Sonoma** | Apple Silicon | ✅ Mbështetje e Plotë | Çipet M1/M2/M3 |
| **Windows 10/11** | x86_64 | ✅ Mbështetje e Plotë | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Eksperimentale | Vetëm shpërblime të distinktivit |

## 🏅 Sistemi i Distinktivave NFT

Fitoni distinktiva përmendore për arritjet në minierë:

| Distinktiva | Kërkesa | Rërësia |
|-------|-------------|--------|
| 🔥 **Bondi G3 Flamekeeper** | Minuar në PowerPC G3 | E Rrallë |
| ⚡ **QuickBasic Listener** | Minuar nga kompjuter DOS | Legjendare |
| 🛠️ **DOS WiFi Alchemist** | Kompjuter DOS i lidhur në rrjet | Mitisore |
| 🏛️ **Pantheon Pioneer** | 100 minatorët e parë | Të Kufizuara |

## 🔒 Modeli i Sigurisë

### Zbulimi Anti-VM

VM-të zbulohen dhe marrin **një miliardtë** më pak se shpërblimet normale:
```
Mac i vërtetë G4:    2.5× shumëzues  = 0,30 RTC/epokë
G4 i emuluar:        0.0000000025×    = 0,0000000003 RTC/epokë
```

### Lidhja e Harduerit

Çdo shenjë hardueri është e lidhur me një portofol. Parandalon:
- Portofol të shumtë në të njëjtin harduer
- Falsifikimin e harduerit
- Sulme Sybil

## 📁 Struktura e Depove

```
Rustchain/
├── rustchain_universal_miner.py    # Minier kryesor (të gjitha platformat)
├── rustchain_v2_integrated.py      # Implementimi i plotë i nyjes
├── fingerprint_checks.py           # Verifikimi i harduerit
├── install.sh                      # Instalues me një rresht
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Libri teknik i bardhë
│   └── chain_architecture.md       # Dokumentet e arkitekturës
├── tools/
│   └── validator_core.py           # Vlerësimi i blloqeve
└── nfts/                           # Përkufizime të distinktivave
```

## 🔗 Projekte të Ngjashme & Lidhje

| Burimet | Lidhja |
|---------|------|
| **Faqja Kryesore** | [rustchain.org](https://rustchain.org) |
| **Eksploruesi i Blloqeve** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Shkëmbim wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Grafiku i Çmimeve** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Ura RTC ↔ wRTC** | [Ura BoTTube](https://bottube.ai/bridge) |
| **Token Mint wRTC** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - Platforma video AI |
| **Moltbook** | [moltbook.com](https://moltbook.com) - Rrjet social AI |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | Drejtuesit NVIDIA për POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | Konkluzioni LLM në POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Përpilues të modernë për Mac-et e vjetra |

## 📝 Artikuj

- [Prova e Vjetërsisë: Një Blockchain Që Shpërblen Harduerin e Vjetër](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [Unë Ekzekutoj LLM-ët në një Server IBM POWER8 768GB](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Atributi

**Një vit zhvillimi, harduer i vjetër, faturat e energjisë dhe një laborator i dedikuar janë futur në këtë.**

Nëse përdorni RustChain:
- ⭐ **Vlerësoni këtë depo** - I ndihmon të tjerët ta gjejnë
- 📝 **Jepni kredite në projektin tuaj** - Mbaje atribucionin
- 🔗 **Lidhuni pas** - Ndani dashurinë

```
RustChain - Prova e Vjetërsisë nga Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Licenca

Licencë MIT - Falas për t'u përdorur, por ju lutemi mbajeni njoftimin për të drejtat e autorit dhe atribucionin.

---

<div align="center">

**Bërë me ⚡ nga [Elyan Labs](https://elyanlabs.ai)**

*"Hardueri juaj i vjetër fiton shpërblime. Bëje minierën kuptimplotë përsëri."*

**Kutitë DOS, PowerPC G4, kompjuterë Win95 - të gjitha kanë vlerë. RustChain e vërteton këtë.**

</div>