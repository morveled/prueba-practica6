from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
import re


class Gender(str, Enum): # Usar Enum para género
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class UserBase(BaseModel): # Campos comunes para operaciones de usuario
    username: str = Field(..., max_length=20)
    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    is_active: bool = True
    is_superuser: bool = False
    profile_picture: Optional[HttpUrl] = None
    nationality: Optional[str] = Field(None, max_length=7)
    occupation: Optional[str] = Field(None, max_length=17)
    date_of_birth: Optional[date] = None
    contact_phone_number: Optional[str] = Field(None, max_length=20)
    gender: Optional[Gender] = None  # Quitar max_length
    address: Optional[str] = None
    address_number: Optional[str] = Field(None, max_length=25)
    address_interior_number: Optional[str] = Field(None, max_length=26)
    address_complement: Optional[str] = None
    address_neighborhood: Optional[str] = None
    address_zip_code: Optional[str] = Field(None, max_length=10)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=24)

class User(BaseModel): #esquema principal de usuario para respuestas API
    id: UUID
    username: str = Field(..., max_length=20)
    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    is_active: bool = True
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    date_joined: datetime
    created_at: datetime
    modified_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    profile_picture: Optional[HttpUrl] = None
    email_verified: bool
    email_verified_at: Optional[datetime] = None
    nationality: Optional[str] = None 
    occupation: Optional[str] = None
    date_of_birth: Optional[date] = None
    contact_phone_number: Optional[str] = None
    gender: Optional[Gender] = None
    address: Optional[str] = None
    address_number: Optional[str] = None
    address_interior_number: Optional[str] = None
    address_complement: Optional[str] = None
    address_neighborhood: Optional[str] = None
    address_zip_code: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True # Permite crear desde ORM objetos (modelos SQLAlchemy/SQLModel) 

class UserCreateRequest(UserBase): #esquema para la creación de usuarios 
    password: str = Field(..., min_length=8, description="Contraseña (se almacenará cifrada).")
    
    @field_validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('La contraseña debe incluir letras y números')
        return v
    
    email: Optional[EmailStr] = None  
    
    is_superuser: Optional[bool] = False
    profile_picture: Optional[HttpUrl] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None
    date_of_birth: Optional[date] = None
    contact_phone_number: Optional[str] = None
    gender: Optional[Gender] = None
    address: Optional[str] = None
    address_number: Optional[str] = None
    address_interior_number: Optional[str] = None
    address_complement: Optional[str] = None
    address_neighborhood: Optional[str] = None
    address_zip_code: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    role: Optional[str] = None

class UserUpdateRequest(UserCreateRequest): # Hereda de UserCreateRequest
    pass

class UserPartialUpdateRequest(BaseModel):
    # Todos los campos opcionales para actualización parcial
    username: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=8)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    profile_picture: Optional[HttpUrl] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None
    date_of_birth: Optional[date] = None
    contact_phone_number: Optional[str] = None
    gender: Optional[Gender] = None
    address: Optional[str] = None
    address_number: Optional[str] = None
    address_interior_number: Optional[str] = None
    address_complement: Optional[str] = None
    address_neighborhood: Optional[str] = None
    address_zip_code: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    role: Optional[str] = None
    
    @field_validator('password')
    def validate_password(cls, v):
        if v is not None:
            if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
                raise ValueError('La contraseña debe incluir letras y números')
        return v

class PasswordChangeRequest(BaseModel): #esquema para la solicitud de cambio de contraseña
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @field_validator('new_password')
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('La contraseña debe incluir letras y números')
        return v

class PasswordResetRequest(BaseModel): #esquema para la solicitud de restablecimiento de contraseña
    email: EmailStr

class PagedUsersResult(BaseModel):
    total: int
    page: int
    limit: int
    users: list[User]  # Usa User que ya existe

class UserBasic(BaseModel): #eschema para información básica de usuario
    """Subconjunto de información del usuario usado en varias respuestas."""
    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    role: Optional[str] = None

class UserDeleteResult(BaseModel): #esquema para resultado de eliminación de usuario
    id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None

class UserRestoreResult(BaseModel): #esquema para resultado de restauración de usuario
    id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None

class UserEmailVerifyResult(BaseModel): #esquema para resultado de verificación de email
    id: UUID
    email: EmailStr
    email_verified: bool
    email_verified_at: Optional[datetime] = None

class UserToggleActiveResult(BaseModel): #esquema para resultado de activación/desactivación de usuario
    id: UUID
    username: str
    is_active: bool

# ============== Esquemas de respuesta de API ==============
class ApiResponseBase(BaseModel): #esquema base para respuestas API
    codigo: int
    mensaje: str

class ApiResponseUserList(ApiResponseBase): #esquema para lista de usuarios
    resultado: PagedUsersResult

class ApiResponseUser(ApiResponseBase): #esquema para un solo usuario
    resultado: User

class ApiResponseUserBasic(ApiResponseBase): #esquema para información básica de usuario
    resultado: UserBasic

class ApiResponseUserDelete(ApiResponseBase): #esquema para resultado de eliminación de usuario
    resultado: UserDeleteResult

class ApiResponseUserRestore(ApiResponseBase): #esquema para resultado de restauración de usuario
    resultado: UserRestoreResult

class ApiResponseUserEmailVerify(ApiResponseBase): #esquema para resultado de verificación de email
    resultado: UserEmailVerifyResult

class ApiResponseUserToggleActive(ApiResponseBase): #esquema para resultado de activación/desactivación de usuario
    resultado: UserToggleActiveResult

class ApiResponseSimple(ApiResponseBase): #esquema para respuestas simples sin datos específicos
    resultado: Optional[dict] = None

class ApiError(ApiResponseBase): #esquema para errores de API
    """Código HTTP asociado al error (4xx o 5xx)."""
    resultado: Optional[dict] = None #el campo resultado es opcional