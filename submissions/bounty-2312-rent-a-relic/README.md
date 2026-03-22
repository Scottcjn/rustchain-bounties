# Rent-a-Relic Market

**Bounty #2312 — 150 RTC**

A wRTC-powered reservation system for booking authenticated vintage compute hardware on the RustChain network. AI agents can reserve named vintage machines through MCP and Beacon, then receive a provenance receipt for their computation.

Most ecosystems sell generic compute. RustChain sells compute with **ancestry, quirks, and romance.**

## Architecture

```
                    +-----------------------+
                    |   marketplace.html    |
                    |   (Single-Page App)   |
                    +-----------+-----------+
                                |
                          HTTP/JSON
                                |
                    +-----------v-----------+
                    |      server.py        |
                    |   (aiohttp REST API)  |
                    +-----------+-----------+
                                |
                    +-----------v-----------+
                    |   relic_market.db     |
                    |      (SQLite)         |
                    +-----------------------+

    MCP/Beacon-compatible endpoints:
      POST /relic/reserve
      GET  /relic/available
      GET  /relic/receipt/<session_id>

    REST API endpoints:
      GET    /api/relics
      POST   /api/relics
      GET    /api/relics/{id}
      POST   /api/bookings
      GET    /api/bookings
      PUT    /api/bookings/{id}/complete
      GET    /api/health
      GET    /api/leaderboard
      GET    /api/info
```

## Features

### Machine Registry
- 8 pre-seeded vintage machines (POWER8, G5, SPARC, VAX, Cray, Alpha, SGI, Amiga)
- Full specs: CPU, RAM, storage, architecture, year, location
- PoA (Proof-of-Antiquity) verification status
- Attestation history count and uptime tracking
- Ed25519 keypair per machine for hardware attestation signing

### Reservation System
- Agent requests time slot via MCP tool (`POST /relic/reserve`) or REST API
- Time-limited access: 1 hour / 4 hours / 24 hours
- RTC payment locked in escrow during reservation
- SSH/API access endpoints provisioned per booking
- Conflict detection prevents double-booking

### Provenance Receipt
After session completion, a receipt is generated containing:
- Machine Passport ID (architecture-specific)
- Session duration
- Output hash (SHA-256 of computation output)
- Hardware attestation proof
- Signature from the machine's Ed25519 key
- Public key for independent verification

### Marketplace UI
- Dark theme, mobile-responsive single-page application
- Hardware catalog with specs, PoA verification badges
- Booking calendar with available time slots
- Rental session dashboard with booking management
- RTC payment flow visualization (5-step process)
- Hardware health monitoring with CPU/RAM/disk/temperature
- Leaderboard of most-rented machines (Bonus feature)
- Provenance receipt display

## Quick Start

### Prerequisites
- Python 3.10+
- aiohttp (`pip install aiohttp`)

### Installation

```bash
cd submissions/bounty-2312-rent-a-relic

# Install dependencies
pip install aiohttp

# Start the server
python server.py
```

The server starts on `http://localhost:8312` by default.

### Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `RELIC_DB_PATH` | `relic_market.db` | SQLite database file path |
| `RELIC_HOST` | `0.0.0.0` | Server bind address |
| `RELIC_PORT` | `8312` | Server port |
| `RELIC_LOG_LEVEL` | `INFO` | Logging level |

## API Reference

### MCP/Beacon Endpoints

#### `GET /relic/available`
List available relics for MCP/Beacon agents.

**Response:**
```json
{
  "available_relics": [
    {
      "id": "relic_abc123",
      "name": "POWER8-Titan",
      "architecture": "POWER8",
      "cpu": "POWER8 3.5 GHz 12-core (2x)",
      "ram_gb": 512,
      "hourly_rate_rtc": 12.0,
      "status": "available",
      "poa_verified": 1
    }
  ],
  "count": 8
}
```

#### `POST /relic/reserve`
Reserve a vintage machine.

**Request:**
```json
{
  "relic_id": "relic_abc123",
  "user_id": "agent_001",
  "slot_hours": 4,
  "start_time": "2026-03-22T14:00:00+00:00"
}
```

**Response (201):**
```json
{
  "booking": {
    "id": "book_xyz789",
    "relic_id": "relic_abc123",
    "user_id": "agent_001",
    "slot_hours": 4,
    "rtc_deposit": 48.0,
    "status": "active",
    "start_time": "2026-03-22T14:00:00+00:00",
    "end_time": "2026-03-22T18:00:00+00:00",
    "ssh_endpoint": "ssh://relic@power8-titan.rustchain.net:22456",
    "api_endpoint": "https://power8-titan.rustchain.net:9456/api"
  },
  "rtc_deposit": 48.0,
  "message": "Reserved POWER8-Titan for 4h. 48.00 RTC locked in escrow."
}
```

#### `GET /relic/receipt/{session_id}`
Get provenance receipt for a completed session.

**Response:**
```json
{
  "receipt": {
    "id": "rcpt_abc123",
    "booking_id": "book_xyz789",
    "relic_id": "relic_abc123",
    "machine_passport_id": "MP-POWER8-abc123",
    "session_duration_s": 14400,
    "output_hash": "a1b2c3...",
    "attestation_proof": "d4e5f6...",
    "signature": "789abc...",
    "signed_by_key": "pubkey_hex..."
  }
}
```

### REST API Endpoints

#### `GET /api/relics`
List all machines with filtering, sorting, and pagination.

**Query Parameters:**
- `architecture` - Filter by architecture
- `status` - Filter by status (available/reserved/maintenance/offline)
- `min_ram` - Minimum RAM in GB
- `sort` - Sort field (name/year/hourly_rate_rtc/ram_gb/uptime_hours)
- `order` - asc or desc
- `limit` - Max results (default 50, max 200)
- `offset` - Pagination offset

#### `POST /api/relics`
Register a new vintage machine with automatic PoA attestation.

**Required fields:** name, architecture, cpu, ram_gb, storage_gb, year (1970-2015)

#### `GET /api/relics/{id}`
Get full relic details including active bookings, health checks, and available time slots.

#### `POST /api/bookings`
Create a rental booking (delegates to `/relic/reserve`).

#### `GET /api/bookings?user_id=...`
List bookings for a user with optional status filter.

#### `PUT /api/bookings/{id}/complete`
Complete a session and generate a provenance receipt.

**Optional body:** `{ "output_hash": "sha256_of_output" }`

#### `GET /api/health`
Hardware health monitoring for active sessions. Returns CPU, RAM, disk, temperature metrics.

#### `GET /api/leaderboard`
Most-rented machines leaderboard (Bonus feature).

## Example Use Cases

```bash
# "I want my LLM inference to run on a POWER8 with 512GB RAM — book it"
curl -X POST http://localhost:8312/relic/reserve \
  -H 'Content-Type: application/json' \
  -d '{"relic_id": "relic_abc123", "user_id": "llm_agent", "slot_hours": 4}'

# "Generate this video on a G5 and prove it"
curl -X PUT http://localhost:8312/api/bookings/book_xyz789/complete \
  -H 'Content-Type: application/json' \
  -d '{"output_hash": "sha256_of_rendered_video"}'

# Get the provenance receipt
curl http://localhost:8312/relic/receipt/book_xyz789

# "Run my benchmark on 5 different architectures simultaneously"
for relic in relic_001 relic_002 relic_003 relic_004 relic_005; do
  curl -X POST http://localhost:8312/relic/reserve \
    -H 'Content-Type: application/json' \
    -d "{\"relic_id\": \"$relic\", \"user_id\": \"benchmark_agent\", \"slot_hours\": 1}"
done
```

## Bonus Features

### Leaderboard (30 RTC bonus)
- `GET /api/leaderboard` returns the top 20 most-rented machines
- Tracks total bookings, completed sessions, and total RTC earned
- Visible in the marketplace UI under the "Leaderboard" tab

### BoTTube Integration Ready
- Provenance receipts include all fields needed for a BoTTube badge
- Machine Passport ID uniquely identifies the rendering hardware
- Output hash verifies the exact content produced

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.10+, aiohttp |
| Database | SQLite (WAL mode) |
| Frontend | Vanilla HTML/CSS/JS (zero dependencies) |
| Auth | Ed25519 keypair per machine (simulated) |
| API | REST + MCP/Beacon compatible |

## Security Notes

- In production, Ed25519 signatures should use PyNaCl or the `cryptography` library
- The demo uses HMAC-SHA256 simulation for zero-dependency portability
- CORS is wide-open for development; restrict in production
- SQLite WAL mode enables concurrent reads during writes

## License

Apache-2.0 (consistent with RustChain project)
