from fastapi import Depends, HTTPException, status, Query, Header
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db #importar dependencia de la base de datos
from app.repositories.user_repository import UserRepository #importar repositorio de usuarios
from app.services.user_service import UserService, get_user_service #importar servicio de usuarios
from app.core.security import verify_token  # Función para verificar JWT
from uuid import UUID
from app.core.config import settings
from typing import Optional, Union
import os

security = HTTPBearer()
security_dev = HTTPBearer(auto_error=False)


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
     
# ========== DEPENDENCIA ORIGINAL (PARA PRODUCCIÓN) ==========
async def get_current_user_id(
    token: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> UUID:
    """Dependencia para producción - usa token JWT"""
    try:
        payload = verify_token(token.credentials)
        user_id: UUID = UUID(payload.get("sub"))
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id  # <Devuelve UUID, no el User
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ========== DEPENDENCIA PARA DESARROLLO ==========
async def get_current_user_id_dev(
    x_dev_user_id: Optional[str] = Header(
        None, 
        description="Header para desarrollo: x-dev-user-id"
    ),
) -> UUID:
    if not x_dev_user_id:
        raise HTTPException(
            status_code=401,
            detail="En desarrollo debes enviar header x-dev-user-id"
        )
    
    try:
        return UUID(x_dev_user_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="x-dev-user-id debe ser UUID válido"
        )

# ========== DEPENDENCIA INTELIGENTE (USA UNA U OTRA) ==========
def get_current_user_id_flexible() -> Depends:
    if settings.ENVIRONMENT == "development":
        print("USANDO DEPENDENCIA DEV")
        return Depends(get_current_user_id_dev)
    else:
        print("USANDO DEPENDENCIA PROD")
        return Depends(get_current_user_id)