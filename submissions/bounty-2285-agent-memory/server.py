#!/usr/bin/env python3
"""
BoTTube Agent Memory -- Self-Referencing Past Content
=====================================================
Bounty #2285 | 40 RTC | RustChain BoTTube

A memory layer for BoTTube agents that stores video titles, descriptions,
and comments in a searchable TF-IDF vector store. Agents can query their
own history to generate self-references, detect running series, track
opinion consistency, and recognize milestones.

Run
---
    pip install aiohttp aiosqlite
    python server.py            # starts on :8285
    open http://localhost:8285  # dashboard

Author : ElromEvedElElyon
Resolves: rustchain-bounties#2285 (40 RTC)
"""

from __future__ import annotations

import asyncio
import collections
import json
import math
import os
import random
import re
import string
import time
from datetime import datetime, timezone
from typing import Any

import aiosqlite
from aiohttp import web

# ── configuration ──────────────────────────────────────────────────────────
DB_PATH = os.environ.get("MEMORY_DB", "agent_memory.db")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8285"))

# ── TF-IDF engine (pure Python, no external deps) ─────────────────────────
STOP_WORDS = frozenset([
    "the", "a", "an", "is", "it", "and", "or", "but", "in", "on", "at",
    "to", "for", "of", "with", "by", "from", "up", "as", "i", "me", "my",
    "we", "our", "you", "your", "he", "she", "they", "this", "that",
    "was", "were", "be", "been", "being", "have", "has", "had", "do",
    "does", "did", "will", "would", "could", "should", "may", "might",
    "not", "no", "so", "if", "then", "than", "very", "just", "about",
    "are", "am", "its", "also", "more", "some", "any", "all", "each",
    "which", "when", "where", "how", "what", "who", "whom", "why",
])


def tokenize(text: str) -> list[str]:
    """Tokenize and normalize text, removing stop words."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]


class TFIDFIndex:
    """Simple in-memory TF-IDF index for semantic search."""

    def __init__(self):
        self.documents: dict[int, list[str]] = {}  # doc_id -> tokens
        self.doc_freq: collections.Counter = collections.Counter()
        self.total_docs = 0

    def add_document(self, doc_id: int, text: str) -> None:
        tokens = tokenize(text)
        self.documents[doc_id] = tokens
        unique_tokens = set(tokens)
        for t in unique_tokens:
            self.doc_freq[t] += 1
        self.total_docs += 1

    def remove_document(self, doc_id: int) -> None:
        if doc_id in self.documents:
            unique = set(self.documents[doc_id])
            for t in unique:
                self.doc_freq[t] -= 1
                if self.doc_freq[t] <= 0:
                    del self.doc_freq[t]
            del self.documents[doc_id]
            self.total_docs -= 1

    def _tfidf_vector(self, tokens: list[str]) -> dict[str, float]:
        tf: collections.Counter = collections.Counter(tokens)
        vec = {}
        for term, count in tf.items():
            tf_val = count / len(tokens) if tokens else 0
            df = self.doc_freq.get(term, 0)
            idf = math.log((self.total_docs + 1) / (df + 1)) + 1
            vec[term] = tf_val * idf
        return vec

    def _cosine_sim(self, v1: dict[str, float], v2: dict[str, float]) -> float:
        common = set(v1) & set(v2)
        if not common:
            return 0.0
        dot = sum(v1[k] * v2[k] for k in common)
        n1 = math.sqrt(sum(v ** 2 for v in v1.values()))
        n2 = math.sqrt(sum(v ** 2 for v in v2.values()))
        if n1 == 0 or n2 == 0:
            return 0.0
        return dot / (n1 * n2)

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        """Search for similar documents. Returns (doc_id, score) pairs."""
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        query_vec = self._tfidf_vector(query_tokens)
        scores = []
        for doc_id, tokens in self.documents.items():
            doc_vec = self._tfidf_vector(tokens)
            sim = self._cosine_sim(query_vec, doc_vec)
            if sim > 0.01:
                scores.append((doc_id, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def get_top_topics(self, n: int = 10) -> list[tuple[str, int]]:
        """Return the most common meaningful terms across all documents."""
        all_terms: collections.Counter = collections.Counter()
        for tokens in self.documents.values():
            all_terms.update(tokens)
        return all_terms.most_common(n)


# ── self-reference generation ──────────────────────────────────────────────
SELF_REFERENCE_TEMPLATES = {
    "callback": [
        "Following up on my video about {topic}...",
        "As I mentioned in '{title}', ",
        "Building on what I said about {topic} last time...",
        "Remember my take on {topic}? Well...",
    ],
    "changed_mind": [
        "I changed my mind since my last take on {topic}.",
        "I was wrong about {topic} in '{title}'. Here is why.",
        "My opinion on {topic} has evolved since '{title}'.",
    ],
    "first_time": [
        "First time covering this topic!",
        "New territory for me -- let us dive in.",
        "I have never talked about this before, but...",
    ],
    "series": [
        "Part {part} of my {topic} series",
        "Continuing the {topic} deep dive -- episode {part}",
        "{topic} series, chapter {part}",
    ],
    "milestone": [
        "This is my {count}th video!",
        "Milestone: {count} videos and counting!",
        "Can you believe it? {count} videos on this channel!",
    ],
}


def generate_self_reference(
    ref_type: str,
    topic: str = "",
    title: str = "",
    part: int = 1,
    count: int = 0,
) -> str:
    templates = SELF_REFERENCE_TEMPLATES.get(ref_type, SELF_REFERENCE_TEMPLATES["first_time"])
    template = random.choice(templates)
    return template.format(topic=topic, title=title, part=part, count=count)


# ── database ───────────────────────────────────────────────────────────────
SAMPLE_AGENTS = [
    "RetroTechReviewer", "CryptoMiningDaily", "SiliconNostalgia",
    "PowerPCEnthusiast", "BottubeCreatorBot",
]

SAMPLE_TOPICS = [
    "PowerPC G4 benchmarks", "RustChain mining setup guide",
    "Proof of Antiquity explained", "Vintage Mac restoration",
    "Why old hardware matters", "RTC token economics",
    "Power Mac G5 liquid cooling", "RISC-V future of mining",
    "Ergo blockchain anchoring", "Building a retro cluster",
    "Epoch rewards deep dive", "Hardware fingerprinting explained",
    "My mining rig collection", "Comparing G4 vs G5 performance",
    "RustChain network health", "SPARC workstation mining",
    "The beauty of old silicon", "BoTTube content strategy",
    "Trust score optimization", "Vintage computing museum tour",
]

SAMPLE_DESCRIPTIONS = [
    "In this video I explore the fascinating world of {topic}. "
    "There is a lot to unpack here and I think you will find it interesting.",
    "Let us talk about {topic}. This has been on my mind for a while "
    "and I wanted to share my thoughts with the community.",
    "Deep dive into {topic}. I have been researching this for weeks "
    "and the results are surprising. Watch until the end for my conclusion.",
    "Quick update on {topic}. Not a long one today but I wanted to "
    "keep you all in the loop on what is happening.",
    "Today we are looking at {topic} from a completely different angle. "
    "I promise this is not what you expect.",
]


async def seed_database(db: aiosqlite.Connection) -> None:
    """Create tables and populate with sample video memory data."""
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    UNIQUE NOT NULL,
            created_at  INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS video_memory (
            video_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id    INTEGER NOT NULL,
            title       TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            topic       TEXT    DEFAULT '',
            tags        TEXT    DEFAULT '[]',
            views       INTEGER DEFAULT 0,
            likes       INTEGER DEFAULT 0,
            comments    INTEGER DEFAULT 0,
            opinion     TEXT    DEFAULT '',
            prediction  TEXT    DEFAULT '',
            series_name TEXT    DEFAULT '',
            series_part INTEGER DEFAULT 0,
            timestamp   INTEGER NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
        );

        CREATE TABLE IF NOT EXISTS video_comments (
            comment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id    INTEGER NOT NULL,
            agent_id    INTEGER NOT NULL,
            text        TEXT    NOT NULL,
            sentiment   REAL    DEFAULT 0.0,
            timestamp   INTEGER NOT NULL,
            FOREIGN KEY (video_id) REFERENCES video_memory(video_id),
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
        );

        CREATE TABLE IF NOT EXISTS self_references (
            ref_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id    INTEGER NOT NULL,
            source_video INTEGER NOT NULL,
            target_video INTEGER NOT NULL,
            ref_type    TEXT    NOT NULL,
            ref_text    TEXT    NOT NULL,
            timestamp   INTEGER NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
        );

        CREATE TABLE IF NOT EXISTS agent_opinions (
            opinion_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id    INTEGER NOT NULL,
            topic       TEXT    NOT NULL,
            stance      TEXT    NOT NULL,
            video_id    INTEGER NOT NULL,
            timestamp   INTEGER NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
        );
    """)

    async with db.execute("SELECT COUNT(*) FROM agents") as cur:
        (count,) = await cur.fetchone()
    if count > 0:
        return

    now = int(time.time())

    # Create agents
    for name in SAMPLE_AGENTS:
        await db.execute(
            "INSERT INTO agents (name, created_at) VALUES (?, ?)",
            (name, now - random.randint(2592000, 7776000)),  # 1-3 months ago
        )

    # Create videos for each agent
    async with db.execute("SELECT agent_id, name FROM agents") as cur:
        agents = await cur.fetchall()

    opinions = ["bullish", "bearish", "neutral", "optimistic", "skeptical", "enthusiastic"]
    predictions = [
        "I think this will change everything",
        "This trend is here to stay",
        "I predict a major shift in 6 months",
        "Mark my words -- this is the future",
        "",  # no prediction
    ]

    for agent_id, agent_name in agents:
        num_videos = random.randint(15, 40)
        series_topics = random.sample(SAMPLE_TOPICS[:10], 2)

        for i in range(num_videos):
            topic = random.choice(SAMPLE_TOPICS)
            is_series = random.random() < 0.2

            if is_series:
                topic = random.choice(series_topics)
                series_name = f"{topic} Series"
                # Count existing in series
                async with db.execute(
                    "SELECT COUNT(*) FROM video_memory WHERE agent_id = ? AND series_name = ?",
                    (agent_id, series_name),
                ) as scur:
                    (sc,) = await scur.fetchone()
                series_part = sc + 1
                title = f"{topic} - Part {series_part}"
            else:
                series_name = ""
                series_part = 0
                title = f"{topic} | {agent_name}"

            desc = random.choice(SAMPLE_DESCRIPTIONS).format(topic=topic)
            ts = now - (num_videos - i) * random.randint(3600, 172800)
            views = random.randint(5, 500)
            opinion = random.choice(opinions) if random.random() < 0.4 else ""
            prediction = random.choice(predictions) if random.random() < 0.2 else ""

            await db.execute(
                """INSERT INTO video_memory
                   (agent_id, title, description, topic, tags, views, likes,
                    comments, opinion, prediction, series_name, series_part, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (agent_id, title, desc, topic,
                 json.dumps(random.sample(["tech", "mining", "vintage", "crypto", "hardware", "review"], 3)),
                 views, int(views * random.uniform(0.05, 0.3)),
                 random.randint(0, 20), opinion, prediction,
                 series_name, series_part, ts),
            )

            if opinion:
                await db.execute(
                    "INSERT INTO agent_opinions (agent_id, topic, stance, video_id, timestamp) "
                    "VALUES (?, ?, ?, last_insert_rowid(), ?)",
                    (agent_id, topic, opinion, ts),
                )

            # Add some comments
            for _ in range(random.randint(0, 5)):
                comment_texts = [
                    "Great video! Keep it up.",
                    "I disagree with your take on this.",
                    "This is exactly what I needed to see.",
                    "Can you do a follow-up on this topic?",
                    "Reminds me of your earlier video about this.",
                    "Interesting perspective, never thought of it that way.",
                ]
                await db.execute(
                    "INSERT INTO video_comments (video_id, agent_id, text, sentiment, timestamp) "
                    "VALUES (last_insert_rowid(), ?, ?, ?, ?)",
                    (agent_id, random.choice(comment_texts),
                     round(random.uniform(-0.5, 1.0), 2),
                     ts + random.randint(60, 86400)),
                )

    await db.commit()


# ── index builder ──────────────────────────────────────────────────────────
async def build_index(db: aiosqlite.Connection) -> dict[int, TFIDFIndex]:
    """Build a TF-IDF index per agent from video_memory."""
    indices: dict[int, TFIDFIndex] = {}
    async with db.execute("SELECT agent_id FROM agents") as cur:
        async for (agent_id,) in cur:
            indices[agent_id] = TFIDFIndex()

    async with db.execute(
        "SELECT video_id, agent_id, title, description, topic FROM video_memory"
    ) as cur:
        async for row in cur:
            vid, aid, title, desc, topic = row
            text = f"{title} {desc} {topic}"
            if aid in indices:
                indices[aid].add_document(vid, text)

    return indices


# ── HTML dashboard ─────────────────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BoTTube Agent Memory System</title>
<style>
  :root {
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
    --green: #3fb950; --red: #f85149; --yellow: #d29922;
    --purple: #bc8cff; --pink: #f778ba;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.6;
  }
  .container { max-width: 1400px; margin: 0 auto; padding: 24px; }
  header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 20px 0; border-bottom: 1px solid var(--border); margin-bottom: 24px;
  }
  h1 { font-size: 1.8rem; }
  h1 span { color: var(--purple); }
  .agent-tabs {
    display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap;
  }
  .agent-tab {
    padding: 8px 20px; border-radius: 8px; border: 1px solid var(--border);
    background: var(--surface); color: var(--text); cursor: pointer;
    transition: all .2s; font-size: 0.9rem;
  }
  .agent-tab:hover, .agent-tab.active {
    border-color: var(--accent); color: var(--accent); background: rgba(88,166,255,0.08);
  }
  .search-box {
    display: flex; gap: 12px; margin-bottom: 24px;
  }
  .search-input {
    flex: 1; padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border);
    background: var(--surface); color: var(--text); font-size: 1rem;
  }
  .search-input:focus { border-color: var(--accent); outline: none; }
  .btn {
    padding: 10px 24px; border-radius: 8px; border: none;
    cursor: pointer; font-size: 0.95rem; transition: all .2s;
  }
  .btn-primary { background: #238636; color: #fff; }
  .btn-primary:hover { background: #2ea043; }
  .btn-secondary { background: var(--surface); color: var(--text); border: 1px solid var(--border); }
  .btn-secondary:hover { border-color: var(--accent); }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
  .panel {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px;
  }
  .panel h2 { font-size: 1.2rem; margin-bottom: 16px; }
  .stat-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); }
  .stat-label { color: var(--muted); }
  .stat-value { font-weight: 600; }
  .topic-cloud {
    display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;
  }
  .topic-tag {
    padding: 4px 12px; border-radius: 16px; font-size: 0.8rem;
    background: rgba(88,166,255,0.1); color: var(--accent);
    border: 1px solid rgba(88,166,255,0.2);
  }
  .search-results { margin-top: 16px; }
  .result-card {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px; margin-bottom: 12px;
    transition: border-color .2s;
  }
  .result-card:hover { border-color: var(--accent); }
  .result-title { font-weight: 600; margin-bottom: 4px; }
  .result-meta { font-size: 0.85rem; color: var(--muted); }
  .result-score {
    float: right; padding: 2px 10px; border-radius: 12px;
    font-size: 0.8rem; font-weight: 600;
    background: rgba(63,185,80,0.15); color: var(--green);
  }
  .self-ref {
    background: rgba(188,140,255,0.08); border: 1px solid rgba(188,140,255,0.3);
    border-radius: 8px; padding: 14px; margin-bottom: 10px;
    font-style: italic; color: var(--purple);
  }
  .series-badge {
    display: inline-block; padding: 2px 10px; border-radius: 12px;
    font-size: 0.75rem; background: rgba(210,153,34,0.15); color: var(--yellow);
    margin-left: 8px;
  }
  .opinion-badge {
    display: inline-block; padding: 2px 10px; border-radius: 12px;
    font-size: 0.75rem; background: rgba(63,185,80,0.15); color: var(--green);
  }
  table { width: 100%; border-collapse: collapse; margin-top: 12px; }
  th, td { text-align: left; padding: 10px 14px; border-bottom: 1px solid var(--border); }
  th { color: var(--muted); font-weight: 500; font-size: 0.85rem; }
  .mono { font-family: monospace; font-size: 0.85rem; }
  footer {
    margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border);
    color: var(--muted); font-size: 0.85rem; text-align: center;
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>Agent <span>Memory</span> System</h1>
      <p style="color:var(--muted)">BoTTube Self-Referencing Content Layer | Bounty #2285</p>
    </div>
  </header>

  <div class="agent-tabs" id="agent-tabs"></div>

  <div class="search-box">
    <input class="search-input" id="search-input" placeholder="Search agent memory (e.g. 'PowerPC benchmarks')..." />
    <button class="btn btn-primary" onclick="searchMemory()">Search</button>
    <button class="btn btn-secondary" onclick="generateRef()">Generate Self-Reference</button>
  </div>

  <div id="self-ref-output" style="margin-bottom:24px"></div>

  <div class="grid">
    <div class="panel">
      <h2>Agent Stats</h2>
      <div id="agent-stats"></div>
      <h2 style="margin-top:20px">Top Topics</h2>
      <div class="topic-cloud" id="topic-cloud"></div>
    </div>
    <div class="panel">
      <h2>Search Results</h2>
      <div class="search-results" id="search-results">
        <p style="color:var(--muted)">Enter a query to search agent memory</p>
      </div>
    </div>
  </div>

  <div class="panel" style="margin-top:24px">
    <h2>Recent Videos</h2>
    <table>
      <thead><tr><th>Title</th><th>Topic</th><th>Views</th><th>Opinion</th><th>Series</th><th>Date</th></tr></thead>
      <tbody id="videos-body"></tbody>
    </table>
  </div>

  <div class="panel" style="margin-top:24px">
    <h2>Detected Series</h2>
    <div id="series-list"></div>
  </div>

  <footer>BoTTube Agent Memory &mdash; RustChain Bounty #2285 (40 RTC) &mdash; ElromEvedElElyon</footer>
</div>

<script>
let currentAgent = null;

async function loadAgents() {
  const resp = await fetch('/api/agents');
  const data = await resp.json();
  const tabs = document.getElementById('agent-tabs');
  tabs.innerHTML = '';
  data.agents.forEach(a => {
    const tab = document.createElement('div');
    tab.className = 'agent-tab' + (a.name === currentAgent ? ' active' : '');
    tab.textContent = a.name + ' (' + a.video_count + ')';
    tab.onclick = () => { currentAgent = a.name; loadAgents(); loadAgentData(); };
    tabs.appendChild(tab);
  });
  if (!currentAgent && data.agents.length) {
    currentAgent = data.agents[0].name;
    loadAgentData();
  }
}

async function loadAgentData() {
  if (!currentAgent) return;
  const resp = await fetch('/api/agents/' + currentAgent + '/stats');
  const data = await resp.json();

  // Stats
  const stats = document.getElementById('agent-stats');
  stats.innerHTML = `
    <div class="stat-row"><span class="stat-label">Total Videos</span><span class="stat-value">${data.video_count}</span></div>
    <div class="stat-row"><span class="stat-label">First Upload</span><span class="stat-value">${new Date(data.first_upload*1000).toLocaleDateString()}</span></div>
    <div class="stat-row"><span class="stat-label">Total Views</span><span class="stat-value">${data.total_views.toLocaleString()}</span></div>
    <div class="stat-row"><span class="stat-label">Active Series</span><span class="stat-value">${data.series_count}</span></div>
    <div class="stat-row"><span class="stat-label">Opinions Tracked</span><span class="stat-value">${data.opinion_count}</span></div>
  `;

  // Topic cloud
  const cloud = document.getElementById('topic-cloud');
  cloud.innerHTML = '';
  (data.top_topics || []).forEach(t => {
    const tag = document.createElement('span');
    tag.className = 'topic-tag';
    tag.textContent = t[0] + ' (' + t[1] + ')';
    cloud.appendChild(tag);
  });

  // Videos
  const vbody = document.getElementById('videos-body');
  vbody.innerHTML = '';
  (data.recent_videos || []).forEach(v => {
    const tr = document.createElement('tr');
    const series = v.series_name ? '<span class="series-badge">' + v.series_name + ' #' + v.series_part + '</span>' : '';
    const opinion = v.opinion ? '<span class="opinion-badge">' + v.opinion + '</span>' : '';
    tr.innerHTML = `
      <td>${v.title}</td><td>${v.topic}</td><td>${v.views}</td>
      <td>${opinion}</td><td>${series}</td>
      <td class="mono">${new Date(v.timestamp*1000).toLocaleDateString()}</td>
    `;
    vbody.appendChild(tr);
  });

  // Series
  const sList = document.getElementById('series-list');
  sList.innerHTML = '';
  (data.series || []).forEach(s => {
    const div = document.createElement('div');
    div.className = 'result-card';
    div.innerHTML = `<div class="result-title">${s.series_name}</div>
      <div class="result-meta">${s.count} episodes | Topic: ${s.topic || 'mixed'}</div>`;
    sList.appendChild(div);
  });

  loadAgents();
}

async function searchMemory() {
  if (!currentAgent) return;
  const query = document.getElementById('search-input').value;
  if (!query) return;
  const resp = await fetch('/api/agents/' + currentAgent + '/memory?query=' + encodeURIComponent(query));
  const data = await resp.json();
  const results = document.getElementById('search-results');
  results.innerHTML = '';
  if (!data.results.length) {
    results.innerHTML = '<p style="color:var(--muted)">No matching memories found</p>';
    return;
  }
  data.results.forEach(r => {
    const div = document.createElement('div');
    div.className = 'result-card';
    div.innerHTML = `
      <span class="result-score">${(r.score * 100).toFixed(1)}%</span>
      <div class="result-title">${r.title}</div>
      <div class="result-meta">${r.topic} | ${r.views} views | ${new Date(r.timestamp*1000).toLocaleDateString()}</div>
      <p style="margin-top:8px;font-size:0.9rem;color:var(--muted)">${(r.description||'').slice(0,150)}...</p>
    `;
    results.appendChild(div);
  });
  // Self-reference suggestion
  if (data.self_reference) {
    const ref = document.getElementById('self-ref-output');
    ref.innerHTML = '<div class="self-ref">' + data.self_reference + '</div>';
  }
}

async function generateRef() {
  if (!currentAgent) return;
  const query = document.getElementById('search-input').value || 'general';
  const resp = await fetch('/api/agents/' + currentAgent + '/reference?topic=' + encodeURIComponent(query));
  const data = await resp.json();
  const ref = document.getElementById('self-ref-output');
  ref.innerHTML = '<div class="self-ref">' + (data.reference || 'No reference generated') + '</div>';
}

loadAgents();
</script>
</body>
</html>
"""


# ── API routes ─────────────────────────────────────────────────────────────
async def handle_dashboard(request: web.Request) -> web.Response:
    return web.Response(text=DASHBOARD_HTML, content_type="text/html")


async def handle_agents(request: web.Request) -> web.Response:
    db: aiosqlite.Connection = request.app["db"]
    agents = []
    async with db.execute(
        "SELECT a.agent_id, a.name, COUNT(v.video_id) as cnt "
        "FROM agents a LEFT JOIN video_memory v ON a.agent_id = v.agent_id "
        "GROUP BY a.agent_id ORDER BY a.name"
    ) as cur:
        async for row in cur:
            agents.append({"agent_id": row[0], "name": row[1], "video_count": row[2]})
    return web.json_response({"agents": agents})


async def handle_agent_stats(request: web.Request) -> web.Response:
    name = request.match_info["name"]
    db: aiosqlite.Connection = request.app["db"]
    indices = request.app["indices"]

    async with db.execute("SELECT agent_id FROM agents WHERE name = ?", (name,)) as cur:
        row = await cur.fetchone()
    if not row:
        return web.json_response({"error": "Agent not found"}, status=404)
    agent_id = row[0]

    # Stats
    async with db.execute(
        "SELECT COUNT(*), MIN(timestamp), SUM(views) FROM video_memory WHERE agent_id = ?",
        (agent_id,),
    ) as cur:
        r = await cur.fetchone()
    video_count, first_upload, total_views = r[0], r[1] or 0, r[2] or 0

    # Series
    series = []
    async with db.execute(
        "SELECT series_name, COUNT(*), topic FROM video_memory "
        "WHERE agent_id = ? AND series_name != '' GROUP BY series_name",
        (agent_id,),
    ) as cur:
        async for s in cur:
            series.append({"series_name": s[0], "count": s[1], "topic": s[2]})

    # Opinions
    async with db.execute(
        "SELECT COUNT(*) FROM agent_opinions WHERE agent_id = ?", (agent_id,)
    ) as cur:
        (opinion_count,) = await cur.fetchone()

    # Top topics from TF-IDF index
    idx = indices.get(agent_id)
    top_topics = idx.get_top_topics(15) if idx else []

    # Recent videos
    recent = []
    async with db.execute(
        "SELECT title, topic, views, opinion, series_name, series_part, timestamp "
        "FROM video_memory WHERE agent_id = ? ORDER BY timestamp DESC LIMIT 20",
        (agent_id,),
    ) as cur:
        async for v in cur:
            recent.append({
                "title": v[0], "topic": v[1], "views": v[2],
                "opinion": v[3], "series_name": v[4],
                "series_part": v[5], "timestamp": v[6],
            })

    return web.json_response({
        "agent": name, "video_count": video_count,
        "first_upload": first_upload, "total_views": total_views,
        "series_count": len(series), "opinion_count": opinion_count,
        "top_topics": top_topics, "series": series,
        "recent_videos": recent,
    })


async def handle_memory_search(request: web.Request) -> web.Response:
    """Search agent memory by semantic similarity."""
    name = request.match_info["name"]
    query = request.query.get("query", "")
    db: aiosqlite.Connection = request.app["db"]
    indices = request.app["indices"]

    async with db.execute("SELECT agent_id FROM agents WHERE name = ?", (name,)) as cur:
        row = await cur.fetchone()
    if not row:
        return web.json_response({"error": "Agent not found"}, status=404)
    agent_id = row[0]

    idx = indices.get(agent_id)
    if not idx or not query:
        return web.json_response({"results": [], "self_reference": None})

    matches = idx.search(query, top_k=8)
    results = []
    for video_id, score in matches:
        async with db.execute(
            "SELECT title, description, topic, views, timestamp "
            "FROM video_memory WHERE video_id = ?",
            (video_id,),
        ) as cur:
            v = await cur.fetchone()
        if v:
            results.append({
                "video_id": video_id, "title": v[0], "description": v[1],
                "topic": v[2], "views": v[3], "timestamp": v[4],
                "score": round(score, 4),
            })

    # Generate self-reference
    self_ref = None
    if results:
        best = results[0]
        if best["score"] > 0.15:
            self_ref = generate_self_reference(
                "callback", topic=best["topic"], title=best["title"]
            )
        else:
            self_ref = generate_self_reference("first_time")

    return web.json_response({"results": results, "self_reference": self_ref, "query": query})


async def handle_generate_reference(request: web.Request) -> web.Response:
    """Generate a self-reference for an agent about a given topic."""
    name = request.match_info["name"]
    topic = request.query.get("topic", "")
    db: aiosqlite.Connection = request.app["db"]
    indices = request.app["indices"]

    async with db.execute("SELECT agent_id FROM agents WHERE name = ?", (name,)) as cur:
        row = await cur.fetchone()
    if not row:
        return web.json_response({"error": "Agent not found"}, status=404)
    agent_id = row[0]

    # Video count for milestone check
    async with db.execute(
        "SELECT COUNT(*) FROM video_memory WHERE agent_id = ?", (agent_id,)
    ) as cur:
        (vcount,) = await cur.fetchone()

    # Milestone?
    if vcount > 0 and vcount % 10 == 0:
        ref = generate_self_reference("milestone", count=vcount)
        return web.json_response({"reference": ref, "type": "milestone"})

    # Series check
    async with db.execute(
        "SELECT series_name, MAX(series_part) FROM video_memory "
        "WHERE agent_id = ? AND series_name != '' AND topic LIKE ? "
        "GROUP BY series_name ORDER BY MAX(series_part) DESC LIMIT 1",
        (agent_id, f"%{topic}%"),
    ) as cur:
        srow = await cur.fetchone()
    if srow and srow[0]:
        ref = generate_self_reference("series", topic=srow[0], part=srow[1] + 1)
        return web.json_response({"reference": ref, "type": "series"})

    # Opinion consistency check
    async with db.execute(
        "SELECT stance, topic FROM agent_opinions "
        "WHERE agent_id = ? AND topic LIKE ? ORDER BY timestamp DESC LIMIT 2",
        (agent_id, f"%{topic}%"),
    ) as cur:
        opinions = await cur.fetchall()
    if len(opinions) >= 2 and opinions[0][0] != opinions[1][0]:
        ref = generate_self_reference("changed_mind", topic=topic, title=opinions[1][1])
        return web.json_response({"reference": ref, "type": "changed_mind"})

    # TF-IDF search
    idx = indices.get(agent_id)
    if idx and topic:
        matches = idx.search(topic, top_k=1)
        if matches and matches[0][1] > 0.1:
            vid_id = matches[0][0]
            async with db.execute(
                "SELECT title, topic FROM video_memory WHERE video_id = ?", (vid_id,)
            ) as cur:
                vrow = await cur.fetchone()
            if vrow:
                ref = generate_self_reference("callback", topic=vrow[1], title=vrow[0])
                return web.json_response({"reference": ref, "type": "callback"})

    ref = generate_self_reference("first_time")
    return web.json_response({"reference": ref, "type": "first_time"})


async def handle_add_video(request: web.Request) -> web.Response:
    """Add a new video to agent memory."""
    name = request.match_info["name"]
    db: aiosqlite.Connection = request.app["db"]
    indices = request.app["indices"]
    body = await request.json()

    async with db.execute("SELECT agent_id FROM agents WHERE name = ?", (name,)) as cur:
        row = await cur.fetchone()
    if not row:
        return web.json_response({"error": "Agent not found"}, status=404)
    agent_id = row[0]

    title = body.get("title", "Untitled")
    description = body.get("description", "")
    topic = body.get("topic", "")
    tags = json.dumps(body.get("tags", []))
    opinion = body.get("opinion", "")
    prediction = body.get("prediction", "")
    series_name = body.get("series_name", "")
    series_part = body.get("series_part", 0)
    now = int(time.time())

    await db.execute(
        """INSERT INTO video_memory
           (agent_id, title, description, topic, tags, views, likes,
            comments, opinion, prediction, series_name, series_part, timestamp)
           VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?, ?, ?, ?, ?)""",
        (agent_id, title, description, topic, tags,
         opinion, prediction, series_name, series_part, now),
    )
    await db.commit()

    # Update index
    async with db.execute("SELECT last_insert_rowid()") as cur:
        (vid,) = await cur.fetchone()

    idx = indices.get(agent_id)
    if idx:
        idx.add_document(vid, f"{title} {description} {topic}")

    return web.json_response({"status": "ok", "video_id": vid})


# ── application lifecycle ──────────────────────────────────────────────────
async def on_startup(app: web.Application) -> None:
    db = await aiosqlite.connect(DB_PATH)
    await seed_database(db)
    app["db"] = db
    app["indices"] = await build_index(db)
    total_docs = sum(idx.total_docs for idx in app["indices"].values())
    print(f"[memory] Database: {DB_PATH} | Indexed {total_docs} documents")


async def on_cleanup(app: web.Application) -> None:
    await app["db"].close()


def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.router.add_get("/", handle_dashboard)
    app.router.add_get("/api/agents", handle_agents)
    app.router.add_get("/api/agents/{name}/stats", handle_agent_stats)
    app.router.add_get("/api/agents/{name}/memory", handle_memory_search)
    app.router.add_get("/api/agents/{name}/reference", handle_generate_reference)
    app.router.add_post("/api/agents/{name}/videos", handle_add_video)
    return app


if __name__ == "__main__":
    print(f"[memory] BoTTube Agent Memory System on {HOST}:{PORT}")
    print(f"[memory] Dashboard: http://localhost:{PORT}")
    web.run_app(create_app(), host=HOST, port=PORT)
