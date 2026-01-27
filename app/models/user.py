from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, DateTime
from datetime import datetime, date
from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa

#table=True le dice a SQLModel que este es un modelo de tabla
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4,
        sa_column=Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False))
    password: str = Field(max_length=128, nullable=False) # Para hash bcrypt
    last_login: Optional[datetime] = Field(default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True))
    is_superuser: bool = Field(default=False, nullable=False)
    first_name: str = Field(max_length=150, nullable=False)
    last_name: str = Field(max_length=150, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    date_joined: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, 
                        server_default=sa.func.now()))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False,
                        server_default=sa.func.now()))
    modified_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False,
                        server_default=sa.func.now(),
                        onupdate=sa.func.now()))
    is_deleted: bool = Field(default=False, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True))
    username: str = Field(max_length=20, unique=True, nullable=False, index=True)
    email: str = Field(max_length=254, unique=True, nullable=True, index=True)
    profile_picture: Optional[str] = Field(default=None, max_length=100, nullable=True)
    email_verified: bool = Field(default=False, nullable=False)
    email_verified_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True))
    nationality: Optional[str] = Field(default=None, max_length=7, nullable=True)
    occupation: Optional[str] = Field(default=None, max_length=17, nullable=True)
    date_of_birth: Optional[date] = Field(default=None, 
        sa_column=Column(sa.Date, nullable=True))
    contact_phone_number: Optional[str] = Field(default=None, max_length=20, nullable=True)
    gender: Optional[str] = Field(default=None, max_length=6, nullable=True)
    address: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    address_number: Optional[str] = Field(default=None, max_length=25, nullable=True)
    address_interior_number: Optional[str] = Field(default=None, max_length=26, nullable=True)
    address_complement: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    address_neighborhood: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    address_zip_code: Optional[str] = Field(default=None, max_length=10, nullable=True)
    address_city: Optional[str] = Field(default=None, max_length=100, nullable=True)
    address_state: Optional[str] = Field(default=None, max_length=100, nullable=True)
    role: Optional[str] = Field(default=None, max_length=24, nullable=True)

    # Propiedades 
    @property
    def full_name(self) -> str:
        """Nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_authenticated(self) -> bool:
        """Verifica si el usuario puede autenticarse"""
        return self.is_active and not self.is_deleted
    
    @property
    def age(self) -> Optional[int]:
        """Calcula la edad a partir de la fecha de nacimiento"""
        if not self.date_of_birth:
            return None
        
        today = date.today()
        age = today.year - self.date_of_birth.year
        
        # Ajustar si aún no ha cumplido años este año
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        
        return age