from flask import Blueprint, request, jsonify
from app.utils.email_utils import send_email

email_bp = Blueprint('email', __name__)

@email_bp.route('/send-email', methods=['POST'])
def send_email_route():
    data = request.json
    required_fields = ['email', 'session_link', 'date', 'time', 'coach_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    try:
        send_email(data['email'], data['session_link'], data['date'], data['time'], data['coach_name'])
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
