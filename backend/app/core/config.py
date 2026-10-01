import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Food Rescue & Surplus Distribution Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "food_rescue_super_secret_jwt_key_2026_antigravity")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days token

    # Database: SQLite fallback for instant zero-config testing, Postgres/PostGIS supported via env
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./food_rescue.db"
    )

    class Config:
        case_sensitive = True

settings = Settings()
