from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, DateTime
import sqlalchemy as sa
from datetime import datetime, date
from typing import Optional
from uuid import UUID, uuid4

# table=True le dice a SQLModel que este es un modelo de tabla
class User(SQLModel, table=True):
    __tablename__ = "users"

    # Identificador único utilizando el tipo UUID nativo de PostgreSQL
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            sa.UUID(as_uuid=True), 
            primary_key=True, 
            nullable=False,
            index=True
        )
    )

    # Autenticación y Seguridad
    username: str = Field(max_length=20, unique=True, nullable=False, index=True)
    email: str = Field(max_length=254, unique=True, nullable=True, index=True)
    password: str = Field(max_length=128, nullable=False) # Hash bcrypt
    
    # Estado del Usuario
    is_active: bool = Field(default=True, nullable=False)
    is_superuser: bool = Field(default=False, nullable=False)
    is_deleted: bool = Field(default=False, nullable=False)
    
    # Información Personal
    first_name: str = Field(max_length=150, nullable=False)
    last_name: str = Field(max_length=150, nullable=False)
    gender: Optional[str] = Field(default=None, max_length=6, nullable=True)
    nationality: Optional[str] = Field(default=None, max_length=7, nullable=True)
    occupation: Optional[str] = Field(default=None, max_length=17, nullable=True)
    date_of_birth: Optional[date] = Field(
        default=None, 
        sa_column=Column(sa.Date, nullable=True)
    )
    contact_phone_number: Optional[str] = Field(default=None, max_length=20, nullable=True)
    profile_picture: Optional[str] = Field(default=None, max_length=100, nullable=True)
    role: Optional[str] = Field(default=None, max_length=24, nullable=True)

    # Verificación de Email
    email_verified: bool = Field(default=False, nullable=False)
    email_verified_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # Dirección
    address: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    address_number: Optional[str] = Field(default=None, max_length=25, nullable=True)
    address_interior_number: Optional[str] = Field(default=None, max_length=26, nullable=True)
    address_complement: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    address_neighborhood: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    address_zip_code: Optional[str] = Field(default=None, max_length=10, nullable=True)
    address_city: Optional[str] = Field(default=None, max_length=100, nullable=True)
    address_state: Optional[str] = Field(default=None, max_length=100, nullable=True)

    # Auditoría y Tiempos (TIMESTAMPTZ en PostgreSQL)
    last_login: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    date_joined: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), 
            nullable=False, 
            server_default=sa.func.now()
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), 
            nullable=False, 
            server_default=sa.func.now()
        )
    )
    modified_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), 
            nullable=False, 
            server_default=sa.func.now(),
            onupdate=sa.func.now()
        )
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    deleted_by: Optional[UUID] = Field(
        default=None,
        sa_column=Column(sa.UUID(as_uuid=True), nullable=True)
    )
    deactivation_reason: Optional[str] = Field(
        default=None,
        sa_column=Column(sa.String(length=255), nullable=True)
    )

    # Propiedades
    @property
    def full_name(self) -> str:
        """Nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_authenticated(self) -> bool:
        """Verifica si el usuario está activo y no ha sido eliminado lógicamente"""
        return self.is_active and not self.is_deleted

    @property
    def age(self) -> Optional[int]:
        """Calcula la edad actual a partir de la fecha de nacimiento"""
        if not self.date_of_birth:
            return None
        today = date.today()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age

