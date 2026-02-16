<div align="center">

# 🧱 RustChain: Proof-of-Antiquity Blockchain

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Den første blokkjeden som belønner vintage maskinvare for å være gammel, ikke rask.**

*Din PowerPC G4 tjener mer enn en moderne Threadripper. Det er poenget.*

[Nettside](https://rustchain.org) • [Live Explorer](https://rustchain.org/explorer) • [Bytt wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Hurtigstart](docs/wrtc.md) • [wRTC Opplæring](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia Ref](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Hurtigstart](#-hurtigstart) • [Hvordan det fungerer](#-hvordan-proof-of-antiquity-fungerer)

</div>

---

## 🪙 wRTC på Solana

RustChain Token (RTC) er nå tilgjengelig som **wRTC** på Solana via BoTTube Bridge:

| Ressurs | Lenke |
|----------|------|
| **Bytt wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Prisgraf** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Hurtigstartguide** | [wRTC Hurtigstart (Kjøp, Bridge, Sikkerhet)](docs/wrtc.md) |
| **Opplæring for onboarding** | [wRTC Bridge + Swap Sikkerhetsguide](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Ekstern Referanse** | [Grokipedia-søk: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Akademiske publikasjoner

| Dokument | DOI | Tema |
|-------|-----|-------|
| **RustChain: One CPU, One Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Proof of Antiquity consensus, hardware fingerprinting |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm for LLM attention (27-96x fordel) |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb entropy for behavioral divergence |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Emotional prompting for 20% video diffusion-gevinster |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | NUMA-distribuert weight banking for LLM inference |

---

## 🎯 Hva gjør RustChain annerledes

| Tradisjonell PoW | Proof-of-Antiquity |
|----------------|-------------------|
| Belønner raskeste maskinvare | Belønner eldste maskinvare |
| Nyere = Bedre | Eldre = Bedre |
| Sløsete energiforbruk | Bevarer datahistorie |
| Kappløp mot bunnen | Belønner digital bevaring |

**Kjerneprinsipp**: Autentisk vintage maskinvare som har overlevd i tiår fortjener anerkjennelse. RustChain snur utvinning (mining) på hodet.

## ⚡ Hurtigstart

### Ett-linjes installasjon (Anbefalt)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Installasjonsprogrammet:
- ✅ Oppdager plattformen din automatisk (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Oppretter en isolert Python virtualenv (ingen forurensning av systemet)
- ✅ Laster ned riktig miner for din maskinvare
- ✅ Setter opp autostart ved oppstart (systemd/launchd)
- ✅ Gir enkel avinstallasjon

### Installasjon med alternativer

**Installer med en spesifikk lommebok (wallet):**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet min-miner-wallet
```

**Avinstaller:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Støttede plattformer
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ IBM POWER8-systemer

### Etter installasjon

**Sjekk saldo i lommeboken:**
```bash
# Merk: Bruker -sk flagg fordi noden kan bruke et selvsignert SSL-sertifikat
curl -sk "https://50.28.86.131/wallet/balance?miner_id=DITT_WALLET_NAVN"
```

**List opp aktive minere:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Sjekk node-helse:**
```bash
curl -sk https://50.28.86.131/health
```

**Hent gjeldende epoch:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Administrer miner-tjenesten:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Sjekk status
systemctl --user stop rustchain-miner      # Stopp mining
systemctl --user start rustchain-miner     # Start mining
journalctl --user -u rustchain-miner -f    # Vis logger
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Sjekk status
launchctl stop com.rustchain.miner         # Stopp mining
launchctl start com.rustchain.miner        # Start mining
tail -f ~/.rustchain/miner.log             # Vis logger
```

### Manuell installasjon
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet DITT_WALLET_NAVN
```

## 💰 Antiquity Multipliers

Maskinvarens alder avgjør dine mining-belønninger:

| Maskinvare | Æra | Multiplier | Eksempel på inntjening |
|----------|-----|------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **Moderne x86_64** | Nåtid | **1.0×** | 0.12 RTC/epoch |

*Multiplikatorer avtar over tid (15%/år) for å forhindre permanent fordel.*

## 🔧 Hvordan Proof-of-Antiquity fungerer

### 1. Hardware Fingerprinting (RIP-PoA)

Hver miner må bevise at maskinvaren deres er ekte, ikke emulert:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Maskinvaresjekker                       │
├─────────────────────────────────────────────────────────────┤
│ 1. Clock-Skew & Oscillator Drift   ← Aldringsmønster i silisium │
│ 2. Cache Timing Fingerprint        ← L1/L2/L3 forsinkelsestone  │
│ 3. SIMD Unit Identity              ← AltiVec/SSE/NEON bias      │
│ 4. Thermal Drift Entropy           ← Varmekurver er unike       │
│ 5. Instruction Path Jitter         ← Microarch jitter-kart      │
│ 6. Anti-Emulation Checks           ← Oppdag VM-er/emulatorer    │
└─────────────────────────────────────────────────────────────┘
```

**Hvorfor det betyr noe**: En SheepShaver VM som utgir seg for å være en G4 Mac vil feile disse sjekkene. Ekte vintage silisium har unike aldringsmønstre som ikke kan forfalskes.

### 2. 1 CPU = 1 Stemme (RIP-200)

I motsetning til PoW hvor hash-kraft = stemmer, bruker RustChain **round-robin konsensus**:

- Hver unike maskinvareenhet får nøyaktig 1 stemme per epoch
- Belønninger deles likt mellom alle stemmeberettigede, og multipliseres deretter med antiquity
- Ingen fordel ved å kjøre flere tråder eller raskere CPU-er

### 3. Epoch-baserte belønninger

```
Epoch-varighet: 10 minutter (600 sekunder)
Base Reward Pool: 1.5 RTC per epoch
Distribusjon: Lik deling × antiquity multiplier
```

**Eksempel med 5 minere:**
```
G4 Mac (2.5×):     0.30 RTC  ████████████████████
G5 Mac (2.0×):     0.24 RTC  ████████████████
Moderne PC (1.0×): 0.12 RTC  ████████
Moderne PC (1.0×): 0.12 RTC  ████████
Moderne PC (1.0×): 0.12 RTC  ████████
                   ─────────
Totalt:            0.90 RTC (+ 0.60 RTC returnert til pool)
```

## 🌐 Nettverksarkitektur

### Live noder (3 aktive)

| Node | Plassering | Rolle | Status |
|------|----------|------|--------|
| **Node 1** | 50.28.86.131 | Primær + Explorer | ✅ Aktiv |
| **Node 2** | 50.28.86.153 | Ergo Anchor | ✅ Aktiv |
| **Node 3** | 76.8.228.245 | Ekstern (Fellesskap) | ✅ Aktiv |

### Ergo Blockchain Anchoring

RustChain ankrer periodisk til Ergo-blokkjeden for uforanderlighet (immutability):

```
RustChain Epoch → Commitment Hash → Ergo-transaksjon (R4 register)
```

Dette gir kryptografisk bevis på at RustChain-tilstanden eksisterte på et spesifikt tidspunkt.

## 📊 API-endepunkter

```bash
# Sjekk nettverkshelse
curl -sk https://50.28.86.131/health

# Hent gjeldende epoch
curl -sk https://50.28.86.131/epoch

# List opp aktive minere
curl -sk https://50.28.86.131/api/miners

# Sjekk saldo i lommeboken
curl -sk "https://50.28.86.131/wallet/balance?miner_id=DIN_WALLET"

# Block explorer (nettleser)
open https://rustchain.org/explorer
```

## 🖥️ Støttede plattformer

| Plattform | Arkitektur | Status | Notater |
|----------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Full støtte | Python 2.5 kompatibel miner |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Full støtte | Anbefales for vintage Mac-er |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Full støtte | Best ytelse |
| **Ubuntu Linux** | x86_64 | ✅ Full støtte | Standard miner |
| **macOS Sonoma** | Apple Silicon | ✅ Full støtte | M1/M2/M3 chipper |
| **Windows 10/11** | x86_64 | ✅ Full støtte | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Eksperimentell | Kun Badge-belønninger |

## 🏅 NFT Badge-system

Tjen minnemerker (badges) for milepæler innen mining:

| Badge | Krav | Sjeldenhet |
|-------|-------------|--------|
| 🔥 **Bondi G3 Flamekeeper** | Mine på PowerPC G3 | Rare |
| ⚡ **QuickBasic Listener** | Mine fra en DOS-maskin | Legendary |
| 🛠️ **DOS WiFi Alchemist** | Koble DOS-maskin til nettverk | Mythic |
| 🏛️ **Pantheon Pioneer** | Første 100 minere | Limited |

## 🔒 Sikkerhetsmodell

### Anti-VM deteksjon
VM-er blir oppdaget og mottar **en milliarddel** av normale belønninger:
```
Ekte G4 Mac:    2.5× multiplikator  = 0.30 RTC/epoch
Emulert G4:     0.0000000025×       = 0.0000000003 RTC/epoch
```

### Hardware Binding
Hvert maskinvare-fingeravtrykk er bundet til én lommebok. Forhindrer:
- Flere lommebøker på samme maskinvare
- Maskinvare-spoofing
- Sybil-angrep

## 📁 Katalogstruktur

```
Rustchain/
├── rustchain_universal_miner.py    # Hoved-miner (alle plattformer)
├── rustchain_v2_integrated.py      # Full node-implementasjon
├── fingerprint_checks.py           # Maskinvare-verifisering
├── install.sh                      # Ett-linjes installasjonsprogram
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Teknisk whitepaper
│   └── chain_architecture.md       # Arkitektur-dokumentasjon
├── tools/
│   └── validator_core.py           # Blokk-validering
└── nfts/                           # Badge-definisjoner
```

## 🔗 Relaterte prosjekter og lenker

| Ressurs | Lenke |
|---------|------|
| **Nettside** | [rustchain.org](https://rustchain.org) |
| **Block Explorer** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Bytt wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Prisgraf** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **wRTC Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - AI videoplattform |
| **Moltbook** | [moltbook.com](https://moltbook.com) - AI sosioalt nettverk |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA-drivere for POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | LLM-inferens på POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Moderne kompilatorer for vintage Mac-er |

## 📝 Artikler

- [Proof of Antiquity: A Blockchain That Rewards Vintage Hardware](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [I Run LLMs on a 768GB IBM POWER8 Server](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Attribusjon

**Et år med utvikling, ekte vintage maskinvare, strømregninger og et dedikert laboratorium gikk med til dette.**

Hvis du bruker RustChain:
- ⭐ **Gi stjerne til dette repoet** – Hjelper andre med å finne det
- 📝 **Oppgi kilde i prosjektet ditt** – Behold attribusjonen
- 🔗 **Lenke tilbake** – Del gleden

```
RustChain - Proof of Antiquity av Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Lisens

MIT License - Gratis å bruke, men vennligst behold opphavsrettsvarselet og attribusjonen.

---

<div align="center">

**Laget med ⚡ av [Elyan Labs](https://elyanlabs.ai)**

*"Din vintage maskinvare tjener belønninger. Gjør mining meningsfylt igjen."*

**DOS-bokser, PowerPC G4-er, Win95-maskiner – alle har verdi. RustChain beviser det.**

</div>
