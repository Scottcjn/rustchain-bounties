#!/usr/bin/env python3
"""SophiaCore Attestation Inspector — Admin Dashboard.

Self-contained HTML+CSS+JS dashboard for human spot-checks of
CAUTIOUS/SUSPICIOUS attestation verdicts.

Served as an inline template from sophia_inspector.py at GET /sophia/dashboard.

RIP-306: SophiaCore Attestation Inspector
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Dashboard HTML (fully self-contained, no external dependencies)
# ---------------------------------------------------------------------------

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SophiaCore Attestation Inspector — Admin Dashboard</title>
<style>
:root {
  --bg-primary: #0f0f1a;
  --bg-secondary: #1a1a2e;
  --bg-card: #16213e;
  --bg-hover: #1a2744;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent-blue: #3b82f6;
  --accent-purple: #8b5cf6;
  --accent-green: #10b981;
  --accent-yellow: #f59e0b;
  --accent-orange: #f97316;
  --accent-red: #ef4444;
  --border: #2d3a57;
  --radius: 10px;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font);
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
}

.container { max-width: 1400px; margin: 0 auto; padding: 24px; }

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
}
.header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.header .subtitle {
  color: var(--text-secondary);
  font-size: 0.85rem;
}
.header .phase-badge {
  background: rgba(139,92,246,0.15);
  color: var(--accent-purple);
  border: 1px solid rgba(139,92,246,0.3);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}
.stat-label { color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
.stat-value { font-size: 2rem; font-weight: 700; margin: 4px 0; }
.stat-value.green { color: var(--accent-green); }
.stat-value.yellow { color: var(--accent-yellow); }
.stat-value.orange { color: var(--accent-orange); }
.stat-value.red { color: var(--accent-red); }
.stat-value.blue { color: var(--accent-blue); }

/* Filters */
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
}
.filters input, .filters select {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: 6px;
  font-family: var(--font);
  font-size: 0.9rem;
}
.filters input:focus, .filters select:focus {
  outline: none;
  border-color: var(--accent-blue);
}
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-family: var(--font);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-refresh { background: var(--accent-blue); color: white; }
.btn-refresh:hover { background: #2563eb; }
.btn-approve { background: var(--accent-green); color: white; }
.btn-approve:hover { background: #059669; }
.btn-reject { background: var(--accent-red); color: white; }
.btn-reject:hover { background: #dc2626; }
.btn-sm { padding: 4px 10px; font-size: 0.8rem; }

/* Table */
.table-container {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow-x: auto;
}
table { width: 100%; border-collapse: collapse; }
thead th {
  background: var(--bg-secondary);
  padding: 12px 16px;
  text-align: left;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
}
tbody tr {
  border-bottom: 1px solid rgba(45,58,87,0.5);
  transition: background 0.15s;
  cursor: pointer;
}
tbody tr:hover { background: var(--bg-hover); }
tbody td { padding: 12px 16px; font-size: 0.9rem; }

.verdict-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}
.verdict-APPROVED { background: rgba(16,185,129,0.15); color: var(--accent-green); }
.verdict-CAUTIOUS { background: rgba(245,158,11,0.15); color: var(--accent-yellow); }
.verdict-SUSPICIOUS { background: rgba(249,115,22,0.15); color: var(--accent-orange); }
.verdict-REJECTED { background: rgba(239,68,68,0.15); color: var(--accent-red); }

.confidence-bar {
  width: 60px;
  height: 6px;
  background: var(--bg-secondary);
  border-radius: 3px;
  overflow: hidden;
  display: inline-block;
  vertical-align: middle;
  margin-left: 6px;
}
.confidence-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }

/* Detail Panel */
.detail-panel {
  display: none;
  position: fixed;
  right: 0;
  top: 0;
  width: 520px;
  height: 100vh;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border);
  box-shadow: -8px 0 32px rgba(0,0,0,0.5);
  z-index: 100;
  overflow-y: auto;
  padding: 24px;
  animation: slideIn 0.25s ease-out;
}
@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
.detail-panel.open { display: block; }
.detail-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.5rem;
  cursor: pointer;
}
.detail-close:hover { color: var(--text-primary); }
.detail-section { margin-bottom: 20px; }
.detail-section h3 {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.detail-json {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.8rem;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
  color: var(--text-secondary);
}
.override-form { display: flex; flex-direction: column; gap: 10px; }
.override-form textarea {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 10px;
  border-radius: 6px;
  font-family: var(--font);
  resize: vertical;
  min-height: 60px;
}
.override-buttons { display: flex; gap: 8px; }

/* Loading */
.loading { text-align: center; padding: 40px; color: var(--text-muted); }
.spinner {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid var(--border);
  border-top-color: var(--accent-blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Advisory banner */
.advisory-banner {
  background: rgba(139,92,246,0.1);
  border: 1px solid rgba(139,92,246,0.3);
  border-radius: var(--radius);
  padding: 12px 20px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: var(--accent-purple);
}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>✨ SophiaCore Attestation Inspector</h1>
      <div class="subtitle">Sophia Elya — Hardware Attestation Review Dashboard</div>
    </div>
    <span class="phase-badge">Phase 1: Advisory</span>
  </div>

  <div class="advisory-banner">
    ℹ️ Phase 1 Advisory Mode — Verdicts are informational only and do not affect miner rewards or multipliers.
  </div>

  <div class="stats-grid" id="stats-grid">
    <div class="stat-card"><div class="stat-label">Total Inspections</div><div class="stat-value blue" id="stat-total">—</div></div>
    <div class="stat-card"><div class="stat-label">✨ Approved</div><div class="stat-value green" id="stat-approved">—</div></div>
    <div class="stat-card"><div class="stat-label">⚠️ Cautious</div><div class="stat-value yellow" id="stat-cautious">—</div></div>
    <div class="stat-card"><div class="stat-label">🔍 Suspicious</div><div class="stat-value orange" id="stat-suspicious">—</div></div>
    <div class="stat-card"><div class="stat-label">❌ Rejected</div><div class="stat-value red" id="stat-rejected">—</div></div>
    <div class="stat-card"><div class="stat-label">Pending Reviews</div><div class="stat-value yellow" id="stat-pending">—</div></div>
  </div>

  <div class="filters">
    <input type="text" id="filter-miner" placeholder="Search miner ID..." style="width: 220px;">
    <select id="filter-verdict">
      <option value="">All Verdicts</option>
      <option value="CAUTIOUS">⚠️ Cautious</option>
      <option value="SUSPICIOUS">🔍 Suspicious</option>
      <option value="APPROVED">✨ Approved</option>
      <option value="REJECTED">❌ Rejected</option>
    </select>
    <button class="btn btn-refresh" onclick="loadData()">↻ Refresh</button>
    <span style="color:var(--text-muted);font-size:0.8rem;margin-left:auto;" id="last-refresh">—</span>
  </div>

  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Miner</th>
          <th>Verdict</th>
          <th>Confidence</th>
          <th>Flags</th>
          <th>Model</th>
          <th>Latency</th>
          <th>Time</th>
          <th>Override</th>
        </tr>
      </thead>
      <tbody id="review-table">
        <tr><td colspan="9" class="loading"><div class="spinner"></div><br>Loading...</td></tr>
      </tbody>
    </table>
  </div>
</div>

<!-- Detail Panel -->
<div class="detail-panel" id="detail-panel">
  <button class="detail-close" onclick="closeDetail()">×</button>
  <h2 id="detail-title" style="margin-bottom:16px;"></h2>

  <div class="detail-section">
    <h3>Verdict</h3>
    <div id="detail-verdict"></div>
  </div>

  <div class="detail-section">
    <h3>Reasoning</h3>
    <div id="detail-reasoning" style="color:var(--text-secondary);font-size:0.9rem;"></div>
  </div>

  <div class="detail-section">
    <h3>Flags</h3>
    <div id="detail-flags"></div>
  </div>

  <div class="detail-section">
    <h3>Fingerprint Data</h3>
    <div class="detail-json" id="detail-fingerprint"></div>
  </div>

  <div class="detail-section">
    <h3>Inspection History</h3>
    <div id="detail-history"></div>
  </div>

  <div class="detail-section" id="override-section">
    <h3>Override Verdict</h3>
    <div class="override-form">
      <textarea id="override-reason" placeholder="Reason for override (required)..."></textarea>
      <div class="override-buttons">
        <button class="btn btn-approve" onclick="submitOverride('APPROVED')">✨ Approve</button>
        <button class="btn btn-reject" onclick="submitOverride('REJECTED')">❌ Reject</button>
      </div>
    </div>
  </div>
</div>

<script>
const API_BASE = window.location.origin;
let currentInspection = null;
let autoRefreshTimer = null;

const EMOJI = { APPROVED: '✨', CAUTIOUS: '⚠️', SUSPICIOUS: '🔍', REJECTED: '❌' };

async function api(path, opts) {
  const r = await fetch(API_BASE + path, opts);
  return r.json();
}

async function loadData() {
  try {
    const [stats, pending] = await Promise.all([
      api('/sophia/stats'),
      api('/sophia/pending'),
    ]);

    // Stats
    document.getElementById('stat-total').textContent = stats.total_inspections || 0;
    const bv = stats.by_verdict || {};
    document.getElementById('stat-approved').textContent = bv.APPROVED || 0;
    document.getElementById('stat-cautious').textContent = bv.CAUTIOUS || 0;
    document.getElementById('stat-suspicious').textContent = bv.SUSPICIOUS || 0;
    document.getElementById('stat-rejected').textContent = bv.REJECTED || 0;
    document.getElementById('stat-pending').textContent = stats.pending_reviews || 0;

    // Table
    const reviews = pending.reviews || [];
    const tbody = document.getElementById('review-table');
    const filterMiner = document.getElementById('filter-miner').value.toLowerCase();
    const filterVerdict = document.getElementById('filter-verdict').value;

    let filtered = reviews;
    if (filterMiner) filtered = filtered.filter(r => r.miner_id.toLowerCase().includes(filterMiner));
    if (filterVerdict) filtered = filtered.filter(r => r.verdict === filterVerdict);

    if (!filtered.length) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:var(--text-muted);padding:40px;">No reviews pending</td></tr>';
    } else {
      tbody.innerHTML = filtered.map(r => {
        const conf = (r.confidence * 100).toFixed(0);
        const confColor = r.confidence > 0.7 ? 'var(--accent-green)' : r.confidence > 0.4 ? 'var(--accent-yellow)' : 'var(--accent-red)';
        const flags = (r.flags || []).join(', ') || '—';
        const override = r.override_verdict ?
          `<span class="verdict-chip verdict-${r.override_verdict}">${EMOJI[r.override_verdict]} ${r.override_verdict}</span>` : '—';
        return `<tr onclick='showDetail(${JSON.stringify(r).replace(/'/g,"&#39;")})'>
          <td>#${r.id}</td>
          <td style="font-family:monospace;font-size:0.8rem;">${r.miner_id.substring(0,20)}${r.miner_id.length>20?'…':''}</td>
          <td><span class="verdict-chip verdict-${r.verdict}">${EMOJI[r.verdict] || ''} ${r.verdict}</span></td>
          <td>${conf}%<div class="confidence-bar"><div class="confidence-fill" style="width:${conf}%;background:${confColor}"></div></div></td>
          <td style="font-size:0.8rem;color:var(--text-muted);">${flags}</td>
          <td style="font-size:0.75rem;color:var(--text-muted);">${r.model_version||'—'}</td>
          <td>${r.latency_ms||0}ms</td>
          <td style="font-size:0.8rem;color:var(--text-muted);">${r.created_at||'—'}</td>
          <td>${override}</td>
        </tr>`;
      }).join('');
    }

    document.getElementById('last-refresh').textContent = 'Last refresh: ' + new Date().toLocaleTimeString();
  } catch (e) {
    console.error('Load failed:', e);
  }
}

async function showDetail(record) {
  currentInspection = record;
  document.getElementById('detail-title').textContent = `${EMOJI[record.verdict]} ${record.miner_id}`;
  document.getElementById('detail-verdict').innerHTML =
    `<span class="verdict-chip verdict-${record.verdict}">${EMOJI[record.verdict]} ${record.verdict}</span> — Confidence: ${(record.confidence*100).toFixed(1)}%`;
  document.getElementById('detail-reasoning').textContent = record.reasoning || 'No reasoning provided';
  document.getElementById('detail-flags').textContent = (record.flags||[]).join(', ') || 'None';

  const fpData = record.fingerprint_data || '{}';
  try {
    document.getElementById('detail-fingerprint').textContent = JSON.stringify(JSON.parse(fpData), null, 2);
  } catch { document.getElementById('detail-fingerprint').textContent = fpData; }

  // Fetch history
  try {
    const hist = await api(`/sophia/history/${encodeURIComponent(record.miner_id)}?limit=10`);
    const rows = (hist.inspections || []).map(h =>
      `<div style="padding:6px 0;border-bottom:1px solid var(--border);font-size:0.8rem;">
        <span class="verdict-chip verdict-${h.verdict}" style="font-size:0.75rem;">${EMOJI[h.verdict]} ${h.verdict}</span>
        ${(h.confidence*100).toFixed(0)}% — ${h.created_at}
        ${h.override_verdict ? ` → <span class="verdict-chip verdict-${h.override_verdict}" style="font-size:0.7rem;">Override: ${h.override_verdict}</span>` : ''}
      </div>`
    ).join('');
    document.getElementById('detail-history').innerHTML = rows || '<span style="color:var(--text-muted)">No history</span>';
  } catch { document.getElementById('detail-history').innerHTML = '<span style="color:var(--text-muted)">Failed to load</span>'; }

  // Show/hide override section based on existing override
  document.getElementById('override-section').style.display = record.override_verdict ? 'none' : 'block';
  document.getElementById('override-reason').value = '';
  document.getElementById('detail-panel').classList.add('open');
}

function closeDetail() {
  document.getElementById('detail-panel').classList.remove('open');
  currentInspection = null;
}

async function submitOverride(verdict) {
  if (!currentInspection) return;
  const reason = document.getElementById('override-reason').value.trim();
  if (!reason) { alert('Reason is required for overrides.'); return; }

  try {
    const result = await api('/sophia/override', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        inspection_id: currentInspection.id,
        verdict: verdict,
        reason: reason,
        admin: 'dashboard_user',
      }),
    });
    if (result.status === 'override_recorded') {
      closeDetail();
      loadData();
    } else {
      alert('Override failed: ' + (result.error || 'Unknown error'));
    }
  } catch (e) {
    alert('Override request failed: ' + e.message);
  }
}

// Filters
document.getElementById('filter-miner').addEventListener('input', loadData);
document.getElementById('filter-verdict').addEventListener('change', loadData);

// Close detail on Escape
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDetail(); });

// Initial load
loadData();

// Auto-refresh every 60s
autoRefreshTimer = setInterval(loadData, 60000);
</script>
</body>
</html>
"""
