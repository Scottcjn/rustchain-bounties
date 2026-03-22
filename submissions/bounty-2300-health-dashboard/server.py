#!/usr/bin/env python3
"""RustChain Multi-Node Health Dashboard — Backend (Bounty #2300, 50 RTC)

Lightweight polling server that checks all 4 RustChain attestation nodes,
stores 24h history, and exposes a JSON API + optional RSS feed for incidents.

Author: ElromEvedElElyon
RTC Wallet: RTC_ElromEvedElElyon_2300
"""

import asyncio
import json
import time
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import aiohttp
    from aiohttp import web
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
    import aiohttp
    from aiohttp import web

DB_PATH = Path(__file__).parent / "health.db"
POLL_INTERVAL = 60  # seconds

NODES = [
    {"id": "node-1", "name": "LiquidWeb US-1", "endpoint": "https://50.28.86.131/health", "location": "LiquidWeb US", "lat": 42.96, "lon": -85.67},
    {"id": "node-2", "name": "LiquidWeb US-2", "endpoint": "https://50.28.86.153/health", "location": "LiquidWeb US", "lat": 42.96, "lon": -85.67},
    {"id": "node-3", "name": "Ryan's Proxmox",  "endpoint": "http://76.8.228.245:8099/health", "location": "US (Proxmox)", "lat": 37.77, "lon": -122.42},
    {"id": "node-4", "name": "Hong Kong",        "endpoint": "http://38.76.217.189:8099/health", "location": "Hong Kong", "lat": 22.32, "lon": 114.17},
]


def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""CREATE TABLE IF NOT EXISTS health_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        status TEXT NOT NULL,
        response_time_ms INTEGER,
        version TEXT,
        uptime INTEGER,
        active_miners INTEGER,
        current_epoch INTEGER,
        error TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT NOT NULL,
        started_at TEXT NOT NULL,
        resolved_at TEXT,
        duration_seconds INTEGER
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hc_node_ts ON health_checks(node_id, timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_inc_node ON incidents(node_id, started_at)")
    conn.commit()
    conn.close()


async def check_node(session, node):
    try:
        start = time.monotonic()
        async with session.get(node["endpoint"], timeout=aiohttp.ClientTimeout(total=10), ssl=False) as resp:
            elapsed = round((time.monotonic() - start) * 1000)
            if resp.status == 200:
                data = await resp.json()
                return {
                    "node_id": node["id"],
                    "status": "up",
                    "response_time_ms": elapsed,
                    "version": data.get("version", "unknown"),
                    "uptime": data.get("uptime", 0),
                    "active_miners": data.get("active_miners", data.get("miners", 0)),
                    "current_epoch": data.get("epoch", data.get("current_epoch", 0)),
                }
            return {"node_id": node["id"], "status": "degraded", "response_time_ms": elapsed, "error": f"HTTP {resp.status}"}
    except Exception as e:
        return {"node_id": node["id"], "status": "down", "response_time_ms": None, "error": str(e)[:200]}


def store_check(result):
    conn = sqlite3.connect(str(DB_PATH))
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO health_checks (node_id, timestamp, status, response_time_ms, version, uptime, active_miners, current_epoch, error) VALUES (?,?,?,?,?,?,?,?,?)",
        (result["node_id"], now, result["status"], result.get("response_time_ms"),
         result.get("version"), result.get("uptime"), result.get("active_miners"),
         result.get("current_epoch"), result.get("error")),
    )
    # Prune records older than 48h
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    conn.execute("DELETE FROM health_checks WHERE timestamp < ?", (cutoff,))
    conn.commit()
    conn.close()


def check_incidents(result):
    conn = sqlite3.connect(str(DB_PATH))
    now = datetime.now(timezone.utc).isoformat()
    node_id = result["node_id"]

    # Find open incident for this node
    row = conn.execute(
        "SELECT id FROM incidents WHERE node_id=? AND resolved_at IS NULL ORDER BY started_at DESC LIMIT 1",
        (node_id,)
    ).fetchone()

    if result["status"] == "down":
        if not row:
            conn.execute("INSERT INTO incidents (node_id, started_at) VALUES (?,?)", (node_id, now))
    else:
        if row:
            conn.execute(
                "UPDATE incidents SET resolved_at=?, duration_seconds=CAST((julianday(?)-julianday(started_at))*86400 AS INTEGER) WHERE id=?",
                (now, now, row[0])
            )
    conn.commit()
    conn.close()


LATEST_STATUS = {}

async def poll_loop():
    while True:
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(*[check_node(session, n) for n in NODES], return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    continue
                store_check(r)
                check_incidents(r)
                LATEST_STATUS[r["node_id"]] = r
        await asyncio.sleep(POLL_INTERVAL)


# --- HTTP API ---

async def handle_status(request):
    """Current status of all nodes."""
    nodes = []
    for n in NODES:
        s = LATEST_STATUS.get(n["id"], {"status": "unknown"})
        nodes.append({**n, **s})
    return web.json_response({"nodes": nodes, "timestamp": datetime.now(timezone.utc).isoformat()})


async def handle_history(request):
    """24h history for a specific node."""
    node_id = request.match_info["node_id"]
    hours = int(request.query.get("hours", 24))
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT timestamp, status, response_time_ms, active_miners, current_epoch FROM health_checks WHERE node_id=? AND timestamp>? ORDER BY timestamp",
        (node_id, cutoff)
    ).fetchall()
    conn.close()
    return web.json_response({
        "node_id": node_id,
        "history": [{"ts": r[0], "status": r[1], "latency": r[2], "miners": r[3], "epoch": r[4]} for r in rows]
    })


async def handle_incidents(request):
    """Recent incidents."""
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT node_id, started_at, resolved_at, duration_seconds FROM incidents ORDER BY started_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return web.json_response({
        "incidents": [{"node_id": r[0], "started_at": r[1], "resolved_at": r[2], "duration_s": r[3]} for r in rows]
    })


async def handle_rss(request):
    """RSS/Atom feed for incidents (bonus)."""
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT node_id, started_at, resolved_at, duration_seconds FROM incidents ORDER BY started_at DESC LIMIT 20"
    ).fetchall()
    conn.close()

    items = ""
    for r in rows:
        status = "Resolved" if r[2] else "ONGOING"
        items += f"""<item>
  <title>{r[0]} — {status}</title>
  <description>Node {r[0]} went down at {r[1]}. {f'Resolved at {r[2]} ({r[3]}s)' if r[2] else 'Still down.'}</description>
  <pubDate>{r[1]}</pubDate>
</item>\n"""

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>RustChain Node Health</title>
  <link>https://rustchain.org/status</link>
  <description>RustChain node incident feed</description>
  {items}
</channel>
</rss>"""
    return web.Response(text=rss, content_type="application/rss+xml")


async def handle_dashboard(request):
    """Serve the dashboard HTML."""
    html_path = Path(__file__).parent / "dashboard.html"
    return web.FileResponse(html_path)


async def start_background_tasks(app):
    app["poller"] = asyncio.create_task(poll_loop())


def create_app():
    app = web.Application()
    app.router.add_get("/", handle_dashboard)
    app.router.add_get("/api/status", handle_status)
    app.router.add_get("/api/history/{node_id}", handle_history)
    app.router.add_get("/api/incidents", handle_incidents)
    app.router.add_get("/rss", handle_rss)
    app.on_startup.append(start_background_tasks)
    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    print("RustChain Health Dashboard running on http://0.0.0.0:8080")
    web.run_app(app, host="0.0.0.0", port=8080)
