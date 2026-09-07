from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/healthspan"
    redis_url: str = "redis://localhost:6379/0"
    opensearch_url: str = "http://localhost:9200"
    object_storage_endpoint: str = "http://localhost:9000"

    class Config:
        env_file = ".env"

settings = Settings()
