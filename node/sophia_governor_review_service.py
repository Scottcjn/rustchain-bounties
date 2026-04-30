# node/sophia_governor_review_service.py

from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "https://your-ollama-server.com:11434"
NOTIFICATION_SERVICE_TOKEN = "your-notification-service-token"

@app.route('/review', methods=['POST'])
def review():
    data = request.get_json()
    
    # Validate the payload
    if not all(key in data for key in ['prompt', 'summary']):
        return jsonify({"error": "Invalid payload"}), 400
    
    # Sanitize the input to prevent prompt injection
    sanitized_prompt = data['prompt']
    sanitized_summary = data['summary']
    
    # Call Ollama with sanitized inputs
    response = requests.post(OLLAMA_URL, json={'prompt': sanitized_prompt, 'summary': sanitized_summary})
    
    if response.status_code == 200:
        return jsonify({"message": "Review submitted successfully"}), 200
    else:
        return jsonify({"error": f"Failed to submit review: {response.text}"}), 500

if __name__ == '__main__':
    app.run(debug=True)