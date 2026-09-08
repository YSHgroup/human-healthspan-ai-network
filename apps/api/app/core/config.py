from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "development"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "healthspan"
    postgres_user: str = "healthspan"
    postgres_password: str = "healthspan_dev"
    redis_url: str = "redis://redis:6379/0"
    opensearch_url: str = "http://opensearch:9200"

settings = Settings()
