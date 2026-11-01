"""Direct Gmail SMTP Dispatcher using App Passwords."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple


def send_gmail_response(
    recipient_email: str,
    subject: str,
    body: str,
) -> Tuple[bool, str]:
    """Sends an email directly through Gmail SMTP using an App Password.

    Args:
        recipient_email: Destination email address.
        subject: Email subject line.
        body: Body text of the email.

    Returns:
        (success: bool, message: str)
    """
    sender_email = os.getenv("GMAIL_USER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        return False, "Gmail credentials (GMAIL_USER or GMAIL_APP_PASSWORD) missing in .env"

    msg = MIMEMultipart()
    msg["From"] = f"Customer Support Desk <{sender_email}>"
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        return True, f"Email sent successfully to {recipient_email}"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Check your Gmail address and 16-character App Password."
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
