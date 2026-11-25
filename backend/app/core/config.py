from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="postgresql://smartwork:smartwork@localhost:5432/smartwork")
    REDIS_URL: str = Field(default="redis://redis:6379/0")
    OLLAMA_HOST: str = Field(default="http://ollama:11434")
    OLLAMA_MODEL: str = Field(default="mistral")
    OLLAMA_TIMEOUT: int = Field(default=60)
    SECRET_KEY: str = Field(default="change-this-to-a-secure-random-string")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    CORS_ORIGINS: list = []

    # File storage
    STORAGE_DIR: str = Field(default="/tmp/smartwork/storage")
    UPLOAD_DIR: str = Field(default="/tmp/smartwork/uploads")
    GENERATED_DIR: str = Field(default="/tmp/smartwork/generated")
    MAX_UPLOAD_SIZE_MB: int = Field(default=50)
    LOG_DIR: str = Field(default="/tmp/smartwork/logs")

    # Vector store (reserved for the next iteration)
    CHROMA_HOST: str = Field(default="localhost")
    CHROMA_PORT: int = Field(default=8000)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def ensure_directories() -> None:
    """Create storage directories used by ingestion and generation."""
    for directory in (
        settings.STORAGE_DIR,
        settings.UPLOAD_DIR,
        settings.GENERATED_DIR,
        settings.LOG_DIR,
    ):
        Path(directory).mkdir(parents=True, exist_ok=True)
