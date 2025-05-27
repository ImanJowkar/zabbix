import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()



SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
PASSWORD = os.getenv('PASSWORD')
USERNAME = os.getenv('USERNAME')

RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')



SUBJECT = 'Test Email'
BODY = 'This is a test email sent using SMTP over SSL.'



def send_email(smtp_server, port, sender_email, username, password, recipient_email, subject, body):


    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject


    msg.attach(MIMEText(body, 'plain'))


    context = ssl.create_default_context()

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(username, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")






send_email(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, USERNAME, PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)