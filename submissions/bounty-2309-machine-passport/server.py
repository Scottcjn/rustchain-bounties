"""
Machine Passport Ledger — On-Chain Hardware Biographies
======================================================
REST API + Web Viewer for RustChain machine passports.
Every relic gets a documented biography: ROM hashes, repair history,
benchmark signatures, provenance, and attestation records.

Endpoints:
  GET  /passport/<machine_id>       - View passport (HTML)
  GET  /api/passports               - List all passports
  GET  /api/passports/<machine_id>  - Get passport JSON
  POST /api/passports               - Create new passport
  PUT  /api/passports/<machine_id>  - Update passport fields
  POST /api/passports/<machine_id>/repair - Add repair log entry
  GET  /api/passports/<machine_id>/pdf    - Download printable PDF
  GET  /api/passports/<machine_id>/qr     - Get QR code PNG
  GET  /api/passports/<machine_id>/hash   - Get ergo-anchored hash

Usage:
  pip install aiohttp aiosqlite qrcode[pil]
  python server.py [--port 8309]
"""

import asyncio
import hashlib
import io
import json
import os
import time
from datetime import datetime
from pathlib import Path

import aiohttp.web
import aiosqlite

DB_PATH = os.environ.get("PASSPORT_DB", "machine_passports.db")
PORT = int(os.environ.get("PORT", 8309))
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8309")

ARCHITECTURES = [
    "68k", "g3g4", "g5", "sparc", "mips", "power8", "apple", "x86",
    "arm", "risc-v", "alpha", "pa-risc", "itanium", "s390"
]


async def init_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row

    await db.execute("""
        CREATE TABLE IF NOT EXISTS passports (
            machine_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            manufacture_year INTEGER,
            architecture TEXT NOT NULL,
            photo_hash TEXT DEFAULT '',
            provenance TEXT DEFAULT '',
            benchmark_cache_timing TEXT DEFAULT '',
            benchmark_simd_identity TEXT DEFAULT '',
            benchmark_thermal_curve TEXT DEFAULT '',
            first_seen TEXT,
            last_seen TEXT,
            total_epochs INTEGER DEFAULT 0,
            total_rtc REAL DEFAULT 0.0,
            owner_wallet TEXT DEFAULT '',
            ergo_hash TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS repair_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL REFERENCES passports(machine_id),
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            technician TEXT DEFAULT '',
            parts_replaced TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)

    await db.execute("CREATE INDEX IF NOT EXISTS idx_repair_machine ON repair_logs(machine_id)")

    # Seed sample data
    cursor = await db.execute("SELECT COUNT(*) FROM passports")
    count = (await cursor.fetchone())[0]
    if count == 0:
        await seed_passports(db)

    await db.commit()
    return db


async def seed_passports(db):
    """Seed with sample machine passports."""
    machines = [
        {
            "machine_id": "fp_g4_001_a7c3e9",
            "name": "Old Faithful",
            "manufacture_year": 2001,
            "architecture": "g3g4",
            "provenance": "eBay lot, 2023. Came with original box and manuals.",
            "benchmark_cache_timing": "L1=64KB/2cy, L2=256KB/7cy, L3=2MB/14cy",
            "benchmark_simd_identity": "AltiVec 128-bit, 162 GFLOPS peak",
            "benchmark_thermal_curve": "idle=42C, load=68C, throttle=85C",
            "total_epochs": 147,
            "total_rtc": 342.8,
        },
        {
            "machine_id": "fp_g5_002_b8d4f1",
            "name": "The Cheese Grater",
            "manufacture_year": 2003,
            "architecture": "g5",
            "provenance": "Grandmother's closet. She used it for email until 2018.",
            "benchmark_cache_timing": "L1=32KB/1cy, L2=512KB/9cy",
            "benchmark_simd_identity": "AltiVec 128-bit, 256 GFLOPS dual-core",
            "benchmark_thermal_curve": "idle=51C, load=78C, throttle=90C",
            "total_epochs": 89,
            "total_rtc": 201.4,
        },
        {
            "machine_id": "fp_sparc_003_c9e5g2",
            "name": "Sun Warrior",
            "manufacture_year": 1998,
            "architecture": "sparc",
            "provenance": "Pawn shop in San Jose, CA. $35.",
            "benchmark_cache_timing": "L1=16KB/2cy, L2=1MB/12cy",
            "benchmark_simd_identity": "VIS 1.0, 64-bit SIMD",
            "benchmark_thermal_curve": "idle=38C, load=62C, throttle=80C",
            "total_epochs": 200,
            "total_rtc": 567.2,
        },
    ]

    repairs = [
        ("fp_g4_001_a7c3e9", "2024-03", "Replaced PRAM battery", "self", "CR2032 battery"),
        ("fp_g4_001_a7c3e9", "2024-08", "Recapped PSU — 4 bulging caps", "local shop", "4x 1000uF 16V Nichicon"),
        ("fp_g5_002_b8d4f1", "2025-01", "Thermal paste replacement", "self", "Arctic MX-4"),
        ("fp_sparc_003_c9e5g2", "2024-06", "Replaced NVRAM chip", "self", "M48T59Y-70PC1"),
    ]

    now = datetime.utcnow().isoformat()
    for m in machines:
        fp = m["machine_id"]
        await db.execute("""
            INSERT INTO passports
            (machine_id, name, manufacture_year, architecture, provenance,
             benchmark_cache_timing, benchmark_simd_identity, benchmark_thermal_curve,
             total_epochs, total_rtc, first_seen, last_seen, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fp, m["name"], m["manufacture_year"], m["architecture"],
              m["provenance"], m["benchmark_cache_timing"],
              m["benchmark_simd_identity"], m["benchmark_thermal_curve"],
              m["total_epochs"], m["total_rtc"],
              "2024-01-01T00:00:00", now, now, now))

    for machine_id, date, desc, tech, parts in repairs:
        await db.execute("""
            INSERT INTO repair_logs (machine_id, date, description, technician, parts_replaced, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (machine_id, date, desc, tech, parts, now))


def compute_ergo_hash(passport_data):
    """Compute ergo-anchored immutability hash for a passport."""
    canonical = json.dumps(passport_data, sort_keys=True, separators=(",", ":"))
    return "ergo_" + hashlib.sha256(canonical.encode()).hexdigest()[:32]


async def passport_to_dict(db, machine_id):
    """Load a full passport with repair logs."""
    cursor = await db.execute("SELECT * FROM passports WHERE machine_id = ?", (machine_id,))
    row = await cursor.fetchone()
    if not row:
        return None

    passport = dict(row)

    cursor = await db.execute(
        "SELECT date, description, technician, parts_replaced FROM repair_logs WHERE machine_id = ? ORDER BY date",
        (machine_id,)
    )
    passport["repair_log"] = [dict(r) for r in await cursor.fetchall()]
    passport["ergo_hash"] = compute_ergo_hash(passport)
    return passport


# ─── HTML Passport Viewer ───────────────────────────────────

PASSPORT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Machine Passport: {name}</title>
<style>
:root {{ --bg:#0d1117;--surface:#161b22;--border:#30363d;--text:#e6edf3;--dim:#8b949e;--accent:#58a6ff;--amber:#B8860B; }}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:var(--bg);color:var(--text);font-family:'Courier New',monospace;max-width:800px;margin:0 auto;padding:24px}}
.passport{{border:3px double var(--amber);padding:24px;background:var(--surface);border-radius:4px}}
.header{{text-align:center;border-bottom:2px solid var(--amber);padding-bottom:16px;margin-bottom:16px}}
.header h1{{font-size:24px;color:var(--amber);letter-spacing:2px}}
.header .subtitle{{color:var(--dim);font-size:12px;margin-top:4px}}
.field{{display:flex;margin:8px 0;gap:12px}}
.field-label{{color:var(--dim);min-width:160px;font-size:13px}}
.field-value{{color:var(--text);font-size:13px}}
.section-title{{color:var(--amber);font-size:14px;margin:20px 0 8px;border-bottom:1px solid var(--border);padding-bottom:4px}}
.repair-entry{{background:var(--bg);padding:8px 12px;margin:4px 0;border-left:3px solid var(--accent);font-size:12px}}
.repair-date{{color:var(--accent);font-weight:bold}}
.hash{{font-size:11px;color:var(--dim);word-break:break-all;margin-top:16px;text-align:center;padding:8px;border:1px dashed var(--border)}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:12px 0}}
.stat-box{{background:var(--bg);padding:12px;text-align:center;border:1px solid var(--border);border-radius:4px}}
.stat-box .val{{font-size:20px;font-weight:bold;color:var(--accent)}}
.stat-box .lbl{{font-size:11px;color:var(--dim);margin-top:4px}}
.qr{{text-align:center;margin:16px 0}}
.qr img{{border:2px solid var(--amber);padding:4px;background:white}}
</style>
</head>
<body>
<div class="passport">
<div class="header">
<h1>MACHINE PASSPORT</h1>
<div class="subtitle">RustChain Hardware Biography — Proof of Antiquity</div>
</div>

<div class="field"><span class="field-label">Machine ID</span><span class="field-value">{machine_id}</span></div>
<div class="field"><span class="field-label">Name</span><span class="field-value">{name}</span></div>
<div class="field"><span class="field-label">Architecture</span><span class="field-value">{architecture}</span></div>
<div class="field"><span class="field-label">Manufacture Year</span><span class="field-value">{manufacture_year}</span></div>
<div class="field"><span class="field-label">Provenance</span><span class="field-value">{provenance}</span></div>

<div class="stats">
<div class="stat-box"><div class="val">{total_epochs}</div><div class="lbl">Epochs Served</div></div>
<div class="stat-box"><div class="val">{total_rtc:.2f}</div><div class="lbl">RTC Earned</div></div>
<div class="stat-box"><div class="val">{age} yrs</div><div class="lbl">Machine Age</div></div>
</div>

<div class="section-title">Benchmark Signatures</div>
<div class="field"><span class="field-label">Cache Timing</span><span class="field-value">{benchmark_cache_timing}</span></div>
<div class="field"><span class="field-label">SIMD Identity</span><span class="field-value">{benchmark_simd_identity}</span></div>
<div class="field"><span class="field-label">Thermal Curve</span><span class="field-value">{benchmark_thermal_curve}</span></div>

<div class="section-title">Repair Log</div>
{repair_log_html}

<div class="qr">
<img src="/api/passports/{machine_id}/qr" alt="QR Code" width="150">
</div>

<div class="hash">Ergo Hash: {ergo_hash}</div>
</div>
</body>
</html>"""


# ─── Handlers ───────────────────────────────────────────────

async def handle_passport_view(request):
    """Render passport as HTML page."""
    machine_id = request.match_info["machine_id"]
    db = request.app["db"]
    passport = await passport_to_dict(db, machine_id)
    if not passport:
        return aiohttp.web.Response(status=404, text="Machine not found")

    repair_html = ""
    for entry in passport.get("repair_log", []):
        repair_html += f'<div class="repair-entry"><span class="repair-date">{entry["date"]}</span> — {entry["description"]}'
        if entry.get("parts_replaced"):
            repair_html += f' (Parts: {entry["parts_replaced"]})'
        repair_html += "</div>\n"

    if not repair_html:
        repair_html = '<div style="color:var(--dim);font-size:12px;padding:8px">No repairs recorded.</div>'

    age = datetime.utcnow().year - (passport.get("manufacture_year") or 2000)

    html = PASSPORT_HTML_TEMPLATE.format(
        **passport,
        age=age,
        repair_log_html=repair_html,
    )
    return aiohttp.web.Response(text=html, content_type="text/html")


async def handle_list_passports(request):
    db = request.app["db"]
    cursor = await db.execute("SELECT machine_id, name, architecture, manufacture_year, total_epochs, total_rtc FROM passports ORDER BY created_at")
    rows = await cursor.fetchall()
    return aiohttp.web.json_response([dict(r) for r in rows])


async def handle_get_passport(request):
    machine_id = request.match_info["machine_id"]
    db = request.app["db"]
    passport = await passport_to_dict(db, machine_id)
    if not passport:
        return aiohttp.web.json_response({"error": "not found"}, status=404)
    return aiohttp.web.json_response(passport)


async def handle_create_passport(request):
    db = request.app["db"]
    data = await request.json()

    required = ["machine_id", "name", "architecture"]
    for field in required:
        if field not in data:
            return aiohttp.web.json_response({"error": f"missing {field}"}, status=400)

    if data["architecture"] not in ARCHITECTURES:
        return aiohttp.web.json_response({"error": f"unknown architecture: {data['architecture']}"}, status=400)

    now = datetime.utcnow().isoformat()
    await db.execute("""
        INSERT INTO passports
        (machine_id, name, manufacture_year, architecture, photo_hash, provenance,
         benchmark_cache_timing, benchmark_simd_identity, benchmark_thermal_curve,
         owner_wallet, first_seen, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["machine_id"], data["name"], data.get("manufacture_year"),
        data["architecture"], data.get("photo_hash", ""),
        data.get("provenance", ""),
        data.get("benchmark_cache_timing", ""),
        data.get("benchmark_simd_identity", ""),
        data.get("benchmark_thermal_curve", ""),
        data.get("owner_wallet", ""),
        now, now, now
    ))
    await db.commit()
    return aiohttp.web.json_response({"status": "created", "machine_id": data["machine_id"]}, status=201)


async def handle_update_passport(request):
    machine_id = request.match_info["machine_id"]
    db = request.app["db"]
    data = await request.json()

    updatable = [
        "name", "manufacture_year", "architecture", "photo_hash", "provenance",
        "benchmark_cache_timing", "benchmark_simd_identity", "benchmark_thermal_curve",
        "owner_wallet", "total_epochs", "total_rtc", "last_seen"
    ]

    sets = []
    values = []
    for field in updatable:
        if field in data:
            sets.append(f"{field} = ?")
            values.append(data[field])

    if not sets:
        return aiohttp.web.json_response({"error": "no updatable fields"}, status=400)

    sets.append("updated_at = ?")
    values.append(datetime.utcnow().isoformat())
    values.append(machine_id)

    await db.execute(f"UPDATE passports SET {', '.join(sets)} WHERE machine_id = ?", values)
    await db.commit()
    return aiohttp.web.json_response({"status": "updated"})


async def handle_add_repair(request):
    machine_id = request.match_info["machine_id"]
    db = request.app["db"]
    data = await request.json()

    if "description" not in data:
        return aiohttp.web.json_response({"error": "missing description"}, status=400)

    now = datetime.utcnow().isoformat()
    await db.execute("""
        INSERT INTO repair_logs (machine_id, date, description, technician, parts_replaced, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        machine_id,
        data.get("date", datetime.utcnow().strftime("%Y-%m")),
        data["description"],
        data.get("technician", ""),
        data.get("parts_replaced", ""),
        now
    ))
    await db.commit()
    return aiohttp.web.json_response({"status": "repair logged"}, status=201)


async def handle_passport_hash(request):
    machine_id = request.match_info["machine_id"]
    db = request.app["db"]
    passport = await passport_to_dict(db, machine_id)
    if not passport:
        return aiohttp.web.json_response({"error": "not found"}, status=404)
    return aiohttp.web.json_response({"machine_id": machine_id, "ergo_hash": passport["ergo_hash"]})


async def handle_passport_qr(request):
    machine_id = request.match_info["machine_id"]
    try:
        import qrcode
        url = f"{BASE_URL}/passport/{machine_id}"
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return aiohttp.web.Response(body=buf.read(), content_type="image/png")
    except ImportError:
        # Fallback: return a simple SVG QR placeholder
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150">
        <rect width="150" height="150" fill="white"/>
        <text x="75" y="75" text-anchor="middle" font-size="10" fill="black">QR: {machine_id[:16]}</text>
        </svg>"""
        return aiohttp.web.Response(text=svg, content_type="image/svg+xml")


async def handle_passport_pdf(request):
    """Generate a printable PDF passport (vintage computer aesthetic)."""
    machine_id = request.match_info["machine_id"]
    db = request.app["db"]
    passport = await passport_to_dict(db, machine_id)
    if not passport:
        return aiohttp.web.json_response({"error": "not found"}, status=404)

    # Generate a text-based PDF alternative (HTML for printing)
    age = datetime.utcnow().year - (passport.get("manufacture_year") or 2000)
    repair_text = "\n".join(
        f"  [{r['date']}] {r['description']}" + (f" (Parts: {r['parts_replaced']})" if r.get("parts_replaced") else "")
        for r in passport.get("repair_log", [])
    ) or "  No repairs recorded."

    pdf_html = f"""<!DOCTYPE html>
<html><head><title>Machine Passport: {passport['name']}</title>
<style>
@media print {{ body {{ margin: 0; }} }}
body {{ font-family: 'Courier New', monospace; max-width: 700px; margin: 40px auto; padding: 20px; border: 3px double #B8860B; }}
h1 {{ text-align: center; border-bottom: 2px solid #B8860B; padding-bottom: 10px; color: #B8860B; letter-spacing: 3px; }}
.field {{ margin: 6px 0; }} .label {{ font-weight: bold; color: #666; }}
.stats {{ display: flex; justify-content: space-around; margin: 20px 0; padding: 10px; border: 1px solid #ccc; }}
.stat {{ text-align: center; }} .stat .val {{ font-size: 24px; font-weight: bold; }} .stat .lbl {{ font-size: 11px; color: #666; }}
.section {{ margin-top: 16px; border-top: 1px solid #ccc; padding-top: 8px; }} .section h2 {{ font-size: 14px; color: #B8860B; }}
.hash {{ font-size: 10px; color: #999; text-align: center; margin-top: 20px; border: 1px dashed #ccc; padding: 8px; }}
.qr {{ text-align: center; margin: 16px 0; }}
</style></head><body>
<h1>MACHINE PASSPORT</h1>
<p style="text-align:center;color:#666;font-size:11px">RustChain Proof of Antiquity — Hardware Biography</p>
<div class="field"><span class="label">Machine ID:</span> {passport['machine_id']}</div>
<div class="field"><span class="label">Name:</span> {passport['name']}</div>
<div class="field"><span class="label">Architecture:</span> {passport['architecture']}</div>
<div class="field"><span class="label">Year:</span> {passport.get('manufacture_year', 'Unknown')}</div>
<div class="field"><span class="label">Provenance:</span> {passport.get('provenance', 'Unknown')}</div>
<div class="stats">
<div class="stat"><div class="val">{passport.get('total_epochs', 0)}</div><div class="lbl">Epochs</div></div>
<div class="stat"><div class="val">{passport.get('total_rtc', 0):.2f}</div><div class="lbl">RTC Earned</div></div>
<div class="stat"><div class="val">{age}</div><div class="lbl">Years Old</div></div>
</div>
<div class="section"><h2>Benchmarks</h2>
<div class="field"><span class="label">Cache:</span> {passport.get('benchmark_cache_timing', 'N/A')}</div>
<div class="field"><span class="label">SIMD:</span> {passport.get('benchmark_simd_identity', 'N/A')}</div>
<div class="field"><span class="label">Thermal:</span> {passport.get('benchmark_thermal_curve', 'N/A')}</div></div>
<div class="section"><h2>Repair Log</h2><pre>{repair_text}</pre></div>
<div class="qr"><img src="/api/passports/{machine_id}/qr" width="120" alt="QR"></div>
<div class="hash">Ergo Hash: {passport['ergo_hash']}</div>
</body></html>"""

    return aiohttp.web.Response(text=pdf_html, content_type="text/html",
                                 headers={"Content-Disposition": f'inline; filename="passport-{machine_id}.html"'})


# ─── App Setup ──────────────────────────────────────────────

async def on_startup(app):
    app["db"] = await init_db()
    print(f"Machine Passport Ledger running on port {PORT}")


async def on_cleanup(app):
    await app["db"].close()


def create_app():
    app = aiohttp.web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    # HTML views
    app.router.add_get("/passport/{machine_id}", handle_passport_view)

    # REST API
    app.router.add_get("/api/passports", handle_list_passports)
    app.router.add_get("/api/passports/{machine_id}", handle_get_passport)
    app.router.add_post("/api/passports", handle_create_passport)
    app.router.add_put("/api/passports/{machine_id}", handle_update_passport)
    app.router.add_post("/api/passports/{machine_id}/repair", handle_add_repair)
    app.router.add_get("/api/passports/{machine_id}/hash", handle_passport_hash)
    app.router.add_get("/api/passports/{machine_id}/qr", handle_passport_qr)
    app.router.add_get("/api/passports/{machine_id}/pdf", handle_passport_pdf)

    # CORS
    async def cors_middleware(app, handler):
        async def middleware(request):
            resp = await handler(request)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
            return resp
        return middleware

    app.middlewares.append(cors_middleware)
    return app


if __name__ == "__main__":
    app = create_app()
    aiohttp.web.run_app(app, port=PORT)
