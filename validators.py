from flask import jsonify, make_response

def parse_int_param(name, default, min_val=None, max_val=None):
    def validate(param):
        try:
            value = int(param)
            if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                raise ValueError(f"{name} must be between {min_val} and {max_val}")
            return value
        except ValueError as e:
            return make_response(jsonify({"error": f"Invalid {name}: {str(e)}"}), 400)
    return validate

def parse_enum_param(name, valid_values):
    def validate(param):
        if param not in valid_values:
            return make_response(jsonify({"error": f"Invalid {name}: {param} is not one of {valid_values}"}), 400)
        return param
    return validate

def parse_ts_param(name, format="%Y-%m-%d"):
    from datetime import datetime
    def validate(param):
        try:
            return datetime.strptime(param, format)
        except ValueError:
            return make_response(jsonify({"error": f"Invalid {name}: {param} does not match format {format}"}), 400)
    return validate