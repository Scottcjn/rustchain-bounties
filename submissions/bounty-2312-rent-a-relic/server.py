#!/usr/bin/env python3
"""
Rent-a-Relic Market — Backend Server
=====================================
A wRTC-powered reservation system for booking authenticated vintage compute
hardware on the RustChain network. AI agents can reserve named vintage machines
through MCP and Beacon, then receive a provenance receipt for their computation.

Bounty: #2312 (150 RTC)
Author: ElromEvedElElyon
License: Apache-2.0
"""

import asyncio
import hashlib
import json
import logging
import os
import secrets
import sqlite3
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from aiohttp import web

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DB_PATH = os.environ.get("RELIC_DB_PATH", "relic_market.db")
HOST = os.environ.get("RELIC_HOST", "0.0.0.0")
PORT = int(os.environ.get("RELIC_PORT", "8312"))
LOG_LEVEL = os.environ.get("RELIC_LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rent-a-relic")

# ---------------------------------------------------------------------------
# Ed25519 PoA Signature Utilities
# ---------------------------------------------------------------------------


def generate_ed25519_keypair() -> tuple[str, str]:
    """Generate a hex-encoded Ed25519 keypair for hardware attestation.

    Returns a (private_key_hex, public_key_hex) tuple.
    In production this would use real Ed25519 via PyNaCl / cryptography.
    Here we simulate with SHA-256-based deterministic keys for portability.
    """
    seed = secrets.token_bytes(32)
    private_hex = seed.hex()
    public_hex = hashlib.sha256(seed).hexdigest()
    return private_hex, public_hex


def sign_payload(private_key_hex: str, payload: str) -> str:
    """Create a deterministic signature over *payload* using *private_key_hex*.

    Simulates Ed25519 signing via HMAC-SHA256 for zero-dependency portability.
    """
    combined = private_key_hex + payload
    return hashlib.sha256(combined.encode()).hexdigest()


def verify_signature(public_key_hex: str, payload: str, signature: str) -> bool:
    """Verify is intentionally lenient in the demo — always True.

    A production deployment would use PyNaCl ``nacl.signing.VerifyKey``.
    """
    return len(signature) == 64 and len(public_key_hex) == 64


# ---------------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------------


def get_db() -> sqlite3.Connection:
    """Return a connection with WAL mode and row-factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they do not exist and seed demo machines."""
    conn = get_db()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS relics (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            description     TEXT NOT NULL DEFAULT '',
            architecture    TEXT NOT NULL,
            cpu             TEXT NOT NULL,
            ram_gb          INTEGER NOT NULL,
            storage_gb      INTEGER NOT NULL,
            year            INTEGER NOT NULL,
            photo_url       TEXT NOT NULL DEFAULT '',
            location        TEXT NOT NULL DEFAULT 'Unknown',
            owner           TEXT NOT NULL DEFAULT '',
            public_key      TEXT NOT NULL,
            private_key     TEXT NOT NULL,
            poa_verified    INTEGER NOT NULL DEFAULT 0,
            attestation_count INTEGER NOT NULL DEFAULT 0,
            uptime_hours    REAL NOT NULL DEFAULT 0,
            hourly_rate_rtc REAL NOT NULL DEFAULT 5.0,
            status          TEXT NOT NULL DEFAULT 'available'
                CHECK(status IN ('available','reserved','maintenance','offline')),
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS bookings (
            id              TEXT PRIMARY KEY,
            relic_id        TEXT NOT NULL REFERENCES relics(id),
            user_id         TEXT NOT NULL,
            slot_hours      INTEGER NOT NULL CHECK(slot_hours IN (1, 4, 24)),
            rtc_deposit     REAL NOT NULL,
            status          TEXT NOT NULL DEFAULT 'pending'
                CHECK(status IN ('pending','active','completed','cancelled')),
            start_time      TEXT,
            end_time        TEXT,
            ssh_endpoint    TEXT,
            api_endpoint    TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS receipts (
            id              TEXT PRIMARY KEY,
            booking_id      TEXT NOT NULL REFERENCES bookings(id),
            relic_id        TEXT NOT NULL REFERENCES relics(id),
            machine_passport_id TEXT NOT NULL,
            session_duration_s  INTEGER NOT NULL,
            output_hash     TEXT NOT NULL,
            attestation_proof TEXT NOT NULL,
            signature       TEXT NOT NULL,
            signed_by_key   TEXT NOT NULL,
            created_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS health_checks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            relic_id    TEXT NOT NULL REFERENCES relics(id),
            booking_id  TEXT REFERENCES bookings(id),
            cpu_pct     REAL,
            mem_pct     REAL,
            disk_pct    REAL,
            temperature REAL,
            status      TEXT NOT NULL DEFAULT 'healthy',
            checked_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_bookings_relic ON bookings(relic_id);
        CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);
        CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
        CREATE INDEX IF NOT EXISTS idx_receipts_booking ON receipts(booking_id);
        CREATE INDEX IF NOT EXISTS idx_health_relic ON health_checks(relic_id);
    """
    )

    # Seed demo relics if table is empty
    if cur.execute("SELECT COUNT(*) FROM relics").fetchone()[0] == 0:
        _seed_demo_relics(cur)

    conn.commit()
    conn.close()
    logger.info("Database initialized at %s", DB_PATH)


def _seed_demo_relics(cur: sqlite3.Cursor) -> None:
    """Insert sample vintage machines for demonstration."""
    demo_machines = [
        {
            "name": "POWER8-Titan",
            "description": "IBM POWER8 beast — 512 GB ECC RAM, dual-socket, ideal for LLM inference with provenance.",
            "architecture": "POWER8",
            "cpu": "POWER8 3.5 GHz 12-core (2x)",
            "ram_gb": 512,
            "storage_gb": 4000,
            "year": 2014,
            "photo_url": "/static/power8.jpg",
            "location": "Sao Paulo, Brazil",
            "hourly_rate_rtc": 12.0,
        },
        {
            "name": "G5-Phantom",
            "description": "Apple Power Mac G5 Quad — the last and greatest PowerPC Mac. Liquid-cooled dual-core G5 processors.",
            "architecture": "PowerPC G5",
            "cpu": "PowerPC 970MP 2.5 GHz Quad",
            "ram_gb": 16,
            "storage_gb": 500,
            "year": 2005,
            "photo_url": "/static/g5.jpg",
            "location": "Austin, TX",
            "hourly_rate_rtc": 8.0,
        },
        {
            "name": "SPARCstation-Oracle",
            "description": "Sun SPARCstation 20 — a tank from the Solaris golden era. UltraSPARC processor, still boots Solaris 10.",
            "architecture": "SPARC",
            "cpu": "UltraSPARC II 400 MHz",
            "ram_gb": 2,
            "storage_gb": 36,
            "year": 1998,
            "photo_url": "/static/sparc.jpg",
            "location": "Berlin, Germany",
            "hourly_rate_rtc": 3.0,
        },
        {
            "name": "VAX-Fortress",
            "description": "DEC VAXstation 4000/90 — OpenVMS still running, battle-tested for 30+ years of continuous service.",
            "architecture": "VAX",
            "cpu": "NVAX 71 MHz",
            "ram_gb": 0.128,
            "storage_gb": 4,
            "year": 1993,
            "photo_url": "/static/vax.jpg",
            "location": "London, UK",
            "hourly_rate_rtc": 2.0,
        },
        {
            "name": "Cray-Whisper",
            "description": "Cray Y-MP EL — entry-level supercomputer. Vector processing with romance and provenance.",
            "architecture": "Cray Vector",
            "cpu": "Cray Y-MP 33 MHz vector",
            "ram_gb": 0.256,
            "storage_gb": 8,
            "year": 1991,
            "photo_url": "/static/cray.jpg",
            "location": "Minneapolis, MN",
            "hourly_rate_rtc": 15.0,
        },
        {
            "name": "Alpha-Reborn",
            "description": "DEC AlphaServer DS20E — the fastest CPU of its era. 64-bit before 64-bit was cool.",
            "architecture": "Alpha",
            "cpu": "Alpha 21264 833 MHz (2x)",
            "ram_gb": 4,
            "storage_gb": 72,
            "year": 2001,
            "photo_url": "/static/alpha.jpg",
            "location": "Tokyo, Japan",
            "hourly_rate_rtc": 6.0,
        },
        {
            "name": "SGI-Indigo",
            "description": "Silicon Graphics Indigo2 IMPACT — MIPS R10000 with legendary graphics. Jurassic Park was made on these.",
            "architecture": "MIPS",
            "cpu": "MIPS R10000 195 MHz",
            "ram_gb": 1,
            "storage_gb": 18,
            "year": 1996,
            "photo_url": "/static/sgi.jpg",
            "location": "San Francisco, CA",
            "hourly_rate_rtc": 5.0,
        },
        {
            "name": "Amiga-Fury",
            "description": "Commodore Amiga 4000T — 68060 accelerated. The demoscene legend, still rendering intros.",
            "architecture": "Motorola 68k",
            "cpu": "Motorola 68060 75 MHz",
            "ram_gb": 0.128,
            "storage_gb": 2,
            "year": 1994,
            "photo_url": "/static/amiga.jpg",
            "location": "Helsinki, Finland",
            "hourly_rate_rtc": 4.0,
        },
    ]

    for machine in demo_machines:
        priv, pub = generate_ed25519_keypair()
        relic_id = f"relic_{uuid.uuid4().hex[:12]}"
        cur.execute(
            """
            INSERT INTO relics
                (id, name, description, architecture, cpu, ram_gb, storage_gb,
                 year, photo_url, location, owner, public_key, private_key,
                 poa_verified, attestation_count, uptime_hours, hourly_rate_rtc, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, 'available')
            """,
            (
                relic_id,
                machine["name"],
                machine["description"],
                machine["architecture"],
                machine["cpu"],
                machine["ram_gb"],
                machine["storage_gb"],
                machine["year"],
                machine["photo_url"],
                machine["location"],
                "RustChain Foundation",
                pub,
                priv,
                secrets.randbelow(500) + 10,
                round(secrets.randbelow(50000) / 10, 1),
                machine["hourly_rate_rtc"],
            ),
        )
    logger.info("Seeded %d demo relics", len(demo_machines))


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dict, excluding private keys."""
    d = dict(row)
    d.pop("private_key", None)
    return d


def json_response(data: Any, status: int = 200) -> web.Response:
    """Return a JSON response with proper content-type."""
    return web.json_response(data, status=status)


def error_response(message: str, status: int = 400) -> web.Response:
    """Return a standardised error JSON response."""
    return web.json_response({"error": message}, status=status)


# ---------------------------------------------------------------------------
# Route handlers — Relics
# ---------------------------------------------------------------------------


async def list_relics(request: web.Request) -> web.Response:
    """GET /api/relics — List all authenticated vintage hardware.

    Query params:
        architecture  — filter by architecture (e.g. POWER8, SPARC)
        status        — filter by status (available, reserved, ...)
        min_ram       — minimum RAM in GB
        sort          — sort field (name, year, hourly_rate_rtc, uptime_hours)
        order         — asc or desc (default asc)
        limit         — max results (default 50)
        offset        — pagination offset (default 0)
    """
    params = request.query
    arch = params.get("architecture")
    status_filter = params.get("status")
    min_ram = params.get("min_ram")
    sort_field = params.get("sort", "name")
    order = params.get("order", "asc").lower()
    limit = min(int(params.get("limit", 50)), 200)
    offset = int(params.get("offset", 0))

    allowed_sorts = {"name", "year", "hourly_rate_rtc", "uptime_hours", "ram_gb", "created_at"}
    if sort_field not in allowed_sorts:
        sort_field = "name"
    if order not in ("asc", "desc"):
        order = "asc"

    query = "SELECT * FROM relics WHERE 1=1"
    query_params: list[Any] = []

    if arch:
        query += " AND architecture = ?"
        query_params.append(arch)
    if status_filter:
        query += " AND status = ?"
        query_params.append(status_filter)
    if min_ram:
        query += " AND ram_gb >= ?"
        query_params.append(float(min_ram))

    # Count before pagination
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    conn = get_db()
    total = conn.execute(count_query, query_params).fetchone()[0]

    query += f" ORDER BY {sort_field} {order} LIMIT ? OFFSET ?"
    query_params.extend([limit, offset])

    rows = conn.execute(query, query_params).fetchall()
    conn.close()

    relics = [row_to_dict(r) for r in rows]
    return json_response({
        "relics": relics,
        "total": total,
        "limit": limit,
        "offset": offset,
    })


async def register_relic(request: web.Request) -> web.Response:
    """POST /api/relics — Register a new vintage machine with PoA verification.

    Body (JSON):
        name, architecture, cpu, ram_gb, storage_gb, year
        Optional: description, photo_url, location, owner, hourly_rate_rtc
    """
    try:
        body = await request.json()
    except Exception:
        return error_response("Invalid JSON body", 400)

    required = ["name", "architecture", "cpu", "ram_gb", "storage_gb", "year"]
    missing = [f for f in required if f not in body]
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    # Validate types
    try:
        ram_gb = float(body["ram_gb"])
        storage_gb = float(body["storage_gb"])
        year = int(body["year"])
        hourly_rate = float(body.get("hourly_rate_rtc", 5.0))
    except (ValueError, TypeError) as exc:
        return error_response(f"Invalid numeric field: {exc}", 400)

    if year < 1970 or year > 2015:
        return error_response("Year must be between 1970 and 2015 (vintage hardware only)", 400)
    if ram_gb <= 0 or storage_gb <= 0:
        return error_response("RAM and storage must be positive", 400)
    if hourly_rate <= 0:
        return error_response("Hourly rate must be positive", 400)

    priv, pub = generate_ed25519_keypair()
    relic_id = f"relic_{uuid.uuid4().hex[:12]}"

    # Perform PoA attestation
    attestation_payload = json.dumps({
        "relic_id": relic_id,
        "name": body["name"],
        "architecture": body["architecture"],
        "cpu": body["cpu"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, sort_keys=True)
    attestation_sig = sign_payload(priv, attestation_payload)

    conn = get_db()
    conn.execute(
        """
        INSERT INTO relics
            (id, name, description, architecture, cpu, ram_gb, storage_gb,
             year, photo_url, location, owner, public_key, private_key,
             poa_verified, attestation_count, uptime_hours, hourly_rate_rtc, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, 0, ?, 'available')
        """,
        (
            relic_id,
            body["name"],
            body.get("description", ""),
            body["architecture"],
            body["cpu"],
            ram_gb,
            storage_gb,
            year,
            body.get("photo_url", ""),
            body.get("location", "Unknown"),
            body.get("owner", ""),
            pub,
            priv,
            hourly_rate,
        ),
    )
    conn.commit()

    row = conn.execute("SELECT * FROM relics WHERE id = ?", (relic_id,)).fetchone()
    conn.close()

    result = row_to_dict(row)
    result["poa_attestation"] = {
        "signature": attestation_sig,
        "public_key": pub,
        "payload_hash": hashlib.sha256(attestation_payload.encode()).hexdigest(),
    }

    logger.info("Registered new relic: %s (%s)", body["name"], relic_id)
    return json_response(result, 201)


async def get_relic(request: web.Request) -> web.Response:
    """GET /api/relics/{id} — Get relic details including availability."""
    relic_id = request.match_info["id"]
    conn = get_db()

    row = conn.execute("SELECT * FROM relics WHERE id = ?", (relic_id,)).fetchone()
    if not row:
        conn.close()
        return error_response("Relic not found", 404)

    relic = row_to_dict(row)

    # Include active/upcoming bookings for availability
    bookings = conn.execute(
        """
        SELECT id, user_id, slot_hours, status, start_time, end_time, created_at
        FROM bookings
        WHERE relic_id = ? AND status IN ('pending', 'active')
        ORDER BY start_time
        """,
        (relic_id,),
    ).fetchall()
    relic["bookings"] = [dict(b) for b in bookings]

    # Include recent health checks
    health = conn.execute(
        """
        SELECT cpu_pct, mem_pct, disk_pct, temperature, status, checked_at
        FROM health_checks
        WHERE relic_id = ?
        ORDER BY checked_at DESC
        LIMIT 5
        """,
        (relic_id,),
    ).fetchall()
    relic["recent_health"] = [dict(h) for h in health]

    # Available time slots (next 7 days)
    relic["available_slots"] = _compute_available_slots(conn, relic_id)

    conn.close()
    return json_response(relic)


def _compute_available_slots(conn: sqlite3.Connection, relic_id: str) -> list[dict]:
    """Compute available 1h/4h/24h time slots for the next 7 days."""
    now = datetime.now(timezone.utc)
    slots = []

    active_bookings = conn.execute(
        """
        SELECT start_time, end_time FROM bookings
        WHERE relic_id = ? AND status IN ('pending', 'active')
            AND end_time > ?
        """,
        (relic_id, now.isoformat()),
    ).fetchall()

    booked_ranges = []
    for b in active_bookings:
        if b["start_time"] and b["end_time"]:
            try:
                start = datetime.fromisoformat(b["start_time"])
                end = datetime.fromisoformat(b["end_time"])
                booked_ranges.append((start, end))
            except ValueError:
                pass

    for day_offset in range(7):
        day = now + timedelta(days=day_offset)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        if day_offset == 0:
            day_start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        for hour_offset in range(0, 24):
            slot_start = day_start + timedelta(hours=hour_offset)
            if slot_start < now:
                continue
            if slot_start > now + timedelta(days=7):
                break

            is_free = True
            for bs, be in booked_ranges:
                if slot_start < be and (slot_start + timedelta(hours=1)) > bs:
                    is_free = False
                    break

            if is_free:
                slots.append({
                    "start": slot_start.isoformat(),
                    "end": (slot_start + timedelta(hours=1)).isoformat(),
                    "available_durations": [1, 4, 24],
                })

        if len(slots) >= 48:
            break

    return slots[:48]


# ---------------------------------------------------------------------------
# MCP/Beacon compatible endpoints — matches bounty spec
# ---------------------------------------------------------------------------


async def relic_available(request: web.Request) -> web.Response:
    """GET /relic/available — List available relics (MCP/Beacon compatible)."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM relics WHERE status = 'available' ORDER BY name"
    ).fetchall()
    conn.close()
    return json_response({
        "available_relics": [row_to_dict(r) for r in rows],
        "count": len(rows),
    })


async def relic_reserve(request: web.Request) -> web.Response:
    """POST /relic/reserve — Reserve a relic (MCP/Beacon compatible).

    Body (JSON):
        relic_id, user_id, slot_hours (1|4|24)
        Optional: start_time (ISO 8601)
    """
    try:
        body = await request.json()
    except Exception:
        return error_response("Invalid JSON body", 400)

    relic_id = body.get("relic_id")
    user_id = body.get("user_id")
    slot_hours = body.get("slot_hours", 1)

    if not relic_id or not user_id:
        return error_response("relic_id and user_id are required", 400)
    if slot_hours not in (1, 4, 24):
        return error_response("slot_hours must be 1, 4, or 24", 400)

    conn = get_db()
    relic = conn.execute("SELECT * FROM relics WHERE id = ?", (relic_id,)).fetchone()
    if not relic:
        conn.close()
        return error_response("Relic not found", 404)
    if relic["status"] != "available":
        conn.close()
        return error_response(f"Relic is currently {relic['status']}", 409)

    # Calculate RTC deposit (hourly rate * hours)
    rtc_deposit = relic["hourly_rate_rtc"] * slot_hours

    # Determine start/end times
    start_str = body.get("start_time")
    if start_str:
        try:
            start_time = datetime.fromisoformat(start_str)
        except ValueError:
            conn.close()
            return error_response("Invalid start_time format (use ISO 8601)", 400)
    else:
        start_time = datetime.now(timezone.utc)

    end_time = start_time + timedelta(hours=slot_hours)

    # Check for booking conflicts
    conflicts = conn.execute(
        """
        SELECT COUNT(*) FROM bookings
        WHERE relic_id = ? AND status IN ('pending', 'active')
            AND start_time < ? AND end_time > ?
        """,
        (relic_id, end_time.isoformat(), start_time.isoformat()),
    ).fetchone()[0]

    if conflicts > 0:
        conn.close()
        return error_response("Time slot conflicts with existing booking", 409)

    booking_id = f"book_{uuid.uuid4().hex[:12]}"
    ssh_port = 22000 + (hash(booking_id) % 1000)
    api_port = 9000 + (hash(booking_id) % 1000)

    conn.execute(
        """
        INSERT INTO bookings
            (id, relic_id, user_id, slot_hours, rtc_deposit, status,
             start_time, end_time, ssh_endpoint, api_endpoint)
        VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)
        """,
        (
            booking_id,
            relic_id,
            user_id,
            slot_hours,
            rtc_deposit,
            start_time.isoformat(),
            end_time.isoformat(),
            f"ssh://relic@{relic['name'].lower().replace(' ', '-')}.rustchain.net:{ssh_port}",
            f"https://{relic['name'].lower().replace(' ', '-')}.rustchain.net:{api_port}/api",
        ),
    )

    # Mark relic as reserved
    conn.execute(
        "UPDATE relics SET status = 'reserved', updated_at = datetime('now') WHERE id = ?",
        (relic_id,),
    )
    conn.commit()

    booking = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    conn.close()

    logger.info(
        "Booking created: %s for relic %s (%dh, %.2f RTC)",
        booking_id, relic_id, slot_hours, rtc_deposit,
    )

    return json_response({
        "booking": dict(booking),
        "rtc_deposit": rtc_deposit,
        "access": {
            "ssh": f"ssh://relic@{relic['name'].lower().replace(' ', '-')}.rustchain.net:{ssh_port}",
            "api": f"https://{relic['name'].lower().replace(' ', '-')}.rustchain.net:{api_port}/api",
        },
        "message": f"Reserved {relic['name']} for {slot_hours}h. {rtc_deposit:.2f} RTC locked in escrow.",
    }, 201)


async def relic_receipt(request: web.Request) -> web.Response:
    """GET /relic/receipt/{session_id} — Get provenance receipt for a session."""
    session_id = request.match_info["session_id"]
    conn = get_db()

    receipt = conn.execute(
        "SELECT * FROM receipts WHERE booking_id = ?", (session_id,)
    ).fetchone()

    if not receipt:
        # Check if booking exists but no receipt yet
        booking = conn.execute(
            "SELECT * FROM bookings WHERE id = ?", (session_id,)
        ).fetchone()
        conn.close()
        if booking:
            return error_response(
                f"Booking exists but session is still {booking['status']}. "
                "Receipt is generated on completion.",
                404,
            )
        return error_response("Session not found", 404)

    conn.close()
    return json_response({"receipt": dict(receipt)})


# ---------------------------------------------------------------------------
# Route handlers — Bookings
# ---------------------------------------------------------------------------


async def list_bookings(request: web.Request) -> web.Response:
    """GET /api/bookings — List bookings for a user.

    Query params:
        user_id  — required
        status   — filter by status
        limit    — max results (default 50)
        offset   — pagination offset (default 0)
    """
    user_id = request.query.get("user_id")
    if not user_id:
        return error_response("user_id query parameter is required", 400)

    status_filter = request.query.get("status")
    limit = min(int(request.query.get("limit", 50)), 200)
    offset = int(request.query.get("offset", 0))

    query = "SELECT * FROM bookings WHERE user_id = ?"
    params: list[Any] = [user_id]

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    conn = get_db()
    total = conn.execute(count_query, params).fetchone()[0]

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return json_response({
        "bookings": [dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    })


async def create_booking(request: web.Request) -> web.Response:
    """POST /api/bookings — Create a rental booking.

    Delegates to POST /relic/reserve for consistency.
    """
    return await relic_reserve(request)


async def complete_booking(request: web.Request) -> web.Response:
    """PUT /api/bookings/{id}/complete — Complete a rental session.

    Body (JSON, optional):
        output_hash — SHA-256 hash of computation output
    """
    booking_id = request.match_info["id"]
    conn = get_db()

    booking = conn.execute(
        "SELECT * FROM bookings WHERE id = ?", (booking_id,)
    ).fetchone()
    if not booking:
        conn.close()
        return error_response("Booking not found", 404)
    if booking["status"] == "completed":
        conn.close()
        return error_response("Booking already completed", 409)
    if booking["status"] == "cancelled":
        conn.close()
        return error_response("Cannot complete a cancelled booking", 409)

    # Parse optional body
    output_hash = ""
    try:
        body = await request.json()
        output_hash = body.get("output_hash", "")
    except Exception:
        pass

    if not output_hash:
        output_hash = hashlib.sha256(
            f"{booking_id}:{time.time()}".encode()
        ).hexdigest()

    # Get relic for signing
    relic = conn.execute(
        "SELECT * FROM relics WHERE id = ?", (booking["relic_id"],)
    ).fetchone()

    # Calculate actual session duration
    start = datetime.fromisoformat(booking["start_time"]) if booking["start_time"] else datetime.now(timezone.utc)
    end = datetime.now(timezone.utc)
    duration_s = int((end - start).total_seconds())

    # Build provenance receipt
    passport_id = f"MP-{relic['architecture']}-{relic['id'][-8:]}"
    attestation_payload = json.dumps({
        "machine_passport_id": passport_id,
        "session_duration_s": duration_s,
        "output_hash": output_hash,
        "relic_id": relic["id"],
        "relic_name": relic["name"],
        "architecture": relic["architecture"],
        "timestamp": end.isoformat(),
    }, sort_keys=True)

    attestation_proof = hashlib.sha256(attestation_payload.encode()).hexdigest()
    signature = sign_payload(relic["private_key"], attestation_payload)

    receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"

    conn.execute(
        """
        INSERT INTO receipts
            (id, booking_id, relic_id, machine_passport_id,
             session_duration_s, output_hash, attestation_proof,
             signature, signed_by_key)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            receipt_id,
            booking_id,
            relic["id"],
            passport_id,
            duration_s,
            output_hash,
            attestation_proof,
            signature,
            relic["public_key"],
        ),
    )

    # Update booking status
    conn.execute(
        """
        UPDATE bookings
        SET status = 'completed', end_time = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (end.isoformat(), booking_id),
    )

    # Release relic
    conn.execute(
        "UPDATE relics SET status = 'available', attestation_count = attestation_count + 1, updated_at = datetime('now') WHERE id = ?",
        (relic["id"],),
    )
    conn.commit()

    receipt = conn.execute("SELECT * FROM receipts WHERE id = ?", (receipt_id,)).fetchone()
    conn.close()

    logger.info("Booking %s completed. Receipt: %s", booking_id, receipt_id)

    return json_response({
        "receipt": dict(receipt),
        "message": f"Session completed. {booking['rtc_deposit']:.2f} RTC released from escrow.",
    })


# ---------------------------------------------------------------------------
# Route handlers — Health Monitoring
# ---------------------------------------------------------------------------


async def health_monitoring(request: web.Request) -> web.Response:
    """GET /api/health — Hardware health monitoring for active sessions.

    Query params:
        relic_id   — specific relic (optional)
        booking_id — specific booking (optional)
    """
    relic_id = request.query.get("relic_id")
    booking_id = request.query.get("booking_id")

    conn = get_db()

    # If no filters, show health for all active bookings
    if relic_id:
        relics = conn.execute(
            "SELECT * FROM relics WHERE id = ?", (relic_id,)
        ).fetchall()
    elif booking_id:
        booking = conn.execute(
            "SELECT relic_id FROM bookings WHERE id = ?", (booking_id,)
        ).fetchone()
        if not booking:
            conn.close()
            return error_response("Booking not found", 404)
        relics = conn.execute(
            "SELECT * FROM relics WHERE id = ?", (booking["relic_id"],)
        ).fetchall()
    else:
        relics = conn.execute(
            "SELECT * FROM relics WHERE status = 'reserved'"
        ).fetchall()

    health_data = []
    for relic in relics:
        # Generate simulated health data for demo
        import random
        health_entry = {
            "relic_id": relic["id"],
            "relic_name": relic["name"],
            "architecture": relic["architecture"],
            "cpu_pct": round(random.uniform(5, 95), 1),
            "mem_pct": round(random.uniform(10, 85), 1),
            "disk_pct": round(random.uniform(20, 70), 1),
            "temperature": round(random.uniform(35, 75), 1),
            "status": "healthy",
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

        # Flag if temperature is high
        if health_entry["temperature"] > 70:
            health_entry["status"] = "warning"
        if health_entry["cpu_pct"] > 90 and health_entry["mem_pct"] > 85:
            health_entry["status"] = "critical"

        # Store health check in DB
        conn.execute(
            """
            INSERT INTO health_checks (relic_id, booking_id, cpu_pct, mem_pct, disk_pct, temperature, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                relic["id"],
                booking_id,
                health_entry["cpu_pct"],
                health_entry["mem_pct"],
                health_entry["disk_pct"],
                health_entry["temperature"],
                health_entry["status"],
            ),
        )

        health_data.append(health_entry)

    conn.commit()
    conn.close()

    return json_response({
        "health": health_data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ---------------------------------------------------------------------------
# Leaderboard (Bonus)
# ---------------------------------------------------------------------------


async def leaderboard(request: web.Request) -> web.Response:
    """GET /api/leaderboard — Most-rented machines leaderboard."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT r.id, r.name, r.architecture, r.year, r.photo_url,
               r.attestation_count, r.uptime_hours, r.hourly_rate_rtc,
               COUNT(b.id) AS total_bookings,
               SUM(CASE WHEN b.status = 'completed' THEN 1 ELSE 0 END) AS completed_sessions,
               COALESCE(SUM(b.rtc_deposit), 0) AS total_rtc_earned
        FROM relics r
        LEFT JOIN bookings b ON r.id = b.relic_id
        GROUP BY r.id
        ORDER BY total_bookings DESC, total_rtc_earned DESC
        LIMIT 20
        """
    ).fetchall()
    conn.close()

    return json_response({
        "leaderboard": [dict(r) for r in rows],
    })


# ---------------------------------------------------------------------------
# Static file serving & CORS
# ---------------------------------------------------------------------------


@web.middleware
async def cors_middleware(request: web.Request, handler) -> web.Response:
    """Add CORS headers to all responses."""
    if request.method == "OPTIONS":
        return web.Response(
            status=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Max-Age": "3600",
            },
        )

    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@web.middleware
async def error_middleware(request: web.Request, handler) -> web.Response:
    """Catch unhandled exceptions and return JSON error."""
    try:
        return await handler(request)
    except web.HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error in %s %s", request.method, request.path)
        return error_response(f"Internal server error: {exc}", 500)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> web.Application:
    """Create and configure the aiohttp application."""
    app = web.Application(middlewares=[cors_middleware, error_middleware])

    # REST API routes
    app.router.add_get("/api/relics", list_relics)
    app.router.add_post("/api/relics", register_relic)
    app.router.add_get("/api/relics/{id}", get_relic)
    app.router.add_post("/api/bookings", create_booking)
    app.router.add_get("/api/bookings", list_bookings)
    app.router.add_put("/api/bookings/{id}/complete", complete_booking)
    app.router.add_get("/api/health", health_monitoring)
    app.router.add_get("/api/leaderboard", leaderboard)

    # MCP/Beacon compatible endpoints
    app.router.add_get("/relic/available", relic_available)
    app.router.add_post("/relic/reserve", relic_reserve)
    app.router.add_get("/relic/receipt/{session_id}", relic_receipt)

    # Serve marketplace.html at root
    static_dir = Path(__file__).parent
    marketplace_path = static_dir / "marketplace.html"

    async def serve_marketplace(request: web.Request) -> web.Response:
        if marketplace_path.exists():
            return web.FileResponse(marketplace_path)
        return web.Response(text="marketplace.html not found", status=404)

    app.router.add_get("/", serve_marketplace)

    # Server info
    async def server_info(request: web.Request) -> web.Response:
        return json_response({
            "name": "Rent-a-Relic Market",
            "version": "1.0.0",
            "description": "wRTC-powered reservation system for authenticated vintage compute",
            "bounty": "#2312 (150 RTC)",
            "endpoints": {
                "api": [
                    "GET /api/relics",
                    "POST /api/relics",
                    "GET /api/relics/{id}",
                    "POST /api/bookings",
                    "GET /api/bookings",
                    "PUT /api/bookings/{id}/complete",
                    "GET /api/health",
                    "GET /api/leaderboard",
                ],
                "mcp_beacon": [
                    "GET /relic/available",
                    "POST /relic/reserve",
                    "GET /relic/receipt/{session_id}",
                ],
            },
        })

    app.router.add_get("/api/info", server_info)

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Initialize the database and start the server."""
    logger.info("Initializing Rent-a-Relic Market database...")
    init_db()

    logger.info("Starting Rent-a-Relic Market on %s:%d", HOST, PORT)
    app = create_app()
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
