from flask import jsonify

def _parse_leaderboard_limit(default=25, max_value=100):
    def parse_limit(limit):
        try:
            limit = int(limit)
            if limit < 1:
                return None, "Limit must be a positive integer"
            if limit > max_value:
                return max_value, None
            return limit, None
        except ValueError:
            return None, "Invalid limit parameter"
    return parse_limit

# ...

@app.route('/api/quests/leaderboard', methods=['GET'])
def quests_leaderboard():
    limit = request.args.get('limit')
    parse_limit = _parse_leaderboard_limit()
    limit, error = parse_limit(limit)
    if error:
        return jsonify({"error": error}), 400
    # ...

@app.route('/api/gamification/leaderboard', methods=['GET'])
def gamification_leaderboard():
    limit = request.args.get('limit')
    parse_limit = _parse_leaderboard_limit()
    limit, error = parse_limit(limit)
    if error:
        return jsonify({"error": error}), 400
    # ...