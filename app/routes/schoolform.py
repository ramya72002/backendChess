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
    

@schoolform_bp.route('/send-email-form-lombardy', methods=['POST'])
def send_email_school_form_lombardy():
    data = request.json
    email = data.get('email')
   

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Email configuration
        sender_email = "connect@chesschamps.us"
        sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
        subject = "Thank You for Enrolling Your Child in the Lombardy Chess Program!"

        body = (
            "Dear Parents,\n\n"
            "We are excited to welcome your child to the after-school chess program at Lombardy Elementary! Thank you for trusting us with your child's chess development and for encouraging their interest in this wonderful game.\n\n"
            "At Chess Champs, we believe that chess not only sharpens minds but also nurtures critical thinking, problem-solving, and concentration skills. Our program is designed to be both fun and educational, and we are committed to making this an enriching experience for your child.\n\n"
            "Classes will begin on Sep 26th, and we have a fantastic lineup of activities planned. Throughout the program, your child will learn valuable chess strategies, participate in friendly matches, and develop their confidence both on and off the board.\n\n"
            "Please don't hesitate to reach out to us if you have any questions or need further information.\n\n"
            "Once again, thank you for enrolling your child in our program. We look forward to an exciting journey ahead!\n\n"
            "Best regards,\n"
            "Training Team\n"
            "Delaware Chess Champs"
        )

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()

        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@schoolform_bp.route('/send-email-form-mpes', methods=['POST'])
def send_email_school_form_mpes():
    data = request.json
    email = data.get('email')
   

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Email configuration
        sender_email = "connect@chesschamps.us"
        sender_password = "iyln tkpp vlpo sjep"  # Use your app-specific password here
        subject = "Thank You for Enrolling Your Child in the Mount Pleasant Elementary School Program!"

        body = (
            "Dear Parents,\n\n"
            "We are excited to welcome your child to the after-school chess program at Mount Pleasant Elementary! Thank you for trusting us with your child's chess development and for encouraging their interest in this wonderful game.\n\n"
            "At Chess Champs, we believe that chess not only sharpens minds but also nurtures critical thinking, problem-solving, and concentration skills. Our program is designed to be both fun and educational, and we are committed to making this an enriching experience for your child.\n\n"
            "Classes will begin on Sep 26th, and we have a fantastic lineup of activities planned. Throughout the program, your child will learn valuable chess strategies, participate in friendly matches, and develop their confidence both on and off the board.\n\n"
            "Please don't hesitate to reach out to us if you have any questions or need further information.\n\n"
            "Once again, thank you for enrolling your child in our program. We look forward to an exciting journey ahead!\n\n"
            "Best regards,\n"
            "Training Team\n"
            "Delaware Chess Champs"
        )

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()

        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

