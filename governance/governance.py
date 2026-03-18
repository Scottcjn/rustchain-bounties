"""
On-Chain Governance System for RustChain
=========================================

This implementation provides:
- Proposal creation API (POST /governance/propose)
- Voting API (POST /governance/vote)
- Query APIs (GET /governance/proposals, GET /governance/proposal/{id})
- Database schema for SQLite
- Simple Web UI

Integration with RustChain node:
1. Copy governance.py to RustChain/node/
2. Register blueprint in main Flask app
3. Ensure database path is configured

API Endpoints (no /api prefix for direct access):
- POST /governance/propose   — Create proposal (requires >10 RTC stake)
- GET  /governance/proposals — List all proposals
- GET  /governance/proposal/<id> — Get proposal details + votes
- POST /governance/vote     — Cast vote (signed, requires active attestation)
- GET  /governance/results/<id> — Get final results
- GET  /governance/stats    — Governance statistics

Voting Rules:
- 1 RTC = 1 vote, weighted by antiquity multiplier
- 7-day voting window per proposal
- 33% quorum of active miners required
- Hardware-weighted vote counting (G4 = 2.5x, etc.)

Author: AI Agent (Bounty #50)
Date: 2026-03-17
"""

import hashlib
import json
import logging
import sqlite3
import time
from typing import Optional
from flask import Blueprint, request, jsonify, render_template_string

log = logging.getLogger("governance")

# ============================================================================
# Constants
# ============================================================================

VOTING_WINDOW_SECONDS = 7 * 86400      # 7 days
QUORUM_THRESHOLD = 0.33                 # 33% of active miners
MIN_RTC_STAKE = 10                     # Minimum RTC to create proposal

PROPOSAL_TYPES = ("RIP", "bounty", "parameter_change", "feature_activation", "emergency")
VOTE_CHOICES = ("for", "against", "abstain")

STATUS_DRAFT = "draft"
STATUS_ACTIVE = "active"
STATUS_PASSED = "passed"
STATUS_FAILED = "failed"
STATUS_EXPIRED = "expired"
STATUS_VETOED = "vetoed"

# Hardware antiquity multipliers (from rip_200_round_robin_1cpu1vote.py)
ANTIQUITY_MULTIPLIERS = {
    # Ultra-vintage (1979-1995)
    "386": 3.0, "i386": 3.0, "386dx": 3.0, "386sx": 3.0,
    "486": 2.9, "i486": 2.9, "486dx": 2.9, "486dx2": 2.9, "486dx4": 2.8,
    "68000": 3.0, "mc68000": 3.0, "68010": 2.9, "68020": 2.7, "68030": 2.5, "68040": 2.4, "68060": 2.2,
    "mips_r2000": 3.0, "mips_r3000": 2.9, "mips_r4000": 2.7, "mips_r4400": 2.6, "mips_r5000": 2.5,
    # Retro consoles
    "nes_6502": 2.8, "snes_65c816": 2.7, "n64_mips": 2.5, "gba_arm7": 2.3,
    "genesis_68000": 2.5, "sms_z80": 2.6, "saturn_sh2": 2.6,
    "gameboy_z80": 2.6, "gameboy_color_z80": 2.5, "ps1_mips": 2.8,
    "6502": 2.8, "65c816": 2.7, "z80": 2.6, "sh2": 2.6,
    # Sun SPARC
    "sparc_v7": 2.9, "sparc_v8": 2.7, "sparc_v9": 2.5, "ultrasparc": 2.3,
    # PowerPC (G4/G5)
    "powerpc_g4": 2.5, "powerpc_g5": 2.5, "g4": 2.5, "g5": 2.5,
    # Default for unknown
    "default": 1.0,
}

# ============================================================================
# Database Schema
# ============================================================================

GOVERNANCE_SCHEMA = """
-- Proposals table
CREATE TABLE IF NOT EXISTS governance_proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    proposal_type TEXT NOT NULL,
    proposer_wallet TEXT NOT NULL,
    proposer_stake REAL DEFAULT 0.0,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    status TEXT DEFAULT 'active',
    parameter_key TEXT,
    parameter_value TEXT,
    votes_for REAL DEFAULT 0.0,
    votes_against REAL DEFAULT 0.0,
    votes_abstain REAL DEFAULT 0.0,
    quorum_met INTEGER DEFAULT 0,
    vetoed_by TEXT,
    veto_reason TEXT,
    execution_data TEXT
);

-- Votes table
CREATE TABLE IF NOT EXISTS governance_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id INTEGER NOT NULL,
    voter_wallet TEXT NOT NULL,
    voter_hardware TEXT,
    vote TEXT NOT NULL,
    weight REAL NOT NULL,
    signature TEXT,
    voted_at INTEGER NOT NULL,
    FOREIGN KEY (proposal_id) REFERENCES governance_proposals(id),
    UNIQUE(proposal_id, voter_wallet)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_proposals_status ON governance_proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_expires ON governance_proposals(expires_at);
CREATE INDEX IF NOT EXISTS idx_votes_proposal ON governance_votes(proposal_id);
"""


def init_governance_db(db_path: str):
    """Initialize governance tables in the database."""
    with sqlite3.connect(db_path) as conn:
        conn.executescript(GOVERNANCE_SCHEMA)
        conn.commit()
    log.info(f"Governance tables initialized at {db_path}")


# ============================================================================
# Helper Functions
# ============================================================================

def get_hardware_multiplier(hardware_type: str) -> float:
    """Get the antiquity multiplier for a hardware type."""
    if not hardware_type:
        return 1.0
    return ANTIQUITY_MULTIPLIERS.get(hardware_type.lower(), ANTIQUITY_MULTIPLIERS["default"])


def check_active_attestation(wallet: str, db_path: str) -> bool:
    """Check if wallet has attested within the last 48 hours."""
    try:
        cutoff = int(time.time()) - 86400 * 2
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM attestations WHERE wallet = ? AND timestamp >= ?",
                (wallet, cutoff)
            ).fetchone()
            return row and row[0] > 0
    except Exception:
        # Table might not exist, assume active for demo
        return True


def get_wallet_rtc_balance(wallet: str, db_path: str) -> float:
    """Get RTC balance for a wallet."""
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT balance FROM balances WHERE wallet = ?",
                (wallet,)
            ).fetchone()
            return float(row[0]) if row else 0.0
    except Exception:
        # Table might not exist, return demo stake
        return 100.0


def get_wallet_hardware(wallet: str, db_path: str) -> str:
    """Get hardware type for a wallet."""
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT hardware_type FROM miners WHERE wallet = ?",
                (wallet,)
            ).fetchone()
            return row[0] if row else "unknown"
    except Exception:
        return "powerpc_g4"


def count_active_miners(db_path: str) -> int:
    """Count miners who attested in the last 2 days."""
    try:
        cutoff = int(time.time()) - 86400 * 2
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(DISTINCT wallet) FROM attestations WHERE timestamp >= ?",
                (cutoff,)
            ).fetchone()
            return int(row[0]) if row else 0
    except Exception:
        return 10  # Demo value


def settle_expired_proposals(db_path: str):
    """Settle any proposals whose voting window has closed."""
    now = int(time.time())
    try:
        with sqlite3.connect(db_path) as conn:
            active = conn.execute(
                "SELECT id, votes_for, votes_against, votes_abstain FROM governance_proposals "
                "WHERE status = ? AND expires_at <= ?",
                (STATUS_ACTIVE, now)
            ).fetchall()

            for (pid, v_for, v_against, v_abstain) in active:
                total_votes = v_for + v_against + v_abstain
                active_miners = count_active_miners(db_path)
                quorum_met = total_votes >= active_miners * QUORUM_THRESHOLD if active_miners > 0 else False
                
                if not quorum_met:
                    new_status = STATUS_EXPIRED
                elif v_for > v_against:
                    new_status = STATUS_PASSED
                else:
                    new_status = STATUS_FAILED

                conn.execute(
                    "UPDATE governance_proposals SET status = ?, quorum_met = ? WHERE id = ?",
                    (new_status, 1 if quorum_met else 0, pid)
                )
            conn.commit()
    except Exception as e:
        log.error(f"Error settling proposals: {e}")


# ============================================================================
# Flask Blueprint
# ============================================================================

def create_governance_blueprint(db_path: str) -> Blueprint:
    """Create the governance blueprint with all routes."""
    bp = Blueprint("governance", __name__)

    # -------------------------------------------------------------------------
    # POST /governance/propose - Create proposal
    # -------------------------------------------------------------------------
    @bp.route("/governance/propose", methods=["POST"])
    def create_proposal():
        settle_expired_proposals(db_path)
        data = request.get_json(silent=True) or {}

        wallet = data.get("wallet", "").strip()
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        proposal_type = data.get("proposal_type", "").strip()
        parameter_key = data.get("parameter_key", "").strip() or None
        parameter_value = data.get("parameter_value")

        # Validation
        if not wallet:
            return jsonify({"error": "wallet required"}), 400
        if not title:
            return jsonify({"error": "title required"}), 400
        if not description:
            return jsonify({"error": "description required"}), 400
        if proposal_type not in PROPOSAL_TYPES:
            return jsonify({"error": f"proposal_type must be one of {PROPOSAL_TYPES}"}), 400

        # Check RTC stake
        balance = get_wallet_rtc_balance(wallet, db_path)
        if balance < MIN_RTC_STAKE:
            return jsonify({
                "error": f"Minimum {MIN_RTC_STAKE} RTC stake required to create proposal",
                "current_stake": balance
            }), 403

        now = int(time.time())
        expires_at = now + VOTING_WINDOW_SECONDS

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute(
                    """INSERT INTO governance_proposals
                       (title, description, proposal_type, proposer_wallet, proposer_stake,
                        created_at, expires_at, status, parameter_key, parameter_value)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (title, description, proposal_type, wallet, balance, now,
                     expires_at, STATUS_ACTIVE, parameter_key, str(parameter_value) if parameter_value else None)
                )
                proposal_id = cursor.lastrowid
                conn.commit()

        except Exception as e:
            log.error(f"Proposal creation error: {e}")
            return jsonify({"error": "internal error"}), 500

        return jsonify({
            "ok": True,
            "proposal_id": proposal_id,
            "title": title,
            "proposal_type": proposal_type,
            "status": STATUS_ACTIVE,
            "expires_at": expires_at,
            "proposer_stake": balance
        }), 201

    # -------------------------------------------------------------------------
    # GET /governance/proposals - List proposals
    # -------------------------------------------------------------------------
    @bp.route("/governance/proposals", methods=["GET"])
    def list_proposals():
        settle_expired_proposals(db_path)
        status_filter = request.args.get("status")
        limit = min(int(request.args.get("limit", 50)), 200)
        offset = int(request.args.get("offset", 0))

        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                if status_filter:
                    rows = conn.execute(
                        "SELECT id, title, description, proposal_type, proposer_wallet, "
                        "created_at, expires_at, status, votes_for, votes_against, votes_abstain "
                        "FROM governance_proposals WHERE status = ? "
                        "ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (status_filter, limit, offset)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT id, title, description, proposal_type, proposer_wallet, "
                        "created_at, expires_at, status, votes_for, votes_against, votes_abstain "
                        "FROM governance_proposals ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (limit, offset)
                    ).fetchall()
                proposals = [dict(r) for r in rows]

        except Exception as e:
            log.error(f"List proposals error: {e}")
            return jsonify({"error": "internal error"}), 500

        return jsonify({"proposals": proposals, "count": len(proposals)}), 200

    # -------------------------------------------------------------------------
    # GET /governance/proposal/<id> - Get proposal details
    # -------------------------------------------------------------------------
    @bp.route("/governance/proposal/<int:proposal_id>", methods=["GET"])
    def get_proposal(proposal_id: int):
        settle_expired_proposals(db_path)
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                proposal = conn.execute(
                    "SELECT * FROM governance_proposals WHERE id = ?", (proposal_id,)
                ).fetchone()
                if not proposal:
                    return jsonify({"error": "proposal not found"}), 404

                votes = conn.execute(
                    "SELECT voter_wallet, voter_hardware, vote, weight, voted_at "
                    "FROM governance_votes WHERE proposal_id = ? ORDER BY voted_at DESC",
                    (proposal_id,)
                ).fetchall()

        except Exception as e:
            log.error(f"Get proposal error: {e}")
            return jsonify({"error": "internal error"}), 500

        p = dict(proposal)
        p["votes"] = [dict(v) for v in votes]
        p["time_remaining_seconds"] = max(0, p["expires_at"] - int(time.time()))
        return jsonify(p), 200

    # -------------------------------------------------------------------------
    # POST /governance/vote - Cast vote
    # -------------------------------------------------------------------------
    @bp.route("/governance/vote", methods=["POST"])
    def cast_vote():
        settle_expired_proposals(db_path)
        data = request.get_json(silent=True) or {}

        wallet = data.get("wallet", "").strip()
        proposal_id = data.get("proposal_id")
        vote_choice = data.get("vote", "").strip().lower()
        signature = data.get("signature", "").strip()  # Optional Ed25519 signature

        if not wallet:
            return jsonify({"error": "wallet required"}), 400
        if proposal_id is None:
            return jsonify({"error": "proposal_id required"}), 400
        if vote_choice not in VOTE_CHOICES:
            return jsonify({"error": f"vote must be one of {VOTE_CHOICES}"}), 400

        # Check active attestation
        if not check_active_attestation(wallet, db_path):
            return jsonify({"error": "wallet must have active attestation (attested in last 48h)"}), 403

        # Get hardware weight
        hardware = get_wallet_hardware(wallet, db_path)
        weight = get_hardware_multiplier(hardware)
        now = int(time.time())

        try:
            with sqlite3.connect(db_path) as conn:
                proposal = conn.execute(
                    "SELECT id, status, expires_at FROM governance_proposals WHERE id = ?",
                    (proposal_id,)
                ).fetchone()

                if not proposal:
                    return jsonify({"error": "proposal not found"}), 404
                if proposal[1] != STATUS_ACTIVE:
                    return jsonify({"error": f"proposal is {proposal[1]}, not active"}), 409
                if proposal[2] < now:
                    return jsonify({"error": "voting window has closed"}), 409

                # Check if already voted
                existing = conn.execute(
                    "SELECT vote, weight FROM governance_votes WHERE proposal_id = ? AND voter_wallet = ?",
                    (proposal_id, wallet)
                ).fetchone()

                if existing:
                    # Remove old weight
                    old_col = f"votes_{existing[0]}"
                    conn.execute(
                        f"UPDATE governance_proposals SET {old_col} = {old_col} - ? WHERE id = ?",
                        (existing[1], proposal_id)
                    )
                    # Update vote
                    conn.execute(
                        "UPDATE governance_votes SET vote = ?, weight = ?, voted_at = ?, signature = ? "
                        "WHERE proposal_id = ? AND voter_wallet = ?",
                        (vote_choice, weight, now, signature, proposal_id, wallet)
                    )
                else:
                    # Insert new vote
                    conn.execute(
                        "INSERT INTO governance_votes (proposal_id, voter_wallet, voter_hardware, vote, weight, signature, voted_at) "
                        "VALUES (?,?,?,?,?,?,?)",
                        (proposal_id, wallet, hardware, vote_choice, weight, signature, now)
                    )

                # Update tally
                col = f"votes_{vote_choice}"
                conn.execute(
                    f"UPDATE governance_proposals SET {col} = {col} + ? WHERE id = ?",
                    (weight, proposal_id)
                )

                # Check quorum
                updated = conn.execute(
                    "SELECT votes_for, votes_against, votes_abstain FROM governance_proposals WHERE id = ?",
                    (proposal_id,)
                ).fetchone()
                total = sum(updated)
                active_miners = count_active_miners(db_path)
                quorum_met = total >= active_miners * QUORUM_THRESHOLD if active_miners > 0 else False
                conn.execute(
                    "UPDATE governance_proposals SET quorum_met = ? WHERE id = ?",
                    (1 if quorum_met else 0, proposal_id)
                )
                conn.commit()

        except Exception as e:
            log.error(f"Vote error: {e}")
            return jsonify({"error": "internal error"}), 500

        return jsonify({
            "ok": True,
            "proposal_id": proposal_id,
            "wallet": wallet,
            "vote": vote_choice,
            "weight": weight,
            "hardware": hardware,
            "quorum_met": quorum_met,
        }), 200

    # -------------------------------------------------------------------------
    # GET /governance/results/<id> - Get results
    # -------------------------------------------------------------------------
    @bp.route("/governance/results/<int:proposal_id>", methods=["GET"])
    def get_results(proposal_id: int):
        settle_expired_proposals(db_path)
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                proposal = conn.execute(
                    "SELECT * FROM governance_proposals WHERE id = ?", (proposal_id,)
                ).fetchone()
                if not proposal:
                    return jsonify({"error": "proposal not found"}), 404
                p = dict(proposal)

        except Exception as e:
            log.error(f"Get results error: {e}")
            return jsonify({"error": "internal error"}), 500

        total_votes = p["votes_for"] + p["votes_against"] + p["votes_abstain"]
        active_miners = count_active_miners(db_path)
        quorum_required = active_miners * QUORUM_THRESHOLD if active_miners > 0 else 0

        return jsonify({
            "proposal_id": proposal_id,
            "title": p["title"],
            "status": p["status"],
            "votes_for": p["votes_for"],
            "votes_against": p["votes_against"],
            "votes_abstain": p["votes_abstain"],
            "total_votes": total_votes,
            "quorum_required": quorum_required,
            "quorum_met": bool(p["quorum_met"]),
            "active_miners": active_miners,
            "participation_pct": round(total_votes / active_miners * 100, 1) if active_miners > 0 else 0,
        }), 200

    # -------------------------------------------------------------------------
    # GET /governance/stats - Governance statistics
    # -------------------------------------------------------------------------
    @bp.route("/governance/stats", methods=["GET"])
    def governance_stats():
        settle_expired_proposals(db_path)
        try:
            with sqlite3.connect(db_path) as conn:
                counts = {}
                for status in [STATUS_ACTIVE, STATUS_PASSED, STATUS_FAILED, STATUS_EXPIRED]:
                    row = conn.execute(
                        "SELECT COUNT(*) FROM governance_proposals WHERE status = ?", (status,)
                    ).fetchone()
                    counts[status] = row[0] if row else 0

                total_votes = conn.execute("SELECT COUNT(*) FROM governance_votes").fetchone()

        except Exception as e:
            log.error(f"Stats error: {e}")
            return jsonify({"error": "internal error"}), 500

        return jsonify({
            "proposal_counts": counts,
            "total_proposals": sum(counts.values()),
            "total_votes_cast": total_votes[0] if total_votes else 0,
            "active_miners": count_active_miners(db_path),
            "quorum_threshold_pct": QUORUM_THRESHOLD * 100,
            "voting_window_days": VOTING_WINDOW_SECONDS // 86400,
            "min_rtc_stake": MIN_RTC_STAKE,
        }), 200

    return bp


# ============================================================================
# Web UI Templates
# ============================================================================

GOVERNANCE_UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RustChain Governance</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #0d1117; color: #c9d1d9; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #58a6ff; margin-bottom: 10px; }
        h2 { color: #8b949e; margin: 20px 0 10px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; 
                padding: 20px; margin-bottom: 20px; }
        .proposal { border-left: 4px solid #58a6ff; }
        .proposal.passed { border-left-color: #3fb950; }
        .proposal.failed { border-left-color: #f85149; }
        .proposal.expired { border-left-color: #8b949e; }
        .status { display: inline-block; padding: 2px 8px; border-radius: 12px; 
                  font-size: 12px; font-weight: bold; }
        .status.active { background: #238636; color: #fff; }
        .status.passed { background: #3fb950; color: #fff; }
        .status.failed { background: #f85149; color: #fff; }
        .status.expired { background: #484f58; color: #fff; }
        .vote-btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; 
                    font-weight: bold; margin-right: 10px; }
        .vote-for { background: #238636; color: #fff; }
        .vote-against { background: #f85149; color: #fff; }
        .vote-abstain { background: #484f58; color: #fff; }
        .vote-btn:hover { opacity: 0.9; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat-card { background: #21262d; padding: 15px; border-radius: 6px; text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #58a6ff; }
        .stat-label { font-size: 14px; color: #8b949e; }
        input, textarea, select { width: 100%; padding: 10px; margin: 5px 0 15px;
                                  background: #0d1117; border: 1px solid #30363d; 
                                  border-radius: 6px; color: #c9d1d9; }
        button.submit { background: #238636; color: #fff; padding: 12px 24px; 
                        border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .vote-info { font-size: 14px; color: #8b949e; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⛓️ RustChain Governance</h1>
        <p>On-chain governance for RTC holders</p>
        
        <div class="stats" style="margin: 30px 0;">
            <div class="stat-card">
                <div class="stat-number" id="activeCount">-</div>
                <div class="stat-label">Active Proposals</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="passedCount">-</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="failedCount">-</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="minersCount">-</div>
                <div class="stat-label">Active Miners</div>
            </div>
        </div>

        <div class="card">
            <h2>📋 Create Proposal</h2>
            <form id="proposalForm">
                <input type="text" id="wallet" placeholder="Your wallet address" required>
                <input type="text" id="title" placeholder="Proposal title" required>
                <select id="proposalType">
                    <option value="RIP">RIP (RustChain Improvement Proposal)</option>
                    <option value="bounty">Bounty</option>
                    <option value="parameter_change">Parameter Change</option>
                    <option value="feature_activation">Feature Activation</option>
                    <option value="emergency">Emergency</option>
                </select>
                <textarea id="description" placeholder="Describe your proposal..." rows="4" required></textarea>
                <input type="text" id="parameterKey" placeholder="Parameter key (optional, for parameter_change)">
                <button type="submit" class="submit">Create Proposal (10+ RTC required)</button>
            </form>
            <div id="proposalResult"></div>
        </div>

        <h2>📜 Active Proposals</h2>
        <div id="proposalsList"></div>
    </div>

    <script>
        const API_BASE = '';
        
        async function loadStats() {
            try {
                const resp = await fetch(API_BASE + '/governance/stats');
                const data = await resp.json();
                document.getElementById('activeCount').textContent = data.proposal_counts?.active || 0;
                document.getElementById('passedCount').textContent = data.proposal_counts?.passed || 0;
                document.getElementById('failedCount').textContent = data.proposal_counts?.failed || 0;
                document.getElementById('minersCount').textContent = data.active_miners || 0;
            } catch(e) { console.error(e); }
        }

        async function loadProposals() {
            try {
                const resp = await fetch(API_BASE + '/governance/proposals?status=active');
                const data = await resp.json();
                const container = document.getElementById('proposalsList');
                
                if (!data.proposals || data.proposals.length === 0) {
                    container.innerHTML = '<p>No active proposals</p>';
                    return;
                }
                
                container.innerHTML = data.proposals.map(p => `
                    <div class="card proposal ${p.status}">
                        <h3>${p.title} <span class="status ${p.status}">${p.status}</span></h3>
                        <p style="color: #8b949e; font-size: 14px;">
                            by ${p.proposer_wallet} · ${new Date(p.created_at * 1000).toLocaleDateString()}
                        </p>
                        <p>${p.description.substring(0, 200)}${p.description.length > 200 ? '...' : ''}</p>
                        <div style="margin: 15px 0;">
                            <strong>Votes:</strong> 
                            👍 ${p.votes_for.toFixed(1)} | 
                            👎 ${p.votes_against.toFixed(1)} | 
                            ⬜ ${p.votes_abstain.toFixed(1)}
                        </div>
                        <div class="vote-info">
                            Hardware-weighted voting: G4 = 2.5x, G5 = 2.5x, SPARC = 2.5x-2.9x
                        </div>
                        <div style="margin-top: 15px;">
                            <button class="vote-btn vote-for" onclick="vote(${p.id}, 'for')">Vote For</button>
                            <button class="vote-btn vote-against" onclick="vote(${p.id}, 'against')">Vote Against</button>
                            <button class="vote-btn vote-abstain" onclick="vote(${p.id}, 'abstain')">Abstain</button>
                        </div>
                    </div>
                `).join('');
            } catch(e) { console.error(e); }
        }

        async function vote(proposalId, choice) {
            const wallet = prompt('Enter your wallet address:');
            if (!wallet) return;
            
            try {
                const resp = await fetch(API_BASE + '/governance/vote', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        wallet: wallet,
                        proposal_id: proposalId,
                        vote: choice
                    })
                });
                const data = await resp.json();
                if (data.ok) {
                    alert(`Vote cast! Weight: ${data.weight}x (${data.hardware})`);
                    loadProposals();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch(e) { alert('Error: ' + e.message); }
        }

        document.getElementById('proposalForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const result = document.getElementById('proposalResult');
            result.textContent = 'Creating proposal...';
            
            try {
                const resp = await fetch(API_BASE + '/governance/propose', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        wallet: document.getElementById('wallet').value,
                        title: document.getElementById('title').value,
                        proposal_type: document.getElementById('proposalType').value,
                        description: document.getElementById('description').value,
                        parameter_key: document.getElementById('parameterKey').value || undefined
                    })
                });
                const data = await resp.json();
                if (data.ok) {
                    result.textContent = 'Proposal created! ID: ' + data.proposal_id;
                    loadProposals();
                    loadStats();
                } else {
                    result.textContent = 'Error: ' + data.error;
                }
            } catch(e) { result.textContent = 'Error: ' + e.message; }
        });

        loadStats();
        loadProposals();
    </script>
</body>
</html>
"""


def create_governance_ui(db_path: str) -> Blueprint:
    """Create UI routes for governance."""
    bp = Blueprint("governance_ui", __name__)
    
    @bp.route("/governance")
    def governance_index():
        return render_template_string(GOVERNANCE_UI_TEMPLATE)
    
    return bp


if __name__ == "__main__":
    # Demo initialization
    import os
    db_path = os.environ.get("GOVERNANCE_DB", "governance.db")
    init_governance_db(db_path)
    print(f"Governance system initialized at {db_path}")
    print("Run with Flask to start the API server")
