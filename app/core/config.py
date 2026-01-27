from pydantic_settings import BaseSettings
from typing import List, Optional, Literal
from pydantic import validator
import json

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "API REST"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    #Define el campo ENVIRONMENT
    ENVIRONMENT: Literal["development", "production", "testing"] = "development"
    
    # API
    API_V1_STR: str = "/api" 
    
    # CORS - Pydantic parsea automáticamente el JSON del .env
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # Database
    # Para SQLite síncrono (para pruebas rápidas)
    # DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_URL: str = "" 
    
    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

     # Validaciones para seguridad
    @validator('SECRET_KEY') # el decorador aplica esta función al campo SECRET_KEY
    def validate_secret_key(cls, v):  # cls=clase, v=valor del campo
        if not v:
            raise ValueError("SECRET_KEY no puede estar vacía")
        if len(v) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
        return v

    @validator('DATABASE_URL') # Aplica a DATABASE_URL
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL no puede estar vacía")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()