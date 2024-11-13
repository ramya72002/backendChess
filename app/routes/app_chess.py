import random
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import app_signup

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from app.utils.email_utils import send_email

appchess_bp = Blueprint('app_chess', __name__)

# Function to generate a random 6-digit profile_id
def generate_unique_profile_id_1():
    while True:
        profile_id = str(random.randint(100000, 999999))  # Generate a random 6-digit number
        # Check if the profile_id already exists in the database
        if app_signup.count_documents({"profile_id": profile_id}) == 0:
            return profile_id
        
@appchess_bp.route('/r')
def home1():
    return "Hello, ramya!"


@appchess_bp.route('/signup_app', methods=['POST'])
def signup_app():
    try:
        # Parse the incoming JSON data
        
        data = request.get_json()
        print(data)

        # Extract and validate required fields
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        school = data.get('school')
        grade = data.get('grade')

        # Optional: Perform validation on the data (e.g., check if email is valid)
        if not name or not email or not phone or not school or not grade:
            return jsonify({"error": "All fields are required"}), 400

        # Generate a unique profile_id
        profile_id = generate_unique_profile_id_1()

        # Prepare document for MongoDB insertion
        form_data = {
            "profile_id": profile_id,  # Add the unique profile_id here
            "name": name,
            "email": email,
            "phone": phone,
            "school": school,
            "grade": grade        }

        # Insert into MongoDB
        app_signup.insert_one(form_data)

        # Optionally, you can send a confirmation email here
        # send_email(email, "Welcome to Chess App!", "Thank you for signing up!")

        return jsonify({"message": "Form submitted successfully!", "profile_id": profile_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@appchess_bp.route('/get_forms1', methods=['GET'])
def get_forms1():
    try:
        # Fetch all documents from the collection
        records = list(app_signup.find({}, {'_id': 0}))  # Exclude the MongoDB ID field
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
