# Beacon Atlas Fix

## Issue 1: /beacon/join returns 404

Fix in `beacon_chat.py`:

```python
@app.route('/beacon/join', methods=['POST'])
def beacon_join():
    data = request.json
    pubkey = data.get('pubkey')
    metadata = data.get('metadata', {})
    
    # Add to database
    conn = sqlite3.connect('/root/beacon/beacon_atlas.db')
    conn.execute('INSERT INTO relay_agents (pubkey, metadata, joined_at) VALUES (?, ?, ?)',
                 (pubkey, json.dumps(metadata), datetime.now()))
    conn.commit()
    conn.close()
    
    return jsonify({'ok': True, 'agent_id': pubkey[:16]})
```

## Issue 2: rustchain.org/beacon/atlas returns 404

Nginx config fix (`/etc/nginx/sites-available/rustchain`):

```nginx
server {
    server_name rustchain.org;
    
    # Existing locations
    location / {
        proxy_pass http://localhost:3000;
    }
    
    # NEW: Beacon Atlas proxy
    location /beacon/ {
        proxy_pass http://localhost:8071/beacon/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:8071/api/;
        proxy_set_header Host $host;
    }
}
```

## Files in this PR

- `beacon-atlas/beacon_chat_fix.py` - Missing endpoint implementation
- `beacon-atlas/nginx.conf` - Nginx configuration for beacon routes