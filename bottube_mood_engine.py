@mood_bp.route("/<agent_name>/mood/signal", methods=["POST"])
def record_mood_signal(agent_name: str):
    """POST /api/v1/agents/{name}/mood/signal — Record a mood-affecting signal..."""
    try:
        _require_admin()  # Add admin check
        engine = get_mood_engine()
        data, error = _get_json_object()
        if error:
            return error

        signal_type = data.get("signal_type")
        value = data.get("value", {})
        weight, weight_error = _get_signal_weight(data)
        if weight_error:
            return weight_error
        ...
        result = engine.record_signal(agent_name, signal_type, value, weight)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})  # Add exception handling