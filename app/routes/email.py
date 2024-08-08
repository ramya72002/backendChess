from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Blueprint, request, jsonify
from app.utils.email_utils import send_email

email_bp = Blueprint('email', __name__)

@email_bp.route('/send-email', methods=['POST'])
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


