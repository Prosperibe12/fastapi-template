import uuid
from typing import Any, Dict
from pydantic import BaseModel, EmailStr, Field

class RegisterSchema(BaseModel):
    """
    Schema for user registration.
    """
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    """
    Schema for user login.
    """
    email: EmailStr
    password: str = Field(min_length=8)

class TokenData(BaseModel):
    "Token data schema."
    access_token: str
    refresh_token: str

class UserData(BaseModel):
    """
    User data schema.
    """
    id: str
    email: EmailStr
    full_name: str
    is_verified: bool

class UserLoginResponse(TokenData):
    """Login Response Schema"""
    user: UserData

class TokenSchema(BaseModel):
    """
    Schema for user registration response.
    """
    id: str
    email: EmailStr
    full_name: str

class EmailSchema(BaseModel):
    """
    Schema for email sending.
    """
    email: EmailStr
    body: Dict[str, Any]

class ResetPasswordSchema(BaseModel):
    """
    Schema for resetting password.
    """
    email: EmailStr

class PasswordConfirmSchema(BaseModel):
    """
    Schema for confirming password reset.
    """
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    is_superuser: bool

    class Config:
        from_attributes = True
