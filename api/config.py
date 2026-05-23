from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str
    frontend_url: str = "http://localhost:8000"


settings = Settings() # type: ignore[call-arg] # Loaded from .env file