#!/usr/bin/env python3
"""
Interactive RustChain Mining Simulator -- Try Before You Mine
=============================================================
Bounty #2301 | 40 RTC | RustChain

A web-based interactive simulator that shows how RustChain mining works
WITHOUT requiring real hardware. Educational tool for onboarding new miners.

Simulates: hardware detection, fingerprinting, attestation submission,
epoch participation (round-robin selection), and reward calculation
with antiquity multipliers.

Run
---
    pip install aiohttp aiosqlite
    python server.py            # starts on :8301
    open http://localhost:8301  # simulator

Author : ElromEvedElElyon
Resolves: rustchain-bounties#2301 (40 RTC)
"""

from __future__ import annotations

import asyncio
import hashlib
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
DB_PATH = os.environ.get("SIM_DB", "mining_simulator.db")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8301"))

# ── hardware definitions ───────────────────────────────────────────────────
HARDWARE_PROFILES = {
    "powerbook-g4": {
        "name": "PowerBook G4",
        "arch": "PowerPC-G4",
        "year": 2003,
        "multiplier": 2.5,
        "description": "Classic Apple PowerPC laptop. The older the hardware, the higher the multiplier.",
        "clock_mhz": 1250,
        "cache_kb": 512,
        "fingerprint_features": ["cache_timing", "branch_prediction", "altivec_latency"],
        "icon": "laptop",
        "color": "#3fb950",
    },
    "powermac-g5": {
        "name": "Power Mac G5",
        "arch": "PowerPC-G5",
        "year": 2004,
        "multiplier": 2.0,
        "description": "Apple's last PowerPC tower. Dual processors, serious compute for its era.",
        "clock_mhz": 2500,
        "cache_kb": 1024,
        "fingerprint_features": ["cache_timing", "branch_prediction", "vmx_latency"],
        "icon": "server",
        "color": "#58a6ff",
    },
    "modern-x86": {
        "name": "Modern x86-64",
        "arch": "x86_64-Haswell",
        "year": 2023,
        "multiplier": 1.0,
        "description": "Standard modern hardware. No antiquity bonus -- proves the value of old silicon.",
        "clock_mhz": 4500,
        "cache_kb": 16384,
        "fingerprint_features": ["cache_timing", "branch_prediction", "avx_timing"],
        "icon": "desktop",
        "color": "#d29922",
    },
    "vm-instance": {
        "name": "Virtual Machine",
        "arch": "VM-KVM",
        "year": 2024,
        "multiplier": 0.000000001,
        "description": "VMs are detected and earn virtually nothing. RustChain rewards REAL hardware.",
        "clock_mhz": 8000,
        "cache_kb": 32768,
        "fingerprint_features": ["hypervisor_detected", "uniform_timing", "no_physical_cache"],
        "icon": "cloud",
        "color": "#f85149",
    },
    "sparc-t5": {
        "name": "SPARC T5 Server",
        "arch": "SPARC-T5",
        "year": 2013,
        "multiplier": 1.8,
        "description": "Oracle SPARC server. Enterprise-grade exotic hardware with strong multiplier.",
        "clock_mhz": 3600,
        "cache_kb": 8192,
        "fingerprint_features": ["cache_timing", "branch_prediction", "sparc_specific"],
        "icon": "server",
        "color": "#bc8cff",
    },
    "power8-ibm": {
        "name": "IBM POWER8",
        "arch": "POWER8",
        "year": 2014,
        "multiplier": 1.5,
        "description": "IBM mainframe-grade processor. Serious compute with decent multiplier.",
        "clock_mhz": 4200,
        "cache_kb": 8192,
        "fingerprint_features": ["cache_timing", "branch_prediction", "smt8_detection"],
        "icon": "server",
        "color": "#f778ba",
    },
}

BASE_RTC_PER_EPOCH = 1.0
EPOCH_DURATION_SEC = 3600  # 1 hour


def blake2b_short(data: str) -> str:
    return hashlib.blake2b(data.encode(), digest_size=16).hexdigest()


# ── simulation engine ──────────────────────────────────────────────────────
class SimulationEngine:
    """Simulates the RustChain mining loop step by step."""

    def simulate_fingerprint(self, hw_id: str) -> dict:
        hw = HARDWARE_PROFILES.get(hw_id, HARDWARE_PROFILES["modern-x86"])
        features = {}
        for feat in hw["fingerprint_features"]:
            if feat == "hypervisor_detected":
                features[feat] = {"detected": True, "confidence": 0.99}
            elif feat == "uniform_timing":
                features[feat] = {"variance": 0.001, "suspicious": True}
            elif feat == "no_physical_cache":
                features[feat] = {"physical_cache": False}
            elif feat == "cache_timing":
                base = 2.0 + (2024 - hw["year"]) * 0.3
                jitter = random.uniform(-0.5, 0.5)
                features[feat] = {
                    "l1_latency_ns": round(base + jitter, 2),
                    "l2_latency_ns": round(base * 3.5 + jitter, 2),
                    "l3_latency_ns": round(base * 12 + jitter, 2) if hw["cache_kb"] > 2048 else None,
                    "variance": round(random.uniform(0.05, 0.4), 3),
                }
            elif feat == "branch_prediction":
                features[feat] = {
                    "miss_rate": round(random.uniform(0.02, 0.15), 4),
                    "btb_size_estimate": random.choice([256, 512, 1024, 2048, 4096]),
                }
            else:
                features[feat] = {
                    "latency_ns": round(random.uniform(1.0, 50.0), 2),
                    "detected": True,
                }

        fingerprint_hash = blake2b_short(
            f"{hw['arch']}-{hw['clock_mhz']}-{json.dumps(features, sort_keys=True)}"
        )
        is_vm = hw_id == "vm-instance"

        return {
            "hardware_id": hw_id,
            "architecture": hw["arch"],
            "fingerprint": fingerprint_hash,
            "features": features,
            "vm_detected": is_vm,
            "trust_score": 0.01 if is_vm else round(random.uniform(0.75, 0.99), 4),
            "clock_mhz": hw["clock_mhz"],
            "cache_kb": hw["cache_kb"],
        }

    def simulate_attestation(self, hw_id: str, fingerprint: dict, epoch: int) -> dict:
        hw = HARDWARE_PROFILES.get(hw_id, HARDWARE_PROFILES["modern-x86"])
        now = int(time.time())
        nonce = blake2b_short(f"{now}-{random.random()}")

        payload = {
            "miner_id": f"sim-{hw_id}-{blake2b_short(hw_id)[:8]}",
            "epoch": epoch,
            "timestamp": now,
            "nonce": nonce,
            "fingerprint": fingerprint["fingerprint"],
            "architecture": hw["arch"],
            "challenge_response": blake2b_short(f"{nonce}-{fingerprint['fingerprint']}"),
        }

        # Validation
        if fingerprint["vm_detected"]:
            return {
                "payload": payload,
                "accepted": True,  # accepted but severely penalized
                "warnings": ["VM detected -- multiplier reduced to near-zero"],
                "penalty": "0.000000001x multiplier applied",
            }

        return {
            "payload": payload,
            "accepted": True,
            "warnings": [],
            "trust_score": fingerprint["trust_score"],
        }

    def simulate_epoch_selection(self, hw_id: str, epoch: int) -> dict:
        hw = HARDWARE_PROFILES.get(hw_id, HARDWARE_PROFILES["modern-x86"])
        # Simulate round-robin selection with other miners
        all_miners = [
            {"id": f"sim-{k}-xxx", "arch": v["arch"], "multiplier": v["multiplier"]}
            for k, v in HARDWARE_PROFILES.items()
        ]
        random.shuffle(all_miners)
        our_miner = f"sim-{hw_id}-xxx"
        selected = all_miners[: random.randint(2, len(all_miners))]
        our_selected = any(m["id"] == our_miner for m in selected)

        return {
            "epoch": epoch,
            "total_miners": len(all_miners),
            "selected_count": len(selected),
            "your_miner": our_miner,
            "you_selected": our_selected,
            "selected_miners": [
                {"id": m["id"], "arch": m["arch"], "multiplier": m["multiplier"]}
                for m in selected
            ],
            "selection_method": "weighted_round_robin",
        }

    def simulate_reward(self, hw_id: str, epoch: int, was_selected: bool) -> dict:
        hw = HARDWARE_PROFILES.get(hw_id, HARDWARE_PROFILES["modern-x86"])
        if not was_selected:
            return {
                "epoch": epoch,
                "base_reward": 0,
                "multiplier": hw["multiplier"],
                "final_reward": 0,
                "reason": "Not selected for this epoch",
            }

        base = BASE_RTC_PER_EPOCH
        multiplier = hw["multiplier"]
        trust_bonus = random.uniform(0.0, 0.1)
        final = base * multiplier + trust_bonus

        return {
            "epoch": epoch,
            "base_reward": base,
            "multiplier": multiplier,
            "trust_bonus": round(trust_bonus, 4),
            "final_reward": round(final, 6),
            "hardware": hw["name"],
            "architecture": hw["arch"],
        }


# ── database ───────────────────────────────────────────────────────────────
async def seed_database(db: aiosqlite.Connection) -> None:
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS simulation_sessions (
            session_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            hardware_id TEXT    NOT NULL,
            epochs_run  INTEGER DEFAULT 0,
            total_rtc   REAL    DEFAULT 0.0,
            started_at  INTEGER NOT NULL,
            last_epoch  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS simulation_epochs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL,
            epoch       INTEGER NOT NULL,
            hardware_id TEXT    NOT NULL,
            selected    INTEGER DEFAULT 0,
            reward      REAL    DEFAULT 0.0,
            fingerprint TEXT    DEFAULT '',
            timestamp   INTEGER NOT NULL,
            FOREIGN KEY (session_id) REFERENCES simulation_sessions(session_id)
        );

        CREATE TABLE IF NOT EXISTS leaderboard (
            entry_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            hardware_id TEXT    NOT NULL,
            total_rtc   REAL    DEFAULT 0.0,
            epochs_run  INTEGER DEFAULT 0,
            avg_reward  REAL    DEFAULT 0.0,
            last_run    INTEGER NOT NULL
        );
    """)

    # Seed leaderboard with sample data
    async with db.execute("SELECT COUNT(*) FROM leaderboard") as cur:
        (count,) = await cur.fetchone()
    if count > 0:
        return

    now = int(time.time())
    for hw_id, hw in HARDWARE_PROFILES.items():
        epochs = random.randint(50, 500)
        avg_reward = BASE_RTC_PER_EPOCH * hw["multiplier"] * 0.6  # ~60% selection rate
        total = round(avg_reward * epochs, 2)
        await db.execute(
            "INSERT INTO leaderboard (hardware_id, total_rtc, epochs_run, avg_reward, last_run) "
            "VALUES (?, ?, ?, ?, ?)",
            (hw_id, total, epochs, round(avg_reward, 4), now),
        )
    await db.commit()


# ── HTML dashboard ─────────────────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RustChain Mining Simulator</title>
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
  .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
  header { text-align: center; padding: 32px 0; margin-bottom: 24px; }
  h1 { font-size: 2.2rem; margin-bottom: 8px; }
  h1 span { color: var(--green); }
  .subtitle { color: var(--muted); font-size: 1.1rem; }
  .hw-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px; margin-bottom: 32px;
  }
  .hw-card {
    background: var(--surface); border: 2px solid var(--border);
    border-radius: 12px; padding: 20px; cursor: pointer;
    transition: all .3s; position: relative; overflow: hidden;
  }
  .hw-card:hover { transform: translateY(-4px); }
  .hw-card.selected { border-width: 3px; }
  .hw-card .multiplier {
    position: absolute; top: 12px; right: 12px;
    padding: 4px 12px; border-radius: 16px; font-weight: 700;
    font-size: 0.9rem;
  }
  .hw-name { font-size: 1.2rem; font-weight: 600; margin-bottom: 4px; }
  .hw-arch { color: var(--muted); font-size: 0.85rem; margin-bottom: 8px; }
  .hw-desc { font-size: 0.85rem; color: var(--muted); margin-bottom: 12px; }
  .hw-specs { font-size: 0.8rem; color: var(--muted); }
  .hw-specs span { color: var(--text); }
  .sim-controls {
    display: flex; gap: 16px; justify-content: center; margin-bottom: 32px;
    flex-wrap: wrap;
  }
  .btn {
    padding: 12px 32px; border-radius: 8px; border: none;
    cursor: pointer; font-size: 1rem; font-weight: 600;
    transition: all .2s;
  }
  .btn-start { background: #238636; color: #fff; font-size: 1.1rem; }
  .btn-start:hover { background: #2ea043; }
  .btn-start:disabled { background: #30363d; cursor: not-allowed; }
  .btn-step { background: var(--surface); color: var(--text); border: 1px solid var(--border); }
  .btn-step:hover { border-color: var(--accent); }
  .btn-reset { background: var(--surface); color: var(--red); border: 1px solid var(--red); }
  .epoch-select { display: flex; gap: 8px; align-items: center; }
  .epoch-select label { color: var(--muted); }
  .epoch-select select {
    padding: 10px; border-radius: 8px; border: 1px solid var(--border);
    background: var(--surface); color: var(--text); font-size: 1rem;
  }
  .simulation-area {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px; margin-bottom: 24px;
    min-height: 300px;
  }
  .step-indicator {
    display: flex; gap: 4px; margin-bottom: 24px; justify-content: center;
  }
  .step {
    width: 120px; padding: 8px; text-align: center; border-radius: 8px;
    font-size: 0.8rem; font-weight: 600; background: var(--bg);
    border: 1px solid var(--border); color: var(--muted);
    transition: all .3s;
  }
  .step.active { border-color: var(--accent); color: var(--accent); background: rgba(88,166,255,0.08); }
  .step.done { border-color: var(--green); color: var(--green); background: rgba(63,185,80,0.08); }
  .step-content { margin-top: 16px; }
  .fingerprint-visual {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 12px;
  }
  .fp-item {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 14px;
  }
  .fp-item .fp-label { color: var(--muted); font-size: 0.8rem; margin-bottom: 4px; }
  .fp-item .fp-value { font-family: monospace; font-size: 0.9rem; }
  .fp-item.warning { border-color: var(--red); }
  .reward-comparison {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px; margin-top: 16px;
  }
  .reward-card {
    padding: 16px; border-radius: 8px; text-align: center;
    border: 1px solid var(--border); background: var(--bg);
  }
  .reward-card .hw-label { font-size: 0.85rem; margin-bottom: 4px; }
  .reward-card .reward-val { font-size: 1.5rem; font-weight: 700; }
  .reward-card .mult { font-size: 0.8rem; color: var(--muted); }
  .log-area {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px; max-height: 300px;
    overflow-y: auto; font-family: monospace; font-size: 0.8rem;
    line-height: 1.8;
  }
  .log-area .log-entry { padding: 2px 0; }
  .log-entry.success { color: var(--green); }
  .log-entry.warn { color: var(--yellow); }
  .log-entry.error { color: var(--red); }
  .log-entry.info { color: var(--accent); }
  .earnings-chart {
    margin-top: 24px; background: var(--surface);
    border: 1px solid var(--border); border-radius: 12px; padding: 24px;
  }
  .earnings-chart h2 { margin-bottom: 16px; font-size: 1.2rem; }
  .chart-bars { display: flex; gap: 4px; align-items: flex-end; height: 200px; }
  .chart-bar {
    flex: 1; border-radius: 4px 4px 0 0; transition: height .5s;
    min-width: 8px; position: relative;
  }
  .chart-bar:hover::after {
    content: attr(data-tooltip); position: absolute; bottom: 100%;
    left: 50%; transform: translateX(-50%); background: var(--surface);
    border: 1px solid var(--border); padding: 4px 8px; border-radius: 4px;
    font-size: 0.75rem; white-space: nowrap;
  }
  .total-earnings {
    text-align: center; margin-top: 16px; font-size: 2rem; font-weight: 700;
  }
  .cta {
    text-align: center; margin-top: 32px; padding: 24px;
    background: var(--surface); border-radius: 12px;
    border: 1px solid var(--border);
  }
  .cta h2 { margin-bottom: 8px; }
  .cta a {
    display: inline-block; margin-top: 12px; padding: 14px 40px;
    background: #238636; color: #fff; text-decoration: none;
    border-radius: 8px; font-size: 1.1rem; font-weight: 600;
  }
  footer {
    margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border);
    color: var(--muted); font-size: 0.85rem; text-align: center;
  }
  @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:.5; } }
  .pulsing { animation: pulse 1s infinite; }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>RustChain <span>Mining</span> Simulator</h1>
    <p class="subtitle">Try Before You Mine -- No Hardware Required</p>
  </header>

  <h2 style="margin-bottom:16px;text-align:center">1. Choose Your Hardware</h2>
  <div class="hw-grid" id="hw-grid"></div>

  <div class="sim-controls">
    <div class="epoch-select">
      <label>Epochs to simulate:</label>
      <select id="epoch-count">
        <option value="1">1 (quick)</option>
        <option value="5">5</option>
        <option value="10" selected>10</option>
        <option value="25">25</option>
        <option value="50">50</option>
      </select>
    </div>
    <button class="btn btn-start" id="start-btn" onclick="startSimulation()" disabled>
      Select Hardware to Start
    </button>
    <button class="btn btn-reset" onclick="resetSim()">Reset</button>
  </div>

  <div class="step-indicator">
    <div class="step" id="step-fp">Fingerprint</div>
    <div class="step" id="step-attest">Attestation</div>
    <div class="step" id="step-select">Selection</div>
    <div class="step" id="step-reward">Reward</div>
  </div>

  <div class="simulation-area">
    <div class="step-content" id="step-content">
      <p style="text-align:center;color:var(--muted);padding:40px">
        Select your hardware above and click Start to begin the simulation
      </p>
    </div>
  </div>

  <div class="log-area" id="log-area">
    <div class="log-entry info">[simulator] Ready. Select hardware and click Start.</div>
  </div>

  <div class="earnings-chart">
    <h2>Epoch Earnings</h2>
    <div class="chart-bars" id="chart-bars"></div>
    <div class="total-earnings">Total: <span id="total-rtc">0.000000</span> RTC</div>
  </div>

  <h2 style="margin:32px 0 16px;text-align:center">Architecture Reward Comparison</h2>
  <div class="reward-comparison" id="reward-comparison"></div>

  <div class="cta">
    <h2>Ready to mine for real?</h2>
    <p style="color:var(--muted)">Download the RustChain miner and start earning RTC with your hardware</p>
    <a href="https://github.com/Scottcjn/Rustchain/releases" target="_blank">
      Download RustChain Miner
    </a>
  </div>

  <footer>RustChain Mining Simulator &mdash; Bounty #2301 (40 RTC) &mdash; ElromEvedElElyon</footer>
</div>

<script>
const HW = %HARDWARE_JSON%;
let selectedHW = null;
let simRunning = false;
let epochResults = [];

function renderHardware() {
  const grid = document.getElementById('hw-grid');
  grid.innerHTML = '';
  Object.entries(HW).forEach(([id, hw]) => {
    const card = document.createElement('div');
    card.className = 'hw-card' + (selectedHW === id ? ' selected' : '');
    card.style.borderColor = selectedHW === id ? hw.color : '';
    card.onclick = () => { selectedHW = id; renderHardware(); updateStartBtn(); };
    card.innerHTML = `
      <div class="multiplier" style="background:${hw.color}22;color:${hw.color}">${hw.multiplier}x</div>
      <div class="hw-name" style="color:${hw.color}">${hw.name}</div>
      <div class="hw-arch">${hw.arch} (${hw.year})</div>
      <div class="hw-desc">${hw.description}</div>
      <div class="hw-specs">Clock: <span>${hw.clock_mhz} MHz</span> | Cache: <span>${hw.cache_kb} KB</span></div>
    `;
    grid.appendChild(card);
  });

  // Reward comparison
  const comp = document.getElementById('reward-comparison');
  comp.innerHTML = '';
  Object.entries(HW).forEach(([id, hw]) => {
    const reward = (1.0 * hw.multiplier).toFixed(6);
    const card = document.createElement('div');
    card.className = 'reward-card';
    card.style.borderColor = selectedHW === id ? hw.color : '';
    card.innerHTML = `
      <div class="hw-label" style="color:${hw.color}">${hw.name}</div>
      <div class="reward-val" style="color:${hw.color}">${reward}</div>
      <div class="mult">RTC/epoch (${hw.multiplier}x)</div>
    `;
    comp.appendChild(card);
  });
}

function updateStartBtn() {
  const btn = document.getElementById('start-btn');
  if (selectedHW) {
    btn.disabled = false;
    btn.textContent = 'Start Mining Simulation';
  } else {
    btn.disabled = true;
    btn.textContent = 'Select Hardware to Start';
  }
}

function log(msg, cls='') {
  const area = document.getElementById('log-area');
  const entry = document.createElement('div');
  entry.className = 'log-entry ' + cls;
  entry.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
  area.appendChild(entry);
  area.scrollTop = area.scrollHeight;
}

function setStep(step) {
  ['fp','attest','select','reward'].forEach(s => {
    const el = document.getElementById('step-' + s);
    el.classList.remove('active', 'done');
  });
  const steps = ['fp','attest','select','reward'];
  const idx = steps.indexOf(step);
  steps.forEach((s, i) => {
    const el = document.getElementById('step-' + s);
    if (i < idx) el.classList.add('done');
    if (i === idx) el.classList.add('active');
  });
}

async function startSimulation() {
  if (!selectedHW || simRunning) return;
  simRunning = true;
  epochResults = [];
  const epochs = parseInt(document.getElementById('epoch-count').value);
  const btn = document.getElementById('start-btn');
  btn.disabled = true;
  btn.textContent = 'Simulating...';

  log('Starting simulation with ' + HW[selectedHW].name + ' for ' + epochs + ' epochs', 'info');

  try {
    const resp = await fetch('/api/simulate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({hardware_id: selectedHW, epochs: epochs})
    });
    const data = await resp.json();

    for (let i = 0; i < data.epochs.length; i++) {
      const ep = data.epochs[i];
      await simulateEpochVisual(ep, i + 1, data.epochs.length);
      epochResults.push(ep);
      updateChart();
      await sleep(600);
    }

    log('Simulation complete! Total earned: ' + data.total_rtc.toFixed(6) + ' RTC', 'success');
    log('Average per epoch: ' + data.avg_reward.toFixed(6) + ' RTC', 'info');
  } catch(e) {
    log('Error: ' + e.message, 'error');
  }

  simRunning = false;
  btn.disabled = false;
  btn.textContent = 'Run Again';
}

async function simulateEpochVisual(ep, num, total) {
  const content = document.getElementById('step-content');

  // Step 1: Fingerprint
  setStep('fp');
  const fp = ep.fingerprint;
  content.innerHTML = '<h3>Epoch ' + ep.epoch + ' (' + num + '/' + total + ') -- Hardware Fingerprinting</h3>' +
    '<div class="fingerprint-visual">' +
    Object.entries(fp.features).map(([k, v]) => {
      const isWarn = v.suspicious || v.detected === true && k === 'hypervisor_detected';
      return '<div class="fp-item' + (isWarn ? ' warning' : '') + '">' +
        '<div class="fp-label">' + k + '</div>' +
        '<div class="fp-value">' + JSON.stringify(v) + '</div></div>';
    }).join('') +
    '</div>' +
    '<p style="margin-top:12px">Fingerprint: <code>' + fp.fingerprint + '</code> | Trust: ' +
    '<span style="color:' + (fp.trust_score > 0.5 ? 'var(--green)' : 'var(--red)') + '">' +
    (fp.trust_score * 100).toFixed(1) + '%</span></p>';
  log('Epoch ' + ep.epoch + ': Fingerprint computed: ' + fp.fingerprint.slice(0,16) + '...', fp.vm_detected ? 'error' : 'success');
  await sleep(400);

  // Step 2: Attestation
  setStep('attest');
  const att = ep.attestation;
  content.innerHTML = '<h3>Epoch ' + ep.epoch + ' -- Attestation Submission</h3>' +
    '<div class="fp-item" style="margin-top:12px"><div class="fp-label">Payload</div>' +
    '<div class="fp-value">' + JSON.stringify(att.payload, null, 2) + '</div></div>' +
    (att.warnings.length ? '<p style="color:var(--red);margin-top:8px">' + att.warnings.join(', ') + '</p>' : '') +
    '<p style="margin-top:8px;color:var(--green)">Attestation accepted</p>';
  log('Epoch ' + ep.epoch + ': Attestation submitted' + (att.warnings.length ? ' (WARNINGS!)' : ''), att.warnings.length ? 'warn' : 'success');
  await sleep(400);

  // Step 3: Selection
  setStep('select');
  const sel = ep.selection;
  content.innerHTML = '<h3>Epoch ' + ep.epoch + ' -- Round-Robin Selection</h3>' +
    '<p>' + sel.selected_count + ' of ' + sel.total_miners + ' miners selected</p>' +
    '<p style="font-size:1.3rem;margin:12px 0;font-weight:700;color:' +
    (sel.you_selected ? 'var(--green)' : 'var(--red)') + '">' +
    (sel.you_selected ? 'YOU WERE SELECTED!' : 'Not selected this epoch') + '</p>' +
    '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">' +
    sel.selected_miners.map(m =>
      '<div style="padding:6px 12px;border-radius:6px;font-size:0.8rem;border:1px solid ' +
      (m.id === sel.your_miner ? 'var(--green)' : 'var(--border)') + ';background:' +
      (m.id === sel.your_miner ? 'rgba(63,185,80,0.1)' : 'var(--bg)') + '">' +
      m.arch + ' (' + m.multiplier + 'x)</div>'
    ).join('') + '</div>';
  log('Epoch ' + ep.epoch + ': Selection: ' + (sel.you_selected ? 'SELECTED' : 'not selected'), sel.you_selected ? 'success' : 'warn');
  await sleep(400);

  // Step 4: Reward
  setStep('reward');
  const rew = ep.reward;
  content.innerHTML = '<h3>Epoch ' + ep.epoch + ' -- Reward Calculation</h3>' +
    '<div style="text-align:center;padding:20px">' +
    '<div style="font-size:3rem;font-weight:700;color:' +
    (rew.final_reward > 0 ? 'var(--green)' : 'var(--muted)') + '">' +
    rew.final_reward.toFixed(6) + ' RTC</div>' +
    '<p style="color:var(--muted);margin-top:8px">' +
    'Base: ' + rew.base_reward + ' x Multiplier: ' + rew.multiplier + 'x' +
    (rew.trust_bonus ? ' + Trust bonus: ' + rew.trust_bonus : '') + '</p>' +
    '</div>';
  log('Epoch ' + ep.epoch + ': Reward: ' + rew.final_reward.toFixed(6) + ' RTC', rew.final_reward > 0 ? 'success' : 'warn');
}

function updateChart() {
  const bars = document.getElementById('chart-bars');
  const total = epochResults.reduce((s, e) => s + e.reward.final_reward, 0);
  document.getElementById('total-rtc').textContent = total.toFixed(6);
  const maxReward = Math.max(...epochResults.map(e => e.reward.final_reward), 0.001);

  bars.innerHTML = '';
  epochResults.forEach(e => {
    const pct = (e.reward.final_reward / maxReward) * 100;
    const bar = document.createElement('div');
    bar.className = 'chart-bar';
    const hw = HW[selectedHW] || {};
    bar.style.height = Math.max(pct, 2) + '%';
    bar.style.background = e.reward.final_reward > 0 ? (hw.color || 'var(--green)') : 'var(--border)';
    bar.setAttribute('data-tooltip', 'E' + e.epoch + ': ' + e.reward.final_reward.toFixed(4) + ' RTC');
    bars.appendChild(bar);
  });
}

function resetSim() {
  epochResults = [];
  document.getElementById('chart-bars').innerHTML = '';
  document.getElementById('total-rtc').textContent = '0.000000';
  document.getElementById('step-content').innerHTML =
    '<p style="text-align:center;color:var(--muted);padding:40px">Select hardware and click Start</p>';
  document.getElementById('log-area').innerHTML =
    '<div class="log-entry info">[simulator] Reset. Ready for new simulation.</div>';
  ['fp','attest','select','reward'].forEach(s =>
    document.getElementById('step-' + s).classList.remove('active','done'));
  simRunning = false;
  updateStartBtn();
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

renderHardware();
</script>
</body>
</html>
"""


# ── API routes ─────────────────────────────────────────────────────────────
async def handle_dashboard(request: web.Request) -> web.Response:
    html = DASHBOARD_HTML.replace(
        "%HARDWARE_JSON%", json.dumps(HARDWARE_PROFILES)
    )
    return web.Response(text=html, content_type="text/html")


async def handle_hardware(request: web.Request) -> web.Response:
    return web.json_response({"hardware": HARDWARE_PROFILES})


async def handle_simulate(request: web.Request) -> web.Response:
    """Run a full mining simulation for N epochs."""
    body = await request.json()
    hw_id = body.get("hardware_id", "modern-x86")
    num_epochs = min(body.get("epochs", 10), 100)
    db: aiosqlite.Connection = request.app["db"]
    engine: SimulationEngine = request.app["engine"]

    if hw_id not in HARDWARE_PROFILES:
        return web.json_response({"error": "Unknown hardware"}, status=400)

    now = int(time.time())
    await db.execute(
        "INSERT INTO simulation_sessions (hardware_id, started_at) VALUES (?, ?)",
        (hw_id, now),
    )
    await db.commit()
    async with db.execute("SELECT last_insert_rowid()") as cur:
        (session_id,) = await cur.fetchone()

    base_epoch = random.randint(400, 900)
    epochs = []
    total_rtc = 0.0

    for i in range(num_epochs):
        epoch = base_epoch + i
        fp = engine.simulate_fingerprint(hw_id)
        attest = engine.simulate_attestation(hw_id, fp, epoch)
        selection = engine.simulate_epoch_selection(hw_id, epoch)
        reward = engine.simulate_reward(hw_id, epoch, selection["you_selected"])

        total_rtc += reward["final_reward"]

        await db.execute(
            "INSERT INTO simulation_epochs "
            "(session_id, epoch, hardware_id, selected, reward, fingerprint, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, epoch, hw_id,
             1 if selection["you_selected"] else 0,
             reward["final_reward"], fp["fingerprint"], now + i),
        )

        epochs.append({
            "epoch": epoch,
            "fingerprint": fp,
            "attestation": attest,
            "selection": selection,
            "reward": reward,
        })

    await db.execute(
        "UPDATE simulation_sessions SET epochs_run=?, total_rtc=?, last_epoch=? WHERE session_id=?",
        (num_epochs, round(total_rtc, 6), base_epoch + num_epochs - 1, session_id),
    )
    await db.commit()

    return web.json_response({
        "session_id": session_id,
        "hardware": HARDWARE_PROFILES[hw_id]["name"],
        "total_epochs": num_epochs,
        "total_rtc": round(total_rtc, 6),
        "avg_reward": round(total_rtc / max(num_epochs, 1), 6),
        "epochs": epochs,
    })


async def handle_leaderboard(request: web.Request) -> web.Response:
    db: aiosqlite.Connection = request.app["db"]
    entries = []
    async with db.execute(
        "SELECT hardware_id, total_rtc, epochs_run, avg_reward FROM leaderboard "
        "ORDER BY total_rtc DESC"
    ) as cur:
        async for row in cur:
            hw = HARDWARE_PROFILES.get(row[0], {})
            entries.append({
                "hardware_id": row[0],
                "hardware_name": hw.get("name", row[0]),
                "multiplier": hw.get("multiplier", 1.0),
                "total_rtc": row[1],
                "epochs_run": row[2],
                "avg_reward": row[3],
            })
    return web.json_response({"leaderboard": entries})


async def handle_calculator(request: web.Request) -> web.Response:
    """What would you earn? Calculator."""
    hw_id = request.query.get("hardware", "modern-x86")
    hours = int(request.query.get("hours", "24"))
    hw = HARDWARE_PROFILES.get(hw_id, HARDWARE_PROFILES["modern-x86"])
    epochs = hours  # 1 epoch per hour
    selection_rate = 0.6 if hw["multiplier"] > 0.001 else 0.01
    avg_per_epoch = BASE_RTC_PER_EPOCH * hw["multiplier"] * selection_rate
    total = avg_per_epoch * epochs

    return web.json_response({
        "hardware": hw["name"],
        "multiplier": hw["multiplier"],
        "hours": hours,
        "epochs": epochs,
        "selection_rate": selection_rate,
        "avg_per_epoch": round(avg_per_epoch, 6),
        "projected_total": round(total, 6),
        "daily_projection": round(avg_per_epoch * 24, 6),
        "monthly_projection": round(avg_per_epoch * 720, 6),
    })


# ── application lifecycle ──────────────────────────────────────────────────
async def on_startup(app: web.Application) -> None:
    db = await aiosqlite.connect(DB_PATH)
    await seed_database(db)
    app["db"] = db
    app["engine"] = SimulationEngine()
    print(f"[simulator] Database: {DB_PATH}")


async def on_cleanup(app: web.Application) -> None:
    await app["db"].close()


def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.router.add_get("/", handle_dashboard)
    app.router.add_get("/api/hardware", handle_hardware)
    app.router.add_post("/api/simulate", handle_simulate)
    app.router.add_get("/api/leaderboard", handle_leaderboard)
    app.router.add_get("/api/calculator", handle_calculator)
    return app


if __name__ == "__main__":
    print(f"[simulator] RustChain Mining Simulator on {HOST}:{PORT}")
    print(f"[simulator] Dashboard: http://localhost:{PORT}")
    web.run_app(create_app(), host=HOST, port=PORT)
