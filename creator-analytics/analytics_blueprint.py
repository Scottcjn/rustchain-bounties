"""Creator Analytics Dashboard — Flask Blueprint for BoTTube (bottube#423).

Endpoints: /api/analytics/views, /api/analytics/top, /api/analytics/audience,
/api/analytics/export.csv, /creator/analytics (page).
"""
from __future__ import annotations

import csv
import io
import time
from datetime import datetime, timezone

from flask import Blueprint, Response, g, jsonify, redirect, render_template, request, url_for

analytics_bp = Blueprint("analytics", __name__, template_folder="templates")

PERIOD_MAP = {"7d": 7, "14d": 14, "30d": 30, "90d": 90}
SORT_MODES = {"views", "engagement", "tips"}


def _parse_period() -> int:
    return PERIOD_MAP.get(request.args.get("period", "30d"), 30)


def _require_login():
    if not g.user:
        return None, None
    from flask import current_app
    db = current_app.extensions.get("bottube_db") or g.get("db")
    if db is None:
        from bottube_server import get_db
        db = get_db()
    return db, g.user["id"]


def _day_labels(n: int) -> list[str]:
    now = int(time.time())
    base = (now // 86400) * 86400
    return [
        datetime.fromtimestamp(base - i * 86400, tz=timezone.utc).strftime("%Y-%m-%d")
        for i in range(n - 1, -1, -1)
    ]


@analytics_bp.route("/api/analytics/views")
def analytics_views():
    """Daily view counts. ?period=7d|14d|30d|90d"""
    db, uid = _require_login()
    if uid is None:
        return jsonify({"error": "Unauthorized"}), 401
    days = _parse_period()
    cutoff = time.time() - days * 86400
    labels = _day_labels(days)
    rows = db.execute(
        "SELECT strftime('%Y-%m-%d', datetime(vw.created_at, 'unixepoch')) AS day,"
        " COUNT(*) AS cnt FROM views vw JOIN videos v ON v.video_id = vw.video_id"
        " WHERE v.agent_id = ? AND vw.created_at >= ? GROUP BY day",
        (uid, cutoff),
    ).fetchall()
    view_map = {r["day"]: int(r["cnt"]) for r in rows}
    return jsonify({"period": f"{days}d", "labels": labels,
                    "views": [view_map.get(d, 0) for d in labels]})


@analytics_bp.route("/api/analytics/top")
def analytics_top():
    """Top videos. ?sort=views|engagement|tips &limit=N"""
    db, uid = _require_login()
    if uid is None:
        return jsonify({"error": "Unauthorized"}), 401
    sort = request.args.get("sort", "views")
    if sort not in SORT_MODES:
        sort = "views"
    limit = max(1, min(50, request.args.get("limit", 10, type=int)))
    order = {"views": "v.views DESC",
             "engagement": "(v.likes * 3.0 + comment_cnt * 2.0 + v.views) DESC",
             "tips": "rtc_tips DESC"}[sort]
    rows = db.execute(
        f"""SELECT v.video_id, v.title, v.views, v.likes, v.dislikes, v.category, v.created_at,
                   (SELECT COUNT(*) FROM comments c WHERE c.video_id = v.video_id) AS comment_cnt,
                   COALESCE((SELECT SUM(t.amount) FROM tips t WHERE t.video_id = v.video_id
                     AND t.to_agent_id = ? AND COALESCE(t.status,'confirmed')='confirmed'), 0) AS rtc_tips
            FROM videos v WHERE v.agent_id = ? AND v.is_removed = 0
            ORDER BY {order}, v.created_at DESC LIMIT ?""",
        (uid, uid, limit),
    ).fetchall()
    return jsonify({"sort": sort, "videos": [
        {"video_id": r["video_id"], "title": r["title"],
         "views": int(r["views"] or 0), "likes": int(r["likes"] or 0),
         "dislikes": int(r["dislikes"] or 0), "comments": int(r["comment_cnt"] or 0),
         "tips_rtc": round(float(r["rtc_tips"] or 0), 6),
         "category": r["category"], "created_at": r["created_at"]}
        for r in rows]})


@analytics_bp.route("/api/analytics/audience")
def analytics_audience():
    """Audience breakdown: human vs AI viewer ratio."""
    db, uid = _require_login()
    if uid is None:
        return jsonify({"error": "Unauthorized"}), 401
    days = _parse_period()
    cutoff = time.time() - days * 86400
    typed = db.execute(
        """SELECT SUM(CASE WHEN a.is_human=1 THEN 1 ELSE 0 END) AS human_views,
                  SUM(CASE WHEN a.is_human=0 THEN 1 ELSE 0 END) AS ai_views
           FROM views vw JOIN videos v ON v.video_id=vw.video_id
           JOIN agents a ON a.id=vw.agent_id
           WHERE v.agent_id=? AND vw.created_at>=? AND vw.agent_id IS NOT NULL""",
        (uid, cutoff)).fetchone()
    anon = db.execute(
        """SELECT COUNT(*) AS cnt FROM views vw JOIN videos v ON v.video_id=vw.video_id
           WHERE v.agent_id=? AND vw.created_at>=? AND vw.agent_id IS NULL""",
        (uid, cutoff)).fetchone()
    human = int(typed["human_views"] or 0)
    ai = int(typed["ai_views"] or 0)
    anonymous = int(anon["cnt"] or 0)
    total = human + ai + anonymous
    return jsonify({
        "period": f"{days}d", "total_views": total,
        "human": human, "ai": ai, "anonymous": anonymous,
        "human_pct": round(human / total * 100, 1) if total else 0,
        "ai_pct": round(ai / total * 100, 1) if total else 0,
        "anonymous_pct": round(anonymous / total * 100, 1) if total else 0})


@analytics_bp.route("/api/analytics/export.csv")
def analytics_export_csv():
    """Export per-video analytics as CSV."""
    db, uid = _require_login()
    if uid is None:
        return jsonify({"error": "Unauthorized"}), 401
    rows = db.execute(
        """SELECT v.video_id, v.title, v.category, v.created_at, v.views, v.likes, v.dislikes,
                  (SELECT COUNT(*) FROM comments c WHERE c.video_id=v.video_id) AS comments,
                  COALESCE((SELECT SUM(t.amount) FROM tips t WHERE t.video_id=v.video_id
                    AND t.to_agent_id=? AND COALESCE(t.status,'confirmed')='confirmed'), 0) AS rtc_tips
           FROM videos v WHERE v.agent_id=? AND v.is_removed=0 ORDER BY v.created_at DESC""",
        (uid, uid)).fetchall()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["video_id", "title", "category", "created_at",
                "views", "likes", "dislikes", "comments", "rtc_tips"])

    def _safe(val):
        if isinstance(val, str) and val and val[0] in ("=", "+", "-", "@"):
            return "'" + val
        return val

    for r in rows:
        ts = r["created_at"]
        created = datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat() if ts else ""
        w.writerow([_safe(r["video_id"]), _safe(r["title"]), _safe(r["category"]), created,
                    int(r["views"] or 0), int(r["likes"] or 0), int(r["dislikes"] or 0),
                    int(r["comments"] or 0), round(float(r["rtc_tips"] or 0), 6)])
    resp = Response(buf.getvalue(), mimetype="text/csv")
    resp.headers["Content-Disposition"] = "attachment; filename=creator-analytics.csv"
    return resp


@analytics_bp.route("/creator/analytics")
def creator_analytics_page():
    """Dedicated analytics dashboard page with Chart.js."""
    if not g.user:
        return redirect(url_for("login"))
    return render_template("creator_analytics.html")
