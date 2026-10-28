import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    pass


def email_delivery_configured() -> bool:
    return bool(settings.smtp_host and settings.email_from)


def send_action_email(recipient: str, action: str, token: str) -> None:
    if not email_delivery_configured():
        raise EmailDeliveryError("SMTP_HOST and EMAIL_FROM must be configured for email delivery.")
    if action not in {"verify-email", "password-reset"}:
        raise ValueError(f"Unsupported email action: {action}")

    subject = "Verify your Healthspan Network account" if action == "verify-email" else "Reset your Healthspan Network password"
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = recipient
    endpoint = "verify-email" if action == "verify-email" else "password-reset/confirm"
    message.set_content(
        "Use this one-time token in the Healthspan Network application:\n\n"
        f"{token}\n\n"
        f"The application submits it to POST /api/v1/auth/{endpoint}.\n"
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password or "")
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError("The configured email provider could not deliver the message.") from exc
