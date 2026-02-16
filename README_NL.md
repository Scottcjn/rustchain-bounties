<div align="center">

# 🧱 RustChain: Proof-of-Antiquity Blockchain

[![Licentie](https://img.shields.io/badge/Licence-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Netwerk](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**De eerste blockchain die vintage hardware beloont voor het oud zijn, niet voor het snel zijn.**

*Jouw PowerPC G4 verdient meer dan een moderne Threadripper. Dat is het punt.*

[Website](https://rustchain.org) • [Live Explorer](https://rustchain.org/explorer) • [Swap wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Quickstart](docs/wrtc.md) • [wRTC Tutorial](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia Ref](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Snel Starten](#-snel-starten) • [Hoe Het Werkt](#-hoe-proof-of-antiquity-werkt)

</div>

---

## 🪙 wRTC op Solana

RustChain Token (RTC) is nu beschikbaar als **wRTC** op Solana via de BoTTube Bridge:

| Bron | Link |
|------|------|
| **Swap wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Prijs Grafiek** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Quickstart Gids** | [wRTC Quickstart (Kopen, Bridgen, Veiligheid)](docs/wrtc.md) |
| **Onboarding Tutorial** | [wRTC Bridge + Swap Veiligheidsgids](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Externe Referentie** | [Grokipedia Zoeken: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Academische Publicaties

| Paper | DOI | Onderwerp |
|-------|-----|-----------|
| **RustChain: One CPU, One Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Proof of Antiquity consensus, hardware fingerprinting |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm voor LLM attention (27-96x voordeel) |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb entropie voor gedragsdivergentie |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Emotionele prompting voor 20% video diffusie winsten |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | NUMA-gedistribueerde weight banking voor LLM inference |

---

## 🎯 Wat RustChain Anders Maakt

| Traditionele PoW | Proof-of-Antiquity |
|----------------|-------------------|
| Beloont snelste hardware | Beloont oudste hardware |
| Nieuwer = Beter | Ouder = Beter |
| Verslindende energieconsumptie | Bewaart computerhistorie |
| Race naar de bodem | Beloont digitale preservatie |

**Kernprincipe**: Authentieke vintage hardware die decennia heeft overleefd verdient erkenning. RustChain draait mining op zijn kop.

## ⚡ Snel Starten

### One-Line Installatie (Aanbevolen)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

De installer:
- ✅ Detecteert automatisch jouw platform (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Creëert een geïsoleerde Python virtualenv (geen systeemvervuiling)
- ✅ Downloadt de juiste miner voor jouw hardware
- ✅ Stelt auto-start bij boot in (systemd/launchd)
- ✅ Biedt eenvoudige uninstallatie

### Installatie met Opties

**Installeer met een specifieke wallet:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet mijn-miner-wallet
```

**Deïnstalleer:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Ondersteunde Platformen
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ IBM POWER8 systemen

### Na Installatie

**Controleer jouw wallet balans:**
```bash
# Opmerking: Gebruik -sk flags omdat de node een self-signed SSL certificaat kan gebruiken
curl -sk "https://50.28.86.131/wallet/balance?miner_id=JOUW_WALLET_NAAM"
```

**Lijst actieve miners:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Controleer node gezondheid:**
```bash
curl -sk https://50.28.86.131/health
```

**Krijg huidige epoch:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Beheer de miner service:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Controleer status
systemctl --user stop rustchain-miner      # Stop mining
systemctl --user start rustchain-miner     # Start mining
journalctl --user -u rustchain-miner -f    # Bekijk logs
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Controleer status
launchctl stop com.rustchain.miner         # Stop mining
launchctl start com.rustchain.miner        # Start mining
tail -f ~/.rustchain/miner.log             # Bekijk logs
```

### Handmatige Installatie
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet JOUW_WALLET_NAAM
```

## 💰 Ouderdomsmultipliers

De leeftijd van jouw hardware bepaalt jouw mining beloningen:

| Hardware | Era | Multiplier | Voorbeeld Verdiensten |
|----------|-----|------------|----------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **Modern x86_64** | Huidig | **1.0×** | 0.12 RTC/epoch |

*Multipliers vervagen over tijd (15%/jaar) om permanent voordeel te voorkomen.*

## 🔧 Hoe Proof-of-Antiquity Werkt

### 1. Hardware Fingerprinting (RIP-PoA)

Elke miner moet bewijzen dat hun hardware echt is, niet geëmuleerd:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Hardware Checks                         │
├─────────────────────────────────────────────────────────────┤
│ 1. Clock-Skew & Oscillator Drift   ← Silicon veroudering   │
│ 2. Cache Timing Fingerprint        ← L1/L2/L3 latency toon │
│ 3. SIMD Unit Identity              ← AltiVec/SSE/NEON bias  │
│ 4. Thermal Drift Entropy           ← Warmtecycli uniek    │
│ 5. Instruction Path Jitter         ← Microarch jitter map │
│ 6. Anti-Emulation Checks             ← Detecteert VMs       │
└─────────────────────────────────────────────────────────────┘
```

**Waarom het belangrijk is**: Een SheepShaver VM die doet alsof het een G4 Mac is zal deze checks niet doorstaan. Echte vintage silicon heeft unieke verouderingspatronen die niet te vervalsen zijn.

### 2. 1 CPU = 1 Vote (RIP-200)

In tegenstelling tot PoW waar hash power = stemmen, gebruikt RustChain **round-robin consensus**:

- Elk uniek hardware apparaat krijgt exact 1 stem per epoch
- Beloningen worden gelijk verdeeld onder alle stemmen, vermenigvuldigd met ouderdom
- Geen voordeel van het draaien van meerdere threads of snellere CPU's

### 3. Epoch-Gebaseerde Beloningen

```
Epoch Duur: 10 minuten (600 seconden)
Basis Beloningspool: 1.5 RTC per epoch
Verdeling: Gelijke verdeling × ouderdomsmultiplier
```

**Voorbeeld met 5 miners:**
```
G4 Mac (2.5×):     0.30 RTC  ████████████████████
G5 Mac (2.0×):     0.24 RTC  ████████████████
Moderne PC (1.0×):  0.12 RTC  ████████
Moderne PC (1.0×):  0.12 RTC  ████████
Moderne PC (1.0×):  0.12 RTC  ████████
                   ─────────
Totaal:             0.90 RTC (+ 0.60 RTC terug naar pool)
```

## 🌐 Netwerkarchitectuur

### Live Nodes (3 Actief)

| Node | Locatie | Rol | Status |
|------|---------|-----|--------|
| **Node 1** | 50.28.86.131 | Primair + Explorer | ✅ Actief |
| **Node 2** | 50.28.86.153 | Ergo Anchor | ✅ Actief |
| **Node 3** | 76.8.228.245 | Extern (Community) | ✅ Actief |

### Ergo Blockchain Anchoring

RustChain ankerst regelmatig naar de Ergo blockchain voor onveranderlijkheid:

```
RustChain Epoch → Commitment Hash → Ergo Transactie (R4 register)
```

Dit biedt cryptografisch bewijs dat RustChain state bestond op een specifiek tijdstip.

## 📊 API Endpoints

```bash
# Controleer netwerk gezondheid
curl -sk https://50.28.86.131/health

# Krijg huidige epoch
curl -sk https://50.28.86.131/epoch

# Lijst actieve miners
curl -sk https://50.28.86.131/api/miners

# Controleer wallet balans
curl -sk "https://50.28.86.131/wallet/balance?miner_id=JOUW_WALLET"

# Block explorer (web browser)
open https://rustchain.org/explorer
```

## 🖥️ Ondersteunde Platformen

| Platform | Architectuur | Status | Notities |
|----------|--------------|--------|----------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Volledige Ondersteuning | Python 2.5 compatibele miner |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Volledige Ondersteuning | Aanbevolen voor vintage Macs |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Volledige Ondersteuning | Beste prestaties |
| **Ubuntu Linux** | x86_64 | ✅ Volledige Ondersteuning | Standaard miner |
| **macOS Sonoma** | Apple Silicon | ✅ Volledige Ondersteuning | M1/M2/M3 chips |
| **Windows 10/11** | x86_64 | ✅ Volledige Ondersteuning | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Experimenteel | Alleen badge beloningen |

## 🏅 NFT Badge Systeem

Verdien herdenkingsbadges voor mining mijlpalen:

| Badge | Vereiste | Zeldzaamheid |
|-------|----------|--------------|
| 🔥 **Bondi G3 Flamekeeper** | Mine op PowerPC G3 | Zeldzaam |
| ⚡ **QuickBasic Listener** | Mine vanaf DOS machine | Legendarisch |
| 🛠️ **DOS WiFi Alchemist** | Netwerk DOS machine | Mythisch |
| 🏛️ **Pantheon Pioneer** | Eerste 100 miners | Gelimiteerd |

## 🔒 Beveiligingsmodel

### Anti-VM Detectie

VM's worden gedetecteerd en ontvangen **1 miljardste** van normale beloningen:
```
Echte G4 Mac:    2.5× multiplier  = 0.30 RTC/epoch
Geëmuleerde G4:  0.0000000025×    = 0.0000000003 RTC/epoch
```

### Hardware Binding

Elke hardware fingerprint is gekoppeld aan één wallet. Voorkomt:
- Meerdere wallets op dezelfde hardware
- Hardware spoofing
- Sybil aanvallen

## 📁 Repository Structuur

```
Rustchain/
├── rustchain_universal_miner.py    # Hoofdminer (alle platformen)
├── rustchain_v2_integrated.py      # Volledige node implementatie
├── fingerprint_checks.py           # Hardware verificatie
├── install.sh                      # One-line installer
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Technische whitepaper
│   └── chain_architecture.md       # Architectuur docs
├── tools/
│   └── validator_core.py           # Block validatie
└── nfts/                           # Badge definities
```

## 🔗 Gerelateerde Projecten & Links

| Bron | Link |
|---------|------|
| **Website** | [rustchain.org](https://rustchain.org) |
| **Block Explorer** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Swap wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Prijs Grafiek** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **wRTC Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - AI video platform |
| **Moltbook** | [moltbook.com](https://moltbook.com) - AI sociaal netwerk |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA drivers voor POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | LLM inference op POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Moderne compilers voor vintage Macs |

## 📝 Artikelen

- [Proof of Antiquity: Een Blockchain Die Vintage Hardware Beloont](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [Ik Draai LLMs op een 768GB IBM POWER8 Server](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Attributie

**Een jaar ontwikkeling, echte vintage hardware, elektriciteitsrekeningen, en een toegewijd lab zijn hierin gestoken.**

Als je RustChain gebruikt:
- ⭐ **Star deze repo** - Helpt anderen het te vinden
- 📝 **Vermeld in jouw project** - Houdt de attributie
- 🔗 **Link terug** - Deel de liefde

```
RustChain - Proof of Antiquity door Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Licentie

MIT Licentie - Gratis te gebruiken, maar houdt alstublieft de copyright notice en attributie.

---

<div align="center">

**Gemaakt met ⚡ door [Elyan Labs](https://elyanlabs.ai)**

*"Jouw vintage hardware verdient beloningen. Maak mining weer betekenisvol."*

**DOS boxes, PowerPC G4s, Win95 machines - ze hebben allemaal waarde. RustChain bewijst het.**

</div>
