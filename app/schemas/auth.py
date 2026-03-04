from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class LoginRequest(BaseModel):
    """DTO para la solicitud de inicio de sesión."""
    username: str = Field(..., max_length=20, description="Nombre de usuario")
    password: str = Field(..., min_length=8, description="Contraseña del usuario")


class TokenResponse(BaseModel):
    """DTO de respuesta con los tokens generados."""
    access_token: str = Field(..., description="Token JWT de acceso")
    refresh_token: str = Field(..., description="Token JWT de refresco")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración del access token en segundos")


class RefreshTokenRequest(BaseModel):
    """DTO para solicitar un nuevo access token usando el refresh token."""
    refresh_token: str = Field(..., description="Token de refresco válido")


class TokenData(BaseModel):
    """Datos decodificados del token JWT (claims internos)."""
    sub: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    is_superuser: bool = False
    token_type: Optional[str] = None  # "access" o "refresh"
    exp: Optional[datetime] = None


class CurrentUser(BaseModel):
    """Representa al usuario autenticado extraído del token JWT."""
    id: UUID
    username: str
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_superuser: bool = False
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
