from pydantic import BaseModel, ConfigDict, Field
from typing import Generic, TypeVar, Optional, Any, List

# Tipo genérico para representar cualquier esquema de datos (User, UserBasic, etc.)
T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    """
    Sobre estándar para respuestas exitosas que devuelven un objeto o lista.
    """
    codigo: int = Field(200, description="Código de estado interno")
    mensaje: str = Field("Operación exitosa", description="Mensaje informativo")
    resultado: Optional[T] = None

    model_config = ConfigDict(from_attributes=True)

class ApiResponseSimple(BaseModel):
    """
    Sobre para respuestas que solo requieren confirmar una acción (ej. eliminaciones).
    """
    codigo: int = 200
    mensaje: str
    resultado: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class ApiError(BaseModel):
    """
    Estructura unificada para el reporte de errores y excepciones.
    """
    codigo: int
    mensaje: str
    resultado: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)

class PagedResponse(BaseModel, Generic[T]):
    """
    Estructura específica para datos paginados.
    """
    total: int = Field(..., description="Total de registros existentes")
    page: int = Field(..., description="Página actual")
    limit: int = Field(..., description="Registros por página")
    data: List[T] = Field(..., description="Lista de registros de la página actual")

    model_config = ConfigDict(from_attributes=True)

