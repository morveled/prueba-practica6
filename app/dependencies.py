from typing import Optional
from uuid import UUID, uuid4
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService

# Dependencia del repositorio
async def get_user_repository() -> UserRepository:
    return UserRepository()

# Dependencia del servicio
async def get_user_service(
    repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repository)

# Dependencia del repositorio de productos
async def get_product_repository() -> ProductRepository:
    return ProductRepository()

# Dependencia del servicio de productos
async def get_product_service(
    repository: ProductRepository = Depends(get_product_repository)
) -> ProductService:
    return ProductService(repository)

# Dependencias de autenticación (Simuladas por ahora según la lógica de "modo desarrollo" del PDF)
async def get_current_user_id() -> UUID:
    """
    Dependencia para obtener el ID del usuario actual desde un token.
    TODO: Implementar validación JWT. Retornando un UUID fijo para desarrollo.
    """
    # En un escenario real, esto extraería el ID del token JWT
    return UUID("00000000-0000-0000-0000-000000000000")

def get_current_user_id_flexible() -> UUID:
    """
    Dependencia flexible que puede manejar tanto desarrollo como producción.
    En desarrollo, podría retornar un ID por defecto o desde un encabezado.
    """
    return UUID("00000000-0000-0000-0000-000000000000")

