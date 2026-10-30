"""
Inventory Service configuration.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_NAME: str = "inventory-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://ibrat:ibrat_dev_password@localhost:5432/inventory_db"
    DATABASE_URL_SYNC: str = "postgresql://ibrat:ibrat_dev_password@localhost:5432/inventory_db"

    JWT_SECRET: str = "change-me-to-a-secure-random-string"
    JWT_ALGORITHM: str = "HS256"

    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    PRODUCT_SERVICE_URL: str = "http://product-service:8002"

    LOW_STOCK_THRESHOLD: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
