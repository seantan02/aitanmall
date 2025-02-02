from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import smtplib

def test_sending(recipient,subject,html):
    try:
        smtp_server = 'smtp.hostinger.com'
        port = 465  # For SSL
        sender_email = 'no-reply@aitanmall.com'  # Enter your address
        password = 'Aitan551813@' # Enter your password
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient
        
        html_part = MIMEText("Hi", "plain")
        # Add HTML/plain-text parts to MIMEMultipart message
        message.attach(html_part)
        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, recipient, message.as_string()
        )
        return True
    except Exception as e:
        return False

def send_html_email(recipient,subject,html):

    try:
        smtp_server = 'smtp.hostinger.com'
        port = 465  # For SSL
        sender_email = 'no-reply@aitanmall.com'  # Enter your address
        password = 'Aitan5358@' # Enter your password
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient
        
        html_part = MIMEText(html, "html")
        # Add HTML/plain-text parts to MIMEMultipart message
        message.attach(html_part)
        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, recipient, message.as_string()
        )
        
        return True
    except Exception as e:
        return e
