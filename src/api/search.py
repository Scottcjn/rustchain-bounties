from flask import request, jsonify
from src.api_videos import _parse_positive_int_query

def search():
    page = _parse_positive_int_query("page", 1)
    per_page = _parse_positive_int_query("per_page", 20, max_value=50)

    if isinstance(page, tuple) or isinstance(per_page, tuple):
        return page if isinstance(page, tuple) else per_page

    # Rest of the function remains the same
    # ...