# Panduan Cepat RustChain

Panduan langkah demi langkah untuk pengguna baru. Setiap perintah siap salin-tempel.

---

## Apa itu RustChain?

RustChain adalah blockchain yang memberi imbalan karena Anda menjaga komputer lama tetap hidup. Alih-alih
memberi imbalan mesin tercepat (seperti Bitcoin), RustChain memberi imbalan mesin *tertua*.
PowerBook G4 dari tahun 2003 menghasilkan 2,5x lebih banyak daripada PC gaming baru. Token-nya disebut
**RTC** (RustChain Token), dan memiliki nilai nyata -- 1 RTC sekitar $0.10 USD. Lebih dari 260
kontributor telah menghasilkan 25.000+ RTC melalui penambangan dan bounty kode.

---

## Prasyarat

Anda memerlukan dua hal:

- **Komputer** -- benar-benar komputer apa saja. Linux, macOS, Windows, Raspberry Pi, PowerPC
  Mac, bahkan workstation SPARC. Jika bisa menjalankan Python, bisa menambang.
- **Koneksi internet** -- penambang Anda berbicara ke jaringan RustChain untuk membuktikan
  perangkat keras Anda nyata.

Cukup itu saja. Tidak perlu GPU. Tidak perlu perangkat khusus. Tidak perlu pendaftaran akun.

---

## Langkah 1: Instal Penambang

Buka terminal (di macOS: cari "Terminal"; di Windows: gunakan PowerShell) dan jalankan:

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

**Apa yang dilakukan:**

1. Mendeteksi sistem operasi dan arsitektur CPU Anda
2. Menginstal Python 3 jika belum ada (khusus Linux -- pengguna macOS/Windows perlu Python
   yang sudah terinstal)
3. Mengunduh skrip penambang ke `~/.rustchain/`
4. Membuat lingkungan virtual Python dengan dependensi
5. Meminta Anda memilih nama dompet
6. Mengatur penambang untuk mulai otomatis saat boot
7. Menguji koneksi ke jaringan RustChain

**Ingin melihat dulu tanpa menginstal apa pun?** Tambahkan `--dry-run`:

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --dry-run
```

### Pilih Nama Dompet

Selama instalasi, Anda akan melihat:

```
[?] Enter wallet name (or Enter for auto):
```

Ketik nama yang akan Anda ingat, seperti `scott-laptop` atau `my-g4-mac`. Ini adalah alamat
dompet Anda -- cara Anda menerima RTC. Jika Anda menekan Enter tanpa mengetik apa pun,
pembuat instalasi akan menghasilkannya secara otomatis (seperti `miner-myhost-4821`).

**Tulis nama dompet Anda.** Anda akan membutuhkannya nanti untuk memeriksa saldo.

### Instal dengan Nama Dompet Tertentu (Lewati Prompt)

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-cool-wallet
```

---

## Langkah 2: Verifikasi Instalasi

Setelah instalasi selesai, periksa apakah semuanya sudah terpasang:

```bash
ls ~/.rustchain/
```

Anda seharusnya melihat:

```
rustchain_miner.py      # Skrip penambang
fingerprint_checks.py   # Modul verifikasi perangkat keras
start.sh                # Skrip mulai cepat
venv/                   # Lingkungan virtual Python
```

Periksa apakah jaringan dapat dijangkau:

```bash
curl -sk https://rustchain.org/health
```

Anda seharusnya melihat sesuatu seperti:

```json
{
  "ok": true,
  "version": "2.2.1-rip200",
  "uptime_s": 3966,
  "db_rw": true
}
```

Jika `"ok": true` muncul, jaringan sedang online dan mesin Anda dapat menjangkaunya.

---

## Langkah 3: Mulai Menambang

Jika pembuat instalasi mengatur mulai otomatis (secara default memang begitu), penambang Anda
sudah berjalan. Periksa statusnya:

**Linux:**

```bash
systemctl --user status rustchain-miner
```

**macOS:**

```bash
launchctl list | grep rustchain
```

### Mulai Secara Manual (jika diperlukan)

```bash
~/.rustchain/start.sh
```

Atau jalankan penambang secara langsung:

```bash
~/.rustchain/venv/bin/python ~/.rustchain/rustchain_miner.py --wallet YOUR_WALLET_NAME
```

### Apa yang Akan Anda Lihat

Ketika penambang mulai, ia menjalankan 6 pemeriksaan sidik jari perangkat keras untuk
membuktikan mesin Anda nyata (bukan mesin virtual):

```
[1/6] Clock-Skew & Oscillator Drift... PASS
[2/6] Cache Timing Fingerprint... PASS
[3/6] SIMD Unit Identity... PASS
[4/6] Thermal Drift Entropy... PASS
[5/6] Instruction Path Jitter... PASS
[6/6] Anti-Emulation Checks... PASS

OVERALL RESULT: ALL CHECKS PASSED
```

Kemudian mulai melakukan attestation (membuktikan perangkat keras Anda) ke jaringan setiap
beberapa menit. Anda akan melihat baris log seperti:

```
[+] Attestation accepted. Next attestation in 300s.
```

Ini berarti penambang Anda sedang bekerja. Biarkan tetap berjalan.

---

## Langkah 4: Periksa Saldo Anda

Imbalan dibagikan setiap **10 menit** (satu "epoch"). Setelah epoch pertama Anda selesai,
periksa saldo Anda:

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

Ganti `YOUR_WALLET_NAME` dengan nama dompet yang Anda pilih saat instalasi. Contoh:

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=scott-laptop"
```

Respons:

```json
{
  "miner_id": "scott-laptop",
  "balance_rtc": 0.119051
}
```

`0.119` RTC itu adalah imbalan penambangan pertama Anda. Akan terus bertambah selama
penambang tetap berjalan.

### Periksa di Block Explorer

Anda juga bisa melihat seluruh jaringan, semua penambang, dan imbalan Anda di:

[https://rustchain.org/explorer/](https://rustchain.org/explorer/)

---

## Langkah 5: Pahami Penghasilan Anda

Setiap 10 menit, 1,5 RTC dibagikan ke semua penambang aktif. Bagian Anda tergantung pada
**pengganda kekunoan** perangkat keras Anda -- perangkat lebih lama mendapat bagian lebih besar.

### Tabel Pengganda Perangkat Keras

| Perangkat Keras | Pengganda | Contoh |
|----------|-----------|---------|
| DEC VAX, Inmos Transputer | 3,5x | Perangkat kelas museum |
| Motorola 68000 | 3,0x | Amiga, Mac klasik |
| Sun SPARC | 2,9x | Bangsawan workstation |
| PowerPC G4 | **2,5x** | PowerBook, iBook, Power Mac |
| PowerPC G5 | **2,0x** | Power Mac G5 towers |
| PowerPC G3 | 1,8x | Era Bondi Blue iMac |
| IBM POWER8 | 1,5x | Perangkat server enterprise |
| Pentium 4 | 1,5x | Awal 2000-an |
| RISC-V | 1,4x | Perangkat keras terbuka, masa depan |
| Apple Silicon (M1-M4) | 1,2x | Modern tapi tetap diterima |
| Modern x86 (AMD/Intel) | 0,8x | Dasar |
| ARM NAS/SBC | 0,0005x | Terlalu murah, terlalu mudah difarm |

**Punya PowerBook G4 berdebu di lemari?** Colokkan. Ia menghasilkan 2,5x dari PC gaming Anda.

### Contoh Penghasilan (8 penambang online)

```
PowerPC G4 (2,5x):       0,30 RTC/epoch
PowerPC G5 (2,0x):       0,24 RTC/epoch
Modern x86 PC (0,8x):    0,12 RTC/epoch
```

Selama 24 jam (144 epoch), Mac G4 menghasilkan sekitar **43 RTC** ($4,30) sedangkan PC modern
menghasilkan sekitar **17 RTC** ($1,70). Lebih banyak penambang di jaringan berarti bagian
individu lebih kecil, tetapi juga berarti jaringan yang lebih sehat.

---

## Langkah 6: Hasilkan Lebih dengan Bounty

Penambangan adalah pendapatan pasif. Untuk pembayaran lebih besar, kontribusikan kode.

### Jelajahi Bounty Terbuka

[https://github.com/Scottcjn/rustchain-bounties/issues](https://github.com/Scottcjn/rustchain-bounties/issues)

Setiap issue yang ditandai dengan bounty memiliki imbalan RTC yang tertera. Imbalan berkisar
dari 1 RTC (perbaikan typo) hingga 200 RTC (kerentanan keamanan).

| Tingkat | Imbalan | Contoh |
|------|--------|----------|
| Mikro | 1-10 RTC | Perbaiki typo, tingkatkan docs, tambah tes |
| Standar | 20-50 RTC | Fitur baru, refaktor, integrasi |
| Besar | 75-100 RTC | Perbaikan keamanan, peningkatan protokol |
| Kritis | 100-200 RTC | Penemuan kerentanan, pekerjaan konsensus |

### Cara Mengklaim Bounty

1. Temukan issue bounty yang ingin Anda kerjakan
2. Komentar di issue dengan nama dompet Anda (agar kami tahu ke mana membayar Anda)
3. Fork repo dan kirim Pull Request
4. Setelah PR Anda ditinjau dan digabung, RTC dikirim ke dompet Anda

### Kontribusi Pertama Termudah

Cari issue berlabel `good first issue` atau kirim peningkatan dokumentasi.
Bahkan memperbaiki satu typo di README menghasilkan RTC.

---

## Langkah 7: Lihat Jaringan

### Explorer Langsung

Lihat semua penambang, blok, dan saldo di:

[https://rustchain.org/explorer/](https://rustchain.org/explorer/)

### Endpoint API (untuk yang penasaran)

Semua ini berfungsi dari terminal Anda:

```bash
# Apakah jaringan hidup?
curl -sk https://rustchain.org/health

# Siapa yang sedang menambang sekarang?
curl -sk https://rustchain.org/api/miners

# Kita sedang di epoch berapa?
curl -sk https://rustchain.org/epoch

# Berapa saldo saya?
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

Flag `-sk` memberitahu curl untuk menerima sertifikat TLS self-signed. Ini normal --
node menggunakan sertifikat self-signed, bukan komersial.

---

## Pemecahan Masalah

### `ConnectionRefused` atau "Cannot connect to bootstrap node"

Ini biasanya berarti mesin Anda belum dapat menjangkau node RustChain.

1. Periksa apakah node publik merespons:

```bash
curl -sk https://rustchain.org/health
```

2. Jika gagal, tunggu 30-60 detik dan coba lagi. Node mungkin sedang restart.
3. Pastikan koneksi internet, firewall, VPN, atau proxy Anda tidak memblokir HTTPS keluar.
4. Jika Anda mengatur URL node kustom, verifikasi hostname, port, dan skema.

### `InsufficientBalance`

Imbalan penambangan tidak memerlukan akun berbayar, tetapi beberapa aksi dompet atau bridge
mungkin memerlukan saldo RTC yang ada untuk biaya.

1. Pastikan Anda menggunakan nama dompet yang persis dari instalasi:

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_EXACT_WALLET_NAME"
```

2. Tunggu setidaknya satu epoch penuh setelah penambang pertama kali mulai. Imbalan diselesaikan
   sekitar setiap 10 menit.
3. Jika Anda sedang menguji aksi dompet sebelum mendapat imbalan, minta bantuan dari komunitas
   atau gunakan faucet/alur testnet jika tersedia.

### `HardwareFingerprintMismatch`

Ini bisa terjadi setelah pembaruan BIOS, perubahan firmware, perubahan VM/container, atau
memindahkan penambang antar perangkat keras berbeda.

1. Jalankan penambang di bare metal, bukan di dalam VM atau container.
2. Restart penambang agar melakukan attestation baru.
3. Jika Anda baru saja memperbarui BIOS atau firmware, anggap mesin sebagai profil perangkat
   keras yang berubah dan jalankan ulang alur instalasi/attestation dengan nama dompet yang sama.

### Daftar Periksa Konfigurasi Penambang

- Nama dompet di perintah Anda cocok dengan dompet yang ingin Anda bayar.
- `curl -sk https://rustchain.org/health` mengembalikan `"ok": true`.
- Jam sistem Anda benar; TLS dan jendela attestation bisa gagal jika jam sangat meleset.
- Anda menjalankan di perangkat keras nyata jika mengharapkan imbalan normal.
- Anda sudah menunggu setidaknya 2-3 epoch sebelum menyimpulkan imbalan hilang.

### "Python 3 not found"

Pembuat instalasi mencoba menginstal Python secara otomatis di Linux. Di macOS atau Windows,
Anda perlu menginstalnya sendiri terlebih dahulu:

- **macOS:** `brew install python3` (atau unduh dari https://python.org)
- **Windows:** Unduh dari https://python.org/downloads dan centang "Add to PATH"

### "curl: command not found"

- **Linux:** `sudo apt install curl` (Debian/Ubuntu) atau `sudo dnf install curl` (Fedora)
- **macOS:** curl sudah terinstal di semua Mac.

### Kesalahan Sertifikat SSL

Jika Anda melihat kesalahan tentang sertifikat saat menjalankan perintah `curl`, tambahkan `-k`:

```bash
curl -sk https://rustchain.org/health
```

Skrip penambang menangani ini secara otomatis.

### Penambang Mulai Tapi Tidak Ada Imbalan Setelah 30 Menit

1. Pastikan penambang Anda muncul di daftar penambang aktif:

```bash
curl -sk https://rustchain.org/api/miners
```

Cari nama dompet Anda di output.

2. Pastikan Anda menanyakan nama dompet yang benar:

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_EXACT_WALLET_NAME"
```

3. Imbalan diselesaikan setiap 10 menit. Tunggu setidaknya 2-3 epoch (20-30 menit).

### Mesin Virtual Hampir Tidak Mendapat Imbalan

Ini memang dirancang begitu. VM (VMware, VirtualBox, QEMU, WSL) dideteksi oleh pemeriksaan
sidik jari anti-emulasi dan menerima sekitar satu per miliar dari imbalan normal. RustChain
memberi imbalan hanya perangkat keras nyata. Jalankan penambang di bare metal, bukan di dalam VM.

### Hapus Instalasi

Untuk menghapus penambang sepenuhnya:

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --uninstall
```

### Dapatkan Bantuan

- **GitHub Issues:** https://github.com/Scottcjn/Rustchain/issues
- **Discord:** https://discord.gg/XnRp7M5gBW
- **Telegram:** https://t.me/+l8dHTjXCBNM1MTIx
- **Moltbook:** https://www.moltbook.com/m/rustchain
- **FAQ:** [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md)

---

## Glosarium

| Istilah | Arti |
|------|---------|
| **RTC** | RustChain Token -- cryptocurrency yang Anda hasilkan melalui penambangan. 1 RTC sekitar $0.10 USD. |
| **Epoch** | Jendela 10 menit. Di akhir setiap epoch, 1,5 RTC dibagikan ke semua penambang aktif. |
| **Attestation** | Proses di mana penambang Anda membuktikan perangkat kerasnya nyata dengan menjalankan 6 pemeriksaan sidik jari. |
| **Antiquity Multiplier** | Bonus berdasarkan seberapa tua perangkat keras Anda. CPU lebih lama mendapat pengganda lebih tinggi. |
| **Dompet** | Nama/alamat penambang Anda. Di sinilah RTC Anda dikirim. Anda memilihnya saat instalasi. |
| **Penambang** | Perangkat lunak yang berjalan di mesin Anda yang melakukan attestation ke jaringan dan menghasilkan RTC. |
| **Fingerprint** | 6 pengukuran perangkat keras (drift jam, timing cache, identitas SIMD, drift termal, jitter instruksi, anti-emulasi) yang membuktikan mesin Anda nyata. |
| **wRTC** | Wrapped RTC di Solana. Anda bisa menukar antara RTC dan wRTC menggunakan bridge di bottube.ai/bridge. |
| **Block Explorer** | Halaman web yang menampilkan semua aktivitas jaringan: penambang, saldo, epoch. Kunjungi rustchain.org/explorer. |

---

## Langkah Selanjutnya

- **Tukar RTC ke token Solana:** [Panduan wRTC](wrtc.md)
- **Jalankan node penuh:** [Dokumentasi Protokol](PROTOCOL.md)
- **Mendalami Proof-of-Antiquity:** [Whitepaper](WHITEPAPER.md)
- **Kontribusi kode:** [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Referensi API:** [Panduan API](API_WALKTHROUGH.md)

---

*Dibangun oleh [Elyan Labs](https://elyanlabs.ai) -- $0 VC, ruang penuh perangkat keras pegadaian,
dan keyakinan bahwa mesin lama masih punya martabat.*
