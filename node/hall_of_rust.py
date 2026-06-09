@hall_bp.route('/hall/eulogy/<fingerprint>', methods=['POST'])
def set_eulogy(fingerprint):
    """Set a eulogy/nickname for a machine. For when it finally dies."""
    err = _require_admin()  # Add admin check
    if err:
        return err
    
    data, error_response = _json_object_or_empty()
    ...
    try:
        ...
        if updates:
            params.append(fingerprint)
            c.execute(f"UPDATE hall_of_rust SET {', '.join(updates)} WHERE fingerprint_hash = ?", params)
            conn.commit()