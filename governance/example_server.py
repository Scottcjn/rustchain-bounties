"""
Example Flask Server Integration
=================================

This example shows how to integrate the governance system with a Flask server.

Usage:
    python example_server.py

The server will start on http://localhost:5000
"""

import sqlite3
from flask import Flask, jsonify, request
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from governance import (
    create_governance_blueprint,
    create_governance_ui,
    init_governance_db,
    GOVERNANCE_SCHEMA
)

app = Flask(__name__)
DB_PATH = "example_governance.db"


def init_db():
    """Initialize the database with governance tables."""
    # Create tables
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(GOVERNANCE_SCHEMA)
        
        # Add sample data for testing
        try:
            # Sample miners (for hardware weights)
            conn.execute("""
                INSERT OR IGNORE INTO miners (wallet, hardware_type, antiquity_multiplier)
                VALUES 
                    ('wallet_g4_1', 'powerpc_g4', 2.5),
                    ('wallet_g4_2', 'powerpc_g4', 2.5),
                    ('wallet_g5_1', 'powerpc_g5', 2.5),
                    ('wallet_sparc', 'sparc_v9', 2.5),
                    ('wallet_486', '486', 2.9)
            """)
            
            # Sample balances
            conn.execute("""
                INSERT OR IGNORE INTO balances (wallet, balance)
                VALUES 
                    ('wallet_g4_1', 100.0),
                    ('wallet_g4_2', 50.0),
                    ('wallet_g5_1', 200.0),
                    ('wallet_sparc', 150.0),
                    ('wallet_486', 75.0),
                    ('test_wallet', 15.0)
            """)
            
            # Sample attestations (active in last 48h)
            import time
            now = int(time.time())
            conn.execute("""
                INSERT OR IGNORE INTO attestations (wallet, timestamp)
                VALUES 
                    ('wallet_g4_1', ?),
                    ('wallet_g4_2', ?),
                    ('wallet_g5_1', ?),
                    ('wallet_sparc', ?),
                    ('wallet_486', ?),
                    ('test_wallet', ?)
            """, (now - 3600,) * 6)  # 1 hour ago
            
            conn.commit()
            print("Sample data inserted")
        except Exception as e:
            print(f"Sample data insertion: {e}")
    
    print(f"Database initialized at {DB_PATH}")


# Initialize database
init_db()

# Register governance blueprints
app.register_blueprint(create_governance_blueprint(DB_PATH))
app.register_blueprint(create_governance_ui(DB_PATH))


@app.route("/")
def index():
    return """
    <h1>RustChain Governance Demo</h1>
    <ul>
        <li><a href="/governance">Governance UI</a></li>
        <li><a href="/governance/proposals">List Proposals</a></li>
        <li><a href="/governance/stats">Statistics</a></li>
    </ul>
    """


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("Starting RustChain Governance Demo Server")
    print("Visit http://localhost:5000/governance for the UI")
    app.run(debug=True, host="0.0.0.0", port=5000)
