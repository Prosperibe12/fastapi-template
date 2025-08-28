from typing import Annotated, Any, Literal

from pydantic import (
   AnyUrl,
   BeforeValidator,
   EmailStr,
   HttpUrl,
   PostgresDsn,
   RedisDsn,
   computed_field
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS origins from a comma-separated string or list."""
    
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    if isinstance(v, list | str):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # application settings
    APP_NAME: str
    API_VERSION: str
    APP_DESCRIPTION: str
    APP_VERSION: str
    ENVIRONMENT: Literal["local", "staging", "production"]
    
    # security ettings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # celery settings
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # sentry settings
    SENTRY_DSN: HttpUrl | None = None
    
    # redis settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str = ""
    REDIS_CACHE_EXPIRE: int

    # db ettings
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        )
    
    @computed_field
    def redis_dsn(self) -> RedisDsn:
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD or None,
            path=f"/{self.REDIS_DB}"
        )
        
    # email settings
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USE_TLS: bool
    EMAIL_USE_SSL: bool
    EMAIL_HOST_USER: EmailStr
    EMAIL_HOST_PASSWORD: str
    
    # admin settings
    ADMIN_USER_NAME: str
    ADMIN_USER_EMAIL: str
    
    # CORS settings
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ]

    @computed_field
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]
    
    @computed_field
    def emails_enabled(self) -> bool:
        return bool(self.EMAIL_HOST and self.EMAIL_HOST_USER)

# Create settings instance
settings = Settings()