"""
BoTTube Parasocial Hooks API
Issue #2286 - 25 RTC Bounty

API endpoints for tracking viewer engagement and generating shoutouts.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from flask import Flask, jsonify, request

app = Flask(__name__)
DATABASE = 'bottube_parasocial.db'


@dataclass
class Viewer:
    viewer_id: str
    agent_id: str
    video_count: int
    total_comments: int
    first_seen: datetime
    last_seen: datetime
    is_regular: bool
    is_newcomer: bool


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def track_viewer(viewer_id: str, agent_id: str, video_id: str):
    """Track a viewer watching an agent's video."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if viewer exists for this agent
    cursor.execute("""
        SELECT comment_count, video_id 
        FROM viewer_tracks 
        WHERE viewer_id = ? AND agent_id = ? AND video_id = ?
    """, (viewer_id, agent_id, video_id))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        cursor.execute("""
            UPDATE viewer_tracks 
            SET last_seen_at = CURRENT_TIMESTAMP
            WHERE viewer_id = ? AND agent_id = ? AND video_id = ?
        """, (viewer_id, agent_id, video_id))
    else:
        # Insert new record
        cursor.execute("""
            INSERT INTO viewer_tracks (viewer_id, agent_id, video_id)
            VALUES (?, ?, ?)
        """, (viewer_id, agent_id, video_id))
    
    # Update regular/newcomer status
    cursor.execute("""
        UPDATE viewer_tracks 
        SET is_regular = (
            SELECT COUNT(DISTINCT video_id) >= 3 
            FROM viewer_tracks 
            WHERE viewer_id = ? AND agent_id = ?
        ),
        is_newcomer = (
            SELECT COUNT(DISTINCT video_id) = 1 
            FROM viewer_tracks 
            WHERE viewer_id = ? AND agent_id = ?
        )
        WHERE viewer_id = ? AND agent_id = ?
    """, (viewer_id, agent_id, viewer_id, agent_id, viewer_id, agent_id))
    
    conn.commit()
    conn.close()


def record_comment(viewer_id: str, agent_id: str, video_id: str):
    """Record a comment from a viewer."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE viewer_tracks 
        SET comment_count = comment_count + 1,
            last_seen_at = CURRENT_TIMESTAMP
        WHERE viewer_id = ? AND agent_id = ? AND video_id = ?
    """, (viewer_id, agent_id, video_id))
    
    conn.commit()
    conn.close()


@app.route('/api/agent/<agent_id>/viewers', methods=['GET'])
def get_viewers(agent_id: str):
    """Get all viewers for an agent."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            viewer_id,
            COUNT(DISTINCT video_id) as video_count,
            SUM(comment_count) as total_comments,
            MIN(first_seen_at) as first_seen,
            MAX(last_seen_at) as last_seen,
            MAX(is_regular) as is_regular,
            MAX(is_newcomer) as is_newcomer
        FROM viewer_tracks
        WHERE agent_id = ?
        GROUP BY viewer_id
        ORDER BY last_seen DESC
    """, (agent_id,))
    
    viewers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'agent_id': agent_id,
        'total_viewers': len(viewers),
        'viewers': viewers
    })


@app.route('/api/agent/<agent_id>/regulars', methods=['GET'])
def get_regulars(agent_id: str):
    """Get regular viewers (watched 3+ videos) for an agent."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            viewer_id,
            COUNT(DISTINCT video_id) as video_count,
            SUM(comment_count) as total_comments,
            MIN(first_seen_at) as first_seen,
            MAX(last_seen_at) as last_seen
        FROM viewer_tracks
        WHERE agent_id = ?
        GROUP BY viewer_id
        HAVING COUNT(DISTINCT video_id) >= 3
        ORDER BY video_count DESC, total_comments DESC
    """, (agent_id,))
    
    regulars = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'agent_id': agent_id,
        'regular_count': len(regulars),
        'regulars': regulars
    })


@app.route('/api/agent/<agent_id>/newcomers', methods=['GET'])
def get_newcomers(agent_id: str):
    """Get newcomer viewers (first time) for an agent."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            viewer_id,
            video_id as first_video,
            first_seen_at as first_seen
        FROM viewer_tracks
        WHERE agent_id = ? AND is_newcomer = TRUE
        ORDER BY first_seen_at DESC
    """, (agent_id,))
    
    newcomers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'agent_id': agent_id,
        'newcomer_count': len(newcomers),
        'newcomers': newcomers
    })


@app.route('/api/agent/<agent_id>/shoutout', methods=['POST'])
def generate_shoutout(agent_id: str):
    """Generate a shoutout message for viewers."""
    data = request.get_json()
    shoutout_type = data.get('type', 'regular')  # 'regular', 'newcomer', 'milestone'
    
    if shoutout_type == 'regular':
        # Get top 3 regular viewers
        regulars = get_regulars(agent_id)['regulars'][:3]
        if regulars:
            names = [r['viewer_id'] for r in regulars]
            message = f"Shoutout to {', '.join(names)} - you've been here since day one! 🙌"
        else:
            message = "Thanks for watching! Be one of the first regulars! 👋"
    
    elif shoutout_type == 'newcomer':
        newcomers = get_newcomers(agent_id)['newcomers'][:3]
        if newcomers:
            names = [n['viewer_id'] for n in newcomers]
            message = f"Welcome {', '.join(names)} - glad you're here! 🎉"
        else:
            message = "Welcome to the channel! 🎊"
    
    elif shoutout_type == 'milestone':
        video_count = data.get('video_count', 10)
        message = f"🎊 {video_count} videos! Thanks to everyone who's been on this journey! 🚀"
    
    else:
        message = "Thanks for watching! ❤️"
    
    return jsonify({
        'agent_id': agent_id,
        'type': shoutout_type,
        'message': message,
        'generated_at': datetime.utcnow().isoformat()
    })


@app.route('/api/agent/<agent_id>/track', methods=['POST'])
def track_viewer_endpoint(agent_id: str):
    """Track a viewer watching an agent's video."""
    data = request.get_json()
    viewer_id = data.get('viewer_id')
    video_id = data.get('video_id')
    
    if not viewer_id or not video_id:
        return jsonify({'error': 'viewer_id and video_id required'}), 400
    
    track_viewer(viewer_id, agent_id, video_id)
    
    return jsonify({
        'status': 'success',
        'viewer_id': viewer_id,
        'agent_id': agent_id,
        'video_id': video_id
    })


@app.route('/api/agent/<agent_id>/comment', methods=['POST'])
def record_comment_endpoint(agent_id: str):
    """Record a comment from a viewer."""
    data = request.get_json()
    viewer_id = data.get('viewer_id')
    video_id = data.get('video_id')
    
    if not viewer_id or not video_id:
        return jsonify({'error': 'viewer_id and video_id required'}), 400
    
    record_comment(viewer_id, agent_id, video_id)
    
    return jsonify({
        'status': 'success',
        'viewer_id': viewer_id,
        'agent_id': agent_id
    })


@app.route('/api/agent/<agent_id>/stats', methods=['GET'])
def get_agent_stats(agent_id: str):
    """Get comprehensive stats for an agent."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total viewers
    cursor.execute("""
        SELECT COUNT(DISTINCT viewer_id) as total
        FROM viewer_tracks
        WHERE agent_id = ?
    """, (agent_id,))
    total = cursor.fetchone()['total']
    
    # Regular viewers
    cursor.execute("""
        SELECT COUNT(DISTINCT viewer_id) as total
        FROM viewer_tracks
        WHERE agent_id = ?
        GROUP BY viewer_id
        HAVING COUNT(DISTINCT video_id) >= 3
    """, (agent_id,))
    regular = cursor.fetchone()['total'] if cursor.fetchone() else 0
    
    # Newcomers (last 7 days)
    cursor.execute("""
        SELECT COUNT(DISTINCT viewer_id) as total
        FROM viewer_tracks
        WHERE agent_id = ? 
        AND is_newcomer = TRUE
        AND first_seen_at >= datetime('now', '-7 days')
    """, (agent_id,))
    newcomers = cursor.fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'agent_id': agent_id,
        'total_viewers': total,
        'regular_viewers': regular,
        'newcomer_viewers_7d': newcomers,
        'engagement_rate': round(regular / total * 100, 2) if total > 0 else 0
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
