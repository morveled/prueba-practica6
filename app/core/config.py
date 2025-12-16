from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "API REST Usuarios"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api" 
    
    # CORS 
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    # Para SQLite síncrono (para pruebas rápidas)
    # DATABASE_URL: str = "sqlite:///./test.db"
    
    # Para SQLite async (se recomienda en FastAPI)
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Para PostgreSQL:
    # DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"  # ⚠️ Cambiar en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()