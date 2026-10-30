"""
User Service configuration.
Loads settings from environment variables with sensible defaults.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """User Service settings."""

    # Service
    SERVICE_NAME: str = "user-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ibrat:ibrat_dev_password@localhost:5432/user_db"
    DATABASE_URL_SYNC: str = "postgresql://ibrat:ibrat_dev_password@localhost:5432/user_db"

    # JWT
    JWT_SECRET: str = "change-me-to-a-secure-random-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # Service URLs
    PRODUCT_SERVICE_URL: str = "http://product-service:8002"
    INVENTORY_SERVICE_URL: str = "http://inventory-service:8005"

    # Image upload
    MAX_IMAGE_SIZE_MB: int = 5
    UPLOAD_DIR: str = "/app/uploads"
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"

    # Admin defaults
    ADMIN_EMAIL: str = "admin@ibrat.com"
    ADMIN_PASSWORD: str = "Admin@12345"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
