from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "wow_character_manager"

    # Blizzard API
    BLIZZARD_CLIENT_ID: str
    BLIZZARD_CLIENT_SECRET: str
    BLIZZARD_REGION: str = "us"

    # App
    APP_NAME: str = "WoW Character Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()