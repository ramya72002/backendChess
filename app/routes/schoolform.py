from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from app.database import schoolform_coll

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
from app.utils.email_utils import send_email
 

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
        RequestFinancialAssistance = data.get('RequestFinancialAssistance')
        SchoolName=data.get('SchoolName')
        
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
            },
            "RequestFinancialAssistance":RequestFinancialAssistance,
            "SchoolName":SchoolName
        }
        

        # Insert into MongoDB
        schoolform_coll.insert_one(form_data)

        return jsonify({"message": "Form submitted successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@schoolform_bp.route('/get_forms', methods=['GET'])
def get_forms():
    try:
        # Fetch all documents from the collection
        records = list(schoolform_coll.find({}, {'_id': 0}))  # Exclude the MongoDB ID field
        
        return jsonify(records), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@schoolform_bp.route('/send-email-form', methods=['POST'])
def send_email_school_form():
    data = request.json
    email = data.get('email')
    parent_first_name = data.get('parent_first_name')
    parent_last_name = data.get('parent_last_name')
    child_first_name = data.get('child_first_name')
    child_last_name = data.get('child_last_name')
    school_name = data.get('SchoolName', "Lombardy Elementary School")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Email configuration
        sender_email = "connect@chesschamps.us"
        sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
        subject = "Thank You for Enrolling Your Child in the Lombardy Chess Program!"

        body = (
            f"Dear {parent_first_name} {parent_last_name},\n\n"
            f"We are excited to welcome {child_first_name}  {child_last_name} to the after-school chess program at {school_name}! "
            f"Thank you for trusting us with your child's chess development and for encouraging their interest in this wonderful game.\n\n"
            
            f"At Chess Champs, we believe that chess sharpens minds and nurtures critical thinking, problem-solving, and concentration skills. "
            f"Our program is both fun and educational, and we are committed to making this an enriching experience for {child_first_name}.\n\n"
            
            f"**Program Details:**\n"
            f"- **Start Date**: 26 Sep 2024\n"
            f"- **Duration**: 10 weeks\n"
            f"- **Time**: 3:30 PM - 4:30 PM\n\n"
            
            f"Throughout the program, {child_first_name} will learn valuable chess strategies, participate in friendly matches, "
            f"and develop confidence both on and off the board.\n\n"
            
            f"Please feel free to contact us if you have any questions or need further information.\n\n"
            
            f"Once again, thank you for enrolling {child_first_name} in our program. We look forward to an exciting journey ahead!\n\n"
            
            f"Best regards,\n"
            f"Training Team\n"
            f"Delaware Chess Champs\n"
            f"connect@chesschamps.us"
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
