import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(email, session_link, date, time, coach_name):
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

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, email, text)
    server.quit()
