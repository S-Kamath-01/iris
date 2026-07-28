# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App metadata ---
    PROJECT_NAME: str = "IRIS"
    APP_ENV: str = "development"

    # --- Database ---
    DATABASE_URL: str

    # --- JWT / Auth ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- BM25 ranking ---
    BM25_K1: float = 1.2
    BM25_B: float = 0.75

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()