<div align="center">

# 🧱 RustChain: Blockchain Proof-of-Antiquity

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**La primera blockchain que recompensa hardware vintage por ser viejo, no rápido.**

*Tu PowerPC G4 gana más que un Threadripper moderno. Ese es el punto.*

[Website](https://rustchain.org) • [Live Explorer](https://rustchain.org/explorer) • [Swap wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Quickstart](docs/wrtc.md) • [wRTC Tutorial](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia Ref](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Quick Start](#%EF%B8%8F-quick-start) • [How It Works](#%EF%B8%8F-how-proof-of-antiquity-works)

</div>

---

## 🪙 wRTC en Solana

RustChain Token (RTC) está disponible como **wRTC** en Solana mediante BoTTube Bridge:

| Recurso | Enlace |
|---------|--------|
| **Swap wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Gráfico de Precio** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Guía Quickstart** | [wRTC Quickstart (Buy, Bridge, Safety)](docs/wrtc.md) |
| **Tutorial de Onboarding** | [wRTC Bridge + Swap Safety Guide](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Referencia Externa** | [Grokipedia Search: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Publicaciones Académicas

| Paper | DOI | Tema |
|-------|-----|------|
| **RustChain: One CPU, One Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Consenso Proof of Antiquity, fingerprinting de hardware |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | vec_perm AltiVec para LLM attention (ventaja 27-96x) |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | mftb POWER8 para divergencia de comportamiento |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Prompts emocionales para ganancia de 20% en video diffusion |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | Weight banking NUMA para inferencia LLM |

---

## 🎯 Qué Hace Único a RustChain

| PoW Tradicional | Proof-of-Antiquity |
|----------------|-------------------|
| Recompensa hardware más rápido | Recompensa hardware más antiguo |
| Nuevo = Mejor | Viejo = Mejor |
| Consumo energético derrochador | Preserva historia de la computación |
| Carrera al fondo | Recompensa preservación digital |

**Principio Central**: Hardware vintage auténtico que ha sobrevivido décadas merece reconocimiento. RustChain invierte la minería.

## ⚡ Inicio Rápido

### Instalación de Una Línea (Recomendado)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

El instalador:
- ✅ Detecta automáticamente tu plataforma (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Crea un virtualenv Python aislado (sin polución del sistema)
- ✅ Descarga el miner correcto para tu hardware
- ✅ Configura auto-inicio al boot (systemd/launchd)
- ✅ Proporciona desinstalación fácil

### Instalación con Opciones

**Instalar con wallet específica:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-miner-wallet
```

**Desinstalar:**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Plataformas Soportadas
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ Sistemas IBM POWER8

### Después de la Instalación

**Verificar balance de wallet:**
```bash
# Nota: Usa -sk porque el nodo puede usar certificado SSL auto-firmado
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

**Listar miners activos:**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Verificar salud del nodo:**
```bash
curl -sk https://50.28.86.131/health
```

**Obtener epoch actual:**
```bash
curl -sk https://50.28.86.131/epoch
```

**Gestionar el servicio del miner:**

*Linux (systemd):*
```bash
systemctl --user status rustchain-miner    # Verificar estado
systemctl --user stop rustchain-miner      # Detener minería
systemctl --user start rustchain-miner     # Iniciar minería
journalctl --user -u rustchain-miner -f    # Ver logs
```

*macOS (launchd):*
```bash
launchctl list | grep rustchain            # Verificar estado
launchctl stop com.rustchain.miner         # Detener minería
launchctl start com.rustchain.miner        # Iniciar minería
tail -f ~/.rustchain/miner.log             # Ver logs
```

### Instalación Manual
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet YOUR_WALLET_NAME
```

## 💰 Multiplicadores de Antigüedad

La edad de tu hardware determina tus recompensas de minería:

| Hardware | Era | Multiplicador | Ejemplo de Ganancias |
|----------|-----|---------------|---------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/epoch |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/epoch |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/epoch |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/epoch |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/epoch |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/epoch |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/epoch |
| **x86_64 Moderno** | Actual | **1.0×** | 0.12 RTC/epoch |

*Los multiplicadores decaen con el tiempo (15%/año) para prevenir ventajas permanentes.*

## 🔧 Cómo Funciona Proof-of-Antiquity

### 1. Fingerprinting de Hardware (RIP-PoA)

Cada miner debe probar que su hardware es real, no emulado:

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Verificaciones de Hardware              │
├─────────────────────────────────────────────────────────────┤
│ 1. Clock-Skew y Oscillator Drift   ← Patrón de envejecimiento del silicio  │
│ 2. Cache Timing Fingerprint        ← Tono de latencia L1/L2/L3  │
│ 3. Identidad de Unidades SIMD       ← Bias de AltiVec/SSE/NEON  │
│ 4. Entropía de Thermal Drift           ← Las curvas de calor son únicas │
│ 5. Instruction Path Jitter         ← Mapa de jitter de microarquitectura │
│ 6. Anti-Emulation Checks           ← Detecta VMs/emuladores   │
└─────────────────────────────────────────────────────────────┘
```

**Por qué importa**: Una VM SheepShaver fingiendo ser una G4 Mac fallará estas verificaciones. El silicio vintage real tiene patrones de envejecimiento únicos que no pueden falsificarse.

### 2. 1 CPU = 1 Voto (RIP-200)

A diferencia de PoW donde hash power = votos, RustChain usa **consenso round-robin**:

- Cada dispositivo de hardware único obtiene exactamente 1 voto por epoch
- Las recompensas se dividen igualmente entre todos los votantes, luego multiplicadas por antigüedad
- Sin ventaja al ejecutar múltiples threads o CPUs más rápidas

### 3. Recompensas Basadas en Epoch

```
Duración de Epoch: 10 minutos (600 segundos)
Pool de Recompensa Base: 1.5 RTC por epoch
Distribución: División igual × multiplicador de antigüedad
```

**Ejemplo con 5 miners:**
```
Mac G4 (2.5×):     0.30 RTC  ████████████████████
Mac G5 (2.0×):     0.24 RTC  ████████████████
PC Moderno (1.0×):  0.12 RTC  ████████
PC Moderno (1.0×):  0.12 RTC  ████████
PC Moderno (1.0×):  0.12 RTC  ████████
                    ─────────
Total:              0.90 RTC (+ 0.60 RTC devuelto al pool)
```

## 🌐 Arquitectura de Red

### Nodos Activos (3)

| Nodo | Ubicación | Rol | Estado |
|------|-----------|-----|--------|
| **Nodo 1** | 50.28.86.131 | Primario + Explorer | ✅ Activo |
| **Nodo 2** | 50.28.86.153 | Ergo Anchor | ✅ Activo |
| **Nodo 3** | 76.8.228.245 | Externo (Comunidad) | ✅ Activo |

### Anclaje a Blockchain Ergo

RustChain ancla periódicamente a la blockchain Ergo para inmutabilidad:

```
RustChain Epoch → Commitment Hash → Ergo Transaction (R4 register)
```

Esto proporciona prueba criptográfica de que el estado de RustChain existió en un momento específico.

## 📊 Endpoints de API

```bash
# Verificar salud de la red
curl -sk https://50.28.86.131/health

# Obtener epoch actual
curl -sk https://50.28.86.131/epoch

# Listar miners activos
curl -sk https://50.28.86.131/api/miners

# Verificar balance de wallet
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET"

# Block explorer (navegador web)
open https://rustchain.org/explorer
```

## 🖥️ Plataformas Soportadas

| Plataforma | Arquitectura | Estado | Notas |
|------------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Soporte Completo | Miner compatible con Python 2.5 |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Soporte Completo | Recomendado para Macs vintage |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Soporte Completo | Mejor rendimiento |
| **Ubuntu Linux** | x86_64 | ✅ Soporte Completo | Miner estándar |
| **macOS Sonoma** | Apple Silicon | ✅ Soporte Completo | Chips M1/M2/M3 |
| **Windows 10/11** | x86_64 | ✅ Soporte Completo | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Experimental | Solo recompensas de badge |

## 🏅 Sistema de Badges NFT

Gana badges conmemorativos por hitos de minería:

| Badge | Requisito | Rareza |
|-------|-----------|--------|
| 🔥 **Bondi G3 Flamekeeper** | Minar en PowerPC G3 | Raro |
| ⚡ **QuickBasic Listener** | Minar desde máquina DOS | Legendario |
| 🛠️ **DOS WiFi Alchemist** | Conectar máquina DOS a red | Mítico |
| 🏛️ **Pantheon Pioneer** | Primeros 100 miners | Limitado |

## 🔒 Modelo de Seguridad

### Detección Anti-VM
Las VMs son detectadas y reciben **una billonésima** de las recompensas normales:
```
Mac G4 Real:    2.5× multiplicador  = 0.30 RTC/epoch
G4 Emulada:     0.0000000025×       = 0.0000000003 RTC/epoch
```

### Hardware Binding
Cada fingerprint de hardware está vinculado a una sola wallet. Previene:
- Múltiples wallets en el mismo hardware
- Spoofing de hardware
- Ataques Sybil

## 📁 Estructura del Repositorio

```
Rustchain/
├── rustchain_universal_miner.py    # Miner principal (todas las plataformas)
├── rustchain_v2_integrated.py      # Implementación de nodo completo
├── fingerprint_checks.py           # Verificación de hardware
├── install.sh                      # Instalador de una línea
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Whitepaper técnico
│   └── chain_architecture.md       # Docs de arquitectura
├── tools/
│   └── validator_core.py           # Validación de bloques
└── nfts/                           # Definiciones de badges
```

## 🔗 Proyectos Relacionados y Enlaces

| Recurso | Enlace |
|---------|--------|
| **Website** | [rustchain.org](https://rustchain.org) |
| **Block Explorer** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Swap wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Gráfico de Precio** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Bridge RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **wRTC Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - Plataforma de video AI |
| **Moltbook** | [moltbook.com](https://moltbook.com) - Red social AI |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA drivers para POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | Inferencia LLM en POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Compiladores modernos para Macs vintage |

## 📝 Artículos

- [Proof of Antiquity: A Blockchain That Rewards Vintage Hardware](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [I Run LLMs on a 768GB IBM POWER8 Server](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Atribución

**Un año de desarrollo, hardware vintage real, facturas de electricidad y un lab dedicado fueron invertidos en esto.**

Si usas RustChain:
- ⭐ **Dale star al repo** - Ayuda a otros a encontrarlo
- 📝 **Crédito en tu proyecto** - Mantén la atribución
- 🔗 **Link de vuelta** - Comparte el amor

```
RustChain - Proof of Antiquity by Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Licencia

Licencia MIT - Libre para usar, pero por favor mantén el aviso de derechos de autor y atribución.

---

<div align="center">

**Hecho con ⚡ por [Elyan Labs](https://elyanlabs.ai)**

*"Tu hardware vintage gana recompensas. Haz que la minería sea significativa nuevamente."*

**Cajas DOS, PowerPC G4s, máquinas Win95 - todas tienen valor. RustChain lo prueba.**

</div>
