<div align="center">

# 🧱 RustChain: Dowieku Dowodu

[![Licencja](https://img.shields.io/badge/Licencja-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Konsensus-Dowód--Dowieku-zielony)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-%C5%BC%C3%B3%C5%82ty)](https://python.org)
[![Sieć](https://img.shields.io/badge/Węz%C5%82y-3%20Aktywne-jasnozielony)](https://rustchain.org/explorer)
[![Jak widziano na BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**Pierwszy blockchain, który nagradza wiekowy sprzęt za to, że jest stary, a nie szybki.**

*Twój PowerPC G4 zarabia więcej niż nowoczesny Threadripper. O to właśnie chodzi.*

[Strona internetowa](https://rustchain.org) • [Eksplorator na żywo](https://rustchain.org/explorer) • [Zamiana wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [Szybki start wRTC](docs/wrtc.md) • [Samouczek wRTC](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia](https://grokipedia.com/search?q=RustChain) • [Biała księga](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Szybki start](#%EF%B8%8F-szybki-start) • [Jak to działa](#-jak-dzia%C5%82a-dowód-dowieku)
</div>

---

## 🪙 wRTC na Solanie

Token RustChain (wRTC) jest dostępny na Solanie poprzez most BoTTube.

| Zasób | Link |
|----------|------|
| **Zamiana wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Wykres cen** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Most RTC ↔ wRTC** | [Most BoTTube](https://bottube.ai/bridge) |
| **Przewodnik szybkiego startu** | [Szybki start wRTC](docs/wrtc.md) |
| **Samouczek wprowadzający** | [Bezpieczny przewodnik po moście wRTC](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Referencje zewnętrzne** | [Grokipedia: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Mint tokena** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Publikacje naukowe

| Publikacja | DOI | Temat |
|-------|-----|-------|
| **RustChain: Jeden CPU, jeden głos** | [DOI: 10.5281/zenodo.18623592](https://doi.org/10.5281/zenodo.18623592) | Konsensus Dowód Dowieku, identyfikacja sprzętu |
| **Niebijunkcyjne załamanie permutacji** | [DOI: 10.5281/zenodo.18623920](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm dla uwagi LLM (27-96x przewaga) |
| **Sprzętowe źródło entropii PSE** | [DOI: 10.5281/zenodo.18623922](https://doi.org/10.5281/zenodo.18623922) | Entropia POWER8 mftb dla dywergencji behawioralnej |
| **Translacja promptów neuromorficznych** | [DOI: 10.5281/zenodo.18623594](https://doi.org/10.5281/zenodo.18623594) | Emocjonalne prompty dla 20% wzrostu dyfuzji wideo |
| **Skarbnice RAM** | [DOI: 10.5281/zenodo.18321905](https://doi.org/10.5281/zenodo.18321905) | Bankowość wag rozproszona w NUMA dla wnioskowania LLM |

---

## 🎯 Czym RustChain się różni

| Tradycyjny PoW | Dowód Dowieku |
|----------------|----------------|
| Nagradza najszybszy sprzęt | Nagradza najstarszy sprzęt |
| Nowocześniejszy = Lepiej | Starszy = Lepiej |
| Marnowanie energii | Zachowuje historię komputerów |
| Wyścig na dno | Nagradza cyfrową ochronę zabytków |

**Zasada podstawowa**: Autentyczny, wiekowy sprzęt, który przetrwał dekady, zasługuje na uznanie. RustChain odwraca wydobycie do góry nogami.

## ⚡ Szybki start

### Jednolinijkowa instalacja (zalecana)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Instalator:
- ✅ Automatycznie wykrywa platformę (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Tworzy izolowane środowisko Python (brak ingerencji w system)
- ✅ Pobiera odpowiedni kopacz dla twojego sprzętu
- ✅ Konfiguruje autostart przy uruchamianiu (systemd/launchd)
- ✅ Zapewnia łatwą dezinstalację

### Instalacja z opcjami

**Zainstaluj z konkretnym portfelem:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet nazwa-mojego-portfela
```

**Dezinstalacja:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Obsługiwane platformy
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ Systemy IBM POWER8

### Po instalacji

**Sprawdź stan portfela:**
```bash
# Uwaga: Używamy flag -sk, bo węzeł może używać samodzielnie podpisanego certyfikatu SSL
curl -sk "https://50.28.86.131/wallet/balance?miner_id=NAZWA_TWOJEGO_PORTFELA"
```

**Lista aktywnych kopaczy:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Sprawdź stan węzła:**
```bash
curl -sk https://50.28.86.131/health
```

**Bieżąca epoka:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Zarządzanie usługą kopacza:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Status
systemctl --user stop rustchain-miner      # Zatrzymaj
systemctl --user start rustchain-miner     # Start
journalctl --user -u rustchain-miner -f    # Logi
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Status
launchctl stop com.rustchain.miner         # Zatrzymaj
launchctl start com.rustchain.miner        # Start
tail -f ~/.rustchain/miner.log             # Logi
```

### Instalacja ręczna
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet NAZWA_TWOJEGO_PORTFELA
```

## 💰 Mnożniki Dowieku

Wiek sprzętu determinuje nagrody wydobywcze:

| Sprzęt | Era | Mnożnik | Przykładowy zysk |
|----------|-----|------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoka |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoka |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoka |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoka |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoka |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoka |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoka |
| **Nowoczesny x86_64** | Obecnie | **1.0×** | 0.12 RTC/epoka |

*Mnożniki maleją z czasem (15% rocznie), aby zapobiec trwałej przewadze.*

## 🔧 Jak działa Dowód Dowieku

### 1. Identyfikacja sprzętu (RIP-PoA)

Każdy kopacz musi udowodnić, że jego sprzęt jest prawdziwy, a nie emulowany:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Testów Sprzętowych                      │
├─────────────────────────────────────────────────────────────┤
│ 1. Odchylenie zegara i dryft oscylatora  ← Wzór starzenia   │
│ 2. Odcisk czasowy pamięci podręcznej     ← Ton L1/L2/L3    │
│ 3. Tożsamość jednostki SIMD              ← Stronniczość    │
│ 4. Entropia dryfu termicznego            ← Krzywe ciepła  │
│ 5. Drganie ścieżki instrukcji            ← Mapa szumu     │
│ 6. Testy anty-emulacyjne                 ← Wykrywanie VM  │
└─────────────────────────────────────────────────────────────┘
```

**Dlaczego to ważne**: Emulator SheepShaver udający Maca G4 nie przejdzie tych testów. Prawdziwy krzem ma unikalne wzorce starzenia, których nie da się podrobić.

### 2. 1 CPU = 1 głos (RIP-200)

W przeciwieństwie do PoW, gdzie moc wydobywcza = głosy, RustChain używa **konsensu round-robin**:
- Każde unikalne urządzenie sprzętowe ma dokładnie 1 głos na epokę
- Nagrody dzielone są równo między wszystkich głosujących, a następnie mnożone przez wiek
- Brak przewagi z uruchamiania wielowątkowości lub szybszych CPU

### 3. Nagrody epokowe

```
Czas trwania epoki: 10 minut (600 sekund)
Bazowy pulut nagród: 1.5 RTC na epokę
Dystrybucja: Równy podział × mnożnik wiekowy
```

**Przykład z 5 kopaczami:**
```
Mac G4 (2.5×):     0.30 RTC  ████████████████████
Mac G5 (2.0×):     0.24 RTC  ████████████████
Nowoczesny PC (1.0×):  0.12 RTC  ████████
Nowoczesny PC (1.0×):  0.12 RTC  ████████
Nowoczesny PC (1.0×):  0.12 RTC  ████████
                   ─────────
Razem:             0.90 RTC (+ 0.60 RTC wraca do puli)
```

## 🌐 Architektura sieci

### Aktywne węzły (3)

| Węzeł | Lokalizacja | Rola | Status |
|------|----------|------|--------|
| **Węzeł 1** | 50.28.86.131 | Główny + Eksplorator | ✅ Aktywny |
| **Węzeł 2** | 50.28.86.153 | Kotwica Ergo | ✅ Aktywny |
| **Węzeł 3** | 76.8.228.245 | Zewnętrzny (Społeczność) | ✅ Aktywny |

### Kotwiczenie w łańcuchu Ergo

RustChain okresowo kotwiczy się w łańcuchu Ergo, zapewniając niezmienność:
```
Epoka RustChain → Skrót zobowiązania → Transakcja Ergo (rejestr R4)
```

Daje to kryptograficzny dowód, że stan RustChain istniał w określonym czasie.

## 📊 Punkty końcowe API

```bash
# Stan sieci
curl -sk https://50.28.86.131/health

# Bieżąca epoka
curl -sk https://50.28.86.131/epoch

# Lista aktywnych kopaczy
curl -sk https://50.28.86.131/api/miners

# Stan portfela
curl -sk "https://50.28.86.131/wallet/balance?miner_id=TWÓJ_PORTFEL"

# Eksplorator (przeglądarka)
open https://rustchain.org/explorer
```

## 🖥️ Obsługiwane platformy

| Platforma | Architektura | Status | Uwagi |
|----------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Pełne wsparcie | Kopacz kompatybilny z Python 2.5 |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Pełne wsparcie | Polecane dla starych Maców |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Pełne wsparcie | Najlepsza wydajność |
| **Ubuntu Linux** | x86_64 | ✅ Pełne wsparcie | Standardowy kopacz |
| **macOS Sonoma** | Apple Silicon | ✅ Pełne wsparcie | Chipy M1/M2/M3 |
| **Windows 10/11** | x86_64 | ✅ Pełne wsparcie | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Eksperymentalnie | Tylko odznaki |

## 🏅 System odznak NFT

Zdobądź pamiątkowe odznaki za kamienie milowe w wydobywaniu:

| Odznaka | Wymaganie | Rzadkość |
|-------|-------------|--------|
| 🔥 **Strażnik Płomienia G3** | Wydobycie na PowerPC G3 | Rzadka |
| ⚡ **Słuchacz QuickBasic** | Wydobycie z DOSa | Legendarna |
| 🛠️ **Alchemik WiFi DOS** | Podłączony DOS do sieci | Mityczna |
| 🏛️ **Pionier Panteonu** | Pierwszych 100 kopaczy | Limitowana |

## 🔒 Model bezpieczeństwa

### Wykrywanie maszyn wirtualnych
Wykrywane VM otrzymują **miliardową** część normalnych nagród:
```
Prawdziwy Mac G4:    2.5× = 0.30 RTC/epoka
Emulowany G4:        0.0000000025× = 0.0000000003 RTC/epoka
```

### Powiązanie sprzętowe
Każdy odcisk sprzętu jest powiązany z jednym portfelem. Zapobiega:
- Wielu portfeli na tym samym sprzęcie
- Fałszowaniu sprzętu
- Atakom Sybilli

## 📁 Struktura repozytorium

```
Rustchain/
├── rustchain_universal_miner.py    # Główny kopacz (wszystkie systemy)
├── rustchain_v2_integrated.py      # Pełna implementacja węzła
├── fingerprint_checks.py           # Weryfikacja sprzętu
├── install.sh                      # Instalator jednolinijkowy
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Biała księga
│   └── chain_architecture.md       # Dokumentacja architektury
├── tools/
│   └── validator_core.py           # Walidacja bloków
└── nfts/                           # Definicje odznak
```

## 🔗 Powiązane projekty i linki

| Zasób | Link |
|---------|------|
| **Strona WWW** | [rustchain.org](https://rustchain.org) |
| **Eksplorator łańcucha** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Zamień wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Wykres cen** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Most RTC ↔ wRTC** | [Most BoTTube](https://bottube.ai/bridge) |
| **Mint wRTC** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - Platforma wideo AI |
| **Moltbook** | [moltbook.com](https://moltbook.com) - Sieć społecznościowa AI |
| [Łatki NVIDIA dla POWER8](https://github.com/Scottcjn/nvidia-power8-patches) | Sterowniki NVIDIA dla POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | Wnioskowanie LLM na POWER8 |
| [Kompilatory PPC](https://github.com/Scottcjn/ppc-compilers) | Nowoczesne kompilatory dla starych Maców |

## 📝 Artykuły

- [Dowód Dowieku: Blockchain który nagradza zabytkowy sprzęt](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [Uruchamiam LLM na 768GB serwerze IBM POWER8](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Atrybucja

**Rok rozwoju, prawdziwy zabytkowy sprzęt, rachunki za prąd i dedykowane laboratorium poszły w ten projekt.**

Jeśli używasz RustChain:
- ⭐ **Dodaj gwiazdkę temu repozytorium** - Pomaga innym je znaleźć
- 📝 **Wymień źródło w swoim projekcie** - Zachowaj atrybucję
- 🔗 **Odnośnik z powrotem** - Podziel się miłością

```
RustChain - Dowód Dowieku autorstwa Scotta (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Licencja

MIT License - Wolne do użytku, prosimy o zachowanie informacji o prawach autorskich i atrybucji.

---

<div align="center">

**Wykonane z ⚡ przez [Elyan Labs](https://elyanlabs.ai)**

*"Twój zabytkowy sprzęt zarabia nagrody. Uczyń wydobycie znowu znaczącym."*

**Komputery DOS, PowerPC G4, maszyny z Win95 - wszystkie mają wartość. RustChain to udowadnia.**

</div>