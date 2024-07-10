from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient,ReturnDocument
from dotenv import load_dotenv
from bson import ObjectId
import os
 
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

app = Flask(__name__)
CORS(app)
load_dotenv()

# Get the MongoDB URI from the environment variable
mongo_uri = os.getenv('MONGO_URI')
# MongoDB setup
client = MongoClient(mongo_uri)
db = client.chessDb
users_collection = db.users


@app.route('/')
def home():
    return "Hello, Flask on Vercel!"

def time_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.route('/create', methods=['POST'])
def create():
    data = request.json
    if data:
        result = users_collection.insert_one(data)
        return jsonify({'message': 'Data created', 'id': str(result.inserted_id)}), 201
    else:
        return "error", 400
    
@app.route('/signup', methods=['POST'])
def signup():
    user_data = request.get_json()
    if user_data:
        email = user_data.get('email')
        contact_number = user_data.get('contactNumber')
        
        # Check if user already exists
        existing_user = users_collection.find_one({'email': email, 'contactNumber': contact_number})
        if existing_user:
            return jsonify({'error': 'User already exists. Please login.'}), 400
        
        # Add new user data
        users_collection.insert_one(user_data)
        return jsonify({'success': True}), 201
    else:
        return jsonify({'error': 'Invalid data format.'}), 400

@app.route('/login', methods=['POST'])
def login():
    login_data = request.get_json()
    email = login_data.get('email') 
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})
    print(user)
    
    
    if user:
        name = user.get('name')
        return jsonify({'success': True, 'message': 'Login successful','name': name}), 200
    return jsonify({'success': False,'message': 'Email and Mobile Number is not registered'}), 200

@app.route('/getuserdetails', methods=['GET'])
def get_user_details():
    email = request.args.get('email')
    level = request.args.get('level')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email parameter is required'}), 400
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})
    
    if user:
        # Update the user's level in the database if not already present
        if not user.get('level'):
            users_collection.update_one({'email': email}, {'$set': {'level': level}})
        
        # Customize this to match your user schema
        user_details = {
            'name': user.get('name', ''),
            'email': user.get('email', ''),
            'image': user.get('image', ''),
            'level': user.get('level', level),  # Include the level in the response
            # Add other fields as needed
        }
        return jsonify({'success': True, 'data': user_details}), 200
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    
@app.route('/imageupdate', methods=['POST'])
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

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
