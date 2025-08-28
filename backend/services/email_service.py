from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from backend.core.config import Settings
from backend.api.auth.schema import EmailSchema

class EmailService:
    """
    Email Service class for sending emails using FastMail.
    args:
        conf (Settings): Configuration settings for the email service.
    """
    def __init__(self, conf: Settings):
        if conf is None:
            raise ValueError("Configuration must be provided for EmailService")
        self.conf = conf
        self.fm = self._set_conf()

    def _set_conf(self):
        """Set the configuration for the email service."""
        config =  ConnectionConfig(
            MAIL_USERNAME = self.conf.EMAIL_HOST_USER,
            MAIL_PASSWORD = self.conf.EMAIL_HOST_PASSWORD,
            MAIL_FROM = self.conf.EMAIL_HOST_USER,
            MAIL_PORT = 587,
            MAIL_SERVER = self.conf.EMAIL_HOST,
            MAIL_STARTTLS = True,
            MAIL_SSL_TLS = False,
            TEMPLATE_FOLDER = Path(__file__).parent.parent / "templates"
        )
        return FastMail(config)

    async def send_email(self, context: EmailSchema, subject, template_name: str):
        """Send an email using the provided context."""
        message = MessageSchema(
            subject=subject,
            recipients=[context.model_dump().get("email")],
            template_body=context.model_dump().get("body"),
            subtype=MessageType.html
        )

        await self.fm.send_message(message, template_name)
