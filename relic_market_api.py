from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# ...

@app.route('/relic/reservation/<reservation_id>', methods=['GET'])
@jwt_required()
def get_reservation(reservation_id):
    # Only return the reservation object if the user is authenticated and owns the reservation
    user_id = get_jwt_identity()
    reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id).first()
    if reservation:
        return jsonify(reservation.to_dict())
    else:
        return jsonify({"error": "Reservation not found or not owned by user"}), 404

@app.route('/relic/reservation/<reservation_id>/start', methods=['POST'])
@jwt_required()
def start_reservation(reservation_id):
    # Only start the reservation if the user is authenticated and owns the reservation
    user_id = get_jwt_identity()
    reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id).first()
    if reservation:
        # Start the reservation
        reservation.start()
        return jsonify({"message": "Reservation started successfully"})
    else:
        return jsonify({"error": "Reservation not found or not owned by user"}), 404

@app.route('/relic/reservation/<reservation_id>/complete', methods=['POST'])
@jwt_required()
def complete_reservation(reservation_id):
    # Only complete the reservation if the user is authenticated and owns the reservation
    user_id = get_jwt_identity()
    reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id).first()
    if reservation:
        # Complete the reservation
        reservation.complete()
        return jsonify({"message": "Reservation completed successfully"})
    else:
        return jsonify({"error": "Reservation not found or not owned by user"}), 404

@app.route('/relic/reservation/<reservation_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_reservation(reservation_id):
    # Only cancel the reservation if the user is authenticated and owns the reservation
    user_id = get_jwt_identity()
    reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id).first()
    if reservation:
        # Cancel the reservation
        reservation.cancel()
        return jsonify({"message": "Reservation cancelled successfully"})
    else:
        return jsonify({"error": "Reservation not found or not owned by user"}), 404

@app.route('/relic/agent/<agent_id>/reservations', methods=['GET'])
@jwt_required()
def get_agent_reservations(agent_id):
    # Only return the reservations for the agent if the user is authenticated and owns the agent
    user_id = get_jwt_identity()
    agent = Agent.query.filter_by(id=agent_id, user_id=user_id).first()
    if agent:
        reservations = Reservation.query.filter_by(agent_id=agent_id).all()
        return jsonify([reservation.to_dict() for reservation in reservations])
    else:
        return jsonify({"error": "Agent not found or not owned by user"}), 404