from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_db #importar dependencia de la base de datos
from app.repositories.user_repository import UserRepository #importar repositorio de usuarios
from app.services.user_service import UserService #importar servicio de usuarios


async def get_user_repository( #recibe la sesión de DB como dependencia
    db: AsyncSession = Depends(get_db) #se inyecta la sesión de DB
) -> UserRepository: 
    """Dependencia para obtener el repositorio de usuarios"""
    return UserRepository(db) #se retorna una instancia del repositorio de usuarios


async def get_user_service( #recibe el repositorio de usuarios como dependencia
    user_repository: UserRepository = Depends(get_user_repository) #se inyecta el repositorio de usuarios
) -> UserService:
    """Dependencia para obtener el servicio de usuarios"""
    return UserService(user_repository) #se retorna una instancia del servicio de usuarios, es decir, se crea el servicio con el repositorio inyectado