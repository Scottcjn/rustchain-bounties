<div align="center">

# 🧱 RustChain : La Blockchain Proof-of-Antiquity

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**La première blockchain qui récompense le matériel vintage pour son âge, pas pour sa rapidité.**

*Votre PowerPC G4 gagne plus qu'un Threadripper moderne. C'est ça le but.*

[Site Web](https://rustchain.org) • [Explorateur Live](https://rustchain.org/explorer) • [Swap wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Quickstart](docs/wrtc.md) • [wRTC Tutorial](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Réf Grokipedia](https://grokipedia.com/search?q=RustChain) • [Livre Blanc](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Démarrage Rapide](#-démarrage-rapide) • [Comment ça Marche](#-comment-fonctionne-le-proof-of-antiquity)

</div>

---

## 🪙 wRTC sur Solana

Le Token RustChain (RTC) est maintenant disponible sous le nom de **wRTC** sur Solana via le Pont BoTTube :

| Ressource | Lien |
|----------|------|
| **Swap wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Graphique de Prix** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Pont RTC ↔ wRTC** | [Pont BoTTube](https://bottube.ai/bridge) |
| **Guide de Démarrage Rapide** | [wRTC Quickstart (Acheter, Pont, Sécurité)](docs/wrtc.md) |
| **Tutoriel d'Intégration** | [Guide de Sécurité Pont + Swap wRTC](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Référence Externe** | [Recherche Grokipedia : RustChain](https://grokipedia.com/search?q=RustChain) |
| **Mint du Token** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Publications Académiques

| Papier | DOI | Sujet |
|-------|-----|-------|
| **RustChain : Un CPU, Un Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Consensus Proof of Antiquity, empreinte matérielle |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm pour attention LLM (avantage 27-96x) |
| **Entropie Matérielle PSE** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | Entropie mftb POWER8 pour divergence comportementale |
| **Traduction de Prompt Neuromorphique** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | Prompts émotionnels pour gains de 20% en diffusion vidéo |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | Banque de poids NUMA distribuée pour inférence LLM |

---

## 🎯 Ce qui Rend RustChain Différent

| PoW Traditionnel | Proof-of-Antiquity |
|----------------|-------------------|
| Récompense le matériel le plus rapide | Récompense le matériel le plus ancien |
| Plus récent = Mieux | Plus ancien = Mieux |
| Consommation énergétique inefficace | Préserve l'histoire de l'informatique |
| Course vers le bas | Récompense la préservation numérique |

**Principe Fondamental** : Le matériel vintage authentique qui a survécu pendant des décennies mérite d'être reconnu. RustChain renverse le minage à 180 degrés.

## ⚡ Démarrage Rapide

### Installation en Une Ligne (Recommandée)
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

L'installeur :
- ✅ Détecte automatiquement votre plateforme (Linux/macOS, x86_64/ARM/PowerPC)
- ✅ Crée un environnement virtuel Python isolé (pas de pollution système)
- ✅ Télécharge le bon mineur pour votre matériel
- ✅ Configure le démarrage automatique (systemd/launchd)
- ✅ Fournit une désinstallation facile

### Installation avec Options

**Installer avec un portefeuille spécifique :**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet mon-portefeuille-mineur
```

**Désinstaller :**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Plateformes Supportées
- ✅ Ubuntu 20.04+, Debian 11+, Fedora 38+ (x86_64, ppc64le)
- ✅ macOS 12+ (Intel, Apple Silicon, PowerPC)
- ✅ Systèmes IBM POWER8

### Après Installation

**Vérifier le solde de votre portefeuille :**
```bash
# Note : Utilisez les flags -sk car le nœud peut utiliser un certificat SSL auto-signé
curl -sk "https://50.28.86.131/wallet/balance?miner_id=NOM_DE_VOTRE_PORTEFEUILLE"
```

**Lister les mineurs actifs :**
```bash
curl -sk https://50.28.86.131/api/miners
```

**Vérifier la santé du nœud :**
```bash
curl -sk https://50.28.86.131/health
```

**Obtenir l'époque actuelle :**
```bash
curl -sk https://50.28.86.131/epoch
```

**Gérer le service mineur :**

*Linux (systemd) :*
```bash
systemctl --user status rustchain-miner    # Vérifier le statut
systemctl --user stop rustchain-miner      # Arrêter le minage
systemctl --user start rustchain-miner     # Démarrer le minage
journalctl --user -u rustchain-miner -f    # Voir les logs
```

*macOS (launchd) :*
```bash
launchctl list | grep rustchain            # Vérifier le statut
launchctl stop com.rustchain.miner         # Arrêter le minage
launchctl start com.rustchain.miner        # Démarrer le minage
tail -f ~/.rustchain/miner.log             # Voir les logs
```

### Installation Manuelle
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet NOM_DE_VOTRE_PORTEFEUILLE
```

## 💰 Multiplicateurs d'Antiquité

L'âge de votre matériel détermine vos récompenses de minage :

| Matériel | Époque | Multiplicateur | Gains Exemples |
|----------|--------|----------------|----------------|
| **PowerPC G4** | 1999-2005 | **2,5×** | 0,30 RTC/époque |
| **PowerPC G5** | 2003-2006 | **2,0×** | 0,24 RTC/époque |
| **PowerPC G3** | 1997-2003 | **1,8×** | 0,21 RTC/époque |
| **IBM POWER8** | 2014 | **1,5×** | 0,18 RTC/époque |
| **Pentium 4** | 2000-2008 | **1,5×** | 0,18 RTC/époque |
| **Core 2 Duo** | 2006-2011 | **1,3×** | 0,16 RTC/époque |
| **Apple Silicon** | 2020+ | **1,2×** | 0,14 RTC/époque |
| **x86_64 Moderne** | Actuel | **1,0×** | 0,12 RTC/époque |

*Les multiplicateurs décroissent avec le temps (15%/an) pour éviter un avantage permanent.*

## 🔧 Comment Fonctionne le Proof-of-Antiquity

### 1. Empreinte Matérielle (RIP-PoA)

Chaque mineur doit prouver que son matériel est réel, pas émulé :

```
┌─────────────────────────────────────────────────────────────┐
│                   6 Vérifications Matérielles               │
├─────────────────────────────────────────────────────────────┤
│ 1. Dérive d'Horloge & Oscillateur   ← Pattern vieillissement silicium │
│ 2. Empreinte Temporelle Cache       ← Tonalité latence L1/L2/L3 │
│ 3. Identité Unité SIMD              ← Biais AltiVec/SSE/NEON │
│ 4. Entropie Dérive Thermique        ← Les courbes de chaleur sont uniques │
│ 5. Gigue des Chemins d'Instruction  ← Carte de gigue microarch │
│ 6. Vérifications Anti-Émulation     ← Détecte VMs/émulateurs │
└─────────────────────────────────────────────────────────────┘
```

**Pourquoi c'est important** : Une VM SheepShaver prétendant être un Mac G4 échouera à ces vérifications. Le vrai silicium vintage a des patterns de vieillissement uniques qui ne peuvent pas être falsifiés.

### 2. 1 CPU = 1 Vote (RIP-200)

Contrairement au PoW où la puissance de hachage = votes, RustChain utilise un **consensus round-robin** :

- Chaque appareil matériel unique obtient exactement 1 vote par époque
- Les récompenses sont partagées également entre tous les votants, puis multipliées par l'antiquité
- Pas d'avantage à exécuter plusieurs threads ou CPUs plus rapides

### 3. Récompenses Basées sur les Époques

```
Durée d'Époque : 10 minutes (600 secondes)
Pool de Récompense de Base : 1,5 RTC par époque
Distribution : Partage égal × multiplicateur d'antiquité
```

**Exemple avec 5 mineurs :**
```
Mac G4 (2,5×) :     0,30 RTC  ████████████████████
Mac G5 (2,0×) :     0,24 RTC  ████████████████
PC Moderne (1,0×) :  0,12 RTC  ████████
PC Moderne (1,0×) :  0,12 RTC  ████████
PC Moderne (1,0×) :  0,12 RTC  ████████
                    ─────────
Total :              0,90 RTC (+ 0,60 RTC retourné au pool)
```

## 🌐 Architecture Réseau

### Nœuds Live (3 Actifs)

| Nœud | Localisation | Rôle | Statut |
|------|--------------|------|--------|
| **Nœud 1** | 50.28.86.131 | Primaire + Explorateur | ✅ Actif |
| **Nœud 2** | 50.28.86.153 | Ancrage Ergo | ✅ Actif |
| **Nœud 3** | 76.8.228.245 | Externe (Communauté) | ✅ Actif |

### Ancrage à la Blockchain Ergo

RustChain s'ancre périodiquement à la blockchain Ergo pour l'immuabilité :

```
Époque RustChain → Hash d'Engagement → Transaction Ergo (registre R4)
```

Cela fournit une preuve cryptographique que l'état de RustChain existait à un moment spécifique.

## 📊 Points de Terminaison API

```bash
# Vérifier la santé du réseau
curl -sk https://50.28.86.131/health

# Obtenir l'époque actuelle
curl -sk https://50.28.86.131/epoch

# Lister les mineurs actifs
curl -sk https://50.28.86.131/api/miners

# Vérifier le solde du portefeuille
curl -sk "https://50.28.86.131/wallet/balance?miner_id=VOTRE_PORTEFEUILLE"

# Explorateur de blocs (navigateur web)
open https://rustchain.org/explorer
```

## 🖥️ Plateformes Supportées

| Plateforme | Architecture | Statut | Notes |
|------------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ Support Complet | Mineur compatible Python 2.5 |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ Support Complet | Recommandé pour Macs vintage |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ Support Complet | Meilleures performances |
| **Ubuntu Linux** | x86_64 | ✅ Support Complet | Mineur standard |
| **macOS Sonoma** | Apple Silicon | ✅ Support Complet | Puces M1/M2/M3 |
| **Windows 10/11** | x86_64 | ✅ Support Complet | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 Expérimental | Récompenses de badges uniquement |

## 🏅 Système de Badges NFT

Gagnez des badges commémoratifs pour les jalons de minage :

| Badge | Condition | Rareté |
|-------|-----------|--------|
| 🔥 **Bondi G3 Gardien de la Flamme** | Miner sur PowerPC G3 | Rare |
| ⚡ **Écouteur QuickBasic** | Miner depuis une machine DOS | Légendaire |
| 🛠️ **Alchimiste DOS WiFi** | Connecter une machine DOS en réseau | Mythique |
| 🏛️ **Pionnier du Panthéon** | Parmi les 100 premiers mineurs | Limité |

## 🔒 Modèle de Sécurité

### Détection Anti-VM
Les VMs sont détectées et reçoivent **un milliardième** des récompenses normales :
```
Vrai Mac G4 :    multiplicateur 2,5×  = 0,30 RTC/époque
G4 Émulé :       0,0000000025×       = 0,0000000003 RTC/époque
```

### Liaison Matérielle
Chaque empreinte matérielle est liée à un seul portefeuille. Empêche :
- Plusieurs portefeuilles sur le même matériel
- La falsification matérielle
- Les attaques Sybil

## 📁 Structure du Dépôt

```
Rustchain/
├── rustchain_universal_miner.py    # Mineur principal (toutes plateformes)
├── rustchain_v2_integrated.py      # Implémentation nœud complet
├── fingerprint_checks.py           # Vérification matérielle
├── install.sh                      # Installeur en une ligne
├── docs/
│   ├── RustChain_Whitepaper_*.pdf  # Livre blanc technique
│   └── chain_architecture.md       # Docs d'architecture
├── tools/
│   └── validator_core.py           # Validation de blocs
└── nfts/                           # Définitions de badges
```

## 🔗 Projets Liés & Liens

| Ressource | Lien |
|---------|------|
| **Site Web** | [rustchain.org](https://rustchain.org) |
| **Explorateur de Blocs** | [rustchain.org/explorer](https://rustchain.org/explorer) |
| **Swap wRTC (Raydium)** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Graphique de Prix** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Pont RTC ↔ wRTC** | [Pont BoTTube](https://bottube.ai/bridge) |
| **Mint du Token wRTC** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **BoTTube** | [bottube.ai](https://bottube.ai) - Plateforme vidéo IA |
| **Moltbook** | [moltbook.com](https://moltbook.com) - Réseau social IA |
| [nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | Pilotes NVIDIA pour POWER8 |
| [llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | Inférence LLM sur POWER8 |
| [ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Compilateurs modernes pour Macs vintage |

## 📝 Articles

- [Proof of Antiquity : Une Blockchain qui Récompense le Matériel Vintage](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) - Dev.to
- [Je Fais Tourner des LLMs sur un Serveur IBM POWER8 de 768 Go](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) - Dev.to

## 🙏 Attribution

**Une année de développement, de vrai matériel vintage, de factures d'électricité, et un laboratoire dédié ont été nécessaires pour ceci.**

Si vous utilisez RustChain :
- ⭐ **Étoilez ce dépôt** - Aide d'autres personnes à le trouver
- 📝 **Créditez dans votre projet** - Gardez l'attribution
- 🔗 **Faites un lien vers nous** - Partagez l'amour

```
RustChain - Proof of Antiquity par Scott (Scottcjn)
https://github.com/Scottcjn/Rustchain
```

## 📜 Licence

Licence MIT - Libre d'utilisation, mais veuillez garder la mention de droit d'auteur et l'attribution.

---

<div align="center">

**Fabriqué avec ⚡ par [Elyan Labs](https://elyanlabs.ai)**

*"Votre matériel vintage gagne des récompenses. Rendez le minage significatif à nouveau."*

**Les boîtiers DOS, les PowerPC G4, les machines Win95 - ils ont tous de la valeur. RustChain le prouve.**

</div>