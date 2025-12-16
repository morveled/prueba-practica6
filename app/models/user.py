from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, DateTime
from datetime import datetime, date
from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    # Campos principales
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(max_length=20, unique=True, index=True)
    password: str = Field(max_length=128)  # Para hash bcrypt
    email: str = Field(max_length=254, unique=True, index=True)
    # Información personal
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    # Estados
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    # Fechas sistema
    last_login: Optional[datetime] = Field(default=None)
    date_joined: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), default=sa.func.now())
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), default=sa.func.now())
    )
    modified_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), default=sa.func.now(), 
                         onupdate=sa.func.now())
    )
    deleted_at: Optional[datetime] = Field(default=None)
    # Perfil
    profile_picture: Optional[str] = Field(default=None, max_length=500)  # Aumentar longitud para URLs
    # Verificación de Email
    email_verified: bool = Field(default=False)
    email_verified_at: Optional[datetime] = Field(default=None)
    # Información 
    nationality: Optional[str] = Field(default=None, max_length=7)
    occupation: Optional[str] = Field(default=None, max_length=17)
    date_of_birth: Optional[date] = Field(default=None)
    contact_phone_number: Optional[str] = Field(default=None, max_length=20)
    gender: Optional[str] = Field(default=None, max_length=10)  # Aumentar para "Other"
    # Dirección
    address: Optional[str] = Field(default=None, sa_column=Column(Text))  
    address_number: Optional[str] = Field(default=None, max_length=25)
    address_interior_number: Optional[str] = Field(default=None, max_length=26)
    address_complement: Optional[str] = Field(default=None, sa_column=Column(Text))  
    address_neighborhood: Optional[str] = Field(default=None, sa_column=Column(Text)) 
    address_zip_code: Optional[str] = Field(default=None, max_length=10)
    address_city: Optional[str] = Field(default=None, max_length=100)
    address_state: Optional[str] = Field(default=None, max_length=100)
    # Rol
    role: Optional[str] = Field(default=None, max_length=24)

    # Campos calculados (propiedades)
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_authenticated(self) -> bool:
        return self.is_active and not self.is_deleted