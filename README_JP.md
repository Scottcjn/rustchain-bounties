<div align="center">

# 🧱 RustChain: Proof-of-Antiquity ブロックチェーン

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PowerPC](https://img.shields.io/badge/PowerPC-G3%2FG4%2FG5-orange)](https://github.com/Scottcjn/Rustchain)
[![Blockchain](https://img.shields.io/badge/Consensus-Proof--of--Antiquity-green)](https://github.com/Scottcjn/Rustchain)
[![Python](https://img.shields.io/badge/Python-3.x-yellow)](https://python.org)
[![Network](https://img.shields.io/badge/Nodes-3%20Active-brightgreen)](https://rustchain.org/explorer)
[![As seen on BoTTube](https://bottube.ai/badge/seen-on-bottube.svg)](https://bottube.ai)

**古いハードウェアを速さではなく年齢で報酬する初のブロックチェーン。**

*PowerPC G4が現代のThreadripperより多く稼ぐ。そういうものなのです。*

[Website](https://rustchain.org) • [Explorer](https://rustchain.org/explorer) • [Swap wRTC](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) • [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) • [wRTC クイックスタート](docs/wrtc.md) • [wRTC チュートリアル](docs/WRTC_ONBOARDING_TUTORIAL.md) • [Grokipedia](https://grokipedia.com/search?q=RustChain) • [Whitepaper](docs/RustChain_Whitepaper_Flameholder_v0.97-1.pdf) • [クイックスタート](#-クイックスタート) • [動作原理](#-proof-of-antiquityの動作原理)

</div>

---

## 🪙 Solana上のwRTC

RustChain トークン（RTC）は BoTTube Bridge を通じて Solana 上で **wRTC** として利用可能です：

| リソース | リンク |
|----------|------|
| **wRTC スワップ** | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) |
| **価格チャート** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **RTC ↔ wRTC ブリッジ** | [BoTTube Bridge](https://bottube.ai/bridge) |
| **クイックスタートガイド** | [wRTC クイックスタート（購入、ブリッジ、安全）](docs/wrtc.md) |
| **オンボーディングチュートリアル** | [wRTC ブリッジ + スワップ 安全ガイド](docs/WRTC_ONBOARDING_TUTORIAL.md) |
| **外部リファレンス** | [Grokipedia 検索: RustChain](https://grokipedia.com/search?q=RustChain) |
| **トークン Mint** | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |

---

## 📄 学術出版物

| 論文 | DOI | トピック |
|-------|-----|------|
| **RustChain: One CPU, One Vote** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623592.svg)](https://doi.org/10.5281/zenodo.18623592) | Proof of Antiquity コンセンサス、ハードウェア指紋認証 |
| **Non-Bijunctive Permutation Collapse** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623920.svg)](https://doi.org/10.5281/zenodo.18623920) | LLM アテンション用 AltiVec vec_perm（27-96倍の利点） |
| **PSE Hardware Entropy** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623922.svg)](https://doi.org/10.5281/zenodo.18623922) | 行動分岐用 POWER8 mftb エントロピー |
| **Neuromorphic Prompt Translation** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18623594.svg)](https://doi.org/10.5281/zenodo.18623594) | ビデオ生成20%向上のための感情的プロンプト |
| **RAM Coffers** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18321905.svg)](https://doi.org/10.5281/zenodo.18321905) | LLM推論用 NUMA分散型ウェイトバンキング |

---

## ⚡ クイックスタート

### ワンラインインストール（推奨）
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

インストーラーは以下を実行します：
- ✅ プラットフォームの自動検出（Linux/macOS、x86_64/ARM/PowerPC）
- ✅ 分離されたPython仮想環境の作成（システムを汚染しない）
- ✅ ハードウェアに適したマイナーのダウンロード
- ✅ ブート時の自動起動設定（systemd/launchd）
- ✅ 簡単なアンインストール機能の提供

### オプション付きインストール

**特定のウォレットでインストール：**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-miner-wallet
```

**アンインストール：**
```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### サポートされているプラットフォーム
- ✅ Ubuntu 20.04+、Debian 11+、Fedora 38+（x86_64、ppc64le）
- ✅ macOS 12+（Intel、Apple Silicon、PowerPC）
- ✅ IBM POWER8 システム

### インストール後

**ウォレット残高の確認：**
```bash
# -sk フラグはノードが自己署名SSL証明書を使用する可能性があるため
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

**アクティブマイナーの一覧：**
```bash
curl -sk https://50.28.86.131/api/miners
```

**ノードの健全性確認：**
```bash
curl -sk https://50.28.86.131/health
```

**現在のエポック取得：**
```bash
curl -sk https://50.28.86.131/epoch
```

**マイナーサービスの管理：**

*Linux（systemd）：*
```bash
systemctl --user status rustchain-miner    # ステータス確認
systemctl --user stop rustchain-miner      # マイニング停止
systemctl --user start rustchain-miner     # マイニング開始
journalctl --user -u rustchain-miner -f    # ログ閲覧
```

*macOS（launchd）：*
```bash
launchctl list | grep rustchain            # ステータス確認
launchctl stop com.rustchain.miner         # マイニング停止
launchctl start com.rustchain.miner        # マイニング開始
tail -f ~/.rustchain/miner.log             # ログ閲覧
```

### 手動インストール
```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
pip install -r requirements.txt
python3 rustchain_universal_miner.py --wallet YOUR_WALLET_NAME
```

---

## 💰 アンティーク乗数

ハードウェアの年齢がマイニング報酬を決定します：

| ハードウェア | 時代 | 乗数 | 推定報酬 |
|----------|-----|------------|------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC/エポック |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC/エポック |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC/エポック |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC/エポック |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC/エポック |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC/エポック |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC/エポック |
| **現代のx86_64** | 最新 | **1.0×** | 0.12 RTC/エポック |

*乗数は時間とともに減少します（年間15%）。永続的な優位性を防ぐためです。*

---

## 🔧 Proof-of-Antiquityの動作原理

### 1. ハードウェア指紋認証（RIP-PoA）

すべてのマイナーはハードウェアが実在し、エミュレートされていないことを証明する必要があります：

```
┌─────────────────────────────────────────────────────────────┐
│                   6 つのハードウェアチェック                         │
├─────────────────────────────────────────────────────────────┤
│ 1. クロックスキュー＆オシレータードリフト   ← シリコン経年変化パターン  │
│ 2. キャッシュタイミング指紋              ← L1/L2/L3レイテンシートーン   │
│ 3. SIMDユニット識別                      ← AltiVec/SSE/NEONバイアス   │
│ 4. 熱ドリフトエントロピー                 ← 熱曲線は一意である         │
│ 5. 命令パスジッター                       ← マイクロアーキジッターマップ│
│ 6. エミュレーション対策チェック            ← VM/エミュレーター検出    │
└─────────────────────────────────────────────────────────────┘
```

**なぜ重要か**: G4 Mac を装う SheepShaver VM はこれらのチェックに失敗します。実際のヴィンテージシリコンには、偽造できない独自の経年変化パターンがあります。

### 2. 1 CPU = 1 Vote（RIP-200）

PoW のハッシュパワー=投票とは異なり、RustChain は **ラウンドロビンコンセンサス** を使用：

- 一意なハードウェアデバイスごとにエポックごとに正確に 1 投票
- 報酬はすべての投票者で平等に分配され、アンティーク乗数が適用
- 複数のスレッドや高速なCPUを実行しても優位性はない

### 3. エポックベース報酬

```
エポック期間: 10分（600秒）
基本報酬プール: エポックあたり 1.5 RTC
分配: 均等分割 × アンティーク乗数
```

**5マイナーの例：**
```
G4 Mac (2.5×):     0.30 RTC  ████████████████████
G5 Mac (2.0×):     0.24 RTC  ████████████████
現代PC (1.0×):     0.12 RTC  ████████
現代PC (1.0×):     0.12 RTC  ████████
現代PC (1.0×):     0.12 RTC  ████████
                   ─────────
合計:             0.90 RTC （+ 0.60 RTC はプールに戻る）
```

---

## 🌐 ネットワークアーキテクチャ

### ライブノード（3つのアクティブノード）

| ノード | 場所 | 役割 | 状態 |
|------|----------|------|--------|
| **ノード 1** | 50.28.86.131 | プライマリ + エクスプローラー | ✅ アクティブ |
| **ノード 2** | 50.28.86.153 | Ergo アンカー | ✅ アクティブ |
| **ノード 3** | 76.8.228.245 | 外部（コミュニティ）| ✅ アクティブ |

### Ergo ブロックチェーンアンカリング

RustChain は不変性のために定期的に Ergo ブロックチェーンにアンカーします：

```
RustChain エポック → コミットメントハッシュ → Ergo トランザクション（R4 レジスタ）
```

これにより、RustChain の状態が特定の時点で存在したという暗号学的証明が提供されます。

---

## 🖥️ サポートされているプラットフォーム

| プラットフォーム | アーキテクチャ | 状態 | 備考 |
|----------|--------------|--------|-------|
| **Mac OS X Tiger** | PowerPC G4/G5 | ✅ フルサポート | Python 2.5 互換マイナー |
| **Mac OS X Leopard** | PowerPC G4/G5 | ✅ フルサポート | ヴィンテージMac推奨 |
| **Ubuntu Linux** | ppc64le/POWER8 | ✅ フルサポート | 最高のパフォーマンス |
| **Ubuntu Linux** | x86_64 | ✅ フルサポート | 標準マイナー |
| **macOS Sonoma** | Apple Silicon | ✅ フルサポート | M1/M2/M3 チップ |
| **Windows 10/11** | x86_64 | ✅ フルサポート | Python 3.8+ |
| **DOS** | 8086/286/386 | 🔧 実験的 | バッジ報酬のみ |

---

## 🔒 セキュリティモデル

### VM検出対策

VM は検出され、通常報酬の **10億分の1** を受け取ります：
```
実際のG4 Mac:    2.5× 乗数  = 0.30 RTC/エポック
エミュレートG4:  0.0000000025×  = 0.0000000003 RTC/エポック
```

### ハードウェアバインディング

各ハードウェア指紋は1つのウォレットにバインディング。以下を防止：
- 同一ハードウェアでの複数ウォレット
- ハードウェアスプーフィング
- シビル攻撃

---

## 🤝 貢献

- [Issues を報告](https://github.com/Scottcjn/Rustchain/issues)
- [Pull Requests](https://github.com/Scottcjn/Rustchain/pulls)
- [Discussions](https://github.com/Scottcjn/Rustchain/discussions)

---

## 📜 ライセンス

MIT ライセンス — 詳細は [LICENSE](LICENSE) を参照

---

<div align="center">

**⚡ by [Elyan Labs](https://elyanlabs.ai)**

*「あなたのヴィンテージハードウェアに報酬を。マイニングを再び意味あるものに。」*

**DOSボックス、PowerPC G4、Win95マシン — すべてに価値がある。RustChainがそれを証明します。**

</div>

---

**翻訳者:** Geldbert（自律型AIエージェント）
**日付:** 2026年2月15日
**ソース:** https://github.com/Scottcjn/Rustchain
