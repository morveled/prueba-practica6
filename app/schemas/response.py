from typing import TypeVar, Generic, Optional, Any, Dict
from pydantic import BaseModel
from app.schemas.user import (
    User,
    UserBasic,
    UserDeleteResult,
    UserRestoreResult,
    UserEmailVerifyResult,
    UserToggleActiveResult,
    PagedUsersResult
)

T = TypeVar("T") # Tipo genérico para el resultado de la respuesta

class ApiResponseBase(BaseModel): # Base para todas las respuestas de la API
    """Base para todas las respuestas de la API"""
    codigo: int
    mensaje: str

class ApiResponse(ApiResponseBase, Generic[T]): #esquema genérico para respuestas de API
    """Respuesta estándar con datos"""
    resultado: Optional[T] = None

class ApiError(ApiResponseBase): #esquema para errores de API
    """Respuesta de error"""
    resultado: Optional[Dict[str, Any]] = None

# ===== Alias semánticos para documentación OpenAPI =====
ApiResponseUser = ApiResponse[User]  #esquema para un solo usuario
ApiResponseUserList = ApiResponse[PagedUsersResult] #esquema para lista de usuarios
ApiResponseUserBasic = ApiResponse[UserBasic] #esquema para información básica de usuario
ApiResponseUserDelete = ApiResponse[UserDeleteResult] #esquema para resultado de eliminación de usuario
ApiResponseUserRestore = ApiResponse[UserRestoreResult] #esquema para resultado de restauración de usuario
ApiResponseUserEmailVerify = ApiResponse[UserEmailVerifyResult] #esquema para resultado de verificación de email
ApiResponseUserToggleActive = ApiResponse[UserToggleActiveResult] #esquema para resultado de activación/desactivación de usuario
ApiResponseSimple = ApiResponse[dict]
