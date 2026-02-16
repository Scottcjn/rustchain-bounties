<div align="center">

# 🧱 RustChain: Proof-of-Antiquity Blockchain

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Den første blockchain, der belønner vintage hardware for at være gammel, ikke hurtig.**

*Din PowerPC G4 tjener mere end en moderne Threadripper. Det er meningen.*

[Hjemmeside](https://rustchain.org) • [Live Explorer](https://rustchain.org/explorer) • [Swap wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Hurtigstart](docs/wrtc.md) • [wRTC Vejledning](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia Ref](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Hurtig Start](#-hurtig-start) • [Sådan Virker Det](#-sådan-proof-of-antiquity-virker)

</div>

---

## 🪙 wRTC på Solana

RustChain Token (RTC) er nu tilgængelig som **wRTC** på Solana via BoTTube Bridge:

| Ressource | Link |
|----------|------|
| **Swap wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Prisdiagram** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Hurtigstartsvejledning** | [wRTC Hurtigstart (Køb, Bridge, Sikkerhed)](docs/wrtc.md) |
| **Onboarding Vejledning** | [wRTC Bridge + Swap Sikkerhedsguide](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Eksternt Reference** | [Grokipedia Søgning: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Akademiske Publikationer

| Papir | DOI | Emne |
|-------|-----|-------|
| **RustChain: One CPU, One Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Proof of Antiquity konsensus, hardware-fingeraftryk |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm til LLM attention (27-96x fordel) |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb entropy til adfærdsdivergens |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Emotionel prompting til 20% video diffusion gevinster |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | NUMA-distribueret vægtbank til LLM inferens |

---

## 🎯 Hvad Gør RustChain Forskellig

| Traditionel PoW | Proof-of-Antiquity |
|----------------|-------------------|
| Belønner hurtigst hardware | Belønner ældste hardware |
| Nyere = Bedre | Ældre = Bedre |
| Spildvorn energiforbrug | Bevarer computerhistorie |
| Løb mod bunden | Belønner digital bevarelse |

**Kerneprincip**: Ægte vintage hardware, der har overlevet årtier, fortjener anerkendelse. RustChain vender miningen på hovedet.

## ⚡ Hurtig Start

### Installér med én linje (Anbefalet)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Installationsværktøjet:
- ✅ Finder automatisk din platform (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Opretter et isoleret Python virtualenv (ingen systemforurening)
- ✅ Downloader den rigtige miner til din hardware
- ✅ Opsætter automatisk start ved opstart (systemd/launchd)
- ✅ Giver nem afinstallation

### Installation med valg

**Installér med specifik wallet:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet min-miner-wallet
```

**Afinstallér:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Understøttede Platforme
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ IBM POWER8 systemer

### Efter Installation

**Tjek din wallet-balance:**
```bash
# Bemærk: Brug -sk flag, fordi noden muligvis bruger et selvsigneret SSL-certifikat
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

**List aktive minere:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Tjek node-sundhed:**
```bash
curl -sk https://50.28.86.131/health
```

**Få nuværende epoch:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Administrer minerenhed:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Tjek status
systemctl --user stop rustchain-miner      # Stop minering
systemctl --user start rustchain-miner     # Start minering
journalctl --user -u rustchain-miner -f    # Vis logs
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Tjek status
launchctl stop com.rustchain.miner         # Stop minering
launchctl start com.rustchain.miner        # Start minering
tail -f ~/.rustchain/miner.log             # Vis logs
```

### Manuel Installation
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet YOUR_WALLET_NAME
```

## 💰 Antikvitetsmultiplikatorer

Din hardwares alder bestemmer dine miningsbelønninger:

| Hardware | Æra | Multiplikator | Eksempelindtjening |
|----------|-----|------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **Moderne x86_64** | Nuværende | **1.0×** | 0.12 RTC/epoch |

*Multiplikatorer aftager over tid (15%/år) for at forhindre permanent fordel.*

## 🔧 Sådan Fungerer Proof-of-Antiquity

### 1. Hardware Fingeraftryk (RIP-PoA)

Hver miner skal bevise, at deres hardware er ægte, ikke emuleret:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Hardwarekontrol                     │
├─────────────────────────────────────────────────────────────┤
│ 1. Urforskydning & Oscillatorafdrift   ← Siliciumaldringsmønster │
│ 2. Cache Timing Fingeraftryk        ← L1/L2/L3-latentone │
│ 3. SIMD-enhedsidentitet              ← AltiVec/SSE/NEON-bias │
│ 4. Termisk Drift Entropy           ← Varmekurver er unikke │
│ 5. Instruktionssti Jitter         ← Mikroarkitektur-jitterkort │
│ 6. Anti-Emulationskontrol         ← Opdager VM'er/emulatorer │
└─────────────────────────────────────────────────────────────┘
```

**Hvorfor det betyder noget**: En SheepShaver VM, der foregiver at være en G4 Mac, vil mislykkes med disse kontroller. Ægte vintage silicium har unikke aldringsmønstre, der ikke kan efterlignes.

### 2. 1 CPU = 1 Stemme (RIP-200)

I modsætning til PoW hvor hash-power = stemmer, bruger RustChain **round-robin konsensus**:

- Hver unik hardwareenhed får nøjagtig 1 stemme per epoch
- Belønninger fordeles lige mellem alle vælgere, ganget med antikvitetsfaktor
- Ingen fordel af at køre flere tråde eller hurtigere CPU'er

### 3. Epoch-baserede Belønninger

```
Epoch Varighed: 10 minutter (600 sekunder)
Basisbeløningspulje: 1.5 RTC per epoch
Fordeling: Lige fordeling × antikvitetsmultiplikator
```

**Eksempel med 5 minere:**
```
G4 Mac (2.5×):     0.30 RTC  ████████████████████
G5 Mac (2.0×):     0.24 RTC  ████████████████
Modern PC (1.0×):  0.12 RTC  ████████
Modern PC (1.0×):  0.12 RTC  ████████
Modern PC (1.0×):  0.12 RTC  ████████
                   ─────────
Total:             0.90 RTC (+ 0.60 RTC returneret til pulje)
```

## 🌐 Netværksarkitektur

### Live Noder (3 Aktive)

| Node | Placering | Rolle | Status |
|------|----------|------|--------|
| **Node 1** | 50.28.86.131 | Primær + Explorer | ✅ Aktiv |
| **Node 2** | 50.28.86.153 | Ergo Anchor | ✅ Aktiv |
| **Node 3** | 76.8.228.245 | Ekstern (Fællesskab) | ✅ Aktiv |

### Ergo Blockchain Forankring

RustChain anker periodisk til Ergo-blockchain for uforanderlighed:

```
RustChain Epoch → Commitment Hash → Ergo Transaktion (R4 register)
```

Dette giver kryptografisk bevis for, at RustChain-tilstanden eksisterede på et bestemt tidspunkt.

## 📊 API Endepunkter

```bash
# Tjek netværkssundhed
curl -sk https://50.28.86.131/health

# Få nuværende epoch
curl -sk https://50.28.86.131/epoch

# Liste aktive minere
curl -sk https://50.28.86.131/api/miners

# Tjek wallet-balance
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET"

# Blokexplorer (webbrowser)
open https://rustchain.org/explorer
```

## 🖥️ Understøttede Platforme

| Platform | Arkitektur | Status | Noter |
|----------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Fuldt Understøttet | Python 2.5 kompatibel miner |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Fuldt Understøttet | Anbefales til vintage Macs |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Fuldt Understøttet | Bedste ydeevne |
| **Ubuntu Linux** | x86_64 | ✅ Fuldt Understøttet | Standardminer |
| **macOS Sonoma** | Apple Silicon | ✅ Fuldt Understøttet | M1/M2/M3 chips |
| **Windows 10/11** | x86_64 | ✅ Fuldt Understøttet | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Eksperimentel | Kun badge-belønninger |

## 🏅 NFT Badge System

Optjen mindesmærke-badges for mining-milestenen:

| Badge | Krav | Sjældenhed |
|-------|-------------|--------|
| 🔥 **Bondi G3 Flamekeeper** | Mine på PowerPC G3 | Sjælden |
| ⚡ **QuickBasic Listener** | Mine fra DOS-maskine | Legendarisk |
| 🛠️ **DOS WiFi Alchemist** | Netværks-DOS-maskine | Mythisk |
| 🏛️ **Pantheon Pioneer** | Første 100 minere | Begrænset |

## 🔒 Sikkerhedsmodel

### Anti-VM Registrering
VM'er registreres og modtager **en milliardtedel** af normale belønninger:
```
Ægte G4 Mac:    2.5× multiplikator  = 0.30 RTC/epoch
Emuleret G4:    0.0000000025×    = 0.0000000003 RTC/epoch
```

### Hardware-binding
Hvert hardware-fingeraftryk er bundet til én wallet. Forhindrer:
- Flere pengepungge fra samme hardware
- Hardware-spoofing
- Sybil-angreb

## 📁 Repository Struktur

```
Rustchain/
├── rustchain_universal_miner.py    # Hovedminer (alle platforme)
├── rustchain_v2_integrated.py      # Fuld node-implementering
├── fingerprint_checks.py           # Hardware-verifikation
├── install.sh                      # One-liner installeringsprogram
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Teknisk whitepaper
│   └── chain_architecture.md       # Arkitektur dokumentation
├── tools/
│   └── validator_core.py           # Blokvalidering
└── nfts/                           # Badge definitioner
```

## 🔗 Relaterede Projekter & Links

| Ressource | Link |
|---------|------|
| **Hjemmeside** | [rustchain.org](https://rustchain.org) |
| **Blokexplorer** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Swap wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Prisdiagram** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **wRTC Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - AI-videoplatform |
| **Moltbook** | [moltbook.com](https://moltbook.com) - AI socialt netværk |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA-drivere til POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | LLM-inferens på POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Moderne compilere til vintage Macs |

## 📝 Artikler

- [Proof of Antiquity: A Blockchain That Rewards Vintage Hardware](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [I Run LLMs on a 768GB IBM POWER8 Server](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Attribuering

**Et års udvikling, ægte vintage hardware, elregninger og et dedikeret laboratorium gik ind i dette.**

Hvis du bruger RustChain:
- ⭐ **Stjerne dette repo** - Hjælper andre med at finde det
- 📝 **Angiv kredit i dit projekt** - Bevar attribueringen
- 🔗 **Link tilbage** - Del kærligheden

```
RustChain - Proof of Antiquity af Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Licens

MIT Licens - Frit at bruge, men behold venligst ophavsretssedlen og attribuering.

---

<div align="center">

**Lavet med ⚡ af [Elyan Labs](https://elyanlabs.ai)**

*"Din vintage hardware tjener belønninger. Gør mining meningsfuld igen."*

**DOS-maskiner, PowerPC G4-maskiner, Win95-maskiner - de har alle værdi. RustChain beviser det.**

</div>
