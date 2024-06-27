from flask import Flask, jsonify, request
from app import ref
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
 


users = []
preferred_language=""
@app.route('/signup', methods=['POST'])
def get_signup():
    user_data = request.get_json()
    if user_data:
        email = user_data.get('email')
        contact_number = user_data.get('contactNumber')
        
        # Check if user already exists
        users = ref.get()
        if users:
            for user_id, user in users.items():
                if isinstance(user, dict):
                    if user.get('email') == email and user.get('contactNumber') == contact_number:
                        return jsonify({'error': 'User already exists. Please login.'}), 400
        
        # Add new user data
        ref.push(user_data)
        return jsonify({'success': True}), 201
    else:
        return jsonify({'error': 'Invalid data format.'}), 400
@app.route('/login', methods=['POST'])
def get_login():
    login_data = request.get_json()
    email = login_data.get('email')
    contact_number = login_data.get('contactNumber')
    preferred_language = login_data.get('preferredLanguage')
    
    if not email or not contact_number:
        return jsonify({'error': 'Email and contact number are required'}), 400
    
    # Retrieve all users from the database
    users = ref.get()
    name=""
    if users:
        for user_id, user in users.items():
            if isinstance(user, dict):
                if user.get('email') == email and user.get('contactNumber') == contact_number:
                    name=user.get('name')
                    print(name)
                    return jsonify({'success': True, 'message': 'Login successful', 'preferredLanguage': preferred_language,'name':name}), 200
    return jsonify({'message': 'Email and Mobile Number is registered'}), 200

