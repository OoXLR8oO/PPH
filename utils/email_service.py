import smtplib
from email.message import EmailMessage

from api.config import settings


def send_email(from_addr, to_addr, subject, body):
    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(settings.email_addr, settings.email_pass)
        smtp.send_message(msg)
