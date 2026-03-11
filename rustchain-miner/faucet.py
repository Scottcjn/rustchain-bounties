#!/usr/bin/env python3
"""
RustChain Testnet Faucet
Provides free test RTC tokens for developers
"""

import os
import json
import random
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import hashlib
import secrets

app = Flask(__name__)
CORS(app)

# Configuration
FAUCET_AMOUNT = 100  # RTC tokens to dispense
COOLDOWN_PERIOD = 24 * 60 * 60  # 24 hours in seconds
MAX_DAILY_REQUESTS = 10  # Max requests per IP per day

# In-memory storage (in production, use a database)
user_requests = {}

# Mock blockchain integration (replace with actual RustChain node API)
BLOCKCHAIN_API_URL = "https://testnet.rustchain.com/api"

def generate_wallet_address():
    """Generate a mock wallet address"""
    return "0x" + ''.join(random.choices('0123456789abcdef', k=40))

def verify_captcha(captcha_response):
    """Verify CAPTCHA response (mock implementation)"""
    # In production, integrate with reCAPTCHA or similar service
    return len(captcha_response) > 0

def send_tokens(wallet_address, amount):
    """Send tokens to wallet address (mock implementation)"""
    try:
        # Mock API call to RustChain blockchain
        response = {
            "success": True,
            "tx_hash": "0x" + ''.join(random.choices('0123456789abcdef', k=64)),
            "amount": amount,
            "to_address": wallet_address
        }
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_user_eligibility(ip_address):
    """Check if user is eligible for faucet"""
    now = time.time()
    
    if ip_address not in user_requests:
        user_requests[ip_address] = {
            "last_request": 0,
            "daily_requests": 0,
            "total_requests": 0
        }
    
    user_data = user_requests[ip_address]
    
    # Reset daily counter if it's a new day
    last_request_time = datetime.fromtimestamp(user_data["last_request"])
    if datetime.now().date() > last_request_time.date():
        user_data["daily_requests"] = 0
    
    # Check cooldown
    if now - user_data["last_request"] < COOLDOWN_PERIOD:
        remaining_time = COOLDOWN_PERIOD - (now - user_data["last_request"])
        return False, remaining_time
    
    # Check daily limit
    if user_data["daily_requests"] >= MAX_DAILY_REQUESTS:
        return False, "daily_limit_exceeded"
    
    return True, None

def update_user_request(ip_address):
    """Update user request data"""
    now = time.time()
    user_requests[ip_address]["last_request"] = now
    user_requests[ip_address]["daily_requests"] += 1
    user_requests[ip_address]["total_requests"] += 1

@app.route('/', methods=['GET'])
def faucet_home():
    """Faucet home page"""
    return """
    <html>
    <head>
        <title>RustChain Testnet Faucet</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
            .container { background: #f9f9f9; padding: 20px; border-radius: 8px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
            .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>RustChain Testnet Faucet</h1>
            <p>Get free test RTC tokens for development on the RustChain testnet.</p>
            <p><strong>Amount:</strong> {} RTC</p>
            <p><strong>Cooldown:</strong> 24 hours</p>
            <p><strong>Daily Limit:</strong> {} requests per day</p>
            
            <form id="faucetForm">
                <div class="form-group">
                    <label for="walletAddress">Wallet Address:</label>
                    <input type="text" id="walletAddress" name="walletAddress" placeholder="0x..." required>
                </div>
                
                <div class="form-group">
                    <label for="captcha">CAPTCHA:</label>
                    <input type="text" id="captcha" name="captcha" placeholder="Enter CAPTCHA" required>
                </div>
                
                <button type="submit">Get Test RTC</button>
            </form>
            
            <div id="message"></div>
        </div>
        
        <script>
            document.getElementById('faucetForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {{
                    walletAddress: formData.get('walletAddress'),
                    captcha: formData.get('captcha')
                }};
                
                fetch('/request', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(data)
                }})
                .then(response => response.json())
                .then(data => {{
                    const messageDiv = document.getElementById('message');
                    if (data.success) {{
                        messageDiv.className = 'message success';
                        messageDiv.textContent = `Success! Transaction hash: ${{data.tx_hash}}`;
                    }} else {{
                        messageDiv.className = 'message error';
                        messageDiv.textContent = data.error || 'An error occurred';
                    }}
                }})
                .catch(error => {{
                    const messageDiv = document.getElementById('message');
                    messageDiv.className = 'message error';
                    messageDiv.textContent = 'Network error: ' + error;
                }});
            }});
        </script>
    </body>
    </html>
    """.format(FAUCET_AMOUNT, MAX_DAILY_REQUESTS)

@app.route('/request', methods=['POST'])
def request_tokens():
    """Handle faucet token requests"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    wallet_address = data.get('walletAddress')
    captcha_response = data.get('captcha')
    
    # Validate inputs
    if not wallet_address or not wallet_address.startswith('0x') or len(wallet_address) != 42:
        return jsonify({"success": False, "error": "Invalid wallet address"}), 400
    
    if not verify_captcha(captcha_response):
        return jsonify({"success": False, "error": "Invalid CAPTCHA"}), 400
    
    # Check user eligibility
    ip_address = request.remote_addr
    eligible, reason = check_user_eligibility(ip_address)
    
    if not eligible:
        if reason == "daily_limit_exceeded":
            return jsonify({"success": False, "error": "Daily limit exceeded"}), 429
        else:
            remaining_hours = int(reason / 3600)
            return jsonify({"success": False, "error": f"Please wait {remaining_hours} hours before requesting again"}), 429
    
    # Send tokens
    result = send_tokens(wallet_address, FAUCET_AMOUNT)
    
    if result["success"]:
        update_user_request(ip_address)
        return jsonify({
            "success": True,
            "tx_hash": result["tx_hash"],
            "amount": FAUCET_AMOUNT,
            "to_address": wallet_address
        })
    else:
        return jsonify({"success": False, "error": result["error"]}), 500

@app.route('/stats', methods=['GET'])
def faucet_stats():
    """Return faucet statistics"""
    total_requests = sum(data["total_requests"] for data in user_requests.values())
    daily_requests = sum(data["daily_requests"] for data in user_requests.values())
    
    return jsonify({
        "total_requests": total_requests,
        "daily_requests": daily_requests,
        "active_users": len(user_requests),
        "faucet_amount": FAUCET_AMOUNT,
        "cooldown_hours": COOLDOWN_PERIOD // 3600
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
