from flask import request, jsonify

def _integer_query_arg(name, default=None):
    """Helper to parse integer query arguments."""
    value = request.args.get(name)
    if value is None:
        return default, None
    try:
        return int(value), None
    except ValueError:
        error = jsonify({"error": f"Invalid integer value for {name}"})
        return None, (error, 400)

# Usage in routes
@app.route('/api/syndication/runs')
def syndication_runs():
    limit, error = _integer_query_arg('limit', 10)
    if error:
        return error
    # ...

@app.route('/api/syndication/report/outbound')
def syndication_report_outbound():
    page, error = _integer_query_arg('page', 1)
    if error:
        return error
    # ...

@app.route('/api/syndication/report/export')
def syndication_report_export():
    export_id, error = _integer_query_arg('export_id')
    if error:
        return error
    # ...