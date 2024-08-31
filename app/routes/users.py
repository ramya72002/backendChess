from flask import Blueprint, request, jsonify
from pymongo import ReturnDocument
from app.database import users_collection
import random
import smtplib
import os
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

users_bp = Blueprint('users', __name__)

# Email configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'kidschesstournament@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'rrcd xdhn dpig ijqk')

# Utility function to send OTP via email
def send_otp(email, otp):
    try:
        subject = "Your OTP for Sign-In to Kids Learning Portal"
        body = f"Your OTP is {otp} "

        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, email, text)
        server.quit()

        print("OTP sent successfully.")
    except Exception as e:
        print(f"Failed to send OTP: {e}")

# Signup API
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

# Login API
@users_bp.route('/login', methods=['POST'])
def signin():
    login_data = request.get_json()
    email = login_data.get('email')
    device_name = login_data.get('device_name')
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})
    
    if user:
        # Check if 'session_id' exists
        if 'session_id' in user:
            return jsonify({'success': True, 'device': True,'device_name':user['device_name']}), 200
        else:
            # Generate a new UUID for session_id
            session_id = str(uuid.uuid4())
            users_collection.update_one({'email': email}, {'$set': {'session_id': session_id,'device_name':device_name}})
            
            # Continue with the OTP process
            if 'otp' not in user or user['otp'] is None:
                otp = random.randint(100000, 999999)
                users_collection.update_one({'email': email}, {'$set': {'otp': otp}})
                send_otp(email, otp)
                return jsonify({'success': True, 'message': 'OTP sent to email.', 'otp_required': True}), 200
            else:
                return jsonify({'success': True, 'message': 'OTP already sent.', 'otp_required': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Email is not registered.'}), 400
    

@users_bp.route('/delete_session', methods=['POST'])
def delete_session():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'success': False, 'message': 'Email is required.'}), 400

    # Find the user and update
    result = users_collection.update_one(
        {'email': email},
        {'$unset': {'session_id': '','device_name':''}}
    )

    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    return jsonify({'success': True, 'message': 'Session ID removed successfully.'}), 200
# OTP Verification API
@users_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    otp_data = request.get_json()
    email = otp_data.get('email')
    otp = otp_data.get('otp')
    print(email,otp)
    # Verify that both email and OTP are provided
    if not email or not otp:
        return jsonify({'success': False, 'message': 'Email and OTP are required.'}), 400

    # Find the user by email
    user = users_collection.find_one({'email': email})
    print(str(user.get('otp')) == otp)

    # Check if user exists and OTP matches
    if user and str(user.get('otp')) == otp:
        # OTP matches, clear it from the database
        users_collection.update_one({'email': email}, {'$unset': {'otp': ""}})
        return jsonify({'success': True, 'message': 'OTP verified successfully.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid OTP or email.'}), 400


@users_bp.route('/getuserdetails', methods=['GET'])
def get_user_details():
    email = request.args.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email parameter is required'}), 400
    
    # Retrieve the user from the database, excluding the _id field
    user = users_collection.find_one(
        {'email': email},
        {'_id': 0}  # Exclude _id field from the results
    )
    
    if user:
        return jsonify({'success': True, 'data': user}), 200
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

@users_bp.route('/calculate_scores', methods=['POST'])
def calculate_scores():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 415
    
    data = request.get_json()
    
    if 'email' not in data:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    
    email = data['email']
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    # Initialize scores dictionary
    scores = {
        "Opening": 0,
        "Middlegame": 0,
        "Endgame": 0,
        "Mixed": 0
    }
    
    # Calculate scores for each category
    puzzle_arena = user.get('PuzzleArena', {})
    
    for category in scores.keys():
        category_arena = puzzle_arena.get(category, {})
        for puzzle_set in category_arena.values():
            for puzzle in puzzle_set.values():
                scores[category] += puzzle.get('score', 0)
    
    # Update the user's record with the calculated scores
    update_result = users_collection.update_one(
        {'email': email},
        {'$set': {'scores': scores}}
    )
    
    # Log the result for debugging
    print(f"Update result: {update_result.raw_result}")
    
    if update_result.modified_count > 0:
        return jsonify({'success': True, 'scores': scores}), 200
    else:
        return jsonify({'success': True, 'scores': scores}), 200

# Your existing database collection
# Make sure to initialize `users_collection` appropriately in your actual code

@users_bp.route('/get_Arena_user', methods=['GET'])
def get_arena_user_details():
    email = request.args.get('email')
    category = request.args.get('category')
    title = request.args.get('title')
    
    if not all([email, category, title]):
        return jsonify({'success': False, 'message': 'Email, category, and title are required'}), 400
    
    # Ensure the category is one of the default categories
    default_categories = ["Opening", "Middlegame", "Endgame", "Mixed"]
    if category not in default_categories:
        return jsonify({'success': False, 'message': f'Category must be one of {default_categories}'}), 400
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})
    
    if user:
        if 'PuzzleArena' not in user:
            return jsonify({'success': False, 'message': 'PuzzleArena field not found'}), 200
        # Check if the PuzzleArena exists and contains the specified category and title
        puzzle_arena = user.get('PuzzleArena', {})
        category_arena = puzzle_arena.get(category, {})
        puzzles = category_arena.get(title, {})
        
        if puzzles:
            return jsonify({'success': True, 'puzzleArena': puzzles}), 200
        else:
            return jsonify({'success': False, 'message': 'PuzzleArena details not found for the specified category and title'}), 200
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
@users_bp.route('/create_Arena_user', methods=['POST'])
def arena_user_details():
    email = request.json.get('email')
    category = request.json.get('category')
    title = request.json.get('title')
    puzzle_no = request.json.get('puzzle_no')
    
    if not all([email, category, title, puzzle_no]):
        return jsonify({'success': False, 'message': 'Email, category, title, and puzzle_no are required'}), 400
    
    try:
        puzzle_no = int(puzzle_no)
    except ValueError:
        return jsonify({'success': False, 'message': 'Puzzle number must be an integer'}), 400
    
    # Ensure the category is one of the default categories
    default_categories = ["Opening", "Middlegame", "Endgame", "Mixed"]
    if category not in default_categories:
        return jsonify({'success': False, 'message': f'Category must be one of {default_categories}'}), 400
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})
    
    if user:
        # Initialize PuzzleArena if not present
        if 'PuzzleArena' not in user:
            user['PuzzleArena'] = {cat: {} for cat in default_categories}
        
        if title not in user['PuzzleArena'][category]:
            # Create new puzzles if title doesn't exist
            puzzles = {f'Puzzle{i+1}': {'started': False, 'option_guessed': None,'timer': 0, 'score': 0} for i in range(puzzle_no)}
            user['PuzzleArena'][category][title] = puzzles
        else:
            # Append new puzzles only if more are needed
            existing_puzzles = user['PuzzleArena'][category][title]
            current_max_puzzle_no = len(existing_puzzles)
            
            if puzzle_no > current_max_puzzle_no:
                # Calculate how many new puzzles are needed
                new_puzzles = {f'Puzzle{i+current_max_puzzle_no+1}': {'started': False, 'option_guessed': None,'timer': 0, 'score': 0} for i in range(puzzle_no - current_max_puzzle_no)}
                existing_puzzles.update(new_puzzles)
        
        # Save the updated user back to the database
        users_collection.update_one({'email': email}, {'$set': user})
        
        return jsonify({'success': True, 'message': user['PuzzleArena']}), 200
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404



@users_bp.route('/update_puzzle_started', methods=['POST'])
def update_puzzle_started():
    email = request.json.get('email')
    category = request.json.get('category')
    title = request.json.get('title')
    puzzle_no = request.json.get('puzzle_no')
    score = request.json.get('score', None)  # Optional score field, default is None
    option_guessed = request.json.get('option_guessed', None)
    timer = request.json.get('timer', 0)

    if not all([email, category, title, puzzle_no]):
        return jsonify({'success': False, 'message': 'Email, category, title, and puzzle_no are required'}), 400

    # Ensure the category is one of the default categories
    default_categories = ["Opening", "Middlegame", "Endgame", "Mixed"]
    if category not in default_categories:
        return jsonify({'success': False, 'message': f'Category must be one of {default_categories}'}), 400

    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})

    if user:
        # Check if the specified title and category exist in the user's PuzzleArena
        if category in user.get('PuzzleArena', {}) and title in user['PuzzleArena'][category]:
            # Update the started flag and score if provided
            puzzle_data = user['PuzzleArena'][category][title].get(puzzle_no, {})
            puzzle_data['started'] = True
            if (puzzle_data['score']==1):
                return jsonify({'success': True, 'message': 'Puzzle started flag and score updated successfully'}), 200

            # Check the existing value of option_guessed in the database
            existing_option_guessed = puzzle_data.get('option_guessed', None)
            
            if existing_option_guessed is False:
                # If option_guessed is False in the database, set score to 0
                puzzle_data['score'] = 0
                
            elif score is not None:
                # Otherwise, update the score as provided
                puzzle_data['score'] = score

            # Update option_guessed based on the input, unless it's False in the database
            if option_guessed is not None:
                puzzle_data['option_guessed'] = option_guessed
            puzzle_data['timer']=timer
            # Update the user document in the database
            users_collection.update_one(
                {'email': email},
                {'$set': {f'PuzzleArena.{category}.{title}.{puzzle_no}': puzzle_data}}
            )

            return jsonify({'success': True, 'message': 'Puzzle started flag and score updated successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Specified category or title not found'}), 404
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

@users_bp.route('/get_visited_info', methods=['GET'])
def get_puzzle_visited_info():
    email = request.args.get('email')
    category = request.args.get('category')
    title = request.args.get('title')
    puzzle_no = request.args.get('puzzle_no')

    if not all([email, category, title, puzzle_no]):
        return jsonify({'success': False, 'message': 'Email, category, title, and puzzle_no are required'}), 400

    # Ensure the category is one of the default categories
    default_categories = ["Opening", "Middlegame", "Endgame", "Mixed"]
    if category not in default_categories:
        return jsonify({'success': False, 'message': f'Category must be one of {default_categories}'}), 400

    # Retrieve the user from the database
    user = users_collection.find_one({'email': email})

    if user:
        # Check if the specified category and title exist in the user's PuzzleArena
        if category in user.get('PuzzleArena', {}) and title in user['PuzzleArena'][category]:
            puzzle_data = user['PuzzleArena'][category][title].get(puzzle_no, {})
            option_guessed = puzzle_data.get('option_guessed', None)

            return jsonify({'success': True, 'option_guessed': option_guessed}), 200
        else:
            return jsonify({'success': False, 'message': 'Specified category or title not found'}), 404
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

@users_bp.route('/updatelevel', methods=['POST'])
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


@users_bp.route('/updatepuzzlescore', methods=['POST'])
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


