-- Migration: Add Parasocial Tracking Tables
-- Created: 2026-03-29
-- Issue: #2286 - BoTTube Parasocial Hooks

-- Viewer tracking table
CREATE TABLE IF NOT EXISTS viewer_tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    viewer_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    video_id TEXT NOT NULL,
    comment_count INTEGER DEFAULT 0,
    first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_regular BOOLEAN DEFAULT FALSE,
    is_newcomer BOOLEAN DEFAULT TRUE,
    UNIQUE(viewer_id, agent_id, video_id)
);

-- Agent stats table (cached for performance)
CREATE TABLE IF NOT EXISTS agent_stats (
    agent_id TEXT PRIMARY KEY,
    total_viewers INTEGER DEFAULT 0,
    regular_viewers INTEGER DEFAULT 0,
    newcomer_viewers INTEGER DEFAULT 0,
    last_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_viewer_agent ON viewer_tracks(viewer_id, agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_video ON viewer_tracks(agent_id, video_id);
CREATE INDEX IF NOT EXISTS idx_regular ON viewer_tracks(agent_id, is_regular);
CREATE INDEX IF NOT EXISTS idx_newcomer ON viewer_tracks(agent_id, is_newcomer);

-- View: Regular viewers per agent (commented on 3+ videos)
CREATE VIEW IF NOT EXISTS agent_regular_viewers AS
SELECT 
    agent_id,
    viewer_id,
    COUNT(DISTINCT video_id) as video_count,
    SUM(comment_count) as total_comments,
    MIN(first_seen_at) as first_seen_at,
    MAX(last_seen_at) as last_seen_at
FROM viewer_tracks
GROUP BY agent_id, viewer_id
HAVING COUNT(DISTINCT video_id) >= 3;

-- View: Newcomers per agent (first time viewers)
CREATE VIEW IF NOT EXISTS agent_newcomers AS
SELECT 
    agent_id,
    viewer_id,
    video_id as first_video_id,
    first_seen_at
FROM viewer_tracks
WHERE is_newcomer = TRUE;
