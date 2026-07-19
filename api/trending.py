from flask import request, jsonify
from.validators import parse_int_param, parse_ts_param

@app.route('/api/trending', methods=['GET'])
def trending():
    limit = parse_int_param('limit', 10, 1, 100)(request.args.get('limit', 10))
    days = parse_int_param('days', 7, 1, 30)(request.args.get('days', 7))
    since = parse_ts_param('since')(request.args.get('since'))

    if isinstance(limit, tuple):
        return limit
    if isinstance(days, tuple):
        return days
    if isinstance(since, tuple):
        return since

    # Your existing logic to fetch and return the trending data
    return jsonify({"trending": []})