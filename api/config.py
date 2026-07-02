# api/config.py
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.app",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    frontend_url: str = "http://localhost:8000"

    admin_username: str
    admin_password_hash: str

    secret_key: SecretStr

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15


settings = Settings()  # type: ignore[call-arg] # Loaded from .env file
