from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Zakat Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 6789

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mawp_ai"

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # File Storage - relative to project root
    UPLOAD_DIR: str = "./backend/uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AI API Configuration (External AI Server)
    AI_API_URL: str = "http://localhost:9999"
    AI_API_KEY: str = "your-api-key-here"

    # AI Models
    LLM_MODEL: str = "qwen3.5-397b-a17b-fp8-thinking"
    EMBEDDING_MODEL: str = "qwen3-vl-embedding-8b"
    ASR_MODEL: str = "qwen3-asr-1.7b"

    # Vector Store - relative to project root
    CHROMA_DB_DIR: str = "./backend/chroma_db"

    # Eligibility Scoring
    ELIGIBILITY_THRESHOLD: float = 0.5

    # Fraud Detection
    SIMILARITY_THRESHOLD: float = 0.85

    class Config:
        env_file = "../../.env"
        case_sensitive = True


settings = Settings()