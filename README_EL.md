<div align="center">

# 🧱 RustChain: Proof-of-Antiquity Blockchain

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Η πρώτη blockchain που ανταμείβει το vintage hardware επειδή είναι παλιό, όχι γρήγορο.**

*Το PowerPC G4 σας κερδίζει περισσότερα από ένα σύγχρονο Threadripper. Αυτό είναι το νόημα.*

[Ιστότοπος](https://rustchain.org) • [Live Explorer](https://rustchain.org/explorer) • [Swap wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Quickstart](docs/wrtc.md) • [wRTC Tutorial](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia Ref](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Quick Start](#-quick-start) • [Πώς Λειτουργεί](#-how-proof-of-antiquity-works)

</div>

---

## 🪙 wRTC στο Solana

Το RustChain Token (RTC) είναι πλέον διαθέσιμο ως **wRTC** στο Solana μέσω της BoTTube Bridge:

| Πόρος | Σύνδεσμος |
|----------|------|
| **Swap wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Διάγραμμα Τιμών** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Οδηγός Quickstart** | [wRTC Quickstart (Αγορά, Bridge, Ασφάλεια)](docs/wrtc.md) |
| **Tutorial Onboarding** | [Οδηγός Ασφάλειας wRTC Bridge + Swap](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Εξωτερική Αναφορά** | [Grokipedia Search: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Ακαδημαϊκές Δημοσιεύσεις

| Δοκίμιο | DOI | Θέμα |
|-------|-----|-------|
| **RustChain: One CPU, One Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Proof of Antiquity consensus, hardware fingerprinting |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm για LLM attention (27-96x πλεονέκτημα) |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb entropy για συμπεριφορική απόκλιση |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Emotional prompting για 20% κέρδη στο video diffusion |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | NUMA-distributed weight banking για LLM inference |

---

## 🎯 Τι Κάνει το RustChain Διαφορετικό

| Παραδοσιακό PoW | Proof-of-Antiquity |
|----------------|-------------------|
| Ανταμείβει το ταχύτερο hardware | Ανταμείβει το παλαιότερο hardware |
| Νεότερο = Καλύτερο | Παλαιότερο = Καλύτερο |
| Σπάταλη κατανάλωση ενέργειας | Διατηρεί την υπολογιστική ιστορία |
| Αγώνας δρόμου στην απόδοση | Ανταμείβει την ψηφιακή διατήρηση |

**Βασική Αρχή**: Το αυθεντικό vintage hardware που έχει επιβιώσει για δεκαετίες αξίζει αναγνώριση. Το RustChain ανατρέπει το mining.

## ⚡ Quick Start

### One-Line Install (Προτείνεται)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Ο installer:
- ✅ Ανιχνεύει αυτόματα την πλατφόρμα σας (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Δημιουργεί ένα απομονωμένο Python virtualenv (χωρίς ρύπανση του συστήματος)
- ✅ Κατεβάζει τον σωστό miner για το hardware σας
- ✅ Ρυθμίζει την αυτόματη εκκίνηση (systemd/launchd)
- ✅ Παρέχει εύκολη απεγκατάσταση

### Εγκατάσταση με Επιλογές

**Εγκατάσταση με συγκεκριμένο wallet:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-miner-wallet
```

**Απεγκατάσταση:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Υποστηριζόμενες Πλατφόρμες
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ Συστήματα IBM POWER8

### Μετά την Εγκατάσταση

**Ελέγξτε το υπόλοιπο του wallet σας:**
```bash
# Σημείωση: Χρήση σημαιών -sk επειδή το node μπορεί να χρησιμοποιεί self-signed SSL certificate
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

**Λίστα ενεργών miners:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Έλεγχος υγείας node:**
```bash
curl -sk https://50.28.86.131/health
```

**Λήψη τρέχοντος epoch:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Διαχείριση της υπηρεσίας miner:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Έλεγχος κατάστασης
systemctl --user stop rustchain-miner      # Διακοπή mining
systemctl --user start rustchain-miner     # Έναρξη mining
journalctl --user -u rustchain-miner -f    # Προβολή logs
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Έλεγχος κατάστασης
launchctl stop com.rustchain.miner         # Διακοπή mining
launchctl start com.rustchain.miner        # Έναρξη mining
tail -f ~/.rustchain/miner.log             # Προβολή logs
```

### Manual Install
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet YOUR_WALLET_NAME
```

## 💰 Πολλαπλασιαστές Αρχαιότητας

Η ηλικία του hardware σας καθορίζει τις ανταμοιβές mining:

| Hardware | Εποχή | Πολλαπλασιαστής | Παράδειγμα Κερδών |
|----------|-----|------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **Σύγχρονο x86_64** | Τρέχον | **1.0×** | 0.12 RTC/epoch |

*Οι πολλαπλασιαστές μειώνονται με την πάροδο του χρόνου (15% ανά έτος) για την πρόληψη μόνιμου πλεονεκτήματος.*

## 🔧 Πώς Λειτουργεί το Proof-of-Antiquity

### 1. Hardware Fingerprinting (RIP-PoA)

Κάθε miner πρέπει να αποδείξει ότι το hardware του είναι αληθινό και όχι emulated:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Hardware Έλεγχοι                        │
├─────────────────────────────────────────────────────────────┤
│ 1. Clock-Skew & Oscillator Drift   ← Μοτίβο γήρανσης πυριτίου│
│ 2. Cache Timing Fingerprint        ← Τόνος latency L1/L2/L3 │
│ 3. SIMD Unit Identity              ← Μεροληψία AltiVec/SSE/NEON│
│ 4. Thermal Drift Entropy           ← Οι θερμικές καμπύλες είναι μοναδικές│
│ 5. Instruction Path Jitter         ← Χάρτης jitter microarch │
│ 6. Anti-Emulation Checks           ← Ανίχνευση VMs/emulators  │
└─────────────────────────────────────────────────────────────┘
```

**Γιατί έχει σημασία**: Ένα SheepShaver VM που προσποιείται ότι είναι G4 Mac θα αποτύχει σε αυτούς τους ελέγχους. Το πραγματικό vintage πυρίτιο έχει μοναδικά μοτίβα γήρανσης που δεν μπορούν να πλαστογραφηθούν.

### 2. 1 CPU = 1 Vote (RIP-200)

Σε αντίθεση με το PoW όπου η ισχύς hashing = ψήφοι, το RustChain χρησιμοποιεί **round-robin consensus**:

- Κάθε μοναδική συσκευή hardware λαμβάνει ακριβώς 1 ψήφο ανά epoch
- Οι ανταμοιβές μοιράζονται εξίσου μεταξύ όλων των ψηφοφόρων και στη συνέχεια πολλαπλασιάζονται με την αρχαιότητα
- Κανένα πλεονέκτημα από την εκτέλεση πολλαπλών threads ή ταχύτερων CPU

### 3. Ανταμοιβές βάσει Epoch

```
Διάρκεια Epoch: 10 λεπτά (600 δευτερόλεπτα)
Base Reward Pool: 1.5 RTC ανά epoch
Διανομή: Ίσο μερίδιο × πολλαπλασιαστής αρχαιότητας
```

**Παράδειγμα με 5 miners:**
```
G4 Mac (2.5×):     0.30 RTC  ████████████████████
G5 Mac (2.0×):     0.24 RTC  ████████████████
Modern PC (1.0×):  0.12 RTC  ████████
Modern PC (1.0×):  0.12 RTC  ████████
Modern PC (1.0×):  0.12 RTC  ████████
                   ─────────
Σύνολο:             0.90 RTC (+ 0.60 RTC επιστρέφονται στο pool)
```

## 🌐 Αρχιτεκτονική Δικτύου

### Ενεργά Nodes (3 Ενεργά)

| Node | Τοποθεσία | Ρόλος | Κατάσταση |
|------|----------|------|--------|
| **Node 1** | 50.28.86.131 | Primary + Explorer | ✅ Ενεργό |
| **Node 2** | 50.28.86.153 | Ergo Anchor | ✅ Ενεργό |
| **Node 3** | 76.8.228.245 | Εξωτερικό (Κοινότητα) | ✅ Ενεργό |

### Ergo Blockchain Anchoring

Το RustChain αγκυροβολεί περιοδικά στο Ergo blockchain για αμεταβλητότητα:

```
RustChain Epoch → Commitment Hash → Ergo Transaction (R4 register)
```

Αυτό παρέχει κρυπτογραφική απόδειξη ότι η κατάσταση του RustChain υπήρχε σε μια συγκεκριμένη χρονική στιγμή.

## 📊 API Endpoints

```bash
# Έλεγχος υγείας δικτύου
curl -sk https://50.28.86.131/health

# Λήψη τρέχοντος epoch
curl -sk https://50.28.86.131/epoch

# Λίστα ενεργών miners
curl -sk https://50.28.86.131/api/miners

# Έλεγχος υπολοίπου wallet
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET"

# Block explorer (web browser)
open https://rustchain.org/explorer
```

## 🖥️ Υποστηριζόμενες Πλατφόρμες

| Πλατφόρμα | Αρχιτεκτονική | Κατάσταση | Σημειώσεις |
|----------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Πλήρης Υποστήριξη | Python 2.5 συμβατός miner |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Πλήρης Υποστήριξη | Προτείνεται για vintage Macs |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Πλήρης Υποστήριξη | Καλύτερη απόδοση |
| **Ubuntu Linux** | x86_64 | ✅ Πλήρης Υποστήριξη | Standard miner |
| **macOS Sonoma** | Apple Silicon | ✅ Πλήρης Υποστήριξη | M1/M2/M3 chips |
| **Windows 10/11** | x86_64 | ✅ Πλήρης Υποστήριξη | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Πειραματικό | Μόνο Badge rewards |

## 🏅 Σύστημα NFT Badge

Κερδίστε αναμνηστικά badges για ορόσημα mining:

| Badge | Απαίτηση | Σπανιότητα |
|-------|-------------|--------|
| 🔥 **Bondi G3 Flamekeeper** | Mining σε PowerPC G3 | Rare |
| ⚡ **QuickBasic Listener** | Mining από DOS machine | Legendary |
| 🛠️ **DOS WiFi Alchemist** | Δικτύωση DOS machine | Mythic |
| 🏛️ **Pantheon Pioneer** | Πρώτοι 100 miners | Limited |

## 🔒 Μοντέλο Ασφαλείας

### Ανίχνευση Anti-VM
Τα VMs ανιχνεύονται και λαμβάνουν το **1 δισεκατομμυριοστό** των κανονικών ανταμοιβών:
```
Πραγματικό G4 Mac:    2.5× multiplier  = 0.30 RTC/epoch
Emulated G4:    0.0000000025×    = 0.0000000003 RTC/epoch
```

### Hardware Binding
Κάθε hardware fingerprint συνδέεται με ένα wallet. Αποτρέπει:
- Πολλαπλά wallets στο ίδιο hardware
- Hardware spoofing
- Sybil attacks

## 📁 Δομή Αποθετηρίου (Repository)

```
Rustchain/
├── rustchain_universal_miner.py    # Κύριος miner (όλες οι πλατφόρμες)
├── rustchain_v2_integrated.py      # Υλοποίηση Full node
├── fingerprint_checks.py           # Επαλήθευση Hardware
├── install.sh                      # One-line installer
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Τεχνικό whitepaper
│   └── chain_architecture.md       # Έγγραφα αρχιτεκτονικής
├── tools/
│   └── validator_core.py           # Επαλήθευση Block
└── nfts/                           # Ορισμοί Badge
```

## 🔗 Σχετικά Projects & Σύνδεσμοι

| Πόρος | Σύνδεσμος |
|---------|------|
| **Ιστότοπος** | [rustchain.org](https://rustchain.org) |
| **Block Explorer** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Swap wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Διάγραμμα Τιμών** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **wRTC Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - AI video platform |
| **Moltbook** | [moltbook.com](https://moltbook.com) - AI social network |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA drivers για POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | LLM inference σε POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Σύγχρονοι compilers για vintage Macs |

## 📝 Άρθρα

- [Proof of Antiquity: A Blockchain That Rewards Vintage Hardware](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [I Run LLMs on a 768GB IBM POWER8 Server](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Attribution

**Ένας χρόνος ανάπτυξης, πραγματικό vintage hardware, λογαριασμοί ρεύματος και ένα εξειδικευμένο εργαστήριο επενδύθηκαν σε αυτό.**

Εάν χρησιμοποιείτε το RustChain:
- ⭐ **Star this repo** - Βοηθά τους άλλους να το βρουν
- 📝 **Credit in your project** - Διατηρήστε την αναφορά (attribution)
- 🔗 **Link back** - Μοιραστείτε την αγάπη

```
RustChain - Proof of Antiquity by Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Άδεια (License)

MIT License - Ελεύθερο για χρήση, αλλά παρακαλούμε διατηρήστε την ειδοποίηση πνευματικών δικαιωμάτων και την αναφορά.

---

<div align="center">

**Κατασκευάστηκε με ⚡ από την [Elyan Labs](https://elyanlabs.ai)**

*"Το vintage hardware σας κερδίζει ανταμοιβές. Κάντε το mining ουσιαστικό ξανά."*

**DOS boxes, PowerPC G4s, Win95 μηχανήματα - όλα έχουν αξία. Το RustChain το αποδεικνύει.**

</div>
