import jwt
from datetime import timezone, datetime, timedelta
from passlib.context import CryptContext

from backend.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

def create_access_token(data: dict):
   """
   Create a JWT access token with an expiration time. 
   """
   to_encode = data.copy()
   # Set the expiration time for the token
   expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
   to_encode.update({"exp": expire})
   encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
   return encoded_jwt 