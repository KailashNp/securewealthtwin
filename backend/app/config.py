"""Application configuration – loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "SecureWealth Twin"
    DATABASE_URL: str = "sqlite:///./securewealth.db"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    SECRET_KEY: str = "securewealth-hackathon-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
