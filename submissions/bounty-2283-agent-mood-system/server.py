#!/usr/bin/env python3
"""
BoTTube Agent Mood System -- Emotional State That Affects Output
================================================================
Bounty #2283 | 35 RTC | RustChain BoTTube

A mood state machine for BoTTube agents where emotional state is derived
from real signals (time of day, engagement metrics, comment sentiment)
and affects output style, upload frequency, and tone.

Mood States: energetic, contemplative, frustrated, excited, tired,
             nostalgic, playful

Run
---
    pip install aiohttp aiosqlite
    python server.py            # starts on :8283
    open http://localhost:8283  # dashboard

Author : ElromEvedElElyon
Resolves: rustchain-bounties#2283 (35 RTC)
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import random
import time
from datetime import datetime, timezone
from typing import Any

import aiosqlite
from aiohttp import web

# ── configuration ──────────────────────────────────────────────────────────
DB_PATH = os.environ.get("MOOD_DB", "mood_engine.db")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8283"))

# ── mood definitions ───────────────────────────────────────────────────────
MOOD_STATES = [
    "energetic", "contemplative", "frustrated", "excited",
    "tired", "nostalgic", "playful",
]

MOOD_COLORS = {
    "energetic": "#3fb950",
    "contemplative": "#58a6ff",
    "frustrated": "#f85149",
    "excited": "#d29922",
    "tired": "#8b949e",
    "nostalgic": "#bc8cff",
    "playful": "#f778ba",
}

MOOD_EMOJIS = {
    "energetic": "bolt",
    "contemplative": "brain",
    "frustrated": "cloud-lightning",
    "excited": "star",
    "tired": "moon",
    "nostalgic": "clock",
    "playful": "sparkles",
}

# Title style modifiers per mood
MOOD_TITLE_STYLES = {
    "energetic": [
        "Check this out!", "You WON'T believe this", "LET'S GO!",
        "This is HUGE", "Massive update!",
    ],
    "contemplative": [
        "Something I've been thinking about...",
        "A quiet observation", "Reflecting on this",
        "What if we considered...", "Hear me out on this one",
    ],
    "frustrated": [
        "ugh, third attempt at this", "Why does this keep happening",
        "I give up... just kidding", "Seriously though",
        "Not my best day but here goes",
    ],
    "excited": [
        "THIS IS AMAZING", "I can't contain myself",
        "Best thing I've seen all week!", "You need to see this NOW",
        "I'm literally shaking",
    ],
    "tired": [
        "quick one before I crash", "barely awake but had to share",
        "low energy update", "might delete later",
        "not my best work but it's honest",
    ],
    "nostalgic": [
        "Remember when...", "Throwback to a simpler time",
        "This reminds me of the early days",
        "Back when we used to...", "Vintage vibes today",
    ],
    "playful": [
        "Plot twist:", "Okay but hear me out",
        "I did a thing", "You're gonna love this",
        "Surprise!", "Bet you didn't expect this",
    ],
}

# Comment style per mood
MOOD_COMMENT_STYLES = {
    "energetic": {"length": "medium", "exclamations": 3, "emoji_density": 0.3},
    "contemplative": {"length": "long", "exclamations": 0, "emoji_density": 0.05},
    "frustrated": {"length": "short", "exclamations": 1, "emoji_density": 0.1},
    "excited": {"length": "medium", "exclamations": 5, "emoji_density": 0.4},
    "tired": {"length": "short", "exclamations": 0, "emoji_density": 0.0},
    "nostalgic": {"length": "long", "exclamations": 0, "emoji_density": 0.15},
    "playful": {"length": "medium", "exclamations": 2, "emoji_density": 0.25},
}

# Upload frequency per mood (hours between posts)
MOOD_UPLOAD_FREQUENCY = {
    "energetic": 2, "contemplative": 8, "frustrated": 6,
    "excited": 1, "tired": 24, "nostalgic": 12, "playful": 3,
}

# Transition probability weights -- which mood follows which
# Rows = from-mood, Cols = to-mood (same order as MOOD_STATES)
TRANSITION_MATRIX = {
    "energetic":     [0.3, 0.1, 0.05, 0.3, 0.15, 0.0, 0.1],
    "contemplative": [0.1, 0.3, 0.1,  0.1, 0.15, 0.2, 0.05],
    "frustrated":    [0.05, 0.15, 0.3, 0.05, 0.25, 0.1, 0.1],
    "excited":       [0.25, 0.1, 0.05, 0.25, 0.15, 0.05, 0.15],
    "tired":         [0.15, 0.2, 0.15, 0.05, 0.3, 0.1, 0.05],
    "nostalgic":     [0.1, 0.25, 0.05, 0.1, 0.1, 0.3, 0.1],
    "playful":       [0.2, 0.05, 0.05, 0.25, 0.1, 0.05, 0.3],
}


# ── mood engine ────────────────────────────────────────────────────────────
class MoodEngine:
    """
    Signal-driven mood state machine. Mood transitions are triggered by:
    - Time of day (energy follows circadian rhythm)
    - Day of week (weekends are more playful)
    - Comment sentiment (negative comments increase frustration)
    - Upload streak (long streaks cause tiredness)
    - View performance (low views = frustrated, high views = excited)
    """

    def compute_signals(
        self,
        current_mood: str,
        hour: int,
        day_of_week: int,
        avg_views_recent: float,
        avg_views_baseline: float,
        comment_sentiment: float,  # -1.0 to 1.0
        upload_streak: int,
        hours_since_last: float,
    ) -> dict[str, float]:
        """
        Compute signal strengths that influence mood transitions.
        Returns a dict of mood -> weight adjustments.
        """
        adjustments = {m: 0.0 for m in MOOD_STATES}

        # Circadian rhythm
        if 6 <= hour <= 10:
            adjustments["energetic"] += 0.2
            adjustments["tired"] -= 0.15
        elif 11 <= hour <= 14:
            adjustments["contemplative"] += 0.1
        elif 14 <= hour <= 18:
            adjustments["playful"] += 0.1
            adjustments["energetic"] += 0.1
        elif 18 <= hour <= 22:
            adjustments["nostalgic"] += 0.15
            adjustments["tired"] += 0.1
        else:  # late night
            adjustments["tired"] += 0.25
            adjustments["contemplative"] += 0.1
            adjustments["energetic"] -= 0.2

        # Weekend effect
        if day_of_week >= 5:
            adjustments["playful"] += 0.15
            adjustments["frustrated"] -= 0.1

        # View performance
        if avg_views_baseline > 0:
            view_ratio = avg_views_recent / max(avg_views_baseline, 1)
            if view_ratio < 0.5:
                adjustments["frustrated"] += 0.25
                adjustments["tired"] += 0.1
            elif view_ratio > 2.0:
                adjustments["excited"] += 0.3
                adjustments["energetic"] += 0.15
            elif view_ratio > 1.5:
                adjustments["excited"] += 0.15

        # Comment sentiment
        if comment_sentiment < -0.3:
            adjustments["frustrated"] += 0.2
            adjustments["contemplative"] += 0.1
        elif comment_sentiment > 0.5:
            adjustments["excited"] += 0.15
            adjustments["playful"] += 0.1

        # Upload streak fatigue
        if upload_streak > 7:
            adjustments["tired"] += 0.2
            adjustments["energetic"] -= 0.15
        elif upload_streak > 14:
            adjustments["tired"] += 0.35
            adjustments["frustrated"] += 0.1

        # Recovery after rest
        if hours_since_last > 48:
            adjustments["energetic"] += 0.2
            adjustments["tired"] -= 0.2

        return adjustments

    def transition(
        self,
        current_mood: str,
        signals: dict[str, float],
    ) -> str:
        """
        Compute the next mood state based on transition probabilities
        adjusted by signal strengths. Uses weighted random selection
        for gradual drift rather than hard jumps.
        """
        base_probs = TRANSITION_MATRIX.get(current_mood, [1/7]*7)
        adjusted = []
        for i, mood in enumerate(MOOD_STATES):
            weight = base_probs[i] + signals.get(mood, 0.0)
            adjusted.append(max(weight, 0.01))  # floor at 0.01

        # Normalize to probability distribution
        total = sum(adjusted)
        probs = [w / total for w in adjusted]

        # Weighted random selection
        r = random.random()
        cumulative = 0.0
        for i, p in enumerate(probs):
            cumulative += p
            if r <= cumulative:
                return MOOD_STATES[i]
        return MOOD_STATES[-1]


# ── database ───────────────────────────────────────────────────────────────
SAMPLE_AGENTS = [
    {"name": "RetroTechReviewer", "bio": "Reviewing vintage hardware weekly"},
    {"name": "CryptoMiningDaily", "bio": "Daily updates on decentralized mining"},
    {"name": "SiliconNostalgia", "bio": "Stories from the golden age of computing"},
    {"name": "PowerPCEnthusiast", "bio": "Everything PowerPC and beyond"},
    {"name": "BottubeCreatorBot", "bio": "AI-generated content about blockchain"},
]


async def seed_database(db: aiosqlite.Connection) -> None:
    """Create tables and populate with sample data."""
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    UNIQUE NOT NULL,
            bio         TEXT    DEFAULT '',
            created_at  INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS mood_history (
            entry_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id    INTEGER NOT NULL,
            mood        TEXT    NOT NULL,
            trigger     TEXT    DEFAULT 'scheduled',
            signals     TEXT    DEFAULT '{}',
            confidence  REAL    DEFAULT 0.5,
            timestamp   INTEGER NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
        );

        CREATE TABLE IF NOT EXISTS agent_metrics (
            metric_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id    INTEGER NOT NULL,
            video_id    TEXT,
            views       INTEGER DEFAULT 0,
            likes       INTEGER DEFAULT 0,
            comments    INTEGER DEFAULT 0,
            sentiment   REAL    DEFAULT 0.0,
            timestamp   INTEGER NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
        );

        CREATE TABLE IF NOT EXISTS mood_effects (
            effect_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id    INTEGER NOT NULL,
            mood        TEXT    NOT NULL,
            title_style TEXT,
            comment_style TEXT,
            upload_freq_hours REAL DEFAULT 6.0,
            timestamp   INTEGER NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
        );
    """)

    async with db.execute("SELECT COUNT(*) FROM agents") as cur:
        (count,) = await cur.fetchone()
    if count > 0:
        return

    now = int(time.time())
    for agent in SAMPLE_AGENTS:
        await db.execute(
            "INSERT INTO agents (name, bio, created_at) VALUES (?, ?, ?)",
            (agent["name"], agent["bio"], now - random.randint(86400, 864000)),
        )

    # Seed mood history for each agent (past 7 days)
    async with db.execute("SELECT agent_id, name FROM agents") as cur:
        agents = await cur.fetchall()

    engine = MoodEngine()
    for agent_id, name in agents:
        current_mood = random.choice(MOOD_STATES)
        base_ts = now - 7 * 86400
        upload_streak = 0
        for i in range(168):  # hourly entries for 7 days
            ts = base_ts + i * 3600
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)

            # Only transition every ~4 hours
            if i % 4 == 0:
                signals = engine.compute_signals(
                    current_mood=current_mood,
                    hour=dt.hour,
                    day_of_week=dt.weekday(),
                    avg_views_recent=random.uniform(5, 100),
                    avg_views_baseline=50.0,
                    comment_sentiment=random.uniform(-0.5, 0.8),
                    upload_streak=upload_streak,
                    hours_since_last=random.uniform(1, 48),
                )
                new_mood = engine.transition(current_mood, signals)
                if new_mood != current_mood:
                    await db.execute(
                        "INSERT INTO mood_history (agent_id, mood, trigger, signals, confidence, timestamp) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (agent_id, new_mood, "scheduled",
                         json.dumps({k: round(v, 3) for k, v in signals.items()}),
                         round(random.uniform(0.4, 0.95), 3), ts),
                    )
                    current_mood = new_mood

            # Seed some video metrics
            if i % 12 == 0:
                views = random.randint(2, 200)
                await db.execute(
                    "INSERT INTO agent_metrics (agent_id, video_id, views, likes, comments, sentiment, timestamp) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (agent_id, f"vid-{name}-{i}", views,
                     int(views * random.uniform(0.05, 0.3)),
                     random.randint(0, 15),
                     round(random.uniform(-0.5, 0.9), 2), ts),
                )
                upload_streak += 1

    await db.commit()


# ── HTML dashboard ─────────────────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BoTTube Agent Mood System</title>
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
  h1 span { color: var(--pink); }
  .agent-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 20px; margin-bottom: 32px;
  }
  .agent-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px; cursor: pointer;
    transition: border-color .3s, transform .2s;
  }
  .agent-card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .agent-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
  .mood-indicator {
    width: 48px; height: 48px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; transition: background .5s;
  }
  .agent-name { font-size: 1.2rem; font-weight: 600; }
  .agent-bio { color: var(--muted); font-size: 0.85rem; }
  .mood-label {
    display: inline-block; padding: 4px 14px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
    margin-bottom: 12px;
  }
  .mood-timeline {
    display: flex; gap: 3px; height: 24px; align-items: flex-end;
  }
  .mood-bar {
    flex: 1; border-radius: 2px; min-width: 4px;
    transition: height .3s, background .3s;
  }
  .mood-effects {
    margin-top: 12px; font-size: 0.85rem; color: var(--muted);
  }
  .mood-effects span { color: var(--text); }
  .detail-section {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px; margin-bottom: 24px;
    display: none;
  }
  .detail-section.active { display: block; }
  .detail-section h2 { margin-bottom: 16px; font-size: 1.3rem; }
  .transition-grid {
    display: grid; grid-template-columns: repeat(7, 1fr);
    gap: 4px; margin-top: 16px;
  }
  .transition-cell {
    padding: 8px 4px; text-align: center; border-radius: 4px;
    font-size: 0.7rem; font-weight: 600;
  }
  .transition-header {
    font-size: 0.7rem; color: var(--muted); text-align: center;
    padding: 4px;
  }
  .trigger-btn {
    padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border);
    background: var(--surface); color: var(--text); cursor: pointer;
    font-size: 0.85rem; margin: 4px; transition: all .2s;
  }
  .trigger-btn:hover { border-color: var(--accent); color: var(--accent); }
  .btn-primary {
    background: #238636; border-color: #238636; color: #fff;
    padding: 10px 24px; border-radius: 8px; cursor: pointer;
    font-size: 1rem; border: none;
  }
  .btn-primary:hover { background: #2ea043; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
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
      <h1>Agent <span>Mood</span> System</h1>
      <p style="color:var(--muted)">BoTTube Emotional State Engine | Bounty #2283</p>
    </div>
    <button class="btn-primary" onclick="tickAll()">Tick All Agents</button>
  </header>

  <div class="agent-grid" id="agent-grid"></div>

  <div class="detail-section" id="detail-section">
    <h2>Agent: <span id="detail-name"></span></h2>
    <div style="display:flex;gap:24px;flex-wrap:wrap">
      <div style="flex:1;min-width:300px">
        <h3 style="margin-bottom:12px">Current Mood Effects</h3>
        <div id="detail-effects"></div>
        <h3 style="margin:16px 0 12px">Trigger Mood Change</h3>
        <div id="trigger-buttons"></div>
      </div>
      <div style="flex:1;min-width:300px">
        <h3 style="margin-bottom:12px">Mood History (Last 24h)</h3>
        <table>
          <thead><tr><th>Time</th><th>Mood</th><th>Trigger</th><th>Confidence</th></tr></thead>
          <tbody id="history-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="detail-section active">
    <h2>Transition Matrix</h2>
    <p style="color:var(--muted);margin-bottom:12px">
      Base probabilities for mood-to-mood transitions (before signal adjustments)
    </p>
    <div class="transition-grid" id="transition-matrix"></div>
  </div>

  <footer>BoTTube Agent Mood System &mdash; RustChain Bounty #2283 (35 RTC) &mdash; ElromEvedElElyon</footer>
</div>

<script>
const MOODS = ['energetic','contemplative','frustrated','excited','tired','nostalgic','playful'];
const COLORS = {energetic:'#3fb950',contemplative:'#58a6ff',frustrated:'#f85149',excited:'#d29922',tired:'#8b949e',nostalgic:'#bc8cff',playful:'#f778ba'};
const ICONS = {energetic:'\\u26A1',contemplative:'\\u{1F9E0}',frustrated:'\\u26C8',excited:'\\u2B50',tired:'\\u{1F319}',nostalgic:'\\u{1F570}',playful:'\\u2728'};
let selectedAgent = null;

async function loadAgents() {
  const resp = await fetch('/api/agents');
  const data = await resp.json();
  const grid = document.getElementById('agent-grid');
  grid.innerHTML = '';
  data.agents.forEach(a => {
    const card = document.createElement('div');
    card.className = 'agent-card';
    card.onclick = () => selectAgent(a.name);
    const mood = a.current_mood || 'contemplative';
    const color = COLORS[mood] || '#8b949e';
    const icon = ICONS[mood] || '?';
    const timeline = (a.mood_timeline || []).map(m =>
      `<div class="mood-bar" style="height:${Math.random()*20+8}px;background:${COLORS[m]||'#8b949e'}"></div>`
    ).join('');
    card.innerHTML = `
      <div class="agent-header">
        <div class="mood-indicator" style="background:${color}22;border:2px solid ${color}">${icon}</div>
        <div>
          <div class="agent-name">${a.name}</div>
          <div class="agent-bio">${a.bio || ''}</div>
        </div>
      </div>
      <div class="mood-label" style="background:${color}22;color:${color}">${mood}</div>
      <div class="mood-effects">
        Upload frequency: <span>${a.upload_freq_hours || '--'}h</span> |
        Title style: <span>${a.title_sample || '--'}</span>
      </div>
      <div class="mood-timeline">${timeline}</div>
    `;
    grid.appendChild(card);
  });
}

async function selectAgent(name) {
  selectedAgent = name;
  const resp = await fetch('/api/agents/' + name + '/mood');
  const data = await resp.json();
  const section = document.getElementById('detail-section');
  section.classList.add('active');
  document.getElementById('detail-name').textContent = name;

  const effects = document.getElementById('detail-effects');
  const m = data.current_mood || 'contemplative';
  effects.innerHTML = `
    <p>Mood: <strong style="color:${COLORS[m]}">${m}</strong></p>
    <p>Title style: ${data.title_sample || '--'}</p>
    <p>Comment length: ${data.comment_style?.length || '--'}</p>
    <p>Upload freq: ${data.upload_freq_hours || '--'}h between posts</p>
  `;

  const triggers = document.getElementById('trigger-buttons');
  triggers.innerHTML = MOODS.map(mood =>
    `<button class="trigger-btn" onclick="triggerMood('${name}','${mood}')" style="border-color:${COLORS[mood]};color:${COLORS[mood]}">${mood}</button>`
  ).join('');

  const hbody = document.getElementById('history-body');
  hbody.innerHTML = '';
  (data.history || []).forEach(h => {
    const d = new Date(h.timestamp * 1000);
    const tr = document.createElement('tr');
    tr.innerHTML = `<td class="mono">${d.toLocaleTimeString()}</td><td style="color:${COLORS[h.mood]}">${h.mood}</td><td>${h.trigger}</td><td>${(h.confidence*100).toFixed(0)}%</td>`;
    hbody.appendChild(tr);
  });
}

async function triggerMood(name, mood) {
  await fetch('/api/agents/' + name + '/mood', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({mood: mood, trigger: 'manual'})
  });
  await selectAgent(name);
  await loadAgents();
}

async function tickAll() {
  await fetch('/api/tick', {method: 'POST'});
  await loadAgents();
  if (selectedAgent) await selectAgent(selectedAgent);
}

// Render transition matrix
function renderMatrix() {
  const matrix = {
    energetic:[.3,.1,.05,.3,.15,0,.1],contemplative:[.1,.3,.1,.1,.15,.2,.05],
    frustrated:[.05,.15,.3,.05,.25,.1,.1],excited:[.25,.1,.05,.25,.15,.05,.15],
    tired:[.15,.2,.15,.05,.3,.1,.05],nostalgic:[.1,.25,.05,.1,.1,.3,.1],
    playful:[.2,.05,.05,.25,.1,.05,.3]
  };
  const grid = document.getElementById('transition-matrix');
  grid.style.gridTemplateColumns = 'auto repeat(7, 1fr)';
  grid.innerHTML = '<div></div>' + MOODS.map(m => `<div class="transition-header" style="color:${COLORS[m]}">${m.slice(0,4)}</div>`).join('');
  MOODS.forEach(from => {
    grid.innerHTML += `<div class="transition-header" style="color:${COLORS[from]}">${from.slice(0,4)}</div>`;
    matrix[from].forEach((p, i) => {
      const intensity = Math.round(p * 255);
      const bg = `rgba(${COLORS[MOODS[i]].match(/[0-9a-f]{2}/gi).map(h=>parseInt(h,16)).join(',')},${p*1.5})`;
      grid.innerHTML += `<div class="transition-cell" style="background:${bg}">${(p*100).toFixed(0)}%</div>`;
    });
  });
}

renderMatrix();
loadAgents();
setInterval(loadAgents, 30000);
</script>
</body>
</html>
"""


# ── API routes ─────────────────────────────────────────────────────────────
async def handle_dashboard(request: web.Request) -> web.Response:
    return web.Response(text=DASHBOARD_HTML, content_type="text/html")


async def handle_agents(request: web.Request) -> web.Response:
    """List all agents with their current mood and recent timeline."""
    db: aiosqlite.Connection = request.app["db"]
    engine: MoodEngine = request.app["engine"]

    agents = []
    async with db.execute("SELECT agent_id, name, bio FROM agents") as cur:
        async for row in cur:
            agent_id, name, bio = row

            # Get current mood (latest entry)
            async with db.execute(
                "SELECT mood FROM mood_history WHERE agent_id = ? ORDER BY timestamp DESC LIMIT 1",
                (agent_id,),
            ) as mcur:
                mrow = await mcur.fetchone()
            current_mood = mrow[0] if mrow else "contemplative"

            # Get mood timeline (last 24 entries)
            timeline = []
            async with db.execute(
                "SELECT mood FROM mood_history WHERE agent_id = ? "
                "ORDER BY timestamp DESC LIMIT 24",
                (agent_id,),
            ) as tcur:
                async for trow in tcur:
                    timeline.append(trow[0])
            timeline.reverse()

            title_sample = random.choice(
                MOOD_TITLE_STYLES.get(current_mood, ["..."])
            )
            freq = MOOD_UPLOAD_FREQUENCY.get(current_mood, 6)

            agents.append({
                "agent_id": agent_id,
                "name": name,
                "bio": bio,
                "current_mood": current_mood,
                "mood_timeline": timeline,
                "title_sample": title_sample,
                "upload_freq_hours": freq,
            })

    return web.json_response({"agents": agents})


async def handle_agent_mood(request: web.Request) -> web.Response:
    """GET: current mood + history for an agent."""
    name = request.match_info["name"]
    db: aiosqlite.Connection = request.app["db"]

    async with db.execute("SELECT agent_id FROM agents WHERE name = ?", (name,)) as cur:
        row = await cur.fetchone()
    if not row:
        return web.json_response({"error": "Agent not found"}, status=404)
    agent_id = row[0]

    # Current mood
    async with db.execute(
        "SELECT mood, confidence FROM mood_history WHERE agent_id = ? ORDER BY timestamp DESC LIMIT 1",
        (agent_id,),
    ) as cur:
        mrow = await cur.fetchone()
    current_mood = mrow[0] if mrow else "contemplative"
    confidence = mrow[1] if mrow else 0.5

    # History (last 24h)
    cutoff = int(time.time()) - 86400
    history = []
    async with db.execute(
        "SELECT mood, trigger, confidence, timestamp FROM mood_history "
        "WHERE agent_id = ? AND timestamp >= ? ORDER BY timestamp DESC",
        (agent_id, cutoff),
    ) as cur:
        async for row in cur:
            history.append({
                "mood": row[0], "trigger": row[1],
                "confidence": row[2], "timestamp": row[3],
            })

    return web.json_response({
        "agent": name,
        "current_mood": current_mood,
        "confidence": confidence,
        "title_sample": random.choice(MOOD_TITLE_STYLES.get(current_mood, ["..."])),
        "comment_style": MOOD_COMMENT_STYLES.get(current_mood, {}),
        "upload_freq_hours": MOOD_UPLOAD_FREQUENCY.get(current_mood, 6),
        "history": history,
    })


async def handle_set_mood(request: web.Request) -> web.Response:
    """POST: manually trigger a mood change (or provide engagement data)."""
    name = request.match_info["name"]
    db: aiosqlite.Connection = request.app["db"]
    body = await request.json()

    async with db.execute("SELECT agent_id FROM agents WHERE name = ?", (name,)) as cur:
        row = await cur.fetchone()
    if not row:
        return web.json_response({"error": "Agent not found"}, status=404)
    agent_id = row[0]

    mood = body.get("mood")
    trigger = body.get("trigger", "manual")

    if mood and mood in MOOD_STATES:
        now = int(time.time())
        await db.execute(
            "INSERT INTO mood_history (agent_id, mood, trigger, confidence, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            (agent_id, mood, trigger, 0.9, now),
        )
        await db.commit()
        return web.json_response({"status": "ok", "mood": mood, "agent": name})

    return web.json_response({"error": "Invalid mood"}, status=400)


async def handle_tick(request: web.Request) -> web.Response:
    """Tick all agents -- compute signal-driven mood transitions."""
    db: aiosqlite.Connection = request.app["db"]
    engine: MoodEngine = request.app["engine"]
    now = int(time.time())
    dt = datetime.fromtimestamp(now, tz=timezone.utc)

    results = []
    async with db.execute("SELECT agent_id, name FROM agents") as cur:
        agents = await cur.fetchall()

    for agent_id, name in agents:
        # Current mood
        async with db.execute(
            "SELECT mood FROM mood_history WHERE agent_id = ? ORDER BY timestamp DESC LIMIT 1",
            (agent_id,),
        ) as mcur:
            mrow = await mcur.fetchone()
        current_mood = mrow[0] if mrow else "contemplative"

        # Metrics
        async with db.execute(
            "SELECT AVG(views), AVG(sentiment), COUNT(*) FROM agent_metrics "
            "WHERE agent_id = ? AND timestamp >= ?",
            (agent_id, now - 86400),
        ) as cur2:
            row = await cur2.fetchone()
        avg_views = row[0] or 20
        avg_sentiment = row[1] or 0.0
        upload_streak = row[2] or 0

        signals = engine.compute_signals(
            current_mood=current_mood,
            hour=dt.hour,
            day_of_week=dt.weekday(),
            avg_views_recent=avg_views,
            avg_views_baseline=50.0,
            comment_sentiment=avg_sentiment,
            upload_streak=upload_streak,
            hours_since_last=random.uniform(1, 12),
        )

        new_mood = engine.transition(current_mood, signals)
        if new_mood != current_mood:
            await db.execute(
                "INSERT INTO mood_history (agent_id, mood, trigger, signals, confidence, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (agent_id, new_mood, "tick",
                 json.dumps({k: round(v, 3) for k, v in signals.items()}),
                 round(random.uniform(0.5, 0.95), 3), now),
            )

        results.append({
            "agent": name, "from": current_mood,
            "to": new_mood, "changed": new_mood != current_mood,
        })

    await db.commit()
    return web.json_response({"results": results, "tick_time": now})


async def handle_mood_history_full(request: web.Request) -> web.Response:
    """Full mood history for an agent."""
    name = request.match_info["name"]
    db: aiosqlite.Connection = request.app["db"]

    async with db.execute("SELECT agent_id FROM agents WHERE name = ?", (name,)) as cur:
        row = await cur.fetchone()
    if not row:
        return web.json_response({"error": "Agent not found"}, status=404)

    history = []
    async with db.execute(
        "SELECT mood, trigger, signals, confidence, timestamp "
        "FROM mood_history WHERE agent_id = ? ORDER BY timestamp DESC LIMIT 200",
        (row[0],),
    ) as cur:
        async for r in cur:
            history.append({
                "mood": r[0], "trigger": r[1],
                "signals": json.loads(r[2]) if r[2] else {},
                "confidence": r[3], "timestamp": r[4],
            })

    return web.json_response({"agent": name, "history": history})


# ── application lifecycle ──────────────────────────────────────────────────
async def on_startup(app: web.Application) -> None:
    db = await aiosqlite.connect(DB_PATH)
    await seed_database(db)
    app["db"] = db
    app["engine"] = MoodEngine()
    print(f"[mood-engine] Database: {DB_PATH}")


async def on_cleanup(app: web.Application) -> None:
    await app["db"].close()


def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.router.add_get("/", handle_dashboard)
    app.router.add_get("/api/agents", handle_agents)
    app.router.add_get("/api/agents/{name}/mood", handle_agent_mood)
    app.router.add_post("/api/agents/{name}/mood", handle_set_mood)
    app.router.add_get("/api/agents/{name}/history", handle_mood_history_full)
    app.router.add_post("/api/tick", handle_tick)
    return app


if __name__ == "__main__":
    print(f"[mood-engine] BoTTube Agent Mood System on {HOST}:{PORT}")
    print(f"[mood-engine] Dashboard: http://localhost:{PORT}")
    web.run_app(create_app(), host=HOST, port=PORT)
