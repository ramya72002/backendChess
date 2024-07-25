from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from pymongo import DESCENDING, MongoClient, ReturnDocument
from dotenv import load_dotenv
import os,re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

app = Flask(__name__)

# Allow requests from specific origins
CORS(app, origins=["https://chess-main.vercel.app","https://chessdemo-alpha.vercel.app","https://chessdemo-l3qrzgj5q-ramyas-projects-4cb2348e.vercel.app","https://chess-main-git-main-ramyas-projects-4cb2348e.vercel.app","http://localhost:3000"])

load_dotenv()

# Get the MongoDB URI from the environment variable
mongo_uri = os.getenv('MONGO_URI')

# MongoDB setup
client = MongoClient(mongo_uri)
db = client.chessDb
admin_collection = db.admin_db 
users_collection = db.users

@app.route('/')
def home():
    return "Hello, Flask on Vercel!"

def time_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@app.route('/studentList', methods=['GET'])
def get_studentList():
    try:
        # Retrieve all documents and convert cursor to a list
        documents = list(users_collection.find({}, {'_id': 0}))
        
        if documents:
            return jsonify(documents), 200
        else:
            return jsonify({"error": "No records found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/del-student', methods=['DELETE'])
def delete_student():
    try:
        email = request.json.get('email')
        if not email:
            return jsonify({"error": "Email is required"}), 400

        result = users_collection.delete_one({"email": email})
        
        if result.deleted_count > 0:
            return jsonify({"message": "Student record deleted successfully"}), 200
        else:
            return jsonify({"error": "Student record not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add-session', methods=['POST'])
def add_session():
    data = request.json

    # Validate required fields
    required_fields = ['date', 'time', 'coach_name', 'session_link']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate session link format (basic check for HTTP/HTTPS)
    if not re.match(r'^https?://', data['session_link']):
        return jsonify({"error": "Invalid session link format"}), 400

    # Prepare the session data
    session_data = {
        "date": data["date"],
        "time": data["time"],
        "coach_name": data["coach_name"],
        "session_link": data["session_link"]
    }

    # Update the document in the collection
    result = admin_collection.update_one(
        {},  # You can specify a filter if needed
        {"$push": {"sessions": session_data}}
    )
    
    if result.modified_count > 0 or result.upserted_id:
        return jsonify({"message": "Session added successfully"}), 201
    else:
        return jsonify({"error": "Failed to add session"}), 500
@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    email = data.get('email')
    session_link = data.get('session_link')
    date = data.get('date')
    time = data.get('time')
    coach_name = data.get('coach_name')

    if not email or not session_link or not date or not time or not coach_name:
        return jsonify({"error": "Email, session link, date, time, and coach name are required"}), 400

    try:
        # Email configuration
        sender_email = "nsriramya30@gmail.com"
        sender_password = "pqvq towd hrrx rhbm"  # Use your app-specific password here
        subject = "Your Chess Session Enrollment"

        body = (
            f"Dear Participant,\n\n"
            f"You have successfully enrolled in the chess session.\n\n"
            f"Details of the session are as follows:\n"
            f"Date: {date}\n"
            f"Time: {time}\n"
            f"Coach: {coach_name}\n"
            f"Session Link: {session_link}\n\n"
            f"We hope you enjoy your session!\n\n"
            f"Best regards,\n"
            f"The Chess Training Team"
        )

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the Gmail server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()

        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sessions', methods=['GET'])
def get_sessions():
    try:
        # Retrieve documents and extract the 'sessions' field from the first document
        document = admin_collection.find_one({}, {'_id': 0, 'sessions': 1})
        
        if document and 'sessions' in document:
            return jsonify(document['sessions']), 200
        else:
            return jsonify({"error": "No sessions found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tornaments', methods=['GET'])
def get_tournaments():
    try:
        # Retrieve documents and extract the 'tournaments' field from the first document
        document = admin_collection.find_one({}, {'_id': 0, 'tournaments': 1})
        
        if document and 'tournaments' in document:
            return jsonify(document['tournaments']), 200
        else:
            return jsonify({"error": "No tournaments found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-tournament', methods=['PUT'])
def update_tournament():
    try:
        data = request.json
        tournament_type = data.get('type')
        tournament_updates = data.get('tournament')

        if not tournament_type or not tournament_updates:
            return jsonify({"error": "Type and tournament details are required"}), 400

        # Prepare the update dictionary
        update_fields = {f"tournaments.$.{key}": value for key, value in tournament_updates.items() if value is not None}

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        # Update the specified tournament
        result = admin_collection.update_one(
            {"tournaments.type": tournament_type},
            {
                "$set": update_fields
            }
        )

        if result.modified_count == 0:
            return jsonify({"error": "No tournament found to update or no changes made"}), 404

        return jsonify({"message": "Tournament updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/del-session', methods=['DELETE'])
def delete_session():
    data = request.json

    # Validate data
    if not all(key in data for key in ('date', 'time')):
        return jsonify({"error": "Date and time must be provided to delete a session"}), 400

    try:
        # Remove the session from the sessions field
        result = admin_collection.update_one(
            {"sessions": {"$elemMatch": {"date": data['date'], "time": data['time']}}},
            {"$pull": {"sessions": {"date": data['date'], "time": data['time']}}}
        )

        if result.modified_count > 0:
            return jsonify({"message": "Session deleted successfully"}), 200
        else:
            return jsonify({"error": "Session not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
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

@app.route('/login', methods=['POST'])
def login():
    login_data = request.get_json()
    email = login_data.get('email') 
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})
    print(user)
    
    
    if user:
        name = user.get('name')
        return jsonify({'success': True, 'message': 'Login successfull','name': name}), 200
    return jsonify({'success': False,'message': 'Email and Mobile Number is not registered'}), 200

@app.route('/getuserdetails', methods=['GET'])
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

    
@app.route('/updatelevel', methods=['POST'])
def update_user_level():
    data = request.get_json()
    user_name = data.get('name')
    user_level = data.get('level')  # Assuming 'level' is the key for the level
    
    if not user_name:
        return jsonify({'success': False, 'message': 'name parameter is required'}), 400
    
    if user_level is None:
        return jsonify({'success': False, 'message': 'level parameter is required'}), 400
    
    try:
        # Update user's level in the database
        user = users_collection.find_one_and_update(
            {'name': user_name},
            {'$set': {'level': user_level}},
            return_document=ReturnDocument.AFTER
        )

        if user:
            user_details = {
                'name': user.get('name', ''),
                'email': user.get('email', ''),
                'image': user.get('image', ''),
                'level': user.get('level', ''),
                # Add other fields as needed
            }
            return jsonify({'success': True, 'data': user_details}), 200
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/updatepuzzlescore', methods=['POST'])
def update_puzzle_score():
    data = request.get_json()
    email = data.get('email')
    addscoretopuzzle = data.get('addscoretopuzzle')
    
    if not email:
        return jsonify({'success': False, 'message': 'email parameter is required'}), 400
    
    if addscoretopuzzle is None:
        return jsonify({'success': False, 'message': 'addscoretopuzzle parameter is required'}), 400
    
    try:
        # Search for the user by email
        user = users_collection.find_one({'email': email})
        
        if user:
            # Check if "puzzle score" field exists and update it
            puzzle_score = user.get('puzzle_score', 0)  # Default to 0 if not present
            new_puzzle_score = puzzle_score + addscoretopuzzle
            
            updated_user = users_collection.find_one_and_update(
                {'email': email},
                {'$set': {'puzzle_score': new_puzzle_score}},
                return_document=ReturnDocument.AFTER
            )
            
            user_details = {
                'name': updated_user.get('name', ''),
                'email': updated_user.get('email', ''),
                'image': updated_user.get('image', ''),
                'level': updated_user.get('level', ''),
                'puzzle_score': updated_user.get('puzzle_score', 0),
                # Add other fields as needed
            }
            return jsonify({'success': True, 'data': user_details}), 200
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run()

