import secrets
from typing import Literal

from pydantic import (
   AnyUrl,
   EmailStr,
   PostgresDsn,
   computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
   """Application settings."""

   model_config = SettingsConfigDict(
      env_file=".env",
      env_file_encoding="utf-8",
      env_ignore_empty= True,
      extra="ignore",
   )

   # Application settings
   APP_NAME: str = "FastAPI Project Template"
   API_VERSION: str = "/api/v1"
   APP_DESCRIPTION: str = "A FastAPI template for building APIs."
   APP_VERSION: str = "0.1.0"
   SECRET_KEY: str = secrets.token_urlsafe(32)
   ALGORITHM: str = "HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days
   CELERY_BROKER_URL: str = "redis://redis:6379/0"
   CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
   ENVIRONMENT: Literal["local", "staging", "production"] = "local"

   # Database settings
   POSTGRES_SERVER: str = "postgres"
   POSTGRES_PORT: int = 5432
   POSTGRES_USER: str = "postgres"
   POSTGRES_PASSWORD: str = "postgres123"
   POSTGRES_DB: str = "starterdb"

   @computed_field
   @property
   def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
      return MultiHostUrl.build(
         scheme="postgresql+psycopg2",
         username=self.POSTGRES_USER,
         password=self.POSTGRES_PASSWORD,
         host=self.POSTGRES_SERVER,
         port=self.POSTGRES_PORT,
         path=self.POSTGRES_DB,
      )
      
   # Email settings
   email_sender: EmailStr | None = None

   # CORS settings
   cors_origins: list[AnyUrl] = []

   @computed_field
   def is_production(self) -> bool:
      return self.app_version.endswith("prod")

settings = Settings()