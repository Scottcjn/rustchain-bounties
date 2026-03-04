# Solution for: Beacon: Rate Limiter Hardening + API-level Throttling
# Issue #557 - rustchain-bounties

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Hardened Rate Limiter Configuration
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://" # Can be replaced with redis:// for production
)

@app.route("/api/v1/beacon/status")
@limiter.limit("10 per minute")
def beacon_status():
    return jsonify({"status": "active", "message": "Beacon is secure and throttled."})

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="ratelimit exceeded", description=str(e.description)), 429

if __name__ == '__main__':
    app.run(port=5000)