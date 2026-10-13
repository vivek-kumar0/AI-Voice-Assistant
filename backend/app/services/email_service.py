import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_password_reset_email(to_email: str, reset_url: str) -> None:
    if not all([settings.smtp_host, settings.smtp_user, settings.smtp_password, settings.from_email]):
        raise RuntimeError("SMTP is not configured. Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD and FROM_EMAIL.")

    msg = EmailMessage()
    msg["Subject"] = "Reset your Nova AI Assistant password"
    msg["From"] = settings.from_email
    msg["To"] = to_email
    msg.set_content(
        "We received a request to reset your Nova AI Assistant password.\n\n"
        f"Open this link to choose a new password:\n{reset_url}\n\n"
        "This link expires in 30 minutes and can be used only once. "
        "If you did not request a password reset, you can safely ignore this email."
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
