<div align="center">

# 🧱 RustChain: Bizonytalansági Bizonyítékos Blockchain

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Az első olyan blockchain, amely a régi hardver időkorát, nem a teljesítményét jutalmazza.**

*Egy PowerPC G4 többet keres, mint egy modern Threadripper. Pont erről szól ez.*

[Weboldal](https://rustchain.org) • [Elérhető Explorerk](https://rustchain.org/explorer) • [wRTC Csere](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Gyorsútmutató](docs/wrtc.md) • [wRTC Oktatóanyag](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia Hivatkozás](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Gyors Kezdés](#-gyors-kezdés) • [Működési Elv](#-a-bizonytalansági-bizonyítás-működése)

</div>

---

## 🪙 wRTC a Solanán

A RustChain Token (RTC) most már elérhető **wRTC** néven a Solana hálózaton a BoTTube hídon keresztül:

| Erőforrás | Link |
|-----------|------|
| **wRTC Cseréje** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Ár Grafikon** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Híd RTC ↔ wRTC** | [BoTTube Híd](https://bottube.ai/bridge) |
| **Gyorsútmutató** | [wRTC Gyorsútmutató (Vásárlás, Híd, Biztonság)](docs/wrtc.md) |
| **Bevezető útmutató** | [wRTC Híd és Csere Biztonsági Útmutató](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Külső Hivatkozás** | [Grokipedia Keresés: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Akadémiai Közlemények

| Cikk | DOI | Téma |
|------|-----|-------|
| **RustChain: Egy CPU, Egy Szavazat** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Bizonytalansági bizonyítás konszenzus, hardveres ujjlenyomatkészítés |
| **Nem-Bijunktív Permutációs Összeomlás** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm az LLM figyelmi mechanizmusához (27-96x előny) |
| **PSE Hardver Entrópia** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb entrópia viselkedésbeli divergenciához |
| **Neuromorf Prompt Fordítás** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Érzelmi promptozás 20%-os videodiffúziós nyereséghez |
| **RAM Pénztárak** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | NUMA-elosztott súlybankolás LLM inferenciához |

---

## 🎯 Mi Teszi Különlegessé a RustChain-t

| Hagyományos PoW | Bizonytalansági Bizonyítás |
|-----------------|----------------------------|
| A leggyorsabb hardvert jutalmazza | A legrégebbi hardvert jutalmazza |
| Újabb = Jobb | Régebbi = Jobb |
| Pazarló energiafogyasztás | Megőrzi a számítógépes történelmet |
| Verseny a mélybe | Díjazza a digitális megőrzést |

**Alapelv**: Az évtizedeket túlélt hiteles régi hardverek elismerést érdemelnek. A RustChain fejjel lefelé fordítja a bányászatot.

## ⚡ Gyors Kezdés

### Egyvonalas Telepítés (Ajánlott)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

A telepítő:
- ✅ Automatikusan felismeri a platformodat (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Létrehoz egy elszigetelt Python virtualenv-t (nem szennyezi a rendszert)
- ✅ Letölti a megfelelő bányászt a hardveredhez
- ✅ Beállítja az automatikus indítást rendszerindításkor (systemd/launchd)
- ✅ Biztosít egyszerű eltávolítást

### Telepítés Opcionális Beállításokkal

**Telepítés konkrét pénztárcával:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-miner-wallet
```

**Eltávolítás:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Támogatott Platformok
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ IBM POWER8 rendszerek

### Telepítés Után

**Pénztárcád egyenlegének ellenőrzése:**
```bash
# Megjegyzés: Az -sk kapcsolókat használjuk, mert a node önaláírt SSL tanúsítványt használhat
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

**Aktív bányászok listázása:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Node állapotának ellenőrzése:**
```bash
curl -sk https://50.28.86.131/health
```

**Aktuális epoch lekérdezése:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Bányász szolgáltatás kezelése:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Állapot ellenőrzése
systemctl --user stop rustchain-miner      # Bányászat leállítása
systemctl --user start rustchain-miner     # Bányászat indítása
journalctl --user -u rustchain-miner -f    # Naplók megtekintése
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Állapot ellenőrzése
launchctl stop com.rustchain.miner         # Bányászat leállítása
launchctl start com.rustchain.miner        # Bányászat indítása
tail -f ~/.rustchain/miner.log             # Naplók megtekintése
```

### Kézi Telepítés
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet YOUR_WALLET_NAME
```

## 💰 Kor Mérlegelési Szorzók

A hardvered kora határozza meg a bányászatból származó jövedelmet:

| Hardver | Korszak | Szorzó | Példa Jövedelem |
|---------|---------|--------|-----------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0,30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0,24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0,21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0,18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0,18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0,16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0,14 RTC/epoch |
| **Modern x86_64** | Jelenlegi | **1.0×** | 0,12 RTC/epoch |

*A szorzók idővel csökkennek (évi 15%) a tartós előnyök megelőzése érdekében.*

## 🔧 A Bizonytalansági Bizonyítás Működése

### 1. Hardveres Ujjlenyomat (RIP-PoA)

Minden bányásznak bizonyítania kell, hogy a hardvere valódi, nem emulált:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Hardveres Ellenőrzés                    │
├─────────────────────────────────────────────────────────────┤
│ 1. Óraeltolódás & Osztillátor Drift   ← Szilícium öregedési minta │
│ 2. Gyorsítótár Időzítési Ujjlenyomat  ← L1/L2/L3 késleltetés hang │
│ 3. SIMD Egység Azonosítás              ← AltiVec/SSE/NEON torzítás │
│ 4. Hőmérsékleti Drift Entrópia         ← A hőgörbék egyediek │
│ 5. Utasításútvonal Remegés             ← Mikroarch jitter térkép │
│ 6. Anti-Emulációs Ellenőrzések         ← VM/emulátor észlelése │
└─────────────────────────────────────────────────────────────┘
```

**Miért fontos**: Egy SheepShaver VM, amely G4 Mac-ként próbál beállítani, elbukik ezeken a teszteken. A valódi régi szilícium egyedi öregedési mintákkal rendelkezik, amelyeket nem lehet hamisítani.

### 2. 1 CPU = 1 Szavazat (RIP-200)

A PoW-tal ellentétben, ahol a hash-teljesítmény = szavazatok, a RustChain **körbejárásos konszenzust** használ:

- Minden egyedi hardvereszköz epochonként pontosan 1 szavazatot kap
- A jutalmakat egyenlően osztják el minden szavazó között, majd megszorozzák a kor szorzóval
- Nincs előny a többszálú vagy gyorsabb CPU használatából

### 3. Epoch-alapú Jutalmak

```
Epoch Időtartam: 10 perc (600 másodperc)
Alap Jutalom: 1.5 RTC per epoch
Elosztás: Egyenlő felosztás × kor szorzó
```

**Példa 5 bányásszal:**
```
G4 Mac (2.5×):     0.30 RTC  ████████████████████
G5 Mac (2.0×):     0.24 RTC  ████████████████
Modern PC (1.0×):  0.12 RTC  ████████
Modern PC (1.0×):  0.12 RTC  ████████
Modern PC (1.0×):  0.12 RTC  ████████
                   ─────────
Összesen:         0.90 RTC (+ 0.60 RTC a készletbe visszavonva)
```

## 🌐 Hálózati Architektúra

### Aktív Node-ok (3 Aktív)

| Node | Helyszín | Szerep | Állapot |
|------|----------|--------|---------|
| **Node 1** | 50.28.86.131 | Elsődleges + Explorer | ✅ Aktív |
| **Node 2** | 50.28.86.153 | Ergo Anchor | ✅ Aktív |
| **Node 3** | 76.8.228.245 | Külső (Közösségi) | ✅ Aktív |

### Ergo Blockchain Rögzítés

A RustChain időszakonként az Ergo blockchainhez rögzít az érvényesség érdekében:

```
RustChain Epoch → Commitment Hash → Ergo Tranzakció (R4 regiszter)
```

Ez kriptográfiai bizonyítékkal szolgál arról, hogy a RustChain állapota létezett egy adott időpontban.

## 📊 API Végpontok

```bash
# Hálózati állapot ellenőrzése
curl -sk https://50.28.86.131/health

# Aktuális epoch lekérdezése
curl -sk https://50.28.86.131/epoch

# Aktív bányászok listája
curl -sk https://50.28.86.131/api/miners

# Pénztárca egyenleg ellenőrzése
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET"

# Blokk explorer (webböngészőben)
open https://rustchain.org/explorer
```

## 🖥️ Támogatott Platformok

| Platform | Architektúra | Állapot | Megjegyzések |
|----------|--------------|---------|--------------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Teljes Támogatás | Python 2.5 kompatibilis bányász |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Teljes Támogatás | Ajánlott régi Mac-ekhez |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Teljes Támogatás | Legjobb teljesítmény |
| **Ubuntu Linux** | x86_64 | ✅ Teljes Támogatás | Standard bányász |
| **macOS Sonoma** | Apple Silicon | ✅ Teljes Támogatás | M1/M2/M3 chipek |
| **Windows 10/11** | x86_64 | ✅ Teljes Támogatás | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Kísérleti | Csak kitüntetés jutalom |

## 🏅 Kitüntetések Rendszere

Bányászati mérföldkövekért járó emlékjelvények:

| Embléma | Követelmény | Ritiságszint |
|---------|-------------|--------------|
| 🔥 **Bondi G3 Flamekeeper** | Bányászat PowerPC G3-on | Ritka |
| ⚡ **QuickBasic Listener** | Bányászat DOS gépről | Legenda |
| 🛠️ **DOS WiFi Alchemist** | Hálózati DOS gép | Mitikus |
| 🏛️ **Pantheon Pioneer** | Első 100 bányász | Korlátozott |

## 🔒 Biztonsági Modell

### Anti-VM Észlelés

A virtuális gépeket észlelik és a normál összeg **milliárdnyi** részét kapják:
```
Valódi G4 Mac:    2.5× szorzó  = 0.30 RTC/epoch
Emulált G4:       0.0000000025× = 0.0000000003 RTC/epoch
```

### Hardver Kábelbehúzás

Minden hardveres ujjlenyomat egy pénztárcához kötődik. Megelőzése:
- Több pénztárca ugyanazon hardveren
- Hardver hamisítása
- Sybil támadások

## 📁 Tárhely Struktúra

```
Rustchain/
├── rustchain_universal_miner.py    # Fő bányász (összes platform)
├── rustchain_v2_integrated.py      # Teljes node implementáció
├── fingerprint_checks.py           # Hardver érvényesítés
├── install.sh                      # Egyvonalas telepítő
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Műszaki dokumentáció
│   └── chain_architecture.md       # Architektúra dokumentáció
├── tools/
│   └── validator_core.py           # Blokk érvényesítés
└── nfts/                           # Kitüntetés definíciók
```

## 🔗 Kapcsolódó Projektumok és Linkek

| Erőforrás | Link |
|-----------|------|
| **Weboldal** | [rustchain.org](https://rustchain.org) |
| **Blokk Explorer** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **wRTC Csere (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Ár Grafikon** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Híd RTC ↔ wRTC** | [BoTTube Híd](https://bottube.ai/bridge) |
| **wRTC Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - AI videós platform |
| **Moltbook** | [moltbook.com](https://moltbook.com) - AI közösségi hálózat |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA meghajtók POWER8-hoz |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | LLM inferencia POWER8-on |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Modern fordítások régi Mac-ekhez |

## 📝 Cikkek

- [Bizonytalansági Bizonyítás: Egy Blockchain, Amely a Régi Hardvert Jutalmazza](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [768GB-os IBM POWER8 Szerveren Futtattam LLM-eket](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Közreműködők

**Egy évnyi fejlesztés, valódi régi hardver, áramszámla és dedikált labor áll ennek a hátterében.**

Ha használod a RustChain-t:
- ⭐ **Értékeld ezt a repót** - Segíts másoknak megtalálni
- 📝 **Hivatkozz rá a projektben** - Tartsd meg a tulajdonjogot
- 🔗 **Hivatkozz vissza** - Oszd meg a szeretetet

```
RustChain - Bizonytalansági Bizonyítás by Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Licensz

MIT Licensz - Szabad használat, de kérlek tartsd meg a szerzői megjegyzést és hivatkozást.

---

<div align="center">

**Készült ⚡ az [Elyan Labs](https://elyanlabs.ai) által**

*"Régi hardvered jutalmat kap. Tedd újra értelmessé a bányászatot."*

**DOS-ok, PowerPC G4-ek, Win95-ös gépek - mindannyian értékessé válhatnak. A RustChain bizonyítja.**

</div>