from flask import Blueprint, request, jsonify
from app.database import users_collection

users_bp = Blueprint('users', __name__)

@users_bp.route('/signup', methods=['POST'])
def signup():
    user_data = request.get_json()
    if user_data:
        email = user_data.get('email')
        level = user_data.get('level')
        contact_number = user_data.get('contactNumber')
        
        # Check if user already exists
        existing_user = users_collection.find_one({'email': email, 'contactNumber': contact_number,'level':level})
        if existing_user:
            return jsonify({'error': 'User already exists. Please login.'}), 400
        
        # Add new user data
        users_collection.insert_one(user_data)
        return jsonify({'success': True}), 201
    else:
        return jsonify({'error': 'Invalid data format.'}), 400


@users_bp.route('/login', methods=['POST'])
def signin():
    login_data = request.get_json()
    email = login_data.get('email') 
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})
    print(user)
    
    
    if user:
        name = user.get('name')
        return jsonify({'success': True, 'message': 'Login successfull','name': name}), 200
    return jsonify({'success': False,'message': 'Email and Mobile Number is not registered'}), 200
