<div align="center">

# 🧱 RustChain: Bloķēšanas ķēdes pierādījums par senatvi (Proof-of-Antiquity)

[![Licence](https://img.shields.io/badge/Licence-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Bloķēšanas ķēde](https://img.shields.io/badge/Konsensuss-Pier%C4%81d%C4%ABjums-par-senatvi-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Tīkls](https://img.shields.io/badge/Mezgli-3%20Akt%C4%ABvi-brightgreen)](https://rustchain.org/explorer)
[![Redzams BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Pirmā bloķēšanas ķēde, kas atalgo veco aparatūru par tās vecumu, nevis ātrumu.**

*Jūsu PowerPC G4 pelna vairāk nekā mūsdienu Threadripper. Tā ir mērķa būtība.*

[Mājas lapa](https://rustchain.org) • [Tiešsaistes pārlūks](https://rustchain.org/explorer) • [Mainīt wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [Ātrs ceļvedis wRTC](docs/wrtc.md) • [wRTC apmācība](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia atsauce](https://grokipedia.com/search?q=RustChain) • [Izpētes dokuments](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Ātra sākšana](#-ātra-sākšana) • [Kā tas darbojas](#-kā-darbojas-pierādījums-par-senatvi)

</div>

---

## 🪙 wRTC uz Solana

RustChain (RTC) tagad pieejams kā **wRTC** uz Solanas, izmantojot BoTTube tiltu:

| Resurss | Saite |
|-------------|--------|
| **Mainīt wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Cenu grafiks** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **RTC ↔ wRTC tilts** | [BoTTube tilts](https://bottube.ai/bridge) |
| **Ātrs ceļvedis** | [wRTC ceļvedis (Pirkt, Tilti, Drošība)](docs/wrtc.md) |
| **Apmācība** | [wRTC tilta un apmaiņas drošības apmācība](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Ārējās atsauces** | [Meklēšana Grokipedia: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Tokenu izveide** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Akadēmiskās publikācijas

| Raksts | DOI | Tēma |
|---------|-----|-------|
| **RustChain: Viens CPU, viens balss** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Pierādījuma-par-senatvi konsensuss, aparatūras pirkstu nospiedumi |
| **Ne-bijunktīvā permutācijas sabrukums** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm LLM uzmanībai (27-96× pārsniegums) |
| **PSE aparatūras entropija** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb entropija |
| **Neiromorfa uzvedņu tulkošana** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Emocionāli uzvedni 20% videodifūzijas uzlabošanai |
| **RAM naudas kastes** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | Izplatītā NUMA svaru bankas LLM secināšanai |

---

## 🎯 Kas padara RustChain atšķirīgu

| Tradicionāla PoW | Proof-of-Antiquity |
|----------------|-------------------|
| Atalgo ātrāko aparatūru | Atalgo vecāko aparatūru |
| Jaunāks = Labāks | Vecāks = Labāks |
 | Iztērējošs enerģijas patēriņš | Saglabā datordatoru vēsturi |
| Lādiņa uz leju cīņa | Digitālas saglabāšanas atzīšana |

**Pamatprincips**: Vēsturiski nozīmīga aparatūra, kas ir izturējusi gadus desmitiem, ir pelnījusi atzīšanu. RustChain apgriež tradicionālo raktuvju darbību otrādi.

## ⚡ Ātra sākšana

### Vienas rindiņas instalēšana (Ieteicams)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Instalators:
- ✅ Automātiski noteiks jūsu platformu (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Izveidos izolētu Python virtualenv (neteiksmē sistēmu)
- ✅ Lejupielādēs piemērotu raktuvnieku jūsu aparatūrai
- ✅ Iestatīs automātisku palaišanu pie ieslēgšanas (systemd/launchd)
- ✅ Nodrošinās vieglu atinstalēšanu

### Instalēšana ar opcijām

**Instalēt ar noteiktu makskoni:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet mana-makskonis
```

**Atinstalēt:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Atbalstītās platformas
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ IBM POWER8 sistēmas

### Pēc instalēšanas

**Pārbaudiet makskonas atlikumu:**
```bash
# Piezīme: Izmanto -sk karodziņu, jo mezgli var izmantot pašpazīstamas SSL sertifikātus
curl -sk "https://50.28.86.131/wallet/balance?miner_id=MAKSKONAS_DATI"
```

**Saraksts ar aktīviem raktuvniekiem:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Pārbaudiet mezga stāvokli:**
```bash
curl -sk https://50.28.86.131/health
```

**Iegūstiet pašreizējo periodu:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Pārvaldiet raktuvnieka pakalpojumu:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Pārbaudīt statusu
systemctl --user stop rustchain-miner      # Apturēt raktuvniecību
systemctl --user start rustchain-miner     # Sākt raktuvniecību
journalctl --user -u rustchain-miner -f    # Skatīt žurnāluzrakstus
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain           # Pārbaudīt statusu
launchctl stop com.rustchain.miner        # Apturēt raktuvniecību
launchctl start com.rustchain.miner       # Sākt raktuvniecību
tail -f ~/.rustchain/miner.log            # Skatīt žurnāluzrakstus
```

### Manuāla instalācija
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet MAKSKONAS_DATI
```

## 💰 Senatves reizinātāji

Jūsu aparatūras vecums nosaka jūsu algas apmēru:

| Aparatūra | Ēra | Reizinātājs | Piemēra peļņa |
|-----------------|-----|-----------|-------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/periodā |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/periodā |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/periodā |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/periodā |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/periodā |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/periodā |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/periodā |
| **x86_64 Mūsdienīgs** | Pašreiz | **1.0×** | 0.12 RTC/periodā |

*Reizinātāji laika gaitā samazinās (15% gadā), lai novērstu mūžīgas priekšrocības.*

## 🔧 Kā darbojas Proof-of-Antiquity (Pierādījums par senatvi)

### 1. Aparatūras pirkstu nospiedums (RIP-PoA)

Katram raktuvniekam jāpierāda, ka viņu aparatūra ir īsta, nevis simulēta:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Aparatūras pārbaudes                    │
├─────────────────────────────────────────────────────────────┤
│ 1. Pulkstenis-nobīde & Oscilatora nobīde ← Silīcija novecošanas modeļi│
│ 2. Kešatmiņas laika pirkstu nospiedumi ← L1/L2/L3 latenču toņi │
│ 3. SIMD vienības identitāte ← AltiVec/SSE/NEON novirzes   │
│ 4. Termiskās novirzes entropija ← Unikāli silīcija sildeklī│
│ 5. Instrukciju ceļa vibrācija ← Mikroarhitektūras jitera karte│
│ 6. Pret-emulācijas pārbaudes ← VM/emulatoru noteikšana     │
└─────────────────────────────────────────────────────────────┘
```

**Kāpēc tas ir svarīgi**: VM SheepShaver, kas izliekas par Mac G4, neizdos šīs pārbaudes. Īstai vēsturiskai aparatūrai ir unikāli novecošanas modeļi, ko nevar viltot.

### 2. 1 CPU = 1 balss (RIP-200)

Atšķirībā no PoW, kur kravas jauda = balss, RustChain izmanto **round-robin konsensu**:

- Katra unikāla aparatūra saņem tieši vienu balsi periodā
- Algas tiek dalītas vienmērīgi starp visiem balsojošajiem, pēc tam reizinātas ar senatvi
- Nav nekādu priekšrocību no vairāku pavedienu vai ātrāku CPU izmantošanas

### 3. Atalgojums, balstīts uz periodiem

```
Perioda ilgums: 10 minūtes (600 sekundes)
Pamata atalgojumu fonds: 1,5 RTC par periodu
Sadalījums: Vienāds sadalījums × senatves reizinātājs
```

**Piemērs ar 5 raktuvniekiem:**
```
Mac G4 (2,5×):     0,30 RTC  ████████████████████
Mac G5 (2,0×):     0,24 RTC  ████████████████
PC Mūsdienīgs (1,0×):  0,12 RTC  ████████
PC Mūsdienīgs (1,0×):  0,12 RTC  ████████
PC Mūsdienīgs (1,0×):  0,12 RTC  ████████
                   ─────────
Kopā:             0,90 RTC (+ 0,60 RTC atgriezti fondā)
```

## 🌐 Tīkla arhitektūra

### Tiešie mezgli (3 aktīvi)

| Mezgls | Atrašanās vieta | Loma | Statuss |
|------|----------|-------|--------|
| **Mezgls 1** | 50.28.86.131 | Primārais + Pārlūks | ✅ Aktīvs |
| **Mezgls 2** | 50.28.86.153 | Ergo enkurmežglis | ✅ Aktīvs |
| **Mezgls 3** | 76.8.228.245 | Ārējais (Kopiena) | ✅ Aktīvs |

### Ergo bloķķēdes enkurmežgli

RustChain periodiski pieslēdzas Ergo bloķķēdei, lai garantētu mūžību:

```
RustChain periods → Iesnieguma hash → Ergo transakcija (reģistrs R4)
```

Tas nodrošina kriptogrāfiskus pierādījumus, ka RustChain stāvoklis pastāvēja konkrētā laika brīdī.

## 📊 API galapunkti

```bash
# Pārbaudīt tīkla stāvokli
curl -sk https://50.28.86.131/health

# Iegūt pašreizējo periodu
curl -sk https://50.28.86.131/epoch

# Saraksts ar aktīviem raktuvniekiem
curl -sk https://50.28.86.131/api/miners

# Pārbaudīt makskonas atlikumu
curl -sk "https://50.28.86.131/wallet/balance?miner_id=MAKSKONA"

# Bloka pārlūks (tīmekļa pārlūks)
open https://rustchain.org/explorer
```

## 🖥️ Atbalstītās platformas

| Platforma | Arhitektūra | Statuss | Piezīmes |
|----------|------------|--------|---------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Pilnīgs atbalsts | Python 2.5 saderīgs raktuvnieks |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Pilnīgs atbalsts | Ieteicams vēsturiskajiem Mac |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Pilnīgs atbalsts | Labākā veiktspēja |
| **Ubuntu Linux** | x86_64 | ✅ Pilnīgs atbalsts | Standarta raktuvnieks |
| **macOS Sonoma** | Apple Silicon | ✅ Pilnīgs atbalsts | M1/M2/M3 čipi |
| **Windows 10/11** | x86_64 | ✅ Pilnīgs atbalsts | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Eksperimentāls | Tikai nozīmju atalgojumi |

## 🏅 NFT nozīmju sistēma

Iegūstiet raktuvniecības sasniegumu nozīmes:

| Nozīme | Prasības | Retums |
|---------|-------------|------------|
| 🔥 **Bondi G3 Uguns sargātājs** | Raktuvniecība uz PowerPC G3 | Reta |
| ⚡ **QuickBasic Klausītājs** | Raktuvniecība no DOS mašīnas | Leģendāra |
| 🛠️ **DOS WiFi Alķīmiķis** | Tīkla pieslēgta DOS mašīna | Mītiska |
| 🏛️ **Panteona Pionieris** | Pirmie 100 raktuvnieki | Ierobežots |

## 🔒 Drošības modelis

### Pret-VM noteikšana

VM tiek noteikti un saņem **1 miljardu** reizes mazāku atalgojumu:
```
Īsts Mac G4:     2,5× reizinātājs  = 0,30 RTC/periodā
Simulēts G4:     0,0000000025×    = 0,0000000003 RTC/periodā
```

### Aparatūras saistīšana
Katrs aparatūras pirkstu nospiedums ir saistīts ar vienu makskoni. Novērš:
- Vairākas makskonas uz vienas aparatūras
- Aparatūras viltošanu
- Sybil uzbrukumus

## 📁 Repozitorija struktūra

```
Rustchain/
├── rustchain_universal_miner.py    # Galvenais raktuvnieks (visas platformas)
├── rustchain_v2_integrated.py      # Pilna mezglu ieviešana
├── fingerprint_checks.py           # Aparatūras verifikācija
├── install.sh                      # Vienas rindiņas instalators
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Tehniskā izpēte
│   └── chain_architecture.md       # Arhitektūras dokumentācija
├── tools/
│   └── validator_core.py           # Bloku validācija
└── nfts/                           # Nozīmju definīcijas
```

## 🔗 Saistītie projekti un saites

| Resurss | Saite |
|-------------|--------|
| **Mājas lapa** | [rustchain.org](https://rustchain.org) |
| **Bloku pārlūks** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Mainīt wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Cenu grafiks** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **RTC ↔ wRTC tilts** | [BoTTube tilts](https://bottube.ai/bridge) |
| **wRTC tokenu izveide** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - AI video platforma |
| **Moltbook** | [moltbook.com](https://moltbook.com) - AI sociālais tīkls |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA draiveri POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | LLM secināšana POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Mūsdienīgi kompilatori vēsturiskajiem Mac |

## 📝 Raksti

- [Proof of Antiquity: Bloķēšanas ķēde, kas atalgo vēsturisko aparatūru](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
| [Es darbinu LLM uz 768GB IBM POWER8 servera](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Atzinības

**Gads attīstībā, īsta vēsturiska aparatūra, elektrības rēķini un īpaši aprīkoti laboratoriju telpas ir gājuši šajā projektā.**

Ja lietojat RustChain:
- ⭐ **Novērtējiet šo repozitoriju** - Palīdz citiem atrast
- 📝 **Norādiet atzinības savā projektā** - Saglabājiet atzinību
- 🔗 **Atgriezeniskās saites** - Palaidiet labu vītni

```
RustChain - Proof of Antiquity no Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Licence

MIT licence - Brīvi lietojams, bet lūdzu saglabājiet autortiesību paziņojumu un atzinību.

---

<div align="center">

**Izveidots ar ⚡ no [Elyan Labs](https://elyanlabs.ai)**

*"Jūsu vēsturiskā aparatūra pelna atlīdzību. Padariet raktuvniecību atkal jēgpilnu."*

**DOS kastes, PowerPC G4, Win95 mašīnas - tām visām ir vērtība. RustChain to pierāda.**

</div>