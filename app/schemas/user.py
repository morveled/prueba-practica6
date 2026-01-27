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
    email: Optional[EmailStr] = None
    first_name: str = Field(..., max_length=150)
    last_name: str = Field(..., max_length=150)
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

class User(BaseModel): #esquema principal de usuario para respuestas API
    id: UUID
    username: str
    email: Optional[EmailStr] = None
    first_name: str
    last_name: str
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime]
    date_joined: datetime
    created_at: datetime
    modified_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime]
    profile_picture: Optional[HttpUrl]
    email_verified: bool
    email_verified_at: Optional[datetime]
    nationality: Optional[str]
    occupation: Optional[str]
    date_of_birth: Optional[date]
    contact_phone_number: Optional[str]
    gender: Optional[Gender]
    address: Optional[str]
    address_number: Optional[str]
    address_interior_number: Optional[str]
    address_complement: Optional[str]
    address_neighborhood: Optional[str]
    address_zip_code: Optional[str]
    address_city: Optional[str]
    address_state: Optional[str]
    role: Optional[str]

    class Config:
        from_attributes = True # Permite crear desde ORM objetos (modelos SQLAlchemy/SQLModel) 

class UserCreateRequest(UserBase): #esquema para la creación de usuarios 
    password: str = Field(..., min_length=8, description="Contraseña (se almacenará cifrada).")
    
    @field_validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('La contraseña debe incluir letras y números')
        return v

class UserUpdateRequest(UserCreateRequest): # Hereda de UserCreateRequest
    pass

class UserPartialUpdateRequest(BaseModel):
    # Todos los campos opcionales para actualización parcial
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
    email: Optional[EmailStr]
    first_name: str
    last_name: str
    is_active: bool
    role: Optional[str] 

    class Config:
        from_attributes = True

class UserDeleteResult(BaseModel): #esquema para resultado de eliminación de usuario
    id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] 

    class Config:
        from_attributes = True

class UserRestoreResult(BaseModel): #esquema para resultado de restauración de usuario
    id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] 

class UserEmailVerifyResult(BaseModel): #esquema para resultado de verificación de email
    id: UUID
    email: EmailStr
    email_verified: bool
    email_verified_at: Optional[datetime]

    class Config:
        from_attributes = True 

class UserToggleActiveResult(BaseModel): #esquema para resultado de activación/desactivación de usuario
    id: UUID
    username: str
    is_active: bool