from bson import ObjectId
from flask import Blueprint, request, jsonify
from app.database import admin_collection,users_collection
import re

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/add-course', methods=['POST'])
def add_course():
    data = request.json
    required_fields = ['email', 'title']
    
    # Check for required fields
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    email = data['email']
    title = data['title']

    # Search for the user by email
    existing_user = users_collection.find_one({'email': email})

    if not existing_user:
        return jsonify({'error': 'User not found'}), 404

    # Check if 'registered_courses' field exists
    if 'registered_courses' not in existing_user:
        users_collection.update_one(
            {'email': email},
            {'$set': {'registered_courses': []}}
        )
        registered_courses = []
    else:
        registered_courses = existing_user['registered_courses']

    # Check if the course title already exists
    for course in registered_courses:
        if course['title'] == title:
            return jsonify({'error': 'You have already registered for this course'}), 200

    # Prepare the new course record
    new_course = {
        'title': title,
        'completed_percentage': 0
    }

    # Add the new course to the 'registered_courses' list
    users_collection.update_one(
        {'email': email},
        {'$push': {'registered_courses': new_course}}
    )

    return jsonify({'message': 'Course registered successfully'}), 200

 
@courses_bp.route('/get-registered-courses', methods=['GET'])
def get_registered_courses():
    email = request.args.get('email')

    if not email:
        return jsonify({'error': "'email' query parameter is required"}), 400

    # Search for the user by email
    existing_user = users_collection.find_one({'email': email})

    if not existing_user:
        return jsonify({'error': 'User not found'}), 404

    # Get the registered courses, or return an empty list if not present
    registered_courses = existing_user.get('registered_courses', [])

    return jsonify({'registered_courses': registered_courses}), 200

 