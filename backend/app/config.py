from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/dropship"
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20
    DB_ECHO: bool = False

    # Redis settings
    REDIS_URL: str = "redis://redis:6379/0"

    # Security settings
    SECRET_KEY: str = "super-secret-key"  # TODO: Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Project settings
    PROJECT_NAME: str = "Dropship Central"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"] # TODO: Restrict in production

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

def get_settings() -> Settings:
    return settings