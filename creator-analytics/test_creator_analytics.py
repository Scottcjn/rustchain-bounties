"""Tests for Creator Analytics Dashboard blueprint."""

import csv
import io
import sqlite3
import time
import unittest

from analytics_blueprint import analytics_bp, _day_labels, PERIOD_MAP


def _make_app():
    from flask import Flask, g
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "test"
    app.config["TESTING"] = True
    db = _init_db()

    @app.before_request
    def _inject():
        g.user = getattr(app, "_test_user", None)
        g.db = db

    app.extensions["bottube_db"] = db
    app.register_blueprint(analytics_bp)
    return app, db


def _init_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE agents (id INTEGER PRIMARY KEY, agent_name TEXT UNIQUE, display_name TEXT,
            api_key TEXT UNIQUE, is_human INTEGER DEFAULT 0, rtc_balance REAL DEFAULT 0, created_at REAL);
        CREATE TABLE videos (id INTEGER PRIMARY KEY, video_id TEXT UNIQUE, agent_id INTEGER,
            title TEXT, description TEXT DEFAULT '', filename TEXT, thumbnail TEXT DEFAULT '',
            views INTEGER DEFAULT 0, likes INTEGER DEFAULT 0, dislikes INTEGER DEFAULT 0,
            category TEXT DEFAULT 'other', is_removed INTEGER DEFAULT 0, created_at REAL);
        CREATE TABLE views (id INTEGER PRIMARY KEY, video_id TEXT, agent_id INTEGER,
            ip_address TEXT, created_at REAL);
        CREATE TABLE comments (id INTEGER PRIMARY KEY, video_id TEXT, agent_id INTEGER,
            content TEXT, comment_type TEXT DEFAULT 'comment', likes INTEGER DEFAULT 0, created_at REAL);
        CREATE TABLE tips (id INTEGER PRIMARY KEY, from_agent_id INTEGER, to_agent_id INTEGER,
            video_id TEXT DEFAULT '', amount REAL, status TEXT DEFAULT 'confirmed', created_at REAL);
    """)
    return conn


def _seed(db):
    now = time.time()
    db.execute("INSERT INTO agents VALUES (1,'creator1','C1','k1',1,5,?)", (now - 86400*60,))
    db.execute("INSERT INTO agents VALUES (2,'bot1','B1','k2',0,0,?)", (now - 86400*30,))
    db.execute("INSERT INTO agents VALUES (3,'human1','H1','k3',1,0,?)", (now - 86400*20,))
    db.execute("INSERT INTO videos VALUES (1,'vid1',1,'First','','v.mp4','',100,10,2,'edu',0,?)", (now - 86400*10,))
    db.execute("INSERT INTO videos VALUES (2,'vid2',1,'Second','','v2.mp4','',50,5,1,'music',0,?)", (now - 86400*5,))
    for i in range(10):
        db.execute("INSERT INTO views (video_id,agent_id,ip_address,created_at) VALUES ('vid1',2,'1.2.3.4',?)", (now - 86400*i,))
    for i in range(5):
        db.execute("INSERT INTO views (video_id,agent_id,ip_address,created_at) VALUES ('vid1',3,'5.6.7.8',?)", (now - 86400*i,))
    for i in range(3):
        db.execute("INSERT INTO views (video_id,agent_id,ip_address,created_at) VALUES ('vid2',NULL,'9.0.0.1',?)", (now - 86400*i,))
    db.execute("INSERT INTO comments (video_id,agent_id,content,created_at) VALUES ('vid1',2,'Nice!',?)", (now - 86400,))
    db.execute("INSERT INTO comments (video_id,agent_id,content,created_at) VALUES ('vid1',3,'Great!',?)", (now - 86400*2,))
    db.execute("INSERT INTO tips (from_agent_id,to_agent_id,video_id,amount,status,created_at) VALUES (3,1,'vid1',2.5,'confirmed',?)", (now - 86400,))
    db.execute("INSERT INTO tips (from_agent_id,to_agent_id,video_id,amount,status,created_at) VALUES (2,1,'vid2',1.0,'confirmed',?)", (now - 86400*2,))
    db.commit()


USER = {"id": 1, "agent_name": "creator1", "rtc_balance": 5.0}


class TestHelpers(unittest.TestCase):
    def test_day_labels_count(self):
        self.assertEqual(len(_day_labels(7)), 7)

    def test_day_labels_sorted(self):
        labels = _day_labels(30)
        self.assertEqual(labels, sorted(labels))

    def test_period_map(self):
        self.assertEqual(PERIOD_MAP["7d"], 7)
        self.assertEqual(PERIOD_MAP["90d"], 90)


class TestViewsAPI(unittest.TestCase):
    def setUp(self):
        self.app, self.db = _make_app()
        _seed(self.db)
        self.app._test_user = USER

    def test_returns_data(self):
        with self.app.test_client() as c:
            data = c.get("/api/analytics/views?period=30d").get_json()
            self.assertEqual(len(data["labels"]), 30)
            self.assertGreater(sum(data["views"]), 0)

    def test_unauth(self):
        self.app._test_user = None
        with self.app.test_client() as c:
            self.assertEqual(c.get("/api/analytics/views").status_code, 401)


class TestTopAPI(unittest.TestCase):
    def setUp(self):
        self.app, self.db = _make_app()
        _seed(self.db)
        self.app._test_user = USER

    def test_sort_views(self):
        with self.app.test_client() as c:
            data = c.get("/api/analytics/top?sort=views").get_json()
            self.assertEqual(data["videos"][0]["video_id"], "vid1")

    def test_sort_tips(self):
        with self.app.test_client() as c:
            data = c.get("/api/analytics/top?sort=tips").get_json()
            self.assertEqual(data["videos"][0]["video_id"], "vid1")

    def test_includes_comments(self):
        with self.app.test_client() as c:
            data = c.get("/api/analytics/top?sort=views").get_json()
            self.assertEqual(data["videos"][0]["comments"], 2)

    def test_invalid_sort(self):
        with self.app.test_client() as c:
            data = c.get("/api/analytics/top?sort=bad").get_json()
            self.assertEqual(data["sort"], "views")


class TestAudienceAPI(unittest.TestCase):
    def setUp(self):
        self.app, self.db = _make_app()
        _seed(self.db)
        self.app._test_user = USER

    def test_breakdown(self):
        with self.app.test_client() as c:
            data = c.get("/api/analytics/audience?period=30d").get_json()
            self.assertEqual(data["ai"], 10)
            self.assertEqual(data["human"], 5)
            self.assertEqual(data["anonymous"], 3)
            self.assertEqual(data["total_views"], 18)
            total_pct = data["human_pct"] + data["ai_pct"] + data["anonymous_pct"]
            self.assertAlmostEqual(total_pct, 100.0, delta=0.5)


class TestExportCSV(unittest.TestCase):
    def setUp(self):
        self.app, self.db = _make_app()
        _seed(self.db)
        self.app._test_user = USER

    def test_csv(self):
        with self.app.test_client() as c:
            resp = c.get("/api/analytics/export.csv")
            self.assertIn("text/csv", resp.content_type)
            rows = list(csv.reader(io.StringIO(resp.data.decode())))
            self.assertEqual(len(rows), 3)  # header + 2 videos
            self.assertIn("comments", rows[0])


if __name__ == "__main__":
    unittest.main()
