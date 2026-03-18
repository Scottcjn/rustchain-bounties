-- ============================================================================
-- RustChain Governance Database Schema
-- ============================================================================
-- This schema provides on-chain governance for RTC holders
-- 
-- Tables:
--   - governance_proposals: Store all governance proposals
--   - governance_votes: Store all votes cast on proposals
--
-- Integration: Requires existing tables:
--   - attestations (wallet, timestamp)
--   - miners (wallet, hardware_type, antiquity_multiplier)
--   - balances (wallet, balance)
-- ============================================================================

-- ============================================================================
-- Proposals Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS governance_proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    proposal_type TEXT NOT NULL CHECK (proposal_type IN ('RIP', 'bounty', 'parameter_change', 'feature_activation', 'emergency')),
    proposer_wallet TEXT NOT NULL,
    proposer_stake REAL DEFAULT 0.0,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('draft', 'active', 'passed', 'failed', 'expired', 'vetoed')),
    parameter_key TEXT,
    parameter_value TEXT,
    votes_for REAL DEFAULT 0.0,
    votes_against REAL DEFAULT 0.0,
    votes_abstain REAL DEFAULT 0.0,
    quorum_met INTEGER DEFAULT 0,
    vetoed_by TEXT,
    veto_reason TEXT,
    execution_data TEXT,
    created_date TEXT DEFAULT (datetime('now')),
    updated_date TEXT DEFAULT (datetime('now'))
);

-- ============================================================================
-- Votes Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS governance_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id INTEGER NOT NULL,
    voter_wallet TEXT NOT NULL,
    voter_hardware TEXT,
    vote TEXT NOT NULL CHECK (vote IN ('for', 'against', 'abstain')),
    weight REAL NOT NULL,
    signature TEXT,
    voted_at INTEGER NOT NULL,
    voted_date TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (proposal_id) REFERENCES governance_proposals(id) ON DELETE CASCADE,
    UNIQUE(proposal_id, voter_wallet)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_proposals_status ON governance_proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_expires ON governance_proposals(expires_at);
CREATE INDEX IF NOT EXISTS idx_proposals_type ON governance_proposals(proposal_type);
CREATE INDEX IF NOT EXISTS idx_proposals_proposer ON governance_proposals(proposer_wallet);
CREATE INDEX IF NOT EXISTS idx_votes_proposal ON governance_votes(proposal_id);
CREATE INDEX IF NOT EXISTS idx_votes_voter ON governance_votes(voter_wallet);

-- ============================================================================
-- View: Active Proposals with Vote Summary
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_active_proposals AS
SELECT 
    p.id,
    p.title,
    p.description,
    p.proposal_type,
    p.proposer_wallet,
    p.created_at,
    p.expires_at,
    p.status,
    p.votes_for,
    p.votes_against,
    p.votes_abstain,
    (p.votes_for + p.votes_against + p.votes_abstain) as total_votes,
    p.quorum_met,
    CASE 
        WHEN p.status = 'active' AND p.expires_at > strftime('%s', 'now') THEN 
            (p.expires_at - strftime('%s', 'now'))
        ELSE 0
    END as time_remaining
FROM governance_proposals p
WHERE p.status = 'active';

-- ============================================================================
-- View: Proposal Results Summary
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_proposal_results AS
SELECT 
    p.id,
    p.title,
    p.proposal_type,
    p.status,
    p.votes_for,
    p.votes_against,
    p.votes_abstain,
    (p.votes_for + p.votes_against + p.votes_abstain) as total_votes,
    CASE 
        WHEN p.votes_for + p.votes_against + p.votes_abstain = 0 THEN 0
        ELSE CAST(p.votes_for AS REAL) / (p.votes_for + p.votes_against + p.votes_abstain) * 100
    END as for_pct,
    CASE 
        WHEN p.votes_for + p.votes_against + p.votes_abstain = 0 THEN 0
        ELSE CAST(p.votes_against AS REAL) / (p.votes_for + p.votes_against + p.votes_abstain) * 100
    END as against_pct,
    p.quorum_met,
    p.created_at,
    p.expires_at
FROM governance_proposals p;

-- ============================================================================
-- Hardware Antiquity Multipliers Reference
-- ============================================================================
-- This is for reference; actual multipliers come from the miners table
-- ============================================================================
-- Ultra-Vintage (1979-1995): 2.2x - 3.0x
--   Intel 386: 3.0x
--   Intel 486: 2.8-2.9x
--   Motorola 68000 series: 2.2-3.0x
--   MIPS R-series: 2.3-3.0x
--
-- Retro Consoles (1983-2001): 2.3x - 2.8x
--   NES 6502: 2.8x
--   SNES 65C816: 2.7x
--   PlayStation 1 MIPS: 2.8x
--
-- PowerPC (1994-2006): 2.5x
--   PowerPC G4: 2.5x
--   PowerPC G5: 2.5x
--
-- Sun SPARC (1987-present): 2.3x - 2.9x
--   SPARC V7: 2.9x
--   SPARC V8: 2.7x
--   SPARC V9: 2.5x
--   UltraSPARC: 2.3x
