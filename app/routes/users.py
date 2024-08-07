from flask import Blueprint, request, jsonify
from pymongo import ReturnDocument
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
        existing_user = users_collection.find_one({'email': email, 'contactNumber': contact_number, 'level': level})
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
        return jsonify({'success': True, 'message': 'Login successful', 'name': name}), 200
    return jsonify({'success': False, 'message': 'Email and Mobile Number is not registered'}), 200


@users_bp.route('/getuserdetails', methods=['GET'])
def get_user_details():
    email = request.args.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email parameter is required'}), 400
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})
    
    if user:
        # Customize this to match your user schema
        user_details = {
            'name': user.get('name', ''),
            'email': user.get('email', ''),
            'image': user.get('image', ''),
            'level': user.get('level', 'level1'),  # Include the level in the response
            'puzzle_score': user.get('puzzle_score', ''),
            # Add other fields as needed
        }
        return jsonify({'success': True, 'data': user_details}), 200
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    

@users_bp.route('/imageupdate', methods=['POST'])
def update_user_image():
    data = request.get_json()
    user_name = data.get('name')
    image_url = data.get('image')  # Assuming 'image' is the key for the image URL
    
    if not user_name:
        return jsonify({'success': False, 'message': 'name parameter is required'}), 400
    
    try:
        # Update user's image in the database
        user = users_collection.find_one_and_update(
            {'name': user_name},
            {'$set': {'image': image_url}},
            return_document=ReturnDocument.AFTER
        )

        if user:
            user_details = {
                'name': user.get('name', ''),
                'email': user.get('email', ''),
                'image': user.get('image', ''),
                'level':user.get('level',''),
                # Add other fields as needed
            }
            return jsonify({'success': True, 'data': user_details}), 200
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
