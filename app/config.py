from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, Field, model_validator
from typing import List, Optional
import cloudinary
import logging

# Configure basic logging
logger = logging.getLogger("uvicorn")

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses .env file in development; uses Vercel env vars in production.
    """

    # --- MongoDB ---
    MONGO_URI: str = Field(..., description="MongoDB connection string")
    MONGO_DB: str = "shop_db"

    # --- JWT ---
    JWT_SECRET: str = Field(..., description="Secret key for signing JWT tokens")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_EXPIRES_SECONDS: int = 3600  # Redundant, but kept for clarity

    # --- Admin Bootstrap ---
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "changeme"  # Change in production!

    # --- Cloudinary ---
    CLOUDINARY_CLOUD_NAME: str = Field(..., description="Cloudinary cloud name")
    CLOUDINARY_API_KEY: str = Field(..., description="Cloudinary API key")
    CLOUDINARY_API_SECRET: str = Field(..., description="Cloudinary API secret")

    # --- App Info ---
    APP_NAME: str = "NabeeraBareera Store API"
    APP_ENV: str = "dev"  # dev, staging, prod
    APP_BASE_URL: AnyHttpUrl = Field("http://localhost:8000", description="Base public URL of the app")

    # --- Server ---
    PORT: int = 8000

    # --- Email (Optional) ---
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""

    # --- CORS ---
    # Use comma-separated origins in Vercel env: "http://localhost:3000,https://nabeerabareera.com"
    CORS_ORIGINS: List[AnyHttpUrl] = []

    # Dynamically add common CORS origins in dev
    @model_validator(mode="after")
    def set_default_cors(self):
        if not self.CORS_ORIGINS:
            if self.APP_ENV == "dev":
                self.CORS_ORIGINS = [
                    "http://localhost:3000",
                    "http://localhost:3001",
                ]
            else:
                # In production, explicitly set in Vercel dashboard
                pass
        return self

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",  # Ignore extra env vars
    }


# Export singleton instance
settings = Settings()

# Configure Cloudinary
try:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    logger.info("✅ Cloudinary configured successfully")
except Exception as e:
    logger.warning(f"⚠️ Cloudinary configuration failed: {e}")
