from flask import Flask, render_template, jsonify, request
import requests
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Configuration
BLOCK_EXPLORER_API = "http://localhost:5000/api"
UPDATE_INTERVAL = 10  # seconds

# Global data store for real-time updates
dashboard_data = {
    'miners': [],
    'agents': [],
    'blocks': [],
    'network_stats': {},
    'transactions': [],
    'last_update': None
}

def fetch_network_stats():
    """Fetch network statistics from block explorer API"""
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/network/stats")
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return {}

def fetch_miners():
    """Fetch active miners data"""
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/miners")
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return []

def fetch_agents():
    """Fetch agent marketplace data"""
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/agents")
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return []

def fetch_recent_blocks():
    """Fetch recent blocks"""
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/blocks/recent?limit=10")
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return []

def fetch_recent_transactions():
    """Fetch recent transactions"""
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/transactions/recent?limit=20")
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return []

def update_dashboard_data():
    """Update dashboard data from API endpoints"""
    global dashboard_data
    
    dashboard_data['network_stats'] = fetch_network_stats()
    dashboard_data['miners'] = fetch_miners()
    dashboard_data['agents'] = fetch_agents()
    dashboard_data['blocks'] = fetch_recent_blocks()
    dashboard_data['transactions'] = fetch_recent_transactions()
    dashboard_data['last_update'] = datetime.now().isoformat()

def background_updater():
    """Background thread to update dashboard data"""
    while True:
        update_dashboard_data()
        time.sleep(UPDATE_INTERVAL)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data"""
    return jsonify(dashboard_data)

@app.route('/api/refresh')
def api_refresh():
    """Manually refresh dashboard data"""
    update_dashboard_data()
    return jsonify({'status': 'success', 'last_update': dashboard_data['last_update']})

if __name__ == '__main__':
    # Start background updater thread
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    # Initialize dashboard data
    update_dashboard_data()
    
    app.run(debug=True, port=5001)te_dashboard_data():
    """Update dashboard data from API endpoints"""
    global dashboard_data
    
    dashboard_data['network_stats'] = fetch_network_stats()
    dashboard_data['miners'] = fetch_miners()
    dashboard_data['agents'] = fetch_agents()
    dashboard_data['blocks'] = fetch_recent_blocks()
    dashboard_data['transactions'] = fetch_recent_transactions()
    dashboard_data['last_update'] = datetime.now().isoformat()

def background_updater():
    """Background thread to update dashboard data"""
    while True:
        update_dashboard_data()
        time.sleep(UPDATE_INTERVAL)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/dashboard')
def dashboard_api():
    """API endpoint for dashboard data"""
    return jsonify(dashboard_data)

@app.route('/api/refresh')
def refresh_data():
    """Manual refresh endpoint"""
    update_dashboard_data()
    return jsonify({'status': 'success', 'last_update': dashboard_data['last_update']})

if __name__ == '__main__':
    # Start background updater thread
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    # Initialize data on startup
    update_dashboard_data()
    
    app.run(debug=True, host='0.0.0.0', port=5001)te_dashboard_data():
    """Background task to update dashboard data"""
    while True:
        try:
            dashboard_data['network_stats'] = fetch_network_stats()
            dashboard_data['miners'] = fetch_miners()
            dashboard_data['agents'] = fetch_agents()
            dashboard_data['blocks'] = fetch_recent_blocks()
            dashboard_data['transactions'] = fetch_recent_transactions()
            dashboard_data['last_update'] = datetime.now().isoformat()
        except Exception as e:
            print(f"Error updating dashboard data: {e}")
        time.sleep(UPDATE_INTERVAL)

# Start background thread for data updates
thread = threading.Thread(target=update_dashboard_data, daemon=True)
thread.start()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/miners')
def miners_dashboard():
    """Miner dashboard page"""
    return render_template('miners.html')

@app.route('/agents')
def agent_marketplace():
    """Agent marketplace page"""
    return render_template('agents.html')

@app.route('/blocks')
def block_explorer():
    """Block explorer page"""
    return render_template('blocks.html')

@app.route('/api/dashboard/data')
def get_dashboard_data():
    """API endpoint for dashboard data"""
    return jsonify(dashboard_data)

@app.route('/api/miners/data')
def get_miners_data():
    """API endpoint for miners data"""
    return jsonify({
        'miners': dashboard_data['miners'],
        'last_update': dashboard_data['last_update']
    })

@app.route('/api/agents/data')
def get_agents_data():
    """API endpoint for agents data"""
    return jsonify({
        'agents': dashboard_data['agents'],
        'last_update': dashboard_data['last_update']
    })

@app.route('/api/blocks/data')
def get_blocks_data():
    """API endpoint for blocks data"""
    return jsonify({
        'blocks': dashboard_data['blocks'],
        'last_update': dashboard_data['last_update']
    })

@app.route('/api/network/stats')
def get_network_stats():
    """API endpoint for network statistics"""
    return jsonify(dashboard_data['network_stats'])

@app.route('/api/transactions/recent')
def get_recent_transactions():
    """API endpoint for recent transactions"""
    limit = request.args.get('limit', 20, type=int)
    transactions = dashboard_data['transactions'][:limit]
    return jsonify(transactions)

@app.route('/api/miner/<miner_id>')
def get_miner_details(miner_id):
    """API endpoint for specific miner details"""
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/miner/{miner_id}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Miner not found'}), 404
    except requests.RequestException:
        return jsonify({'error': 'API unavailable'}), 503

@app.route('/api/agent/<agent_id>')
def get_agent_details(agent_id):
    """API endpoint for specific agent details"""
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/agent/{agent_id}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except requests.RequestException:
        return jsonify({'error': 'API unavailable'}), 503

@app.route('/api/block/<block_hash>')
def get_block_details(block_hash):
    """API endpoint for specific block details"""
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/block/{block_hash}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Block not found'}), 404
    except requests.RequestException:
        return jsonify({'error': 'API unavailable'}), 503

@app.route('/api/transaction/<tx_hash>')
def get_transaction_details(tx_hash):
    """API endpoint for specific transaction details"""
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/transaction/{tx_hash}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Transaction not found'}), 404
    except requests.RequestException:
        return jsonify({'error': 'API unavailable'}), 503

@app.route('/api/search')
def search():
    """API endpoint for search functionality"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    try:
        response = requests.get(f"{BLOCK_EXPLORER_API}/search?q={query}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Search failed'}), 500
    except requests.RequestException:
        return jsonify({'error': 'API unavailable'}), 503

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test API connectivity
        response = requests.get(f"{BLOCK_EXPLORER_API}/health", timeout=5)
        api_status = "healthy" if response.status_code == 200 else "unhealthy"
    except requests.RequestException:
        api_status = "unavailable"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'api_status': api_status,
        'last_data_update': dashboard_data['last_update']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)