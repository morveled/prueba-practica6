from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest, UserPartialUpdateRequest
from app.schemas.response import PagedResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.core.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    UserNotDeletedException,
    UserAlreadyActiveException,
    UserAlreadyInactiveException,
    InvalidCredentialsException,
    PasswordMismatchException
)

class UserService:
    def __init__(self, user_repository: UserRepository):
        """
        Inicializa el servicio de usuarios con su repositorio correspondiente.
        """
        self.user_repo = user_repository

    async def create_user(self, db: AsyncSession, *, obj_in: UserCreateRequest) -> User:
        """
        Gestiona el registro de nuevos usuarios validando duplicidad y aplicando hash a la contraseña.
        """
        # 1. Verificar si el nombre de usuario ya está registrado
        user_exists = await self.user_repo.get_by_username(db, username=obj_in.username)
        if user_exists:
            raise UserAlreadyExistsException(conflict_type="username", value=obj_in.username)

        # 2. Verificar si el correo electrónico ya está registrado
        if obj_in.email:
            email_exists = await self.user_repo.get_by_email(db, email=obj_in.email)
            if email_exists:
                raise UserAlreadyExistsException(conflict_type="email", value=obj_in.email)

        # 3. Aplicar hash a la contraseña antes de persistir
        obj_in_hashed = obj_in.model_copy(update={"password": get_password_hash(obj_in.password)})

        # 4. Crear el usuario utilizando el repositorio genérico
        return await self.user_repo.create(db, obj_in=obj_in_hashed)

    async def authenticate_user(
        self, db: AsyncSession, *, username: str, password: str
    ) -> Optional[User]:
        """
        Valida las credenciales de un usuario y retorna el objeto User si es exitoso.
        """
        user = await self.user_repo.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def get_user_by_id(self, db: AsyncSession, *, user_id: Any, include_inactive: bool = False) -> User:
        """
        Retorna un usuario por su ID o lanza una excepción 404 si no existe.
        """
        user = await self.user_repo.get(db, id=user_id)
        if not user:
            raise UserNotFoundException(user_id=user_id)
        
        # Si no se permiten inactivos/eliminados y el usuario lo está
        if not include_inactive and (user.is_deleted or not user.is_active):
            raise UserAlreadyInactiveException()
            
        return user

    async def get_multi_users(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        limit: int = 10,
        sort_by: str = "created_at",
        order: str = "desc",
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        Obtiene una lista paginada de usuarios con filtros de búsqueda y estado.
        """
        return await self.user_repo.get_multi_users(
            db, 
            page=page, 
            limit=limit,
            sort_by=sort_by,
            order=order,
            search=search,
            is_active=is_active,
            is_deleted=is_deleted
        )

    async def update_user(
        self, db: AsyncSession, *, user_id: Any, obj_in: UserPartialUpdateRequest
    ) -> User:
        """
        Actualiza la información de un usuario existente.
        """
        db_obj = await self.get_user_by_id(db, user_id=user_id)
        
        # Si se incluye una nueva contraseña, se debe hashear
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = get_password_hash(update_data["password"])
            
        return await self.user_repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def delete_user(
        self, 
        db: AsyncSession, 
        *, 
        user_id: Any, 
        hard_delete: bool = False,
        deleted_by: Optional[UUID] = None,
        reason: Optional[str] = None
    ) -> Optional[User]:
        """
        Elimina a un usuario. Puede ser física (hard_delete) o lógica (soft_delete).
        """
        db_obj = await self.get_user_by_id(db, user_id=user_id, include_inactive=True)

        if hard_delete:
            return await self.user_repo.remove(db, id=user_id)
        
        # Evitar doble eliminación lógica
        if db_obj.is_deleted:
            raise UserAlreadyInactiveException()

        return await self.user_repo.soft_delete(
            db, 
            user_id=user_id, 
            deleted_by=deleted_by, 
            deactivation_reason=reason
        )

    async def restore_user(self, db: AsyncSession, *, user_id: Any) -> User:
        """
        Restaura un usuario eliminado lógicamente.
        """
        db_obj = await self.get_user_by_id(db, user_id=user_id, include_inactive=True)
        
        if not db_obj.is_deleted:
            raise UserNotDeletedException()
        
        # Restaurar estado y limpiar campos de auditoría de borrado
        update_data = {
            "is_deleted": False,
            "is_active": True,
            "deleted_at": None,
            "deleted_by": None,
            "deactivation_reason": None
        }
        return await self.user_repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def change_password(
        self, 
        db: AsyncSession, 
        *, 
        user_id: Any, 
        current_password: str, 
        new_password: str
    ) -> User:
        """
        Cambia la contraseña de un usuario validando primero su contraseña actual.
        """
        db_obj = await self.get_user_by_id(db, user_id=user_id)

        if not verify_password(current_password, db_obj.password):
            raise InvalidCredentialsException()
        
        update_data = {"password": get_password_hash(new_password)}
        return await self.user_repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def activate_user(self, db: AsyncSession, *, user_id: Any) -> User:
        """
        Activa un usuario que se encuentra desactivado.
        """
        db_obj = await self.get_user_by_id(db, user_id=user_id, include_inactive=True)
        
        if db_obj.is_active and not db_obj.is_deleted:
            raise UserAlreadyActiveException()
        
        # Al activar, limpiamos la razón de desactivación
        update_data = {
            "is_active": True, 
            "is_deleted": False,
            "deactivation_reason": None
        }
        return await self.user_repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def deactivate_user(self, db: AsyncSession, *, user_id: Any, reason: Optional[str] = None) -> User:
        """
        Desactiva a un usuario sin eliminarlo.
        """
        db_obj = await self.get_user_by_id(db, user_id=user_id)
        
        if not db_obj.is_active:
            raise UserAlreadyInactiveException()
        
        return await self.user_repo.update(db, db_obj=db_obj, obj_in={"is_active": False, "deactivation_reason": reason})

