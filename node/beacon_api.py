# ...

def post_chat(self, request):
    # Input validation
    if not request.json or 'message' not in request.json:
        return {'error': 'Invalid request'}, 400

    # Added authentication check
    if not self._require_admin_key(request):
        return {'error': 'Unauthorized'}, 401

    # Existing code to handle chat message
    # ...

### FILE: node/airdrop_v2.py