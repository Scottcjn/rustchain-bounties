#!/usr/bin/env python3
"""
Beacon Atlas - Fix for /beacon/join endpoint
Add to beacon_chat.py
"""

from flask import Flask, request, jsonify
import sqlite3, json
from datetime import datetime

# Add this to your existing beacon_chat.py

def setup_beacon_join(app):
    """Register the /beacon/join endpoint"""
    
    @app.route('/beacon/join', methods=['POST'])
    def beacon_join():
        """Auto-register new agents"""
        data = request.json
        pubkey = data.get('pubkey')
        metadata = data.get('metadata', {})
        
        if not pubkey:
            return jsonify({'error': 'pubkey required'}), 400
        
        try:
            conn = sqlite3.connect('/root/beacon/beacon_atlas.db')
            conn.execute(
                'INSERT INTO relay_agents (pubkey, metadata, joined_at) VALUES (?, ?, ?)',
                (pubkey, json.dumps(metadata), datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'ok': True,
                'agent_id': pubkey[:16],
                'message': 'Agent registered successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/beacon/status', methods=['GET'])
    def beacon_status():
        """Check beacon server status"""
        return jsonify({
            'status': 'online',
            'endpoints': ['/beacon/join', '/beacon/status', '/api/agents']
        })

if __name__ == '__main__':
    app = Flask(__name__)
    setup_beacon_join(app)
    app.run(host='0.0.0.0', port=8071)