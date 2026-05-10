from pydantic_settings import BaseSettings
from typing import Optional


import os
from pathlib import Path

# 项目根目录（backend 目录）
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # SQLite
    SQLITE_DB_PATH: str = str(BACKEND_DIR / "wow_character_manager.db")

    # App
    APP_NAME: str = "WoW Character Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    
    # 默认数据源路径
    DEFAULT_ACCOUNTANT_PATH: str = ""
    DEFAULT_TDINSPECT_PATH: str = ""
    DEFAULT_ATLASLOOT_PATH: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
