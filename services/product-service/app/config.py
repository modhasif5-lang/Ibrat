"""
Product Service configuration.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_NAME: str = "product-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://ibrat:ibrat_dev_password@localhost:5432/product_db"
    DATABASE_URL_SYNC: str = "postgresql://ibrat:ibrat_dev_password@localhost:5432/product_db"

    JWT_SECRET: str = "change-me-to-a-secure-random-string"
    JWT_ALGORITHM: str = "HS256"

    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"

    USER_SERVICE_URL: str = "http://user-service:8001"
    INVENTORY_SERVICE_URL: str = "http://inventory-service:8005"

    MAX_IMAGE_SIZE_MB: int = 5
    UPLOAD_DIR: str = "/app/uploads"
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
