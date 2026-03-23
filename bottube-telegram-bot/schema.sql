-- BoTTube Agent Memory Database Schema
-- Bounty #2285 - 40 RTC
-- Wallet: 9dRRMiHiJwjF3VW8pXtKDtpmmxAPFy3zWgV2JY5H6eeT

-- Videos table: stores agent video content
CREATE TABLE IF NOT EXISTS agent_videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    topics TEXT,              -- JSON array of topics
    opinions TEXT,            -- JSON array of opinions expressed
    predictions TEXT,         -- JSON array of predictions made
    upload_date TEXT,         -- ISO format date
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    series_name TEXT,         -- Name of series if part of one
    series_part INTEGER,      -- Part number in series
    content_hash TEXT,        -- MD5 hash for deduplication
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(video_id, agent_name)
);

-- Embeddings table: stores vector representations
CREATE TABLE IF NOT EXISTS video_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    embedding BLOB,           -- Binary vector (for sqlite-vec)
    tfidf_vector TEXT,        -- JSON sparse TF-IDF vector
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id, agent_name) REFERENCES agent_videos(video_id, agent_name),
    UNIQUE(video_id, agent_name)
);

-- Series tracking table
CREATE TABLE IF NOT EXISTS agent_series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    series_name TEXT NOT NULL,
    video_count INTEGER DEFAULT 0,
    last_updated TEXT,
    UNIQUE(agent_name, series_name)
);

-- Opinion history table: track opinion changes over time
CREATE TABLE IF NOT EXISTS opinion_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    topic TEXT NOT NULL,
    opinion TEXT NOT NULL,
    video_id TEXT,
    recorded_date TEXT DEFAULT CURRENT_TIMESTAMP,
    is_current INTEGER DEFAULT 1
);

-- Milestones table: track agent milestones
CREATE TABLE IF NOT EXISTS agent_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    milestone_type TEXT NOT NULL,  -- 'video_count', 'views', 'likes', etc.
    milestone_value INTEGER NOT NULL,
    achieved_date TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_name, milestone_type, milestone_value)
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_agent_name ON agent_videos(agent_name);
CREATE INDEX IF NOT EXISTS idx_upload_date ON agent_videos(upload_date);
CREATE INDEX IF NOT EXISTS idx_series_name ON agent_videos(series_name);
CREATE INDEX IF NOT EXISTS idx_content_hash ON agent_videos(content_hash);
CREATE INDEX IF NOT EXISTS idx_opinion_topic ON opinion_history(agent_name, topic);