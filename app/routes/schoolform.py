from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import schoolform_coll
schoolform_bp = Blueprint('schoolform', __name__)

@schoolform_bp.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Parse the incoming JSON data
        data = request.json
        
        # Extract and validate required fields
        parent_first_name = data.get('parent_first_name')
        parent_last_name = data.get('parent_last_name')
        child_first_name = data.get('child_first_name')
        child_last_name = data.get('child_last_name')
        child_grade = data.get('child_grade')
        email = data.get('email')
        phone = data.get('phone')
        address_line_1 = data.get('address_line_1')
        address_line_2 = data.get('address_line_2')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip_code')
        
        # Optional: Perform validation on the data here (e.g., check if email is valid)

        # Prepare document for MongoDB insertion
        form_data = {
            "parent_name": {
                "first": parent_first_name,
                "last": parent_last_name
            },
            "child_name": {
                "first": child_first_name,
                "last": child_last_name
            },
            "child_grade": child_grade,
            "email": email,
            "phone": phone,
            "address": {
                "line_1": address_line_1,
                "line_2": address_line_2,
                "city": city,
                "state": state,
                "zip_code": zip_code
            }
        }

        # Insert into MongoDB
        schoolform_coll.insert_one(form_data)

        return jsonify({"message": "Form submitted successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400