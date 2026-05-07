from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # SQLite
    SQLITE_DB_PATH: str = "./wow_character_manager.db"

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
