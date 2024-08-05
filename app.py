from flask import Flask, jsonify, request, send_file, send_file
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient, errors
from gridfs import GridFS
from dotenv import load_dotenv
import os
from io import BytesIO
from bson import ObjectId
 
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
fs = GridFS(db)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'images' not in request.files:
        return jsonify({'error': 'No images part in the request'}), 400

    files = request.files.getlist('images')
    file_ids = []
    for file in files:
        try:
            file_id = fs.put(file, filename=file.filename, content_type=file.content_type)
            file_ids.append(str(file_id))  # Convert ObjectId to string
        except errors.PyMongoError as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Images uploaded successfully', 'file_ids': file_ids}), 200

@app.route('/get', methods=['GET'])
def get_images():
    try:
        files = fs.find().sort('_id', -1).limit(5)  # Limit to the last 5 uploads
        image_data = []
        for file in files:
            image_data.append({
                'id': str(file._id),  # Convert ObjectId to string
                'filename': file.filename,
                'url': f"/image/{file._id}"
            })
        return jsonify({'images': image_data}), 200
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image/<file_id>', methods=['GET'])
def get_image(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(BytesIO(file.read()), mimetype=file.content_type, as_attachment=False, attachment_filename=file.filename)
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500



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
    contact_number = login_data.get('contactNumber')
    preferred_language = login_data.get('preferredLanguage')
    
    if not email or not contact_number:
        return jsonify({'error': 'Email and contact number are required'}), 400
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email, 'contactNumber': contact_number})
    print(user)
    print(users_collection)
    print(db)
    
    if user:
        name = user.get('name')
        return jsonify({'success': True, 'message': 'Login successful', 'preferredLanguage': preferred_language, 'name': name}), 200
    return jsonify({'message': 'Email and Mobile Number is not registered'}), 400


if __name__ == '__main__':
    app.run()
