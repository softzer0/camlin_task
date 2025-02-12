from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow"
    )

    # API settings
    PROJECT_NAME: str = "Currency Wallet API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database settings
    MONGODB_URL: str = "mongodb://localhost:27017"

    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key-here"  # Change in production!
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # NBP API settings
    NBP_API_BASE_URL: str = "https://api.nbp.pl/api"
    EXCHANGE_RATES_CACHE_TTL: int = 1800  # 30 minutes

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"

    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]

    # Server settings
    WEB_CONCURRENCY: int = 4


@lru_cache
def get_settings() -> Settings:
    return Settings()
