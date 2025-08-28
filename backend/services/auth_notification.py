import json
from typing import Any, Dict

from backend.api.auth.schema import EmailSchema, TokenSchema
from backend.core.security import create_url_token
from backend.core.config import settings
from .email_service import EmailService

class AuthNotificationService:
    """Service for handling authentication-related notifications."""

    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    async def send_email_with_token(
        self, data: Dict[str, Any],
        subject: str, email_template: str, link_path: str
    ) -> None:
        """Send an email with a tokenized link."""

        user_data = json.loads(data)
        token_schema = TokenSchema(
            id=str(user_data["id"]),
            email=user_data["email"],
            full_name=user_data["full_name"]
        )

        token = create_url_token(token_schema.model_dump())
        verification_link = f"http://localhost:8000{settings.API_VERSION}{link_path}/{token}"

        email_body = token_schema.model_dump()
        email_body["link"] = verification_link

        email_payload = EmailSchema(
            email=user_data["email"],
            body=email_body
        )

        await self.email_service.send_email(email_payload, subject, email_template)

    async def send_registration_email(self, data: Dict[str, Any]) -> None:
        """send a registration email to the provided email address."""

        await self.send_email_with_token(
            data=data,
            subject="Welcome to Our Service! Please Verify Your Email",
            email_template="register_email.html",
            link_path="/auth/verify"
        )

    async def send_reset_password_email(self, data: Dict[str, Any]) -> None:
        """send a password reset email to the provided email address."""

        await self.send_email_with_token(
            data=data,
            subject="Reset Your Password",
            email_template="reset_password_email.html",
            link_path="/auth/password-reset-confirm"
        )
