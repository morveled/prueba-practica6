from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal


class ProductBase(BaseModel):
    """Campos comunes para operaciones de producto."""
    name: str = Field(..., max_length=255, description="Nombre del producto")
    type: str = Field(..., max_length=10, description="Tipo de producto")
    price: Decimal = Field(..., gt=0, max_digits=8, decimal_places=2, description="Precio del producto")
    status: bool = Field(default=True, description="Estado de disponibilidad del producto")
    description: Optional[str] = Field(None, description="Descripción detallada del producto")
    product_key: Optional[str] = Field(None, max_length=8, description="Clave única asignada al producto")
    image_link: Optional[str] = Field(None, max_length=200, description="URL de la imagen representativa del producto")

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return v


class Product(ProductBase):
    """Esquema principal de producto para respuestas de la API (incluye metadatos). Hereda de ProductBase."""
    id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductCreateRequest(ProductBase):
    """Esquema para la creación de nuevos productos."""
    pass


class ProductUpdateRequest(ProductBase):
    """Esquema para actualización completa (PUT). Hereda de ProductBase."""
    pass


class ProductPartialUpdateRequest(BaseModel):
    """Esquema para actualización parcial (PATCH). Todos los campos son opcionales."""
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=10)
    price: Optional[Decimal] = Field(None, gt=0, max_digits=8, decimal_places=2)
    status: Optional[bool] = None
    description: Optional[str] = None
    product_key: Optional[str] = Field(None, max_length=8)
    image_link: Optional[str] = Field(None, max_length=200)

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return v


class ProductBasic(BaseModel):
    """Subconjunto de información para respuestas rápidas."""
    id: UUID
    name: str
    type: str
    price: Decimal
    status: bool
    product_key: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductDeleteResult(BaseModel):
    """Resultado de la operación de eliminación."""
    id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductRestoreResult(BaseModel):
    """Resultado de la operación de restauración."""
    id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductToggleStatusResult(BaseModel):
    """Resultado de la operación de cambio de estado de disponibilidad."""
    id: UUID
    name: str
    status: bool

    model_config = ConfigDict(from_attributes=True)
