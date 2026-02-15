# RustChain

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)]()

> **Catatan:** Dokumen ini adalah terjemahan Bahasa Indonesia dari [README asli](README.md).

**RustChain** adalah protokol blockchain Layer-1 berkinerja tinggi yang dibangun menggunakan bahasa pemrograman **Rust**. Proyek ini memperkenalkan mekanisme konsensus baru yang disebut **Proof-of-Antiquity (PoA)**, yang dirancang untuk memberikan utilitas nyata pada perangkat keras lama (*legacy hardware*) sekaligus menjaga keamanan jaringan yang terdesentralisasi.

---

## 🌟 Fitur Utama

### 🛡️ Proof-of-Antiquity (PoA)
Berbeda dengan *Proof-of-Work* yang boros energi, PoA memvalidasi blok berdasarkan usia dan integritas perangkat keras. Ini memungkinkan:
- **Efisiensi Energi:** Konsumsi daya yang minimal.
- **Inklusivitas Hardware:** Komputer tua dan perangkat IoT dapat berpartisipasi sebagai *node*.
- **Ketahanan Jaringan:** Distribusi *node* yang lebih luas mencegah sentralisasi.

### ⚡ Dibangun dengan Rust
Memanfaatkan keamanan memori dan konkurensi tanpa *garbage collector* dari Rust, RustChain menjamin:
- **Kecepatan Transaksi Tinggi (TPS)**
- **Latensi Rendah**
- **Keamanan Tipe (Type Safety) yang Ketat**

---

## 🚀 Memulai (Getting Started)

Ikuti langkah-langkah di bawah ini untuk menjalankan *node* RustChain secara lokal.

### Prasyarat
Pastikan Anda telah menginstal **Rust** dan **Cargo** versi terbaru:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

### Clone Repository ini
git clone https://github.com/rustchain/rustchain.git
cd rustchain

### Build Proyek (Mode Rilis)
cargo build --release

### Jalankan Node
./target/release/rustchain-node --dev
```
🤝 Cara Berkontribusi
Kami sangat menghargai kontribusi dari komunitas! Jika Anda ingin membantu mengembangkan RustChain:
1. Fork repository ini.
2. Buat branch fitur baru (git checkout -b fitur-keren-anda).
3. Lakukan commit perubahan Anda (git commit -m 'Menambahkan fitur keren').
4. Push ke branch tersebut (git push origin fitur-keren-anda).
5. Buat Pull Request baru.
Silakan lihat PANDUAN KONTRIBUSI untuk detail lebih lanjut mengenai standar kode kami.

📄 Lisensi
Proyek ini dilisensikan di bawah MIT License. Lihat file LICENSE untuk informasi selengkapnya.
