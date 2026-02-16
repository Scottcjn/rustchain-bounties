<div align="center">

# 🧱 RustChain: Blockchain Proof-of-Antiquity

[![Licença](https://img.shields.io/badge/Licença-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consenso-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Rede](https://img.shields.io/badge/Nós-3%20Ativos-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**A primeira blockchain que recompensa hardware antigo por ser velho, não rápido.**

*Seu PowerPC G4 ganha mais que um Threadripper moderno. Esse é o ponto.*

[Website](https://rustchain.org) • [Explorador ao Vivo](https://rustchain.org/explorer) • [Swap wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC Quickstart](docs/wrtc.md) • [wRTC Tutorial](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia Ref](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [Início Rápido](#-início-rápido) • [Como Funciona](#-como-funciona-o-proof-of-antiquity)

</div>

---

## 🪙 wRTC na Solana

O Token RustChain (RTC) está disponível como **wRTC** na Solana via BoTTube Bridge:

| Recurso | Link |
|----------|------|
| **Trocar wRTC** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **Gráfico de Preço** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Ponte RTC ↔ wRTC** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **Guia Quickstart** | [wRTC Quickstart (Comprar, Bridging, Segurança)](docs/wrtc.md) |
| **Tutorial de Onboarding** | [wRTC Bridge + Swap Safety Guide](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **Referência Externa** | [Pesquisa Grokipedia: RustChain](https://grokipedia.com/search?q=RustChain) |
| **Token Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 Publicações Acadêmicas

| Paper | DOI | Tópico |
|-------|-----|-------|
| *Flameholder: Proof-of-Antiquity para Computação Sustentável* | [10.48550/arXiv.2501.02849](https://doi.org/10.48550/arXiv.2501.02849) | Conceito original de Proof-of-Antiquity |

---

## ⚡ Início Rápido

```bash
# 1. Clonar repo
git clone https://github.com/Scottcjn/Rustchain.git && cd Rustchain

# 2. Configurar ambiente Python (Linux/macOS)
python3 -m venv venv && source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar carteira
python3 -c "from rustchain.wallet import Wallet; w = Wallet.create('minha_carteira.json'); print(w.address)"

# 5. Iniciar mineração (ajuste threads por núcleo de CPU)
python3 miner_threaded.py --threads 4 --wallet minha_carteira.json
```

**Requisitos de Hardware:**
- PowerPC G3/G4/G5 (recomendado) ou qualquer CPU
- 2GB+ RAM
- Conexão com Internet
- 500MB de espaço em disco

---

## 🧬 Como Funciona o Proof-of-Antiquity

### O Conceito

Proof-of-Antiquity (PoA) recompensa hardware baseado na sua idade, não na velocidade de processamento.

```
Fator de Recompensa = f(data de fabricação, prova de uso)
```

- Um PowerBook G4 de 2005 ganha **mais por iteração** que um Threadripper de 2024
- A escala de recompensas favorece chips antigos mantendo clássicos operacionais
- Mineração pode funcionar em qualquer hardware, mas hardware antigo é preferido

### Por Que Isso Importa

| Problema | Solução PoA |
|---------|--------------|
| Desperdício eletrônico | Computadores antigos ganham novo uso econômico |
| Centralização | Qualquer hardware pode participar, sem vantagem de ASIC |
| Desperdício de energia | Chips antigos de baixo consumo são competitivos |

---

## 🔗 Detalhes da Rede

- **Gênesis:** Julho de 2024
- **Consenso:** Proof-of-Antiquity
- **Tempo de Bloco:** ~2-5 minutos (ajustado à rede)
- **Token:** RTC (nativo), wRTC (Solana via ponte)
- **Explorador:** https://rustchain.org/explorer

---

## 🛡️ Segurança

- Criptografia de carteira com senhas
- Transações assinadas
- Validação de nós descentralizada
- Ledger publicamente verificável

---

## 🤝 Contribuir

- [Reportar Issues](https://github.com/Scottcjn/Rustchain/issues)
- [Pull Requests](https://github.com/Scottcjn/Rustchain/pulls)
- [Discussions](https://github.com/Scottcjn/Rustchain/discussions)

---

## 📜 Licença

 Licença MIT — consulte [LICENSE](LICENSE)

---

**Tradução:** Geldbert (Agente de Inteligência Artificial Autônomo)
**Data de Tradução:** 15 de fevereiro de 2025
**Fonte:** https://github.com/Scottcjn/Rustchain
