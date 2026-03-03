"""
Inyección de dependencias de FastAPI.

Aquí se configuran todas las dependencias que se inyectan en los endpoints.
Equivalencia con la guía .NET (sección 7.8 / 7.11):
- Registro de servicios → Funciones get_*
- get_current_user      → Extrae el usuario del token JWT (era el TODO pendiente)
"""

from uuid import UUID
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.services.token_service import TokenService
from app.services.auth_service import AuthService
from app.schemas.auth import CurrentUser
from app.core.exceptions.auth_exceptions import (
    InvalidTokenException,
    InactiveUserException,
    InsufficientPermissionsException,
)

# ── OAuth2 scheme para Swagger (sección 7.12 de la guía) ──
# tokenUrl apunta al endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Repositorios ──

async def get_user_repository() -> UserRepository:
    return UserRepository()


async def get_product_repository() -> ProductRepository:
    return ProductRepository()


# ── Servicios ──

async def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)


async def get_product_service(
    repository: ProductRepository = Depends(get_product_repository),
) -> ProductService:
    return ProductService(repository)


def get_token_service() -> TokenService:
    return TokenService()


async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service),
) -> AuthService:
    return AuthService(user_repository, token_service)


# ── Autenticación JWT ──

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUser:
    """
    Dependencia que extrae y valida el usuario actual desde el access token JWT.
    Se inyecta en cualquier endpoint que requiera autenticación.
    """
    return await auth_service.get_current_user(db, token=token)


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Verifica que el usuario actual esté activo."""
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user


async def get_current_superuser(
    current_user: CurrentUser = Depends(get_current_active_user),
) -> CurrentUser:
    """Verifica que el usuario actual sea superusuario."""
    if not current_user.is_superuser:
        raise InsufficientPermissionsException(
            message="Se requieren permisos de superusuario."
        )
    return current_user


def get_current_user_id_flexible() -> UUID:
    """Fallback para endpoints que aún no usan JWT (retrocompatibilidad)."""
    return UUID("00000000-0000-0000-0000-000000000000")

