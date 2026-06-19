import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@ai-money-manager.com")
ENV = os.getenv("ENV", "development")


def send_email(to: str, subject: str, body: str, html: bool = False) -> bool:
    """Send an email via SMTP. In development, logs to console instead."""
    if ENV == "development" or not SMTP_HOST:
        logger.info("[DEV EMAIL] To: %s | Subject: %s", to, subject)
        logger.info("[DEV EMAIL] Body: %s", body[:200])
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, [to], msg.as_string())

        logger.info("Email sent to %s: %s", to, subject)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, e, exc_info=True)
        return False


def send_password_reset_email(to: str, token: str, frontend_url: str = "") -> bool:
    """Send password reset email with token."""
    if not frontend_url:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost")
    reset_link = f"{frontend_url}/reset-password?token={token}"

    subject = "Password Reset Request - AI Money Manager"
    body = f"""Hi,

You requested a password reset for your AI Money Manager account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

— AI Money Manager Team
"""

    return send_email(to, subject, body)
