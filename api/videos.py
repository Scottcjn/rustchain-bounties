from flask import request, jsonify
from.validators import parse_int_param

@app.route('/api/videos', methods=['GET'])
def videos():
    page = parse_int_param('page', 1, 1, 100)(request.args.get('page', 1))

    if isinstance(page, tuple):
        return page

    # Your existing logic to fetch and return the videos
    return jsonify({"videos": []})

@app.route('/api/videos/<id>/related', methods=['GET'])
def related_videos(id):
    limit = parse_int_param('limit', 10, 1, 100)(request.args.get('limit', 10))

    if isinstance(limit, tuple):
        return limit

    # Your existing logic to fetch and return the related videos
    return jsonify({"related_videos": []})