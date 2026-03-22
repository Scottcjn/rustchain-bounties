# Machine Passport Ledger — Hardware Biographies for RustChain

Every relic machine gets a documented biography: ROM hashes, repair history, benchmark signatures, provenance, and attestation records. A miner stops being just an address and becomes a documented character.

## Features

- **Complete Passport Data Structure**: machine_id, name, manufacture_year, architecture, photo_hash, provenance, benchmarks, attestation history, repair log
- **Web Viewer**: `rustchain.org/passport/<machine_id>` with vintage terminal aesthetic
- **REST API**: Full CRUD for passports + repair log management
- **Ergo-Anchored Hash**: SHA-256 immutability hash of canonical JSON
- **QR Code Generation**: Links to on-chain passport viewer
- **Printable PDF**: Vintage computer aesthetic with all passport data
- **Auto-Seeded**: 3 sample machines with repair histories

## Quick Start

```bash
pip install aiohttp aiosqlite qrcode[pil]
python server.py --port 8309
# Open http://localhost:8309/passport/fp_g4_001_a7c3e9
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/passport/<id>` | HTML passport viewer |
| GET | `/api/passports` | List all passports |
| GET | `/api/passports/<id>` | Get passport JSON |
| POST | `/api/passports` | Create new passport |
| PUT | `/api/passports/<id>` | Update passport fields |
| POST | `/api/passports/<id>/repair` | Add repair log entry |
| GET | `/api/passports/<id>/hash` | Get ergo-anchored hash |
| GET | `/api/passports/<id>/qr` | QR code PNG |
| GET | `/api/passports/<id>/pdf` | Printable PDF view |

## Bounty

Closes #2309 — Machine Passport Ledger (70 RTC + 20 RTC bonus)

**Wallet**: RTC_ElromEvedElElyon_2309
