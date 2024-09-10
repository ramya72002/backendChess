from bson import ObjectId
from flask import Blueprint, request, jsonify
import requests
from app.database import admin_collection,users_collection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
import os

learn_bp = Blueprint('Learn_chess', __name__)



@learn_bp.route('/send_course1_reg_email', methods=['POST'])
def send_course_email1():
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