from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, extra="allow")

    PROJECT_NAME: str = "OmniChannel Cloud CRM & Call Center"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./crm_call_center.db")
    SECRET_KEY: str = "crm-call-center-super-secret-key-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    MAX_QUEUE_WAIT_SECONDS: int = 300
    SLA_WARN_MINUTES: int = 15

settings = Settings()
