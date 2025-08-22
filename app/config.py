# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, Field
from typing import List
import cloudinary

class Settings(BaseSettings):
    # --- MongoDB ---
    MONGO_URI: str
    MONGO_DB: str = "shop_db"

    # --- JWT ---
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_EXPIRES_SECONDS: int = 3600

    # --- Admin bootstrap ---
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "changeme"

    # --- Cloudinary ---
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # --- App info ---
    APP_NAME: str = "NabeeraBareera Store API"
    APP_ENV: str = "dev"  # dev, staging, prod
    APP_BASE_URL: AnyHttpUrl = Field("http://localhost:8000", env="APP_BASE_URL")

    # --- Server ---
    PORT: int = 8000

    # --- Email ---
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""

    # --- CORS ---
    CORS_ORIGINS: List[AnyHttpUrl] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

# Export singleton
settings = Settings()

# Configure Cloudinary immediately after loading settings
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)
