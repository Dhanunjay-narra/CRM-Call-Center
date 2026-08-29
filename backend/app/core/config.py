import os
from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CallSphere CRM"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "callsphere_crm_super_secure_jwt_secret_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    OTP_EXPIRE_MINUTES: int = 10

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "*"
    ]

    # Database
    DATABASE_URL: Optional[str] = None
    SYNC_DATABASE_URL: Optional[str] = None
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    @property
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Fallback to local SQLite for frictionless local development & fast testing
        return "sqlite+aiosqlite:///./callsphere.db"

    @property
    def get_sync_database_url(self) -> str:
        if self.SYNC_DATABASE_URL:
            return self.SYNC_DATABASE_URL
        if self.DATABASE_URL and "sqlite" not in self.DATABASE_URL:
            # Convert asyncpg URL to standard psycopg2 if needed
            return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        return "sqlite:///./callsphere.db"

    # Redis & Caching
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Telephony & Omnichannel Providers
    TELEPHONY_PROVIDER: str = "simulator"  # "simulator", "twilio", "asterisk"
    SMS_PROVIDER: str = "simulator"        # "simulator", "twilio", "aws_sns"
    WHATSAPP_PROVIDER: str = "simulator"   # "simulator", "meta", "twilio"
    EMAIL_PROVIDER: str = "simulator"      # "simulator", "sendgrid", "smtp"

    # SMTP Configuration (if using SMTP)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "notifications@callsphere.local"

    # Storage
    STORAGE_TYPE: str = "local"  # "local", "s3"
    STORAGE_LOCAL_DIR: str = "./uploads"
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
