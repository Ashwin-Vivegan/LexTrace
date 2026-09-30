import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration settings using Pydantic Settings.
    Environment variables or defaults configure database URL, upload directories,
    chunking settings, and document size/extension limits.
    """
    APP_NAME: str = "LexTrace Legal Intelligence"
    DEBUG: bool = True
    
    # Database connection string
    DATABASE_URL: str = "sqlite:///./data/lextrace.db"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    DATA_DIR: str = "./data"
    
    # Document Upload Limits
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}
    
    # Document Chunking Configuration
    CHUNK_SIZE_CHARS: int = 1000
    CHUNK_OVERLAP_CHARS: int = 150
    DEFAULT_PAGE_SIZE: int = 50
    
    # Groq LLM Configuration (Milestone 5)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Ensure critical data & upload directories exist automatically
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
