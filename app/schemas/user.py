from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
import re

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class UserBase(BaseModel):
    """Campos comunes para operaciones de usuario."""
    first_name: str = Field(..., max_length=150)
    last_name: str = Field(..., max_length=150)
    username: str = Field(..., max_length=20)
    email: Optional[EmailStr] = None
    is_active: bool = True
    is_superuser: bool = False
    profile_picture: Optional[HttpUrl] = None
    nationality: Optional[str] = Field(None, max_length=7)
    occupation: Optional[str] = Field(None, max_length=17)
    date_of_birth: Optional[date] = None
    contact_phone_number: Optional[str] = Field(None, max_length=20)
    gender: Optional[Gender] = None
    address: Optional[str] = None
    address_number: Optional[str] = Field(None, max_length=25)
    address_interior_number: Optional[str] = Field(None, max_length=26)
    address_complement: Optional[str] = None
    address_neighborhood: Optional[str] = None
    address_zip_code: Optional[str] = Field(None, max_length=10)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=24)

class User(UserBase):
    """Esquema principal de usuario para respuestas de la API (incluye metadatos). Hereda de UserBase"""
    id: UUID
    last_login: Optional[datetime] = None
    date_joined: datetime
    created_at: datetime
    modified_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    email_verified: bool
    email_verified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserCreateRequest(UserBase):
    """Esquema para la creación de nuevos usuarios."""
    password: str = Field(..., min_length=8, description="Contraseña (se almacenará cifrada).")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('La contraseña debe incluir al menos una letra y un número')
        return v

class UserUpdateRequest(UserCreateRequest):
    """Esquema para actualización completa (PUT). Hereda de UserCreateRequest"""
    pass

class UserPartialUpdateRequest(BaseModel):
    """Esquema para actualización parcial (PATCH). Todos los campos son opcionales."""
    username: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=8)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
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
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
                raise ValueError('La contraseña debe incluir al menos una letra y un número')
        return v

class UserBasic(BaseModel):
    """Subconjunto de información para respuestas rápidas."""
    id: UUID
    username: str
    email: Optional[EmailStr] = None
    first_name: str
    last_name: str
    is_active: bool
    role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PagedUsersResult(BaseModel):
    """Resultado paginado de usuarios."""
    total: int
    page: int
    limit: int
    users: List[User]

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('La nueva contraseña debe incluir letras y números')
        return v

class PasswordResetRequest(BaseModel):
    email: EmailStr

class UserDeleteResult(BaseModel):
    id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class UserRestoreResult(BaseModel):
    id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class UserEmailVerifyResult(BaseModel):
    id: UUID
    email: EmailStr
    email_verified: bool
    email_verified_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class UserToggleActiveResult(BaseModel):
    id: UUID
    username: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

