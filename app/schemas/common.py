from pydantic import BaseModel, Field, ConfigDict
from typing import Generic, TypeVar, Optional, Any, List
from enum import Enum

# Tipo genérico para envolver cualquier modelo en una respuesta paginada o estándar
T = TypeVar("T")

class SortOrder(str, Enum):
    """Define las direcciones de ordenamiento permitidas."""
    ASC = "asc"
    DESC = "desc"

class ApiResponse(BaseModel, Generic[T]):
    """Esquema genérico para respuestas exitosas con datos."""
    codigo: int = 200
    mensaje: str = "Operación exitosa"
    resultado: Optional[T] = None
    
    model_config = ConfigDict(from_attributes=True)

class ApiResponseSimple(BaseModel):
    """
    Esquema para respuestas que no devuelven un objeto complejo.
    Basado en el estándar observado en la documentación del proyecto.
    """
    codigo: int = 200
    mensaje: str
    resultado: dict = Field(default_factory=dict)

class ApiError(BaseModel):
    """Estructura estándar para reportar errores al cliente."""
    codigo: int
    mensaje: str
    resultado: Optional[Any] = None

class PaginationParams(BaseModel):
    """Parámetros base para solicitudes de listado paginado."""
    page: int = Field(1, ge=1, description="Número de página (mínimo 1)")
    limit: int = Field(10, ge=1, le=100, description="Registros por página (máximo 100)")

class SortingParams(BaseModel):
    """Parámetros para controlar el ordenamiento de los resultados."""
    sort_by: str = Field("created_at", description="Campo por el cual ordenar")
    order: SortOrder = Field(SortOrder.DESC, description="Dirección del ordenamiento")

class SearchParams(BaseModel):
    """Parámetros para realizar búsquedas globales o filtradas."""
    search: Optional[str] = Field(None, description="Texto de búsqueda general")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo/inactivo")

class PagedResult(BaseModel, Generic[T]):
    """
    Estructura genérica para resultados paginados.
    Sustituye y generaliza esquemas específicos de listado.
    """
    total: int
    page: int
    limit: int
    data: List[T]

    model_config = ConfigDict(from_attributes=True)

