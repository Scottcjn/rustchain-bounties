"""Auto-generated API endpoints."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from flask import Flask, jsonify, request


app = Flask(__name__)

# In-memory storage
data_store: Dict[str, Any] = {}


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route("/api/v1/data", methods=["GET"])
def get_data():
    """Get all data."""
    return jsonify({"data": list(data_store.values())})


@app.route("/api/v1/data/<key>", methods=["GET"])
def get_data_by_key(key: str):
    """Get data by key."""
    if key in data_store:
        return jsonify({"key": key, "value": data_store[key]})
    return jsonify({"error": "Not found"}), 404


@app.route("/api/v1/data", methods=["POST"])
def create_data():
    """Create new data."""
    data = request.get_json()
    key = data.get("key", f"item_{len(data_store)}")
    data_store[key] = data
    return jsonify({"key": key, "created": True}), 201


@app.route("/api/v1/data/<key>", methods=["PUT"])
def update_data(key: str):
    """Update data."""
    if key not in data_store:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    data_store[key].update(data)
    return jsonify({"key": key, "updated": True})


@app.route("/api/v1/data/<key>", methods=["DELETE"])
def delete_data(key: str):
    """Delete data."""
    if key in data_store:
        del data_store[key]
        return jsonify({"deleted": True})
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
