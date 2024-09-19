from email import errors
from bson import ObjectId
from flask import Blueprint, request, jsonify
from pymongo import ReturnDocument
import random
import smtplib
from app.database import db, fs
import os
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.database import schoolform_coll


inschool_bp = Blueprint('inschool', __name__)
# Email configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'connect@chesschamps.us')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'iyln tkpp vlpo sjep')

# Utility function to send OTP via email
def send_otp(email, otp):
    try:
        subject = "Your OTP for Sign-In to Online Portal"
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

@inschool_bp.route('/signin_inschool', methods=['POST'])
def signinschool():
    login_data = request.get_json()
    email = login_data.get('email')
    device_name = login_data.get('device_name')
    
    # Retrieve the user from the database
    user = schoolform_coll.find_one({'email': email})
    
    if user["group"]=="In School Program":
        # Check if 'session_id' exists
        if 'session_id' in user:
            return jsonify({'success': True, 'device': True,'device_name':user['device_name']}), 200
        else:
            # Generate a new UUID for session_id
            session_id = str(uuid.uuid4())
            schoolform_coll.update_one({'email': email}, {'$set': {'session_id': session_id,'device_name':device_name}})
            
            # Continue with the OTP process
            if 'otp' not in user or user['otp'] is None:
                otp = random.randint(100000, 999999)
                schoolform_coll.update_one({'email': email}, {'$set': {'otp': otp}})
                send_otp(email, otp)
                return jsonify({'success': True, 'message': 'OTP sent to email.', 'otp_required': True}), 200
            else:
                return jsonify({'success': True, 'message': 'OTP already sent.', 'otp_required': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Email is not registered.'}), 400
    

@inschool_bp.route('/delete_session_inschool', methods=['POST'])
def delete_session_inschool():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'success': False, 'message': 'Email is required.'}), 400

    # Find the user and update
    result = schoolform_coll.update_one(
        {'email': email},
        {'$unset': {'session_id': '','device_name':''}}
    )

    if result.matched_count == 0:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    return jsonify({'success': True, 'message': 'Session ID removed successfully.'}), 200
# OTP Verification API
@inschool_bp.route('/verify_otp_inschool', methods=['POST'])
def verify_otp_inschool():
    otp_data = request.get_json()
    email = otp_data.get('email')
    otp = otp_data.get('otp')
    print(email,otp)
    # Verify that both email and OTP are provided
    if not email or not otp:
        return jsonify({'success': False, 'message': 'Email and OTP are required.'}), 400

    # Find the user by email
    user = schoolform_coll.find_one({'email': email})
    print(str(user.get('otp')) == otp)

    # Check if user exists and OTP matches
    if user and str(user.get('otp')) == otp:
        # OTP matches, clear it from the database
        schoolform_coll.update_one({'email': email}, {'$unset': {'otp': ""}})
        return jsonify({'success': True, 'message': 'OTP verified successfully.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid OTP or email.'}), 400

@inschool_bp.route('/getinschooldetails', methods=['GET'])
def get_user_inschool_details():
    email = request.args.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email parameter is required'}), 400
    
    # Retrieve the user from the database, excluding the _id field
    user = schoolform_coll.find_one(
        {'email': email},
        {'_id': 0}  # Exclude _id field from the results
    )
    
    if user:
        return jsonify({'success': True, 'data': user}), 200
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404


@inschool_bp.route('/imageupdateinschool', methods=['POST'])
def update_user_inschool_image():
    data = request.get_json()
    profile_id = data.get('profile_id')
    image_url = data.get('image')  # Assuming 'image' is the key for the image URL
    
    if not profile_id:
        return jsonify({'success': False, 'message': 'name parameter is required'}), 400
    
    try:
        # Update user's image in the database
        user = schoolform_coll.find_one_and_update(
            {'profile_id': profile_id},
            {'$set': {'image': image_url}},
            return_document=ReturnDocument.AFTER
        )

        if user:
            user_details = {
                'profile_id': user.get('profile_id', ''),
                'email': user.get('email', ''),
                'image': user.get('image', ''),
            }
            return jsonify({'success': True, 'data': user_details}), 200
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500\
        

@inschool_bp.route('/create_Arena_user_inschool', methods=['POST'])
def arena_user_details_inschool():
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
    user = schoolform_coll.find_one({'email': email})
    
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
        schoolform_coll.update_one({'email': email}, {'$set': user})
        
        return jsonify({'success': True, 'message': user['PuzzleArena']}), 200
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    

@inschool_bp.route('/images/title', methods=['GET'])
def get_images_by_title():
    title=request.args.get('title')
    level = request.args.get('level')
    category = request.args.get('category')
    try:
        # Find the image set by both title and level
        image_set = db.image_sets.find_one({'title': title, 'level': level,'category': category})
        if not image_set:
            return jsonify({'error': 'No images found with the given title and level'}), 404
        print(image_set)

        image_data = []
        for file_id in image_set['file_ids']:
            file = fs.get(ObjectId(image_set['file_ids'][file_id]['id']))
            image_data.append({
                'id': image_set['file_ids'][file_id]['id'],
                'filename': file.filename,
                'url': f"/image/{image_set['file_ids'][file_id]['id']}"
            })

        return jsonify({'images': image_data}), 200
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500


@inschool_bp.route('/update_puzzle_started_inschool', methods=['POST'])
def update_puzzle_started_inschool():
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
    user = schoolform_coll.find_one({'email': email})

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
            schoolform_coll.update_one(
                {'email': email},
                {'$set': {f'PuzzleArena.{category}.{title}.{puzzle_no}': puzzle_data}}
            )

            return jsonify({'success': True, 'message': 'Puzzle started flag and score updated successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Specified category or title not found'}), 404
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

@inschool_bp.route('/get_Arena_user_inschool', methods=['GET'])
def get_Arena_user_inschool():
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
    user = schoolform_coll.find_one({'email': email})
    
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
    

@inschool_bp.route('/get_visited_info_inschool', methods=['GET'])
def get_puzzle_visited_info_inschool():
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
    user = schoolform_coll.find_one({'email': email})

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


@inschool_bp.route('/update_registered_courses_inschool', methods=['POST'])
def update_registered_courses_inschool():
    email = request.json.get('email')
    course_title = request.json.get('course_title')
    status = request.json.get('status')

    if not all([email, course_title, status]):
        return jsonify({'success': False, 'message': 'Email, course_title, and status are required'}), 400

    # Retrieve the user from the database
    user = schoolform_coll.find_one({'email': email})

    if user:
        # Initialize registered_courses if it does not exist
        if 'registered_inschool_courses' not in user:
            user['registered_inschool_courses'] = []

        # Find the specific course
        course = next((course for course in user['registered_inschool_courses'] if course['course_title'] == course_title), None)
        
        if course:
            # Check if the current status in the database is 'Completed'
            if course['status'] == 'Completed' and status == 'In Progress':
                return jsonify({'success': True, 'message': 'Cannot update to In Progress as the course is already completed'}), 200

            # Update the existing course entry
            schoolform_coll.update_one(
                {'email': email, 'registered_inschool_courses.course_title': course_title},
                {'$set': {'registered_inschool_courses.$.status': status}}
            )
        else:
            # Add a new course entry
            schoolform_coll.update_one(
                {'email': email},
                {'$push': {'registered_inschool_courses': {'course_title': course_title, 'status': status, 'completed': 0}}}
            )
        
        return jsonify({'success': True, 'message': 'Registered courses updated successfully'}), 200
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404



@inschool_bp.route('/update-course-completion-inschool', methods=['POST'])
def update_course_completion_inschool():
    data = request.json
    required_fields = ['email', 'course_title', 'completed']

    # Check for required fields
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    email = data['email']
    course_title = data['course_title']
    completed = data['completed']

    # Search for the user by email
    existing_user = schoolform_coll.find_one({'email': email})

    if not existing_user:
        return jsonify({'error': 'User not found'}), 404

    # Check if 'registered_inschool_courses' field exists
    if 'registered_inschool_courses' not in existing_user:
        return jsonify({'error': 'No registered_inschool_courses found for this user'}), 404

    registered_inschool_courses = existing_user['registered_inschool_courses']
    
    # Find the course
    course_found = False
    for course in registered_inschool_courses:
        if course['course_title'] == course_title:
            course_found = True
            # Check if the new completed value is greater
            if course['completed'] < completed:
                # Update the completed_percentage
                schoolform_coll.update_one(
                    {'email': email, 'registered_inschool_courses.course_title': course_title},
                    {'$set': {'registered_inschool_courses.$.completed': completed}}
                )
                return jsonify({'message': 'Course completion updated successfully'}), 200
            else:
                return jsonify({'message': 'No update needed, completed value is not greater'}), 200

    if not course_found:
        return jsonify({'error': 'Course not found'}), 404

@inschool_bp.route('/calculate_scores_inschool', methods=['POST'])
def calculate_scores_inschool():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 415
    
    data = request.get_json()
    
    if 'email' not in data:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    
    email = data['email']
    
    # Retrieve the user from the database
    user = schoolform_coll.find_one({'email': email})
    
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
    update_result = schoolform_coll.update_one(
        {'email': email},
        {'$set': {'scores': scores}}
    )
    
    # Log the result for debugging
    print(f"Update result: {update_result.raw_result}")
    
    if update_result.modified_count > 0:
        return jsonify({'success': True, 'scores': scores}), 200
    else:
        return jsonify({'success': True, 'scores': scores}), 200