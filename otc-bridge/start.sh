#!/bin/bash
# RustChain OTC Bridge - Quick Start Script

echo "🚀 Starting RustChain OTC Bridge..."

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Start the Flask server
echo "🌐 Starting API server on port 5000..."
python3 app.py