from flask import jsonify

def _parse_recent_comments_limit(limit):
    try:
        limit = int(limit)
        if limit < 0:
            return None, "Limit must be a non-negative integer"
        return limit, None
    except ValueError:
        return None, "Limit must be an integer"

def _parse_recent_comments_since(since):
    try:
        since = float(since)
        if not since == since:  # check for NaN
            return None, "Since must be a finite number"
        if since < 0:
            return None, "Since must be a non-negative number"
        return since, None
    except ValueError:
        return None, "Since must be a number"

def recent_comments():
    limit = request.args.get('limit')
    since = request.args.get('since')

    if limit is not None:
        limit, limit_error = _parse_recent_comments_limit(limit)
        if limit_error is not None:
            return jsonify({"error": limit_error}), 400

    if since is not None:
        since, since_error = _parse_recent_comments_since(since)
        if since_error is not None:
            return jsonify({"error": since_error}), 400

    # rest of the function remains the same