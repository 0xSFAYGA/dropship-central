from typing import List, Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    These settings are loaded from environment variables and/or a .env file.
    """

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        "development",
        description="The application environment.",
    )
    DEBUG: bool = Field(
        False,
        description="Enable debug mode. Should be False in production.",
    )

    # API Settings
    API_HOST: str = Field("0.0.0.0", description="The host for the API server.")
    API_PORT: int = Field(8000, description="The port for the API server.")

    # Database Settings
    DATABASE_URL: PostgresDsn = Field(
        ...,
        description="The PostgreSQL connection URL.",
        examples=["postgresql+asyncpg://user:password@host:port/db"],
    )
    DB_ECHO: bool = Field(
        False,
        description="Enable echoing of SQL statements for debugging.",
    )

    # Redis Settings
    REDIS_URL: RedisDsn = Field(
        ...,
        description="The Redis connection URL.",
        examples=["redis://user:password@host:port/db"],
    )

    # JWT Settings
    SECRET_KEY: str = Field(
        ...,
        description="A secure random string for signing JWTs. MUST be kept secret.",
    )
    ALGORITHM: str = Field("HS256", description="The algorithm for signing JWTs.")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        15,
        description="The expiration time for access tokens in minutes.",
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        7,
        description="The expiration time for refresh tokens in days.",
    )

    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="A list of allowed origins for CORS.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_default=True,
    )


settings = Settings()
