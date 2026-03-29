#!/usr/bin/env python3
"""
Initialize the database for BoTTube Parasocial Hooks API
"""

import sqlite3
import os

DATABASE = 'bottube_parasocial.db'

def init_db():
    """Initialize the database with schema."""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create viewer tracking table
    cursor.execute("""
        CREATE TABLE viewer_tracks (
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
        )
    """)
    
    # Create agent stats table
    cursor.execute("""
        CREATE TABLE agent_stats (
            agent_id TEXT PRIMARY KEY,
            total_viewers INTEGER DEFAULT 0,
            regular_viewers INTEGER DEFAULT 0,
            newcomer_viewers INTEGER DEFAULT 0,
            last_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_viewer_agent ON viewer_tracks(viewer_id, agent_id)")
    cursor.execute("CREATE INDEX idx_agent_video ON viewer_tracks(agent_id, video_id)")
    cursor.execute("CREATE INDEX idx_regular ON viewer_tracks(agent_id, is_regular)")
    cursor.execute("CREATE INDEX idx_newcomer ON viewer_tracks(agent_id, is_newcomer)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {DATABASE}")

if __name__ == '__main__':
    init_db()
