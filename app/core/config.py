from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Literal, Optional, Any
from pydantic import field_validator, AnyHttpUrl, json_schema
import json

class Settings(BaseSettings):
    # --- Project Configuration ---
    PROJECT_NAME: str = "API REST Usuarios"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "production", "testing"] = "development"
    
    # --- API Configuration ---
    API_V1_STR: str = "/api"
    
    # --- CORS Configuration ---
    # Pydantic parsea automáticamente el JSON del .env
    # Se utiliza Any para manejar la entrada desde el .env que viene como string
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # --- PostgreSQL Configuration ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        if isinstance(v, str) and v:
            return v
        
        # Si no se proporciona DATABASE_URL, se puede construir desde los campos individuales
        # Nota: info.data contiene los valores ya validados de los otros campos
        return v

    # --- Security & Authentication ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v:
            raise ValueError("SECRET_KEY no puede estar vacía")
        if len(v) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres para ser segura")
        return v

    # --- Pagination Defaults ---
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # --- Pydantic Config ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Instancia de configuración para ser importada en el resto de la app
settings = Settings()

