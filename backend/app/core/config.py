from pydantic import computed_field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    MP_ACCESS_TOKEN:  Optional[str] = None
    MP_PUBLIC_KEY:    Optional[str] = None
    MP_WEBHOOK_URL:   Optional[str] = None
    NGROK_URL:        Optional[str] = None

    # --- CORS y Frontend ---
    CORS_ORIGINS:       str = "http://localhost:5173"
    VITE_FRONTEND_URL:  str = "http://localhost:5173"
    VITE_API_URL:       str = "http://localhost:8000"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    rate_limit_default_burst: int = 100
    rate_limit_default_per_minute: int = 60
    rate_limit_auth_burst: int = 20
    rate_limit_auth_per_minute: int = 5


    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
