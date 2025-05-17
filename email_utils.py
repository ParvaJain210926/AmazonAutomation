import smtplib
from email.message import EmailMessage
from config import EMAIL, PASSWORD, SMTP_SERVER, SMTP_PORT

def send_email(subject, content):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)