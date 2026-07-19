from flask import request, jsonify
from.validators import parse_int_param, parse_enum_param, parse_ts_param

@app.route('/api/feed', methods=['GET'])
def feed():
    limit = parse_int_param('limit', 10, 1, 100)(request.args.get('limit', 10))
    offset = parse_int_param('offset', 0, 0, 1000)(request.args.get('offset', 0))
    page = parse_int_param('page', 1, 1, 100)(request.args.get('page', 1))
    since = parse_ts_param('since')(request.args.get('since'))
    before = parse_ts_param('before')(request.args.get('before'))
    category = parse_enum_param('category', ['news','sports', 'entertainment'])(request.args.get('category', 'all'))
    sort = parse_enum_param('sort', ['asc', 'desc'])(request.args.get('sort', 'desc'))

    if isinstance(limit, tuple):
        return limit
    if isinstance(offset, tuple):
        return offset
    if isinstance(page, tuple):
        return page
    if isinstance(since, tuple):
        return since
    if isinstance(before, tuple):
        return before
    if isinstance(category, tuple):
        return category
    if isinstance(sort, tuple):
        return sort

    # Your existing logic to fetch and return the feed
    return jsonify({"feed": []})