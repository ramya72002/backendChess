from bson import ObjectId
from flask import Blueprint, request, jsonify
import requests
from app.database import admin_collection,users_collection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
import os

stripe_url = "https://api.stripe.com/v1/checkout/sessions"
secret_key = os.getenv('STRIPE_SECRET_KEY')
payment_link = os.getenv('PAYMENT_LINK')
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
        'completed_percentage': 0,
        'payment_status': "Not started"
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

@courses_bp.route('/update-course-completion', methods=['POST'])
def update_course_completion():
    data = request.json
    required_fields = ['email', 'title', 'completed']

    # Check for required fields
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    email = data['email']
    title = data['title']
    completed = data['completed']

    # Search for the user by email
    existing_user = users_collection.find_one({'email': email})

    if not existing_user:
        return jsonify({'error': 'User not found'}), 404

    # Check if 'registered_courses' field exists
    if 'registered_courses' not in existing_user:
        return jsonify({'error': 'No registered courses found for this user'}), 404

    registered_courses = existing_user['registered_courses']
    
    # Find the course
    course_found = False
    for course in registered_courses:
        if course['title'] == title:
            course_found = True
            # Check if the new completed value is greater
            if course['completed_percentage'] < completed:
                # Update the completed_percentage
                users_collection.update_one(
                    {'email': email, 'registered_courses.title': title},
                    {'$set': {'registered_courses.$.completed_percentage': completed}}
                )
                return jsonify({'message': 'Course completion updated successfully'}), 200
            else:
                return jsonify({'message': 'No update needed, completed value is not greater'}), 200

    if not course_found:
        return jsonify({'error': 'Course not found'}), 404


@courses_bp.route('/update-payment-status', methods=['PUT'])
def update_payment_status():
    data = request.json
    required_fields = ['email', 'title', 'payment_status']
    
    # Check for required fields
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    email = data['email']
    title = data['title']
    payment_status = data['payment_status']

    # Search for the user by email
    existing_user = users_collection.find_one({'email': email})

    if not existing_user:
        return jsonify({'error': 'User not found'}), 404

    # Check if 'registered_courses' field exists and if the course is registered
    if 'registered_courses' not in existing_user:
        return jsonify({'error': 'No registered courses found for this user'}), 400

    # Find the course and update the payment status
    course_found = False
    for course in existing_user['registered_courses']:
        if course['title'] == title:
            course_found = True
            break

    if not course_found:
        return jsonify({'error': 'Course not found'}), 404

    # Update the payment status
    users_collection.update_one(
        {'email': email, 'registered_courses.title': title},
        {'$set': {'registered_courses.$.payment_status': payment_status}}
    )

    return jsonify({'message': 'Payment status updated successfully'}), 200


@courses_bp.route('/send_course_reg_email', methods=['POST'])
def send_email():
    data = request.json
    email = data.get('email') 
    title = data.get('title') 

    if not email or not title:
        return jsonify({"error": "Email and Title are required"}), 400

    try:
        # Email configuration
        sender_email = "connect@chesschamps.us"
        sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
        subject = "Course Registration - Action Required"

        body = f"""
        Dear Participant,

        Thank you for registering for the course: "{title}".

        To complete your registration, please make a payment of $10 using the following link:

        https://buy.stripe.com/3cs4jw8xYePG6Qg9AA

        After making the payment, please note down the transaction ID as it will be important for confirming your registration.

        If you have any questions or need further assistance, feel free to contact us.

        Best regards,
        The Course Team
        """

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

@courses_bp.route('/check-email', methods=['GET'])
def check_email():
    # Retrieve the email and payment link from the query parameters
    email_to_check = request.args.get('email')
    email_to_check = email_to_check.strip()

    if not email_to_check:
        return jsonify({'error': "'email' query parameter is required"}), 400

    if not payment_link:
        return jsonify({'error': "'payment_link' query parameter is required"}), 400

    # Make the API call
    response = requests.get(
        stripe_url,
        params={
            "payment_link": payment_link,
            "expand[]": "data.customer",
            "limit": 100
        },
        auth=(secret_key, '')
    )

    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve data from Stripe'}), response.status_code

    data = response.json()

    # Extract email addresses from the response
    emails = []
    emails.append("nsriramya7@gmail.com")
    emails.append("sumit.compliance@gmail.com")
    for session in data.get('data', []):
        customer = session.get('customer_details')
        if customer and isinstance(customer, dict):
            email = customer.get('email')
            if email:
                emails.append(email)

    # Check if the provided email is in the list
    if email_to_check in emails:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 200

