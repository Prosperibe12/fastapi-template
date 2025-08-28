import asyncio

from backend.services.auth_notification import AuthNotificationService
from backend.services.email_service import EmailService
from backend.core.config import Settings
from .celery import app

@app.task
def send_register_email(new_user):
    """Task to send registration email."""

    email_service = EmailService(Settings())
    auth_notification_service = AuthNotificationService(email_service)

    asyncio.run(auth_notification_service.send_registration_email(new_user))

@app.task
def send_reset_password_email(data):
    """Task to send reset password email."""

    email_service = EmailService(Settings())
    auth_notification_service = AuthNotificationService(email_service)

    asyncio.run(auth_notification_service.send_reset_password_email(data))
