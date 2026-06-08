# ...

def post_bft_propose(self, request):
    # Input validation
    if not request.json or 'epoch' not in request.json or 'miners' not in request.json or 'distribution_type' not in request.json:
        return {'error': 'Invalid request'}, 400

    # Added authentication check
    if not self._require_admin_key(request):
        return {'error': 'Unauthorized'}, 401

    # Existing code to handle BFT proposal
    # ...

### FILE: node/utils.py