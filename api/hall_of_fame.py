from flask import Blueprint, request, jsonify
from db.database import get_db_connection
import logging

hall_of_fame_bp = Blueprint('hall_of_fame', __name__)

@hall_of_fame_bp.route('/machine', methods=['GET'])
def get_machine():
    fingerprint_hash = request.args.get('fingerprint_hash')
    
    if not fingerprint_hash:
        return jsonify({'error': 'fingerprint_hash parameter is required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fingerprint_hash, cpu_id, total_hashes, mining_sessions, 
                   first_seen, last_seen, last_rust_data
            FROM hall_of_rust 
            WHERE fingerprint_hash = ?
        ''', (fingerprint_hash,))
        
        machine = cursor.fetchone()
        
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        
        machine_data = {
            'fingerprint_hash': machine[0],
            'cpu_id': machine[1],
            'total_hashes': machine[2],
            'mining_sessions': machine[3],
            'first_seen': machine[4],
            'last_seen': machine[5],
            'last_rust_data': machine[6]
        }
        
        conn.close()
        return jsonify(machine_data)
        
    except Exception as e:
        logging.error(f"Error fetching machine details: {e}")
        return jsonify({'error': 'Internal server error'}), 500