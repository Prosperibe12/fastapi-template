import secrets
from datetime import timezone, datetime, timedelta

import jwt
from loguru import logger
from fastapi import Depends, Request
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from itsdangerous.url_safe import URLSafeSerializer

from backend.core.config import settings
from backend.models.redis_conn import redis_conn
from backend.core.custom_exceptions import (
    InvalidTokenError,
    ServiceError,
    BlacklistedTokenError
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
url_token = URLSafeSerializer("secret-key")

def create_url_token(data: dict):
    """
    create a URL-safe token with the provided data.
    """
    return url_token.dumps(data)

def decode_url_token(token):
    """
    decode a URL token and return the data.
    """
    try:
        return url_token.loads(token)
    except Exception as e:
        logger.error(f"Error decoding URL token: {str(e)}")
        
        raise ServiceError(
            message="Invalid URL token",
            token=token
        ) from e

def get_password_hash(password):
    """   
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, exp: timedelta = None, refresh: bool = False):
    """
    Create a JWT access token or a refresh token.
    """
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + (
        exp if exp is not None else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode.update(
        {
            "exp": expire,
            "jti": secrets.token_urlsafe(32),
            "refresh": refresh
        }
    )
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str):
    """
    Decode and validate a JWT token and return the payload.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except (jwt.DecodeError, jwt.ExpiredSignatureError, InvalidTokenError):
        raise InvalidTokenError("Invalid or Expired Token")

async def blacklist_token(token: str, exp: int = 60 * 60 * 24 * 7):
    """
    blacklist a token by storing it in Redis with an expiration time.
    """
    redis = await redis_conn()

    await redis.setex(
        name=f"blacklist:{token}",
        time=exp,
        value=""
    )
    
async def is_token_blacklisted(token: str) -> bool:
    """
    check if a token is blacklisted by checking its presence in Redis.
    """
    redis = await redis_conn()
    
    exists = await redis.exists(f"blacklist:{token}")
    
    return exists is not None and exists > 0

class TokenBearer(HTTPBearer):
    """
    Custom HTTPBearer class to override the authenticate method.
    """
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)
        
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        """
        Override the __call__ method to decode the token and return the payload.
        """
        credentials = await super().__call__(request)
        token = credentials.credentials

        payload = await self.verify_access_token(token)
        
        return payload

    async def verify_access_token(self, token: str):
        """
        Child Classes should implement this method to verify the token type.
        """
        raise NotImplementedError

class AccessTokenBearer(TokenBearer):
    """
    Access token bearer class for access tokens.
    Validates if the token provided is an access token and check if blacklisted
    """
    async def verify_access_token(self, token: str):
        
        payload = decode_token(token)
        
        if await is_token_blacklisted(payload["jti"]):
            raise BlacklistedTokenError()
        
        if payload.get("refresh", False):
            raise InvalidTokenError("Invalid access token, refresh token provided instead.")
        
        return payload

class RefreshTokenBearer(TokenBearer):
    """
    Refresh token bearer class for refresh tokens.
    """
    async def verify_access_token(self, token: str):

        payload = decode_token(token)

        if await is_token_blacklisted(payload["jti"]):
            raise BlacklistedTokenError()
        
        if not payload.get("refresh", False):
            raise InvalidTokenError("Invalid refresh token, access token provided instead.")
        
        return payload 
