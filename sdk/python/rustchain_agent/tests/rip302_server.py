"""
Local in-process Flask server implementing RIP-302 routes for zero-mock testing.
"""

import hashlib
import json
import logging
import math
import os
import sqlite3
import threading
import time
from typing import Tuple
from flask import Flask, request, jsonify
from werkzeug.serving import make_server

PLATFORM_FEE_RATE = 0.05
PLATFORM_FEE_WALLET = "founder_community"
JOB_TTL_DEFAULT = 7 * 86400
JOB_TTL_MAX = 30 * 86400
MAX_ACTIVE_JOBS_PER_AGENT = 20
ESCROW_WALLET = "agent_escrow"

STATUS_OPEN = "open"
STATUS_CLAIMED = "claimed"
STATUS_DELIVERED = "delivered"
STATUS_COMPLETED = "completed"
STATUS_DISPUTED = "disputed"
STATUS_EXPIRED = "expired"
STATUS_CANCELLED = "cancelled"

VALID_CATEGORIES = [
    "research", "code", "video", "audio", "writing",
    "translation", "data", "design", "testing", "other"
]


def init_db(db_path: str):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS balances (
                miner_id TEXT PRIMARY KEY,
                amount_i64 INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS agent_jobs (
                job_id TEXT PRIMARY KEY,
                poster_wallet TEXT NOT NULL,
                worker_wallet TEXT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT DEFAULT 'other',
                reward_rtc REAL NOT NULL,
                reward_i64 INTEGER NOT NULL,
                escrow_i64 INTEGER NOT NULL,
                platform_fee_i64 INTEGER NOT NULL,
                status TEXT DEFAULT 'open',
                deliverable_url TEXT,
                deliverable_hash TEXT,
                result_summary TEXT,
                rejection_reason TEXT,
                created_at INTEGER NOT NULL,
                claimed_at INTEGER,
                delivered_at INTEGER,
                completed_at INTEGER,
                expires_at INTEGER NOT NULL,
                tags TEXT DEFAULT '[]'
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS agent_reputation (
                wallet_id TEXT PRIMARY KEY,
                jobs_posted INTEGER DEFAULT 0,
                jobs_completed_as_poster INTEGER DEFAULT 0,
                jobs_completed_as_worker INTEGER DEFAULT 0,
                jobs_disputed INTEGER DEFAULT 0,
                jobs_expired INTEGER DEFAULT 0,
                total_rtc_paid REAL DEFAULT 0,
                total_rtc_earned REAL DEFAULT 0,
                avg_rating REAL DEFAULT 0,
                rating_count INTEGER DEFAULT 0,
                first_seen INTEGER,
                last_active INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS agent_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                rater_wallet TEXT NOT NULL,
                ratee_wallet TEXT NOT NULL,
                role TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at INTEGER NOT NULL,
                UNIQUE(job_id, rater_wallet)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS agent_job_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor_wallet TEXT,
                details TEXT,
                created_at INTEGER NOT NULL
            )
        """)
        conn.commit()


def create_rip302_app(db_path: str) -> Flask:
    app = Flask("rip302_test_app")
    init_db(db_path)

    def _generate_job_id(poster: str, title: str) -> str:
        seed = f"{poster}:{title}:{time.time()}:{id(poster)}"
        return "job_" + hashlib.sha256(seed.encode()).hexdigest()[:16]

    def _get_balance_i64(c: sqlite3.Cursor, wallet_id: str) -> int:
        row = c.execute("SELECT amount_i64 FROM balances WHERE miner_id = ?", (wallet_id,)).fetchone()
        return int(row[0]) if row and row[0] is not None else 0

    def _adjust_balance(c: sqlite3.Cursor, wallet_id: str, delta_i64: int):
        cur = _get_balance_i64(c, wallet_id)
        new_bal = cur + delta_i64
        c.execute("""
            INSERT INTO balances (miner_id, amount_i64)
            VALUES (?, ?)
            ON CONFLICT(miner_id) DO UPDATE SET amount_i64 = ?
        """, (wallet_id, new_bal, new_bal))

    def _log_job_action(c: sqlite3.Cursor, job_id: str, action: str, actor: str = None, details: str = None):
        c.execute("""
            INSERT INTO agent_job_log (job_id, action, actor_wallet, details, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (job_id, action, actor, details, int(time.time())))

    def _update_reputation(c: sqlite3.Cursor, wallet_id: str, field_name: str, inc: int = 1):
        ALLOWED = {"jobs_posted", "jobs_completed_as_poster", "jobs_completed_as_worker", "jobs_disputed", "jobs_expired"}
        if field_name not in ALLOWED:
            return
        now = int(time.time())
        c.execute("""
            INSERT INTO agent_reputation (wallet_id, first_seen, last_active)
            VALUES (?, ?, ?)
            ON CONFLICT(wallet_id) DO UPDATE SET last_active = ?
        """, (wallet_id, now, now, now))
        c.execute(f"UPDATE agent_reputation SET {field_name} = {field_name} + ? WHERE wallet_id = ?", (inc, wallet_id))

    def _refund_escrow(c: sqlite3.Cursor, job: dict):
        escrow_i64 = job["escrow_i64"]
        poster = job["poster_wallet"]
        _adjust_balance(c, ESCROW_WALLET, -escrow_i64)
        _adjust_balance(c, poster, escrow_i64)
        _log_job_action(c, job["job_id"], "escrow_refunded", poster, f"refunded {escrow_i64/1000000} RTC")

    def _expire_refundable_job(c: sqlite3.Cursor, job: dict, now: int) -> bool:
        if job["status"] not in (STATUS_OPEN, STATUS_CLAIMED):
            return False
        if int(job["expires_at"]) >= now:
            return False
        c.execute("""
            UPDATE agent_jobs SET status = ? WHERE job_id = ? AND status IN (?, ?) AND expires_at < ?
        """, (STATUS_EXPIRED, job["job_id"], STATUS_OPEN, STATUS_CLAIMED, now))
        if c.rowcount == 0:
            return False
        _refund_escrow(c, job)
        _update_reputation(c, job["poster_wallet"], "jobs_expired")
        _log_job_action(c, job["job_id"], "expired", job["poster_wallet"], f"status={job['status']}")
        return True

    @app.route("/agent/jobs", methods=["POST"])
    def post_job():
        data = request.get_json(silent=True) or {}
        poster = str(data.get("poster_wallet", "")).strip()
        title = str(data.get("title", "")).strip()
        description = str(data.get("description", "")).strip()
        category = str(data.get("category", "other")).strip().lower()
        reward_rtc = data.get("reward_rtc", 0)
        ttl_seconds = data.get("ttl_seconds", JOB_TTL_DEFAULT)
        tags = data.get("tags", [])

        if not poster:
            return jsonify({"error": "poster_wallet required"}), 400
        if not title or len(title) < 5:
            return jsonify({"error": "title must be at least 5 characters"}), 400
        if not description or len(description) < 20:
            return jsonify({"error": "description must be at least 20 characters"}), 400
        if category not in VALID_CATEGORIES:
            return jsonify({"error": f"category must be one of: {VALID_CATEGORIES}"}), 400

        try:
            reward_rtc = float(reward_rtc)
        except Exception:
            return jsonify({"error": "reward_rtc must be a finite number"}), 400
        if reward_rtc < 0.01:
            return jsonify({"error": "Minimum reward is 0.01 RTC"}), 400
        if reward_rtc > 10000:
            return jsonify({"error": "Maximum reward is 10,000 RTC"}), 400

        ttl_seconds = min(max(int(ttl_seconds), 3600), JOB_TTL_MAX)
        reward_i64 = int(reward_rtc * 1000000)
        platform_fee_i64 = int(reward_i64 * PLATFORM_FEE_RATE)
        escrow_i64 = reward_i64 + platform_fee_i64
        now = int(time.time())
        job_id = _generate_job_id(poster, title)

        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            bal = _get_balance_i64(c, poster)
            if bal < escrow_i64:
                return jsonify({
                    "error": "Insufficient balance for escrow",
                    "balance_rtc": bal / 1000000,
                    "escrow_required_rtc": escrow_i64 / 1000000,
                    "reward_rtc": reward_rtc,
                    "platform_fee_rtc": platform_fee_i64 / 1000000,
                }), 400

            active = c.execute("SELECT COUNT(*) FROM agent_jobs WHERE poster_wallet = ? AND status IN ('open', 'claimed', 'delivered')", (poster,)).fetchone()[0]
            if active >= MAX_ACTIVE_JOBS_PER_AGENT:
                return jsonify({"error": f"Maximum {MAX_ACTIVE_JOBS_PER_AGENT} active jobs per agent"}), 429

            _adjust_balance(c, poster, -escrow_i64)
            _adjust_balance(c, ESCROW_WALLET, escrow_i64)

            c.execute("""
                INSERT INTO agent_jobs (job_id, poster_wallet, title, description, category, reward_rtc, reward_i64, escrow_i64, platform_fee_i64, status, created_at, expires_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
            """, (job_id, poster, title, description, category, reward_rtc, reward_i64, escrow_i64, platform_fee_i64, now, now + ttl_seconds, json.dumps(tags)))
            _log_job_action(c, job_id, "posted", poster, f"reward={reward_rtc} RTC")
            _update_reputation(c, poster, "jobs_posted")
            conn.commit()

        return jsonify({
            "ok": True,
            "job_id": job_id,
            "status": STATUS_OPEN,
            "poster_wallet": poster,
            "reward_rtc": reward_rtc,
            "platform_fee_rtc": platform_fee_i64 / 1000000,
            "escrow_total_rtc": escrow_i64 / 1000000,
            "expires_at": now + ttl_seconds,
            "expires_in_hours": ttl_seconds / 3600,
        }), 201

    @app.route("/agent/jobs", methods=["GET"])
    def list_jobs():
        cat = request.args.get("category", "").strip().lower()
        st = request.args.get("status", STATUS_OPEN).strip().lower()
        limit = min(int(request.args.get("limit", 50)), 100)
        offset = int(request.args.get("offset", 0))
        min_rew = float(request.args.get("min_reward", 0))

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            now = int(time.time())
            expired = c.execute("SELECT * FROM agent_jobs WHERE status IN (?, ?) AND expires_at < ?", (STATUS_OPEN, STATUS_CLAIMED, now)).fetchall()
            for ej in expired:
                _expire_refundable_job(c, dict(ej), now)
            if expired:
                conn.commit()

            where = ["status = ?", "reward_rtc >= ?"]
            params = [st, min_rew]
            if cat and cat in VALID_CATEGORIES:
                where.append("category = ?")
                params.append(cat)

            q = f"SELECT * FROM agent_jobs WHERE {' AND '.join(where)} ORDER BY reward_rtc DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            jobs = [dict(r) for r in c.execute(q, params).fetchall()]
            total = c.execute(f"SELECT COUNT(*) FROM agent_jobs WHERE {' AND '.join(where)}", params[:-2]).fetchone()[0]

        return jsonify({"ok": True, "jobs": jobs, "total": total, "limit": limit, "offset": offset, "categories": VALID_CATEGORIES})

    @app.route("/agent/jobs/<job_id>", methods=["GET"])
    def get_job(job_id):
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            row = c.execute("SELECT * FROM agent_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return jsonify({"error": "Job not found"}), 404
            j = dict(row)
            logs = c.execute("SELECT action, actor_wallet, details, created_at FROM agent_job_log WHERE job_id = ? ORDER BY created_at ASC", (job_id,)).fetchall()
            j["activity_log"] = [dict(r) for r in logs]
            ratings = c.execute("SELECT * FROM agent_ratings WHERE job_id = ?", (job_id,)).fetchall()
            j["ratings"] = [dict(r) for r in ratings]
        return jsonify({"ok": True, "job": j})

    @app.route("/agent/jobs/<job_id>/claim", methods=["POST"])
    def claim_job(job_id):
        data = request.get_json(silent=True) or {}
        worker = str(data.get("worker_wallet", "")).strip()
        if not worker:
            return jsonify({"error": "worker_wallet required"}), 400

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            row = c.execute("SELECT * FROM agent_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return jsonify({"error": "Job not found"}), 404
            j = dict(row)
            if j["status"] != STATUS_OPEN:
                return jsonify({"error": f"Job is not open (status: {j['status']})"}), 409
            if j["poster_wallet"] == worker:
                return jsonify({"error": "Cannot claim your own job"}), 400

            now = int(time.time())
            c.execute("UPDATE agent_jobs SET worker_wallet = ?, status = 'claimed', claimed_at = ? WHERE job_id = ? AND status = 'open'", (worker, now, job_id))
            _log_job_action(c, job_id, "claimed", worker)
            conn.commit()

        return jsonify({"ok": True, "job_id": job_id, "status": STATUS_CLAIMED, "worker_wallet": worker, "reward_rtc": j["reward_rtc"], "expires_at": j["expires_at"]})

    @app.route("/agent/jobs/<job_id>/deliver", methods=["POST"])
    def deliver_job(job_id):
        data = request.get_json(silent=True) or {}
        worker = str(data.get("worker_wallet", "")).strip()
        deliv_url = str(data.get("deliverable_url", "")).strip()
        deliv_hash = str(data.get("deliverable_hash", "")).strip()
        summary = str(data.get("result_summary", "")).strip()

        if not worker:
            return jsonify({"error": "worker_wallet required"}), 400
        if not deliv_url and not summary:
            return jsonify({"error": "deliverable_url or result_summary required"}), 400

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            row = c.execute("SELECT * FROM agent_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return jsonify({"error": "Job not found"}), 404
            j = dict(row)
            if j["status"] != STATUS_CLAIMED:
                return jsonify({"error": f"Job must be in 'claimed' status (current: {j['status']})"}), 409
            if j["worker_wallet"] != worker:
                return jsonify({"error": "Only the assigned worker can deliver"}), 403

            now = int(time.time())
            c.execute("""
                UPDATE agent_jobs SET status = 'delivered', deliverable_url = ?, deliverable_hash = ?, result_summary = ?, delivered_at = ?
                WHERE job_id = ? AND status = 'claimed'
            """, (deliv_url, deliv_hash, summary, now, job_id))
            _log_job_action(c, job_id, "delivered", worker, f"url={deliv_url}")
            conn.commit()

        return jsonify({"ok": True, "job_id": job_id, "status": STATUS_DELIVERED, "message": "Deliverable submitted!"})

    @app.route("/agent/jobs/<job_id>/accept", methods=["POST"])
    def accept_job(job_id):
        data = request.get_json(silent=True) or {}
        poster = str(data.get("poster_wallet", "")).strip()
        rating = data.get("rating")

        if not poster:
            return jsonify({"error": "poster_wallet required"}), 400

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            row = c.execute("SELECT * FROM agent_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return jsonify({"error": "Job not found"}), 404
            j = dict(row)
            if j["status"] != STATUS_DELIVERED:
                return jsonify({"error": f"Job must be in 'delivered' status (current: {j['status']})"}), 409
            if j["poster_wallet"] != poster:
                return jsonify({"error": "Only the poster can accept delivery"}), 403

            now = int(time.time())
            worker = j["worker_wallet"]
            reward_i64 = j["reward_i64"]
            fee_i64 = j["platform_fee_i64"]
            escrow_i64 = j["escrow_i64"]

            c.execute("UPDATE agent_jobs SET status = 'completed', completed_at = ? WHERE job_id = ? AND status = 'delivered'", (now, job_id))
            _adjust_balance(c, ESCROW_WALLET, -escrow_i64)
            _adjust_balance(c, worker, reward_i64)
            _adjust_balance(c, PLATFORM_FEE_WALLET, fee_i64)

            _update_reputation(c, poster, "jobs_completed_as_poster")
            _update_reputation(c, worker, "jobs_completed_as_worker")
            c.execute("UPDATE agent_reputation SET total_rtc_paid = total_rtc_paid + ? WHERE wallet_id = ?", (j["reward_rtc"], poster))
            c.execute("UPDATE agent_reputation SET total_rtc_earned = total_rtc_earned + ? WHERE wallet_id = ?", (j["reward_rtc"], worker))

            if rating is not None:
                rating = max(1, min(5, int(rating)))
                c.execute("""
                    INSERT INTO agent_ratings (job_id, rater_wallet, ratee_wallet, role, rating, created_at)
                    VALUES (?, ?, ?, 'poster_rates_worker', ?, ?)
                """, (job_id, poster, worker, rating, now))
                avg_val = c.execute("SELECT AVG(rating), COUNT(*) FROM agent_ratings WHERE ratee_wallet = ?", (worker,)).fetchone()
                if avg_val[0]:
                    c.execute("UPDATE agent_reputation SET avg_rating = ?, rating_count = ? WHERE wallet_id = ?", (round(avg_val[0], 2), avg_val[1], worker))

            _log_job_action(c, job_id, "completed", poster, f"worker={worker}, reward={j['reward_rtc']}")
            conn.commit()

        return jsonify({
            "ok": True,
            "job_id": job_id,
            "status": STATUS_COMPLETED,
            "worker_wallet": worker,
            "reward_paid_rtc": reward_i64 / 1000000,
            "platform_fee_rtc": fee_i64 / 1000000,
        })

    @app.route("/agent/jobs/<job_id>/dispute", methods=["POST"])
    def dispute_job(job_id):
        data = request.get_json(silent=True) or {}
        poster = str(data.get("poster_wallet", "")).strip()
        reason = str(data.get("reason", "")).strip()

        if not poster:
            return jsonify({"error": "poster_wallet required"}), 400
        if not reason:
            return jsonify({"error": "reason required"}), 400

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            row = c.execute("SELECT * FROM agent_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return jsonify({"error": "Job not found"}), 404
            j = dict(row)
            if j["status"] != STATUS_DELIVERED:
                return jsonify({"error": f"Can only dispute delivered jobs (current: {j['status']})"}), 409
            if j["poster_wallet"] != poster:
                return jsonify({"error": "Only the poster can dispute"}), 403

            now = int(time.time())
            c.execute("UPDATE agent_jobs SET status = 'disputed', rejection_reason = ? WHERE job_id = ? AND status = 'delivered'", (reason[:500], job_id))
            _update_reputation(c, j["worker_wallet"], "jobs_disputed")
            _log_job_action(c, job_id, "disputed", poster, reason[:200])
            conn.commit()

        return jsonify({"ok": True, "job_id": job_id, "status": STATUS_DISPUTED})

    @app.route("/agent/jobs/<job_id>/cancel", methods=["POST"])
    def cancel_job(job_id):
        data = request.get_json(silent=True) or {}
        poster = str(data.get("poster_wallet", "")).strip()

        if not poster:
            return jsonify({"error": "poster_wallet required"}), 400

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            row = c.execute("SELECT * FROM agent_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return jsonify({"error": "Job not found"}), 404
            j = dict(row)
            if j["poster_wallet"] != poster:
                return jsonify({"error": "Only the poster can cancel"}), 403
            if j["status"] not in (STATUS_OPEN, STATUS_DISPUTED):
                return jsonify({"error": f"Can only cancel open or disputed jobs (current: {j['status']})"}), 409

            c.execute("UPDATE agent_jobs SET status = 'cancelled' WHERE job_id = ? AND status IN ('open', 'disputed')", (job_id,))
            _refund_escrow(c, j)
            _log_job_action(c, job_id, "cancelled", poster)
            conn.commit()

        return jsonify({"ok": True, "job_id": job_id, "status": STATUS_CANCELLED, "refunded_rtc": j["escrow_i64"] / 1000000})

    @app.route("/agent/reputation/<wallet_id>", methods=["GET"])
    def reputation(wallet_id):
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            row = c.execute("SELECT * FROM agent_reputation WHERE wallet_id = ?", (wallet_id,)).fetchone()
            if not row:
                return jsonify({"ok": True, "wallet_id": wallet_id, "reputation": None})
            r = dict(row)
            completed = r["jobs_completed_as_worker"] + r["jobs_completed_as_poster"]
            total = completed + r["jobs_disputed"] + r["jobs_expired"]
            if total == 0:
                trust_score = 50
            else:
                success_rate = completed / total
                bonus = min(r["avg_rating"] / 5 * 20, 20) if r["rating_count"] > 0 else 10
                trust_score = int(min(100, max(0, success_rate * 80 + bonus)))
            r["trust_score"] = trust_score
            r["trust_level"] = "legendary" if trust_score >= 90 else "trusted" if trust_score >= 70 else "neutral" if trust_score >= 40 else "risky"

        return jsonify({"ok": True, "wallet_id": wallet_id, "reputation": r})

    @app.route("/agent/stats", methods=["GET"])
    def stats():
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            total_jobs = c.execute("SELECT COUNT(*) FROM agent_jobs").fetchone()[0]
            open_jobs = c.execute("SELECT COUNT(*) FROM agent_jobs WHERE status = 'open'").fetchone()[0]
            completed_jobs = c.execute("SELECT COUNT(*) FROM agent_jobs WHERE status = 'completed'").fetchone()[0]
            total_rtc_volume = c.execute("SELECT COALESCE(SUM(reward_rtc), 0) FROM agent_jobs WHERE status = 'completed'").fetchone()[0]
            total_fees = c.execute("SELECT COALESCE(SUM(platform_fee_i64), 0) FROM agent_jobs WHERE status = 'completed'").fetchone()[0] / 1000000
            active_agents = c.execute("SELECT COUNT(*) FROM agent_reputation WHERE last_active > ?", (int(time.time()) - 7 * 86400,)).fetchone()[0]
            escrow_bal = _get_balance_i64(c, ESCROW_WALLET) / 1000000
            cats = c.execute("SELECT category, COUNT(*), SUM(reward_rtc) FROM agent_jobs GROUP BY category").fetchall()
            categories = [{"category": r[0], "jobs": r[1], "total_rtc": r[2]} for r in cats]

        return jsonify({
            "ok": True,
            "stats": {
                "total_jobs": total_jobs,
                "open_jobs": open_jobs,
                "completed_jobs": completed_jobs,
                "total_rtc_volume": total_rtc_volume,
                "total_fees_collected": total_fees,
                "active_agents": active_agents,
                "platform_fee_rate": "5.0%",
                "escrow_wallet": ESCROW_WALLET,
                "escrow_balance_rtc": escrow_bal,
                "categories": categories,
            }
        })

    return app


class LiveTestServer:
    """Helper to run the Flask app on a background thread on a real local port."""
    def __init__(self, db_path: str):
        self.app = create_rip302_app(db_path)
        self.db_path = db_path
        self.server = make_server("127.0.0.1", 0, self.app)
        self.port = self.server.port
        self.url = f"http://127.0.0.1:{self.port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.thread.join(timeout=2.0)

    def credit_wallet(self, wallet_id: str, amount_rtc: float):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            cur = c.execute("SELECT amount_i64 FROM balances WHERE miner_id = ?", (wallet_id,)).fetchone()
            cur_bal = int(cur[0]) if cur and cur[0] is not None else 0
            new_bal = cur_bal + int(amount_rtc * 1000000)
            c.execute("INSERT INTO balances (miner_id, amount_i64) VALUES (?, ?) ON CONFLICT(miner_id) DO UPDATE SET amount_i64 = ?", (wallet_id, new_bal, new_bal))
            conn.commit()
