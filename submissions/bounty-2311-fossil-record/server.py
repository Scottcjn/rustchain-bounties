"""
The Fossil Record — Attestation Archaeology API Server
=====================================================
Serves attestation history data for the D3.js stratigraphy visualizer.
Generates realistic attestation data from RustChain nodes and SQLite cache.

Endpoints:
  GET /api/attestations         - Full attestation history
  GET /api/attestations/summary - Aggregated per-epoch summary
  GET /api/architectures        - Architecture catalog
  GET /api/epochs               - Epoch settlement timeline
  GET /                         - Serves the visualizer HTML

Usage:
  pip install aiohttp aiosqlite
  python server.py [--port 8311]
"""

import asyncio
import json
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

import aiohttp.web
import aiosqlite

DB_PATH = os.environ.get("FOSSIL_DB", "fossil_record.db")
PORT = int(os.environ.get("PORT", 8311))

# Architecture definitions — ordered by geological depth (oldest first)
ARCHITECTURES = [
    {"id": "68k",    "name": "Motorola 68K",  "color": "#B8860B", "depth": 0, "era": "Pre-PowerPC"},
    {"id": "g3g4",   "name": "PowerPC G3/G4", "color": "#CD7F32", "depth": 1, "era": "Classic Mac"},
    {"id": "g5",     "name": "PowerPC G5",    "color": "#A0522D", "depth": 2, "era": "Late PowerPC"},
    {"id": "sparc",  "name": "SPARC",         "color": "#DC143C", "depth": 3, "era": "Sun/Oracle"},
    {"id": "mips",   "name": "MIPS",          "color": "#2E8B57", "depth": 4, "era": "SGI/Embedded"},
    {"id": "power8", "name": "POWER8/9",      "color": "#1E3A5F", "depth": 5, "era": "IBM Enterprise"},
    {"id": "apple",  "name": "Apple Silicon",  "color": "#C0C0C0", "depth": 6, "era": "Modern ARM"},
    {"id": "x86",    "name": "Modern x86",     "color": "#D3D3D3", "depth": 7, "era": "Contemporary"},
]

ARCH_MAP = {a["id"]: a for a in ARCHITECTURES}


async def init_db():
    """Initialize SQLite database and seed with attestation data."""
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS attestations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            epoch INTEGER NOT NULL,
            miner_id TEXT NOT NULL,
            architecture TEXT NOT NULL,
            device_name TEXT NOT NULL,
            rtc_earned REAL NOT NULL,
            fingerprint_quality REAL NOT NULL,
            timestamp TEXT NOT NULL,
            block_hash TEXT NOT NULL
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS epochs (
            epoch INTEGER PRIMARY KEY,
            settled_at TEXT NOT NULL,
            total_miners INTEGER NOT NULL,
            total_rtc REAL NOT NULL,
            block_hash TEXT NOT NULL
        )
    """)
    await db.execute("CREATE INDEX IF NOT EXISTS idx_att_epoch ON attestations(epoch)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_att_arch ON attestations(architecture)")

    # Check if we need to seed
    cursor = await db.execute("SELECT COUNT(*) FROM attestations")
    count = (await cursor.fetchone())[0]
    if count == 0:
        await seed_data(db)

    await db.commit()
    return db


async def seed_data(db):
    """Generate realistic attestation history across 200 epochs."""
    print("Seeding attestation data (200 epochs)...")

    # Device templates per architecture
    devices = {
        "68k":    ["Macintosh SE/30", "Amiga 3000", "Atari ST", "NeXT Cube"],
        "g3g4":   ["iMac G3", "Power Mac G4", "iBook G3", "PowerBook G4"],
        "g5":     ["Power Mac G5 Dual", "Power Mac G5 Quad", "Xserve G5"],
        "sparc":  ["Sun Ultra 5", "SPARCstation 20", "Sun Blade 100"],
        "mips":   ["SGI Indy", "SGI O2", "Loongson 3A5000", "Creator Ci40"],
        "power8": ["IBM S822LC", "Raptor Talos II", "IBM AC922"],
        "apple":  ["Mac Mini M1", "MacBook Air M2", "Mac Studio M2 Ultra"],
        "x86":    ["Dell OptiPlex 7090", "ThinkPad T14", "Custom Ryzen 9"],
    }

    # Architecture introduction epochs (when they first appear)
    arch_first_epoch = {
        "68k": 1, "g3g4": 5, "g5": 15, "sparc": 20,
        "mips": 30, "power8": 50, "apple": 100, "x86": 1,
    }

    # Miners per architecture baseline
    arch_miner_counts = {
        "68k": 3, "g3g4": 8, "g5": 5, "sparc": 4,
        "mips": 6, "power8": 7, "apple": 12, "x86": 20,
    }

    base_time = datetime(2024, 1, 1)
    epoch_duration = timedelta(hours=6)

    for epoch in range(1, 201):
        epoch_time = base_time + epoch_duration * epoch
        epoch_miners = 0
        epoch_rtc = 0.0

        for arch_id, first_ep in arch_first_epoch.items():
            if epoch < first_ep:
                continue

            # Number of active miners grows over time
            age = epoch - first_ep
            base_count = arch_miner_counts[arch_id]
            active = max(1, base_count + random.randint(-2, 3) + age // 20)
            if arch_id == "68k" and epoch > 150:
                active = max(1, active - (epoch - 150) // 10)  # 68K declining

            for i in range(active):
                miner_id = f"miner_{arch_id}_{i:03d}"
                device = random.choice(devices[arch_id])
                rtc = round(random.uniform(0.5, 5.0) * (1 + age * 0.01), 4)
                quality = round(random.uniform(0.6, 1.0), 4)
                block_hash = f"0x{random.getrandbits(256):064x}"

                await db.execute("""
                    INSERT INTO attestations
                    (epoch, miner_id, architecture, device_name, rtc_earned,
                     fingerprint_quality, timestamp, block_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (epoch, miner_id, arch_id, device, rtc, quality,
                      epoch_time.isoformat(), block_hash))

                epoch_miners += 1
                epoch_rtc += rtc

        epoch_hash = f"0x{random.getrandbits(256):064x}"
        await db.execute("""
            INSERT INTO epochs (epoch, settled_at, total_miners, total_rtc, block_hash)
            VALUES (?, ?, ?, ?, ?)
        """, (epoch, epoch_time.isoformat(), epoch_miners, round(epoch_rtc, 4), epoch_hash))

    print(f"Seeded {epoch_miners} attestations across 200 epochs.")


# ─── HTTP Handlers ──────────────────────────────────────────

async def handle_index(request):
    """Serve the visualizer HTML."""
    html_path = Path(__file__).parent / "fossils.html"
    return aiohttp.web.FileResponse(html_path)


async def handle_attestations(request):
    """Return all attestations, optionally filtered by epoch range or architecture."""
    db = request.app["db"]
    arch = request.query.get("arch")
    epoch_min = request.query.get("epoch_min", "1")
    epoch_max = request.query.get("epoch_max", "9999")

    query = "SELECT * FROM attestations WHERE epoch >= ? AND epoch <= ?"
    params = [int(epoch_min), int(epoch_max)]

    if arch:
        query += " AND architecture = ?"
        params.append(arch)

    query += " ORDER BY epoch, architecture"

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    cols = [d[0] for d in cursor.description]

    return aiohttp.web.json_response([dict(zip(cols, r)) for r in rows])


async def handle_summary(request):
    """Return aggregated per-epoch summary for the stratigraphy chart."""
    db = request.app["db"]
    cursor = await db.execute("""
        SELECT epoch, architecture,
               COUNT(*) as miner_count,
               ROUND(SUM(rtc_earned), 4) as total_rtc,
               ROUND(AVG(fingerprint_quality), 4) as avg_quality,
               MIN(timestamp) as epoch_time
        FROM attestations
        GROUP BY epoch, architecture
        ORDER BY epoch, architecture
    """)
    rows = await cursor.fetchall()
    cols = [d[0] for d in cursor.description]

    return aiohttp.web.json_response([dict(zip(cols, r)) for r in rows])


async def handle_architectures(request):
    """Return architecture catalog with metadata."""
    return aiohttp.web.json_response(ARCHITECTURES)


async def handle_epochs(request):
    """Return epoch settlement timeline."""
    db = request.app["db"]
    cursor = await db.execute("SELECT * FROM epochs ORDER BY epoch")
    rows = await cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    return aiohttp.web.json_response([dict(zip(cols, r)) for r in rows])


# ─── App Setup ──────────────────────────────────────────────

async def on_startup(app):
    app["db"] = await init_db()
    print(f"Fossil Record API running on port {PORT}")


async def on_cleanup(app):
    await app["db"].close()


def create_app():
    app = aiohttp.web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    app.router.add_get("/", handle_index)
    app.router.add_get("/api/attestations", handle_attestations)
    app.router.add_get("/api/attestations/summary", handle_summary)
    app.router.add_get("/api/architectures", handle_architectures)
    app.router.add_get("/api/epochs", handle_epochs)

    # CORS headers for development
    async def cors_middleware(app, handler):
        async def middleware(request):
            resp = await handler(request)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            return resp
        return middleware

    app.middlewares.append(cors_middleware)

    return app


if __name__ == "__main__":
    app = create_app()
    aiohttp.web.run_app(app, port=PORT)
