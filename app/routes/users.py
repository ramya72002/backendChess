from flask import Blueprint, request, jsonify
from app.database import users_collection

users_bp = Blueprint('users', __name__)

@users_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    required_fields = ['email', 'password', 'name', 'level']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    try:
        users_collection.insert_one(data)
        return jsonify({'message': 'User signed up successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/signin', methods=['POST'])
def signin():
    data = request.json
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    try:
        user = users_collection.find_one({'email': data['email'], 'password': data['password']})
        if user:
            return jsonify({'message': 'Sign-in successful', 'user': user}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
