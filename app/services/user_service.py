from typing import Optional, Dict, Any, Tuple
from uuid import UUID
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreateRequest, UserUpdateRequest, UserPartialUpdateRequest,
    User, PagedUsersResult, UserBasic, UserDeleteResult, 
    UserRestoreResult, UserEmailVerifyResult, UserToggleActiveResult
)
from app.core.security import verify_password, get_password_hash

class UserService:
    def __init__(self, user_repository: UserRepository): #se recibe el repositorio como parametro
        self.user_repository = user_repository #se asigna el repositorio al atributo de la clase 
    
    async def get_users( #metodo para obtener usuarios con paginación y filtros
        self, 
        skip: int = 0, #para paginacion: skip y limit
        limit: int = 10, 
        is_active: Optional[bool] = None, #filtro por estado activo, eliminado, superusuario y email verificado
        is_deleted: Optional[bool] = None, 
        is_superuser: Optional[bool] = None, 
        email_verified: Optional[bool] = None, 
        sort_by: str = "created_at", 
        order: str = "desc"
    ) -> PagedUsersResult: 
        """Obtener usuarios con paginación y filtros"""
        # Validar límites
        if limit > 100:
            limit = 100
        
        # Obtener datos del repositorio
        users, total = await self.user_repository.get_multi(
            skip=skip,
            limit=limit,
            is_active=is_active,
            is_deleted=is_deleted,
            is_superuser=is_superuser,
            email_verified=email_verified,
            sort_by=sort_by,
            order=order
        )
        
        # Calcular página actual
        page = (skip // limit) + 1 if limit > 0 else 1
        
        return PagedUsersResult( #se retorna convertido a esquema PagedUsersResult
            total=total,
            page=page,
            limit=limit,
            users=[User.model_validate(user) for user in users]
        )
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]: #se obtiene un usuario por su ID
        """Obtener un usuario por su ID"""
        user = await self.user_repository.get_by_id(user_id) #se obtiene el usuario del repositorio
        if not user:
            return None
        return User.model_validate(user) #se retorna convertido a esquema User
    
    async def get_user_basic(self, user_id: UUID) -> Optional[UserBasic]: #se obtiene información básica de un usuario
        """Obtener información básica de un usuario"""
        user = await self.user_repository.get_by_id(user_id) #se obtiene el usuario del repositorio
        if not user:
            return None
        
        return UserBasic(   #se retorna convertido a esquema UserBasic
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            role=user.role
        )
    
    async def create_user(self, user_data: UserCreateRequest) -> User:
        """Crear un nuevo usuario"""
        # Verificar si email ya existe (si se proporcionó)
        if user_data.email:
            existing_user = await self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El email ya está registrado"
                )
        
        # Verificar si username ya existe
        existing_username = await self.user_repository.get_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya está en uso"
            )
        
        # Crear usuario
        user = await self.user_repository.create(user_data) #se crea el usuario en el repositorio
        return User.model_validate(user) #se retorna convertido a esquema User
    
    async def update_user(self, user_id: UUID, user_data: UserUpdateRequest) -> User: #se actualiza un usuario completamente
        """Actualizar completamente un usuario (PUT)"""
        
        user = await self.user_repository.update(user_id, user_data) 
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return User.model_validate(user)  
    
    async def partial_update_user(self, user_id: UUID, user_data: UserPartialUpdateRequest) -> User: #se actualiza un usuario parcialmente
        """Actualizar parcialmente un usuario (PATCH)"""
        user = await self.user_repository.partial_update(user_id, user_data) #se actualiza el usuario en el repositorio
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return User.model_validate(user) 
    
    async def delete_user(self, user_id: UUID) -> Optional[UserDeleteResult]: #se elimina lógicamente un usuario
        """Eliminar lógicamente un usuario"""
        user = await self.user_repository.soft_delete(user_id) #soft delete marca el usuario como eliminado pwro no lo borra físicamente
        if not user:
            return None
        
        return UserDeleteResult(
            id=user.id,
            is_deleted=user.is_deleted,
            deleted_at=user.deleted_at
        )
    
    async def restore_user(self, user_id: UUID) -> Optional[UserRestoreResult]:
        """Restaurar un usuario eliminado"""
        user = await self.user_repository.restore(user_id)
        if not user:
            return None
        
        return UserRestoreResult(
            id=user.id,
            is_deleted=user.is_deleted,
            deleted_at=user.deleted_at
        )
    
    async def toggle_user_active(self, user_id: UUID) -> Optional[UserToggleActiveResult]:
        """Alternar estado activo/inactivo"""
        user = await self.user_repository.toggle_active(user_id)
        if not user:
            return None
        
        return UserToggleActiveResult(
            id=user.id,
            username=user.username,
            is_active=user.is_active
        )
    
    async def verify_user_email(self, user_id: UUID) -> Optional[UserEmailVerifyResult]:
        """Verificar email de usuario"""
        user = await self.user_repository.verify_email(user_id)
        if not user:
            return None
        
        return UserEmailVerifyResult(
            id=user.id,
            email=user.email,
            email_verified=user.email_verified,
            email_verified_at=user.email_verified_at
        )
    
    async def change_password( #se cambia la contraseña de un usuario
        self, 
        user_id: UUID, 
        current_password: str,
        new_password: str,
        confirm_password: str
    ) -> Dict[str, Any]:
        """Cambiar contraseña de usuario"""
        if new_password != confirm_password: #verificar que las nuevas contraseñas coincidan
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden"
            )
        
        # Obtener usuario para verificar la contraseña actual
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar contraseña actual que sea correcta
        if not verify_password(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Actualizar contraseña usando hash bcrypt
        updated_user = await self.user_repository.update_password(user_id, new_password)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar contraseña"
            )
        
        return {"message": "Contraseña actualizada exitosamente"}
    
    async def request_password_reset(self, email: str) -> None: #se solicita restablecimiento de contraseña
        """Solicitar restablecimiento de contraseña"""
        # Verificar si el usuario existe
        user = await self.user_repository.get_by_email(email)
        if not user:
            # No se dice si el email existe o no para seguridad
            return
        pass