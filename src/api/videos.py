from flask import request, jsonify

def _parse_positive_int_query(param_name, default, min_value=1, max_value=None):
    """Parse a positive integer query parameter."""
    param_value = request.args.get(param_name)
    if param_value is None:
        return default

    try:
        param_value = int(param_value)
    except ValueError:
        return jsonify({"error": f"Invalid {param_name} parameter"}), 400

    if param_value < min_value or (max_value is not None and param_value > max_value):
        return jsonify({"error": f"{param_name} parameter out of range"}), 400

    return param_value

def get_videos():
    page = _parse_positive_int_query("page", 1)
    per_page = _parse_positive_int_query("per_page", 20, max_value=50)

    if isinstance(page, tuple) or isinstance(per_page, tuple):
        return page if isinstance(page, tuple) else per_page

    # Rest of the function remains the same
    # ...