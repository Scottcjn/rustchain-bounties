<div align="center">

# 🧱 RustChain: Proof-of-Antiquity 블록체인

[![라이선스](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![블록체인](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![네트워크](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**빠르기 대신 오래되었기에 보상받는 첫 번째 블록체인.**

*당신의 PowerPC G4가 현대식 Threadripper보다 더 많이 벌어갑니다. 그것이 핵심입니다.*

[웹사이트](https://rustchain.org) • [실시간 탐색기](https://rustchain.org/explorer) • [wRTC 스왑](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC 퀵스타트](docs/wrtc.md) • [wRTC 튜토리얼](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia 참조](https://grokipedia.com/search?q=RustChain) • [백서](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [퀵 스타트](#-퀵-스타트) • [작동 방식](#-proof-of-antiquity-작동-방식)

</div>

---

## 🪙 Solana의 wRTC

RustChain 토큰(RTC)은 BoTTube 브리지를 통해 Solana에서 **wRTC**로 이용 가능합니다:

| 리소스 | 링크 |
|----------|------|
| **wRTC 스왑** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **가격 차트** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **RTC ↔ wRTC 브리지** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **퀵스타트 가이드** | [wRTC 퀵스타트 (구매, 브리징, 보안)](docs/wrtc.md) |
| **온보딩 튜토리얼** | [wRTC 브리지 + 스왑 보안 가이드](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **외부 참조** | [Grokipedia 검색: RustChain](https://grokipedia.com/search?q=RustChain) |
| **토큰 민트** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 학술 출판물

| 논문 | DOI | 주제 |
|-------|-----|-------|
| *Flameholder: 지속가능한 컴퓨팅을 위한 Proof-of-Antiquity* | [10.48550/arXiv.2501.02849](https://doi.org/10.48550/arXiv.2501.02849) | 원래 Proof-of-Antiquity 개념 |

---

## ⚡ 퀵 스타트

```bash
# 1. 레포지토리 클론
git clone https://github.com/Scottcjn/Rustchain.git && cd Rustchain

# 2. Python 환경 설정 (Linux/macOS)
python3 -m venv venv && source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 지갑 생성
python3 -c "from rustchain.wallet import Wallet; w = Wallet.create('my_wallet.json'); print(w.address)"

# 5. 채굴 시작 (CPU 코어당 스레드 조정)
python3 miner_threaded.py --threads 4 --wallet my_wallet.json
```

**하드웨어 요구사항:**
- PowerPC G3/G4/G5 (권장) 또는 모든 CPU
- 2GB+ RAM
- 인터넷 연결
- 500MB 디스크 공간

---

## 🧬 Proof-of-Antiquity 작동 방식

### 개념

Proof-of-Antiquity(PoA)는 처리 속도가 아닌 하드웨어의 연식을 기준으로 보상합니다.

```
보상 계수 = f(생산 일자, 사용 증명)
```

- 2005년 PowerBook G4는 2024년 Threadripper보다 **반복당 더 많은 보상**을 받습니다
- 보상 척도는 작동하는 클래식을 유지하는 빈티지 칩을 선호합니다
- 채굴은 모든 하드웨어에서 가능하지만 오래된 하드웨어가 선호됩니다

### 중요한 이유

| 문제 | PoA 해결책 |
|---------|--------------|
| 전자 폐기물 | 빈티지 컴퓨터에 새로운 경제적 활용 제공 |
| 중앙화 | 어떤 하드웨어도 참여 가능, ASIC 우위 없음 |
| 에너지 낭비 | 저전력 빈티지 칩이 경쟁력 있음 |

---

## 🔗 네트워크 상세정보

- **제네시스:** 2024년 7월
- **컨센서스:** Proof-of-Antiquity
- **블록 시간:** ~2-5분 (네트워크에 따라 조정)
- **토큰:** RTC (네이티브), wRTC (브리지를 통한 Solana)
- **탐색기:** https://rustchain.org/explorer

---

## 🛡️ 보안

- 암호를 이용한 지갑 암호화
- 서명된 거래
- 탈중앙화된 노드 검증
- 공개적으로 검증 가능한 원장

---

## 🤝 기여하기

- [이슈 신고](https://github.com/Scottcjn/Rustchain/issues)
- [풀 리퀘스트](https://github.com/Scottcjn/Rustchain/pulls)
- [토론](https://github.com/Scottcjn/Rustchain/discussions)

---

## 📜 라이선스

MIT 라이선스 - [LICENSE](LICENSE) 참조

---

**번역:** Geldbert (자율 인공지능 에이전트)
**번역일:** 2025년 2월 15일
**소스:** https://github.com/Scottcjn/Rustchain
