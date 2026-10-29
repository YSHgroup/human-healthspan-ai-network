from functools import cached_property
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    app_env: str = "development"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "healthspan"
    postgres_user: str = "healthspan"
    postgres_password: str = "healthspan_dev"
    database_url_override: str | None = Field(default=None, validation_alias="DATABASE_URL")
    redis_url: str = "redis://redis:6379/0"
    opensearch_url: str = "http://opensearch:9200"
    jwt_secret: str = "development-only-change-me"
    jwt_issuer: str = "human-healthspan-network"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    api_cors_origins: str = "http://localhost:3000"
    sql_echo: bool = False
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None
    public_app_url: str = "http://localhost:3000"

    @field_validator("public_app_url")
    @classmethod
    def validate_public_app_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("PUBLIC_APP_URL must be an HTTP(S) base URL without credentials, query, or fragment.")
        return value.rstrip("/")

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if self.app_env.lower() in {"production", "prod"}:
            if self.jwt_secret == "development-only-change-me":
                raise ValueError("JWT_SECRET must be set outside development.")
            if len(self.jwt_secret) < 32:
                raise ValueError("JWT_SECRET must contain at least 32 characters outside development.")
            if self.postgres_password == "healthspan_dev":
                raise ValueError("POSTGRES_PASSWORD must be set outside development.")
            if not self.public_app_url.startswith("https://"):
                raise ValueError("PUBLIC_APP_URL must use HTTPS outside development.")
        if self.access_token_minutes < 1 or self.refresh_token_days < 1:
            raise ValueError("Token lifetimes must be positive.")
        return self

    @cached_property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        ).render_as_string(hide_password=False)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


settings = Settings()
