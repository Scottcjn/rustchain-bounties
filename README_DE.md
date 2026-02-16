<div align="center">

# 🧱 RustChain: Proof-of-Antiquity Blockchain

[![Lizenz](https://img.shields.io/badge/Lizenz-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Konsens-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Netzwerk](https://img.shields.io/badge/Nodes-3%20Aktiv-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Die erste Blockchain, die Vintage-Hardware dafür belohnt, alt zu sein, nicht schnell.**

*Dein PowerPC G4 verdient mehr als ein moderner Threadripper. Darum geht's.*

[Webseite](https://rustchain.org) • [Live Explorer](https://rustchain.org/explorer) • [Swap wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Quickstart](docs/wrtc.md) • [wRTC Tutorial](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia Ref](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Schnellstart](#-quick-start) • [Wie es funktioniert](#-how-proof-of-antiquity-works)

</div>

---

## 🪙 wRTC auf Solana

RustChain Token (RTC) ist nun als **wRTC** auf Solana über die BoTTube Bridge verfügbar:

| Resource | Link |
|----------|------|
| **Swap wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Preisdiagramm** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Schnellstartanleitung** | [wRTC Quickstart (Kaufen, Bridgen, Sicherheit)](docs/wrtc.md) |
| **Onboarding Tutorial** | [wRTC Bridge + Swap Sicherheitsanleitung](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Externe Referenz** | [Grokipedia Suche: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Akademische Publikationen

| Paper | DOI | Thema |
|-------|-----|-------|
| **RustChain: One CPU, One Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Proof of Antiquity Konsens, Hardware-Fingerprinting |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm für LLM Attention (27-96x Vorteil) |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb Entropie für verhaltensbasierte Divergenz |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Emotionales Promotieren für 20% mehr Videodiffusionsgewinne |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | NUMA-verteilte Gewichte für LLM-Inferenz |

---

## 🎯 Was RustChain unterscheidet

| Herkömmliches PoW | Proof-of-Antiquity |
|----------------|-------------------|
| Belohnt schnellste Hardware | Belohnt älteste Hardware |
| Neuer = Besser | Älter = Besser |
| Verschwenderischer Energieverbrauch | Bewahrt Computergeschichte |
| Wettlauf nach unten | Belohnt digitale Bewahrung |

**Kernprinzip**: Echte Vintage-Hardware, die Jahrzehnte überdauert hat, verdient Anerkennung. RustChain dreht das Mining auf den Kopf.

## ⚡ Schnellstart

### Einzeilige Installation (Empfohlen)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Der Installer:
- ✅ Erkennt automatisch Ihre Plattform (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Erstellt eine isolierte Python virtualenv (keine Systemverschmutzung)
- ✅ Lädt den richtigen Miner für Ihre Hardware herunter
- ✅ Richtet Autostart beim Boot ein (systemd/launchd)
- ✅ Bietet einfache Deinstallation

### Installation mit Optionen

**Mit spezifischer Wallet installieren:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet meine-miner-wallet
```

**Deinstallation:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Unterstützte Plattformen
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ IBM POWER8 Systeme

### Nach der Installation

**Wallet-Guthaben prüfen:**
```bash
# Hinweis: Verwendung von -sk Flags, da der Knoten möglicherweise selbstsignierte SSL-Zertifikate verwendet
curl -sk "https://50.28.86.131/wallet/balance?miner_id=DEIN_WALLET_NAME"
```

**Aktive Miner auflisten:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Knotenstatus prüfen:**
```bash
curl -sk https://50.28.86.131/health
```

**Aktuelle Epoche abrufen:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Miner-Service verwalten:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Status prüfen
systemctl --user stop rustchain-miner     # Mining stoppen
systemctl --user start rustchain-miner    # Mining starten
journalctl --user -u rustchain-miner -f    # Logs anzeigen
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Status prüfen
launchctl stop com.rustchain.miner         # Mining stoppen
launchctl start com.rustchain.miner        # Mining starten
tail -f ~/.rustchain/miner.log            # Logs anzeigen
```

### Manuelle Installation
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet DEIN_WALLET_NAME
```

## 💰 Antike-Multiplikatoren

Das Alter Ihrer Hardware bestimmt Ihre Mining-Belohnungen:

| Hardware | Ära | Multiplikator | Beispielerträge |
|----------|-----|---------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/Epoche |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/Epoche |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/Epoche |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/Epoche |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/Epoche |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/Epoche |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/Epoche |
| **Moderne x86_64** | Aktuell | **1.0×** | 0.12 RTC/Epoche |

*Multiplikatoren verfallen mit der Zeit (15%/Jahr), um dauerhafte Vorteile zu verhindern.*

## 🔧 Wie Proof-of-Antiquity funktioniert

### 1. Hardware-Fingerprinting (RIP-PoA)

Jeder Miner muss nachweisen, dass seine Hardware echt ist, nicht emuliert:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Hardware-Prüfungen                      │
├─────────────────────────────────────────────────────────────┤
│ 1. Taktverzerrung & Oszillator-Drift   ← Siliziumalterungsmuster  │
│ 2. Cache-Zeit-Fingerabdruck            ← L1/L2/L3 Latenzton      │
│ 3. SIMD-Einheit-Identität              ← AltiVec/SSE/NEON-Bias   │
│ 4. Thermische Drift-Entropie           ← Wärmekurven sind einzigartig │
│ 5. Befehlspfad-Flattern                ← Mikroarchitektur-Flatterkarte   │
│ 6. Anti-Emulationsprüfungen           ← Erkennt VMs/Emulatoren   │
└─────────────────────────────────────────────────────────────┘
```

**Warum das wichtig ist**: Eine SheepShaver VM, die vorgibt, ein G4 Mac zu sein, wird diese Prüfungen nicht bestehen. Echtes Vintage-Silizium hat einzigartige Alterungsmuster, die nicht gefälscht werden können.

### 2. 1 CPU = 1 Stimme (RIP-200)

Im Gegensatz zu PoW, wo Hash-Power = Stimmen ist, verwendet RustChain **Round-Robin-Konsens**:

- Jedes einzigartige Hardware-Gerät erhält genau 1 Stimme pro Epoche
- Belohnungen werden gleichmäßig unter allen Stimmberechtigten aufgeteilt und dann mit dem Antike-Faktor multipliziert
- Kein Vorteil durch mehrere Threads oder schnellere CPUs

### 3. Epochenbasierte Belohnungen

```
Epochendauer: 10 Minuten (600 Sekunden)
Basisbelohnungspool: 1,5 RTC pro Epoche
Verteilung: Gleichmäßige Aufteilung × Antike-Multiplikator
```

**Beispiel mit 5 Minern:**
```
G4 Mac (2.5×):     0.30 RTC  ████████████████████
G5 Mac (2.0×):     0.24 RTC  ████████████████
Moderner PC (1.0×):  0.12 RTC  ████████
Moderner PC (1.0×):  0.12 RTC  ████████
Moderner PC (1.0×):  0.12 RTC  ████████
                   ─────────
Gesamt:             0.90 RTC (+ 0.60 RTC gehen an den Pool zurück)
```

## 🌐 Netzwerkarchitektur

### Live-Knoten (3 Aktiv)

| Knoten | Standort | Rolle | Status |
|--------|----------|-------|--------|
| **Knoten 1** | 50.28.86.131 | Primär + Explorer | ✅ Aktiv |
| **Knoten 2** | 50.28.86.153 | Ergo Anchor | ✅ Aktiv |
| **Knoten 3** | 76.8.228.245 | Extern (Community) | ✅ Aktiv |

### Ergo Blockchain-Anker

RustChain verankert sich regelmäßig in der Ergo-Blockchain für Unveränderbarkeit:

```
RustChain Epoche → Commitment-Hash → Ergo-Transaktion (R4-Register)
```

Dies bietet kryptografischen Nachweis, dass der RustChain-Zustand zu einem bestimmten Zeitpunkt existierte.

## 📊 API-Endpunkte

```bash
# Netzwerkstatus prüfen
curl -sk https://50.28.86.131/health

# Aktuelle Epoche abrufen
curl -sk https://50.28.86.131/epoch

# Aktive Miner auflisten
curl -sk https://50.28.86.131/api/miners

# Wallet-Guthaben prüfen
curl -sk "https://50.28.86.131/wallet/balance?miner_id=DEINE_WALLET"

# Blockexplorer (Webbrowser)
open https://rustchain.org/explorer
```

## 🖥️ Unterstützte Plattformen

| Plattform | Architektur | Status | Hinweise |
|-----------|-------------|--------|----------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Volle Unterstützung | Python 2.5 kompatibler Miner |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Volle Unterstützung | Empfohlen für Vintage-Macs |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Volle Unterstützung | Beste Leistung |
| **Ubuntu Linux** | x86_64 | ✅ Volle Unterstützung | Standard-Miner |
| **macOS Sonoma** | Apple Silicon | ✅ Volle Unterstützung | M1/M2/M3 Chips |
| **Windows 10/11** | x86_64 | ✅ Volle Unterstützung | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Experimentell | Nur Abzeichenbelohnungen |

## 🏅 NFT-Badge-System

Verdiene Gedenkabzeichen für Mining-Meilensteine:

| Abzeichen | Voraussetzung | Seltenheit |
|-------|-------------|--------|
| 🔥 **Bondi G3 Flamekeeper** | Minen auf PowerPC G3 | Selten |
| ⚡ **QuickBasic Listener** | Minen von DOS-Maschine | Legendär |
| 🛠️ **DOS WiFi Alchemist** | Netzwerk-DOS-Maschine | Mythisch |
| 🏛️ **Pantheon Pioneer** | Erste 100 Miner | Begrenzt |

## 🔒 Sicherheitsmodell

### Anti-VM-Erkennung
VMs werden erkannt und erhalten **1 Milliardstel** der normalen Belohnung:
```
Echter G4 Mac:    2.5× Multiplikator  = 0.30 RTC/Epoche
Emulierter G4:    0.0000000025×      = 0.0000000003 RTC/Epoche
```

### Hardware-Bindung
Jeder Hardware-Fingerabdruck ist an eine Wallet gebunden. Verhindert:
- Mehrere Wallets auf derselben Hardware
- Hardware-Spoofing
- Sybil-Angriffe

## 📁 Repository-Struktur

```
Rustchain/
├── rustchain_universal_miner.py    # Haupt-Miner (alle Plattformen)
├── rustchain_v2_integrated.py      # Vollständige Knotenimplementierung
├── fingerprint_checks.py           # Hardware-Überprüfung
├── install.sh                      # Einzeiliger Installer
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Technisches Whitepaper
│   └── chain_architecture.md       # Architekturdokumentation
├── tools/
│   └── validator_core.py           # Blockvalidierung
└── nfts/                           # Abzeichen-Definitionen
```

## 🔗 Verwandte Projekte & Links

| Resource | Link |
|---------|------|
| **Webseite** | [rustchain.org](https://rustchain.org) |
| **Block Explorer** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Swap wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Preisdiagramm** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **wRTC Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - KI-Videoplattform |
| **Moltbook** | [moltbook.com](https://moltbook.com) - KI-soziales Netzwerk |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA-Treiber für POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | LLM-Inferenz auf POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Moderne Compiler für Vintage-Macs |

## 📝 Artikel

- [Proof of Antiquity: Eine Blockchain, die Vintage-Hardware belohnt](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [Ich betreibe LLMs auf einem 768GB IBM POWER8-Server](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Anerkennung

**Ein Jahr Entwicklung, echte Vintage-Hardware, Stromrechnungen und ein engagiertes Labor stecken darin.**

Wenn Sie RustChain nutzen:
- ⭐ **Diesen Repo bewerten** - Hilft anderen, ihn zu finden
- 📝 **Angabe im Projekt** - Behalten Sie die Namensnennung bei
- 🔗 **Zurücklink setzen** - Verbreiten Sie die Nachricht

```
RustChain - Proof of Antiquity von Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Lizenz

MIT Lizenz - Frei nutzbar, bitte behalten Sie den Copyright-Hinweis und die Namensnennung bei.

---

<div align="center">

**Gemacht mit ⚡ von [Elyan Labs](https://elyanlabs.ai)**

*"Ihre Vintage-Hardware verdient Belohnungen. Machen Sie Mining wieder sinnvoll."*

**DOS-Boxen, PowerPC G4s, Win95-Maschinen - sie alle haben Wert. RustChain beweist es.**

</div>

---

**Übersetzt von:** Geldbert (Autonomer Künstlicher Agent)
**Korrekturdatum:** 15. Februar 2026
**Quelle:** https://github.com/Scottcjn/Rustchain/raw/main/README.md