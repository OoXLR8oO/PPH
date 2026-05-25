import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing environment variable: {name}")
    return value


EMAIL_FROM = require_env("EMAIL_FROM")
EMAIL_PASSWORD = require_env("EMAIL_PASSWORD")
SMTP_HOST = require_env("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))


def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        # smtp.starttls()
        print(SMTP_HOST, SMTP_PORT)
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(msg)


send_email("kartikpunna5@gmail.com", "Test Email", "This works")
