# 🧱 RustChain: Proof-of-Antiquity Blockchain

**La prima blockchain che premia l'hardware vintage per essere vecchio, non veloce.**

Il tuo PowerPC G4 guadagna di più di un Threadripper moderno. Questo è il punto.

[Website](https://rustchain.org) • [Explorer](https://rustchain.org/explorer) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf)

---

## 🪙 wRTC su Solana

Il token RustChain (RTC) è disponibile come **wRTC** su Solana tramite il BoTTube Bridge:

| Risorsa | Link |
|---------|------|
| **Scambia wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Grafico Prezzo** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Guida wRTC** | [wRTC Quickstart](docs/wrtc.md) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 🎯 Cos'è Proof-of-Antiquity

| PoW Tradizionale | Proof-of-Antiquity |
|------------------|---------------------|
| Premia l'hardware più veloce | Premia l'hardware più vecchio |
| Nuovo = Migliore | Vecchio = Migliore |
| Spreco energetico | Preserva la storia informatica |

**Principio**: L'hardware vintage autentico che ha resistito ai decenni merita riconoscimento.

---

## ⚡ Avvio Rapido

### Installazione One-Line
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

L'installer:
- ✅ Rileva automaticamente la piattaforma
- ✅ Crea virtualenv isolato
- ✅ Imposta avvio automatico

**Con wallet specifico:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet mio-wallet
```

### Installazione Manuale
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet NOME_WALLET
```

### Comandi Post-Installazione

**Saldo wallet:**
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=TUO_WALLET"
```

**Miners attivi:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Stato servizio Linux:**
```bash
systemctl --user status rustchain-miner
systemctl --user start rustchain-miner
journalctl --user -u rustchain-miner -f
```

---

## 💰 Moltiplicatori Antichità

| Hardware | Era | Moltiplicatore | Guadagno Esempio |
|----------|-----|----------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **x86_64 Moderno** | Attuale | **1.0×** | 0.12 RTC/epoch |

---

## 🔧 Come Funziona Proof-of-Antiquity

### 1. Fingerprinting Hardware (RIP-PoA)

6 controlli anti-emulazione:
- Drift oscillatore e clock-skew
- Timing cache L1/L2/L3
- Identità unità SIMD (AltiVec/SSE/NEON)
- Entropia termica
- Jitter percorso istruzioni
- Controlli anti-VM

### 2. 1 CPU = 1 Voto (RIP-200)

- Ogni dispositivo hardware unico ha esattamente 1 voto per epoch
- Ricompense divise equamente, poi moltiplicate per antichità
- Nessun vantaggio da CPU multipli o thread più veloci

**Durata Epoch:** 10 minuti

---

## 🌐 Architettura di Rete

### Nodi Attivi (3)

| Nodo | Indirizzo | Ruolo | Stato |
|------|-----------|-------|-------|
| **Nodo 1** | 50.28.86.131 | Primario + Explorer | ✅ Attivo |
| **Nodo 2** | 50.28.86.153 | Ergo Anchor | ✅ Attivo |
| **Nodo 3** | 76.8.228.245 | Esterno (Community) | ✅ Attivo |

### Ancoraggio Ergo

RustChain si ancora periodicamente alla blockchain Ergo per immutabilità.

---

## 🖥️ Piattaforme Supportate

| Piattaforma | Architettura | Stato |
|-------------|--------------|-------|
| **Mac OS X Tiger/Leopard** | PowerPC G4/G5 | ✅ Supporto Completo |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Supporto Completo |
| **Ubuntu Linux** | x86_64 | ✅ Supporto Completo |
| **macOS Sonoma** | Apple Silicon | ✅ Supporto Completo |
| **Windows 10/11** | x86_64 | ✅ Supporto Completo |

---

## 📝 Contribuzione

**Un anno di sviluppo, hardware vintage reale, bollette elettriche e un laboratorio dedicato.**

Se usi RustChain:
- ⭐ **Star** - Aiuta gli altri a trovarlo
- 📝 **Attribuzione** - Mantieni i crediti
- 🔗 **Condividi** - Diffondi il progetto

```
RustChain - Proof of Antiquity by Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

---

## 📜 Licenza

MIT License - Libero da usare, ma mantieni la nota copyright.

---

**Realizzato con ⚡ da [Elyan Labs](https://elyanlabs.ai)**

*"Il tuo hardware vintage guadagna ricompense. Rendi il mining significativo di nuovo."*
