"""Application configuration settings for AI Meeting Action-Item Extractor."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """System-wide configuration using environment variables."""

    APP_NAME: str = "AI Meeting Action-Item Extractor"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", env="APP_ENV")

    # Database
    DATABASE_URL: str = Field(
        default=f"sqlite:///{BASE_DIR / 'meeting_actions.db'}",
        env="DATABASE_URL",
    )

    # AI Provider Settings
    AI_PROVIDER: str = Field(default="mock", env="AI_PROVIDER")  # mock | rule | openai | local
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    LOCAL_MODEL_NAME: str = Field(default="", env="LOCAL_MODEL_NAME")

    # System parameters
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    ENABLE_SEMANTIC_SEARCH: bool = Field(default=False, env="ENABLE_SEMANTIC_SEARCH")
    CONFIDENCE_THRESHOLD_REVIEW: float = Field(default=0.70, env="CONFIDENCE_THRESHOLD_REVIEW")
    SIMILARITY_THRESHOLD_DUPLICATE: float = Field(default=0.65, env="SIMILARITY_THRESHOLD_DUPLICATE")

    # Paths
    BASE_PATH: Path = BASE_DIR
    DATA_PATH: Path = BASE_DIR / "data"
    REPORTS_PATH: Path = BASE_DIR / "reports"
    MODELS_PATH: Path = BASE_DIR / "models"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
