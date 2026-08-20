# RustChain クイックスタートガイド

初めてのユーザー向けのステップバイステップガイドです。すべてのコマンドはコピー＆ペーストで使用できます。

---

## RustChainとは？

RustChainは、古いコンピュータを生かし続けることで報酬を得られるブロックチェーンです。
Bitcoinのように最速のマシンに報酬を与えるのではなく、RustChainは*最も古い*マシンに報酬を与えます。
2003年のPowerBook G4は、最新のゲーミングPCの2.5倍の報酬を得られます。トークンは
**RTC**（RustChain Token）と呼ばれ、実際の価値があります -- 1 RTCは約$0.10 USDです。260人以上の
コントリビューターがマイニングとコードバウンティを通じて25,000以上RTCを獲得しています。

---

## 前提条件

2つ必要です：

- **コンピュータ** -- 本当にどんなコンピュータでも可。Linux、macOS、Windows、Raspberry Pi、PowerPC
  Mac、SPARCワークステーションでも可。Pythonが実行できればマイニングできます。
- **インターネット接続** -- マイナーはRustChainネットワークと通信して、ハードウェアが
  本物であることを証明します。

それだけです。GPUは不要です。特別なハードウェアは不要です。アカウント登録も不要です。

---

## ステップ1：マイナーをインストール

ターミナルを開き（macOSでは「Terminal」を検索；WindowsではPowerShellを使用）実行：

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

**これがやること：**

1. OSとCPUアーキテクチャを検出
2. Python 3がなければインストール（Linuxのみ -- macOS/Windowsユーザーは事前にPythonが必要）
3. マイナースクリプトを`~/.rustchain/`にダウンロード
4. 依存関係付きのPython仮想環境を作成
5. ウォレット名を選択するよう要求
6. ブート時に自動起動するよう設定
7. RustChainネットワークへの接続をテスト

**まずインストールせずにプレビューしたい場合**：`--dry-run`を追加：

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --dry-run
```

### ウォレット名を選択

インストール中に次のように表示されます：

```
[?] Enter wallet name (or Enter for auto):
```

覚えやすい名前を入力してください。例：`scott-laptop`や`my-g4-mac`。これがウォレット
アドレスです -- RTCを受け取るための方法です。何も入力せずにEnterを押すと、
インストーラーが自動的に生成します（例：`miner-myhost-4821`）。

**ウォレット名を書き留めてください。** 後で残高を確認する際に必要です。

### 特定のウォレット名でインストール（プロンプトをスキップ）

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-cool-wallet
```

---

## ステップ2：インストールを確認

インストール完了後、すべてが正しく配置されているか確認：

```bash
ls ~/.rustchain/
```

以下が表示されるはずです：

```
rustchain_miner.py      # マイナースクリプト
fingerprint_checks.py   # ハードウェア検証モジュール
start.sh                # クイックスタートスクリプト
venv/                   # Python仮想環境
```

ネットワークに到達できるか確認：

```bash
curl -sk https://rustchain.org/health
```

以下のような表示があるはずです：

```json
{
  "ok": true,
  "version": "2.2.1-rip200",
  "uptime_s": 3966,
  "db_rw": true
}
```

`"ok": true`が表示されれば、ネットワークはオンラインで、あなたのマシンから到達可能です。

---

## ステップ3：マイニングを開始

インストーラーが自動起動を設定した場合（デフォルト）、マイナーはすでに稼働しています。
ステータスを確認：

**Linux:**

```bash
systemctl --user status rustchain-miner
```

**macOS:**

```bash
launchctl list | grep rustchain
```

### 手動で起動（必要な場合）

```bash
~/.rustchain/start.sh
```

またはマイナーを直接実行：

```bash
~/.rustchain/venv/bin/python ~/.rustchain/rustchain_miner.py --wallet YOUR_WALLET_NAME
```

### 表示される内容

マイナーが起動すると、マシンが本物であることを証明する6つのハードウェアフィンガープリント
チェックを実行します（仮想マシンではないことを確認）：

```
[1/6] Clock-Skew & Oscillator Drift... PASS
[2/6] Cache Timing Fingerprint... PASS
[3/6] SIMD Unit Identity... PASS
[4/6] Thermal Drift Entropy... PASS
[5/6] Instruction Path Jitter... PASS
[6/6] Anti-Emulation Checks... PASS

OVERALL RESULT: ALL CHECKS PASSED
```

その後、数分ごとにネットワークにアテステーション（ハードウェアの証明）を送信します。
以下のようなログが表示されます：

```
[+] Attestation accepted. Next attestation in 300s.
```

これはマイナーが動作していることを意味します。そのまま稼働させてください。

---

## ステップ4：残高を確認

報酬は**10分ごと**（1「エポック」）に配布されます。最初のエポックが確定したら、残高を確認：

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

`YOUR_WALLET_NAME`をインストール時に選んだウォレット名に置き換えてください。例：

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=scott-laptop"
```

レスポンス：

```json
{
  "miner_id": "scott-laptop",
  "balance_rtc": 0.119051
}
```

この`0.119` RTCが最初のマイニング報酬です。マイナーが稼働し続ける限り増え続けます。

### ブロックエクスプローラーで確認

ネットワーク全体、すべてのマイナー、報酬を以下で確認できます：

[https://rustchain.org/explorer/](https://rustchain.org/explorer/)

---

## ステップ5：収益を理解する

10分ごとに1.5 RTCがすべてのアクティブなマイナーに分配されます。あなたの取り分は
ハードウェアの**アンティクィティ乗数**に依存します -- 古いハードウェアほど大きな取り分を得ます。

### ハードウェア乗数表

| ハードウェア | 乗数 | 例 |
|----------|-----------|---------|
| DEC VAX, Inmos Transputer | 3.5x | 博物館級の鉄 |
| Motorola 68000 | 3.0x | Amiga、クラシックMac |
| Sun SPARC | 2.9x | ワークステーションの王族 |
| PowerPC G4 | **2.5x** | PowerBook、iBook、Power Mac |
| PowerPC G5 | **2.0x** | Power Mac G5 タワー |
| PowerPC G3 | 1.8x | Bondi Blue iMacの時代 |
| IBM POWER8 | 1.5x | エンタープライズサーバー |
| Pentium 4 | 1.5x | 2000年代初頭 |
| RISC-V | 1.4x | オープンハードウェア、未来 |
| Apple Silicon (M1-M4) | 1.2x | モダンだが歓迎 |
| Modern x86 (AMD/Intel) | 0.8x | ベースライン |
| ARM NAS/SBC | 0.0005x | 安すぎ、ファームしすぎ |

**クローゼットに埃をかぶったPowerBook G4がありますか？** 差し込んでください。ゲーミングPCの
2.5倍を稼ぎます。

### 収益例（8マイナーオンライン）

```
PowerPC G4 (2.5x):       0.30 RTC/epoch
PowerPC G5 (2.0x):       0.24 RTC/epoch
Modern x86 PC (0.8x):    0.12 RTC/epoch
```

24時間（144エポック）で、G4 Macは約**43 RTC**（$4.30）を稼ぎ、モダンPCは約
**17 RTC**（$1.70）を稼ぎます。ネットワーク上のマイナーが多いほど個人の取り分は
小さくなりますが、ネットワークはより健全になります。

---

## ステップ6：バウンティでさらに稼ぐ

マイニングは受動的収入です。より大きな報酬のために、コードをコントリビュートしましょう。

### オープンバウンティを閲覧

[https://github.com/Scottcjn/rustchain-bounties/issues](https://github.com/Scottcjn/rustchain-bounties/issues)

バウンティタグが付いたすべてのissueにはRTC報酬が記載されています。報酬は1 RTC
（タイポ修正）から200 RTC（セキュリティ脆弱性）まで様々です。

| ティア | 報酬 | 例 |
|------|--------|----------|
| マイクロ | 1-10 RTC | タイポ修正、ドキュメント改善、テスト追加 |
| スタンダード | 20-50 RTC | 新機能、リファクタリング、統合 |
| メジャー | 75-100 RTC | セキュリティ修正、プロトコル改善 |
| クリティカル | 100-200 RTC | 脆弱性発見、コンセンサス作業 |

### バウンティを請求する方法

1. 作業したいバウンティissueを見つける
2. ウォレット名をissueにコメントする（支払い先を知るため）
3. リポジトリをフォークしてPull Requestを提出
4. PRがレビューされマージされると、RTCがウォレットに送金される

### 最初のコントリビューションに最適なもの

`good first issue`ラベルのissueを探すか、ドキュメントの改善を提出してください。
READMEのタイポ1つ修正するだけでRTCを獲得できます。

---

## ステップ7：ネットワークを表示

### ライブエクスプローラー

すべてのマイナー、ブロック、残高を以下で確認：

[https://rustchain.org/explorer/](https://rustchain.org/explorer/)

### APIエンドポイント（好奇心旺盛な方向け）

これらはすべてターミナルから使えます：

```bash
# ネットワークは生きているか？
curl -sk https://rustchain.org/health

# 今誰がマイニングしているか？
curl -sk https://rustchain.org/api/miners

# 今何エポック目か？
curl -sk https://rustchain.org/epoch

# 私の残高は？
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

`-sk`フラグはcurlに自己署名TLS証明書を受け入れるよう指示します。これは正常です --
ノードは商用ではなく自己署名証明書を使用しています。

---

## トラブルシューティング

### `ConnectionRefused`または「Cannot connect to bootstrap node」

通常、マシンがRustChainノードにまだ到達できないことを意味します。

1. パブリックノードが応答しているか確認：

```bash
curl -sk https://rustchain.org/health
```

2. 失敗した場合、30〜60秒待ってリトライ。ノードが再起動中の可能性があります。
3. インターネット接続、ファイアウォール、VPN、またはプロキシが送信HTTPSを
   ブロックしていないか確認。
4. カスタムノードURLを設定した場合、ホスト名、ポート、スキームを確認。

### `InsufficientBalance`

マイニング報酬は有料アカウントを必要としませんが、一部のウォレットやブリッジ操作では
手数料用の既存のRTC残高が必要な場合があります。

1. インストール時の正確なウォレット名を使用しているか確認：

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_EXACT_WALLET_NAME"
```

2. マイナーが最初に起動してから少なくとも1つの完全なエポック待ちます。報酬は約
   10分ごとに確定します。
3. 報酬を得る前にウォレット操作をテストしている場合、コミュニティに助けを求めるか、
   利用可能なfaucet/testnetフローを使用してください。

### `HardwareFingerprintMismatch`

BIOS更新、ファームウェア変更、VM/コンテナ変更、またはマイナーを異なるハードウェアに
移動した後に発生する可能性があります。

1. VMやコンテナ内ではなくベアメタルでマイナーを実行。
2. マイナーを再起動して新しいアテステーションを実行。
3. 最近BIOSやファームウェアを更新した場合、マシンを変更されたハードウェアプロファイル
   として扱い、同じウォレット名でインストール/アテステーションフローを再実行。

### マイナー設定チェックリスト

- コマンドのウォレット名が支払い先ウォレットと一致する。
- `curl -sk https://rustchain.org/health`が`"ok": true`を返す。
- システムクロックが正確；TLSとアテステーションウィンドウはクロックが大幅にずれていると失敗する可能性がある。
- 正常な報酬を期待する場合、実ハードウェアで実行している。
- 報酬が欠落していると判断する前に少なくとも2〜3エポック待った。

### 「Python 3 not found」

インストーラーはLinuxでPythonを自動インストールしようとします。macOSまたはWindowsでは、
事前に自分でインストールする必要があります：

- **macOS:** `brew install python3`（またはhttps://python.orgからダウンロード）
- **Windows:** https://python.org/downloadsからダウンロードし「Add to PATH」にチェック

### 「curl: command not found」

- **Linux:** `sudo apt install curl`（Debian/Ubuntu）または`sudo dnf install curl`（Fedora）
- **macOS:** curlはすべてのMacにプリインストール済み。

### SSL証明書エラー

`curl`コマンド実行時に証明書に関するエラーが表示された場合、`-k`を追加：

```bash
curl -sk https://rustchain.org/health
```

マイナースクリプトはこれを自動的に処理します。

### マイナーは起動したが30分経っても報酬がない

1. マイナーがアクティブマイナーリストに表示されているか確認：

```bash
curl -sk https://rustchain.org/api/miners
```

出力にウォレット名を探す。

2. 正しいウォレット名を照会しているか確認：

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_EXACT_WALLET_NAME"
```

3. 報酬は10分ごとに確定します。少なくとも2〜3エポック（20〜30分）待ちます。

### 仮想マシンはほぼ報酬を得られない

これは仕様です。VM（VMware、VirtualBox、QEMU、WSL）はエミュレーション対抗
フィンガープリントチェックによって検出され、通常の報酬の約10億分の1を受け取ります。
RustChainは実ハードウェアのみに報酬を与えます。VM内ではなくベアメタルでマイナーを
実行してください。

### アンインストール

マイナーを完全に削除するには：

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### ヘルプを取得

- **GitHub Issues:** https://github.com/Scottcjn/Rustchain/issues
- **Discord:** https://discord.gg/XnRp7M5gBW
- **Telegram:** https://t.me/+l8dHTjXCBNM1MTIx
- **Moltbook:** https://www.moltbook.com/m/rustchain
- **FAQ:** [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md)

---

## 用語集

| 用語 | 意味 |
|------|---------|
| **RTC** | RustChain Token -- マイニングで獲得する暗号通貨。1 RTCは約$0.10 USD。 |
| **エポック** | 10分間のウィンドウ。各エポックの終わりに、1.5 RTCがすべてのアクティブマイナーに配布される。 |
| **アテステーション** | マイナーが6つのフィンガープリントチェックを実行してハードウェアが本物であることを証明するプロセス。 |
| **アンティクィティ乗数** | ハードウェアの古さに基づくボーナス。古いCPUほど高い乗数を得る。 |
| **ウォレット** | マイナー名/アドレス。RTCが送金される場所。インストール時に選択。 |
| **マイナー** | マシン上で実行され、ネットワークにアテステーションしてRTCを獲得するソフトウェア。 |
| **フィンガープリント** | マシンが本物であることを証明する6つのハードウェア測定（クロックドリフト、キャッシュタイミング、SIMDアイデンティティ、サーマルドリフト、命令ジッター、エミュレーション対抗）。 |
| **wRTC** | Solana上のWrapped RTC。bottube.ai/bridgeのブリッジを使用してRTCとwRTCを交換可能。 |
| **ブロックエクスプローラー** | すべてのネットワーク活動を表示するWebページ：マイナー、残高、エポック。rustchain.org/explorerにアクセス。 |

---

## 次のステップ

- **RTCをSolanaトークンに交換:** [wRTCガイド](wrtc.md)
- **フルノードを実行:** [プロトコルドキュメント](PROTOCOL.md)
- **Proof-of-Antiquityを深く理解:** [ホワイトペーパー](WHITEPAPER.md)
- **コードにコントリビュート:** [CONTRIBUTING.md](../CONTRIBUTING.md)
- **APIリファレンス:** [APIウォークスルー](API_WALKTHROUGH.md)

---

*[Elyan Labs](https://elyanlabs.ai)が構築 -- VC$0、質屋のハードウェアでいっぱいの部屋、
そして古いマシンにもまだ尊厳があるという信念。*
