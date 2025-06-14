"""
Application configuration settings.

This module contains all configuration settings for the application,
with support for environment variables via .env file.
"""

from pathlib import Path
from pydantic_settings import BaseSettings # Updated for Pydantic v2
from pydantic import Field # Field remains in pydantic core

# Define BASE_DIR at the module level for accessibility
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Directory settings
    # BASE_DIR is now at module level
    KNOWLEDGE_DIR: Path = Field(default=BASE_DIR / "knowledge", env="KNOWLEDGE_DIR")
    ARCHIVE_DIR: Path = Field(default=BASE_DIR / "archive", env="ARCHIVE_DIR")
    OUTPUT_DIR: Path = Field(default=BASE_DIR / "output", env="OUTPUT_DIR")
    LOGS_DIR: Path = Field(default=BASE_DIR / "logs", env="LOGS_DIR")

    # File processing
    MAX_FILE_SIZE_MB: int = Field(default=50, env="MAX_FILE_SIZE_MB")

    # API Keys
    ELEVENLABS_API_KEY: str = Field(default="", env="ELEVENLABS_API_KEY")

    class Config:
        """Pydantic config."""

        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
settings.KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
settings.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
