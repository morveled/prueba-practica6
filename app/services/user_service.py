import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
    UserDeleteResult,
    UserPartialUpdateRequest,
    UserRestoreResult,
    PasswordChangeRequest,
    PasswordResetRequest, 
    User as UserSchema,
    Gender
)
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    UserNotDeletedException,
    EmailAlreadyVerifiedException,
    InvalidCredentialsException,
    UserAlreadyActiveException,
    UserAlreadyInactiveException,
    PasswordMismatchException,
    EmailNotVerifiedException,
    EmailNotFoundException,
    PermissionDeniedException
)

class UserService:
    
    def __init__(self, repository: UserRepository):
        self.repository = repository

    # ========== AUTHENTICACION ==========
    async def authenticate_user(
        self, 
        email: str, 
        password: str
    ) -> Tuple[User, str]:
        """Autentica un usuario y genera un token de acceso.
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
        Returns:
            Tuple[User, str]: Usuario autenticado y token JWT
        Raises:
            InvalidCredentialsException: Si las credenciales son incorrectas
            UserInactiveException: Si el usuario está inactivo o eliminado
        """
        # Buscar usuario por email
        user = await self.repository.get_by_email(email, active_only=False)
        
        if not user:
            raise InvalidCredentialsException("Email o contraseña incorrectos")
        
        # Verificar contraseña
        if not verify_password(password, user.password):
            raise InvalidCredentialsException("Email o contraseña incorrectos")
        
        # Verificar que el usuario esté activo
        if user.is_deleted or not user.is_active:
            raise UserInactiveException("Usuario inactivo o eliminado")
        
        # Generar token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username
        }
        access_token = create_access_token(token_data)
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        await self.repository.update(user)
        
        return user, access_token

    async def verify_token_and_get_user(self, user_id: UUID) -> User:
        """Verifica que el usuario del token exista y esté activo.
        Args:
            user_id: ID del usuario extraído del token
        Returns:
            User: Usuario activo 
        Raises:
            UserNotFoundException: Si el usuario no existe
            UserInactiveException: Si el usuario está inactivo
        """
        user = await self.repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundException("Usuario no encontrado")
        
        if user.is_deleted or not user.is_active:
            raise UserInactiveException("Usuario inactivo o eliminado")
        
        return user

    # ========== REGISTRO ==========
    async def register_user(self, user_data: UserCreateRequest) -> User:  #no tocar
        """Registra un nuevo usuario en el sistema.
        Args:
            user_data: Datos del usuario a crear (UserCreateRequest)
        Returns:
            User: Usuario creado
        Raises:
            UserAlreadyExistsException: Si el email o username ya existen
        """
        # Validar que el email no exista (si se proporciona)
        if user_data.email and await self.repository.exists_by_email(user_data.email, active_only=False):
             raise UserAlreadyExistsException("email", user_data.email)
        
        # Validar que el username no exista
        if await self.repository.exists_by_username(user_data.username, active_only=False):
            raise UserAlreadyExistsException("username", user_data.username)
        
        # Crear instancia del usuario con todos los campos
        # 2. Preparar timestamps (Usando la forma moderna para evitar warnings)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        # Preparar datos del usuario
        user_dict = user_data.model_dump(exclude={'password'}, exclude_unset=True)
        
        # Crear usuario con campos requeridos y opcionales
        user = User(
            # Campos requeridos
            username=user_data.username.strip(),
            first_name=user_data.first_name.strip(),
            last_name=user_data.last_name.strip(),
            password=get_password_hash(user_data.password),  # Hashear password
            # Email (opcional pero común)
            email=user_data.email.lower().strip() if user_data.email else None,
            # Campos de estado
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser,
            is_deleted=False,
            email_verified=False,
            # Timestamps
            created_at=now,
            modified_at=now,
            date_joined=now,
            last_login=None,
            deleted_at=None,
            email_verified_at=None,
            # Campos de perfil opcionales
            profile_picture=str(user_data.profile_picture) if user_data.profile_picture else None,
            nationality=user_data.nationality,
            occupation=user_data.occupation,
            date_of_birth=user_data.date_of_birth,
            contact_phone_number=user_data.contact_phone_number,
            gender=user_data.gender.value if user_data.gender else None,
            # Campos de dirección opcionales
            address=user_data.address,
            address_number=user_data.address_number,
            address_interior_number=user_data.address_interior_number,
            address_complement=user_data.address_complement,
            address_neighborhood=user_data.address_neighborhood,
            address_zip_code=user_data.address_zip_code,
            address_city=user_data.address_city,
            address_state=user_data.address_state,
            # Role
            role=user_data.role
        )
        # Persistir en BD
        created_user = await self.repository.add(user)
        
        return created_user

    # ========== OPERACIONES READ ==========
    async def get_user_by_id(    #no tocar
        self, 
        user_id: UUID, 
        include_inactive: bool = False
    ) ->User:
        """
        Obtiene un usuario por ID.

        Raises:
            UserNotFoundException: Si el usuario no existe
        """
        user = await self.repository.get_by_id(
            user_id=user_id,
            include_inactive=include_inactive
        )

        if not user:
            raise UserNotFoundException(user_id=user_id)

        return user

    async def get_user_by_email(self, email: str) -> User:
        """Obtiene un usuario por email.
        Args:
            email: Email del usuario 
        Returns:
            User: Usuario encontrado 
        Raises:
            UserNotFoundException: Si el usuario no existe
        """
        user = await self.repository.get_by_email(email, active_only=True)
        
        if not user:
            raise UserNotFoundException(f"Usuario con email {email} no encontrado")
        
        return user

    async def list_users(  #no tocar
        self,
        page: int = 1,
        limit: int = 100,
        search: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort: str = "created_at",
        order: str = "desc",
        is_active: Optional[bool] = None,
        is_deleted: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        email_verified: Optional[bool] = None,
        include_inactive: bool = False
    ) -> Tuple[List[User], int]:
        """Lista usuarios con filtros y paginación.
        Args:
            skip: Offset para paginación
            limit: Límite de resultados
            search: Texto de búsqueda
            filters: Filtros adicionales
            sort_by: Campo para ordenar
            sort_order: Orden (asc/desc)
            include_inactive: Si True, incluye usuarios inactivos   
        Returns:
            Tuple[List[User], int]: Lista de usuarios y total
        """
        # Validar límite máximo
        if limit > 100:
            limit = 100
        
        users, total = await self.repository.get_multi(
            page=page,
            limit=limit,
            search=search,
            filters=filters,
            sort=sort,
            order=order,
            is_active=is_active,
            is_deleted=is_deleted,
            is_superuser=is_superuser,
            active_only=not include_inactive
        )
        
        return users, total

    async def count_users(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        include_inactive: bool = False
    ) -> int:
        """Cuenta el total de usuarios.
        Args:
            filters: Filtros opcionales
            include_inactive: Si True, incluye usuarios inactivos  
        Returns:
            int: Total de usuarios
        """
        return await self.repository.count(
            filters=filters,
            active_only=not include_inactive
        )

    # ========== OPERACIONES UPDATE ==========
    async def update_user_full(  #no tocar
        self, 
        user_id: UUID, 
        update_data: UserUpdateRequest,
        current_user_id: UUID
    ) -> User:
        """Actualización completa de un usuario (PUT).
        Args:
            user_id: ID del usuario a actualizar
            update_data: Datos completos del usuario (UserUpdateRequest)
            current_user_id: ID del usuario que realiza la acción   
        Returns:
            User: Usuario actualizado    
        Raises:
            UserNotFoundException: Si el usuario no existe
            UserAlreadyExistsException: Si intenta usar email/username ya existente
        """
        # Obtener usuario existente
        user = await self.get_user_by_id(user_id)
        # Validar email único si cambió
        if update_data.email and update_data.email != user.email:
            if await self.repository.exists_by_email(update_data.email):
                raise UserAlreadyExistsException(
                    f"El email {update_data.email} ya está en uso"
                )
        # Validar username único si cambió
        if update_data.username != user.username:
            if await self.repository.exists_by_username(update_data.username):
                raise UserAlreadyExistsException(
                    f"El username {update_data.username} ya está en uso"
                )
        # Actualizar todos los campos
        user.username = update_data.username.strip()
        user.email = update_data.email.lower().strip() if update_data.email else None
        user.first_name = update_data.first_name.strip()
        user.last_name = update_data.last_name.strip()
        user.is_active = update_data.is_active
        user.is_superuser = update_data.is_superuser
        # Actualizar password si se proporciona
        if update_data.password:
            user.password = get_password_hash(update_data.password)
        # Campos de perfil
        user.profile_picture = str(update_data.profile_picture) if update_data.profile_picture else None
        user.nationality = update_data.nationality
        user.occupation = update_data.occupation
        user.date_of_birth = update_data.date_of_birth
        user.contact_phone_number = update_data.contact_phone_number
        user.gender = update_data.gender
        # Campos de dirección
        user.address = update_data.address
        user.address_number = update_data.address_number
        user.address_interior_number = update_data.address_interior_number
        user.address_complement = update_data.address_complement
        user.address_neighborhood = update_data.address_neighborhood
        user.address_zip_code = update_data.address_zip_code
        user.address_city = update_data.address_city
        user.address_state = update_data.address_state
        user.role = update_data.role
        # Persistir cambios
        updated_user = await self.repository.update(user)
        
        return updated_user

    async def update_user_partial( #no tocar
        self, 
        user_id: UUID, 
        update_data: UserPartialUpdateRequest,
        current_user_id: UUID
    ) -> User:
        """Actualización parcial de un usuario (PATCH).
        Args:
            user_id: ID del usuario a actualizar
            update_data: Datos parciales del usuario (UserPartialUpdateRequest)
            current_user_id: ID del usuario que realiza la acción  
        Returns:
            User: Usuario actualizado   
        Raises:
            UserNotFoundException: Si el usuario no existe
            UserAlreadyExistsException: Si intenta usar email/username ya existente
        """
        # Obtener usuario existente
        user = await self.get_user_by_id(user_id)
        
        # Obtener solo los campos que fueron proporcionados
        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
        
        # Validar email único si se está actualizando
        if 'email' in update_dict and update_dict['email'] != user.email:
            if await self.repository.exists_by_email(update_dict['email']):
                raise UserAlreadyExistsException(
                    f"El email {update_dict['email']} ya está en uso"
                )
            user.email = update_dict['email'].lower().strip()
        
        # Validar username único si se está actualizando
        if 'username' in update_dict and update_dict['username'] != user.username:
            if await self.repository.exists_by_username(update_dict['username']):
                raise UserAlreadyExistsException(
                    f"El username {update_dict['username']} ya está en uso"
                )
            user.username = update_dict['username'].strip()
        
        # Actualizar password si se proporciona
        if 'password' in update_dict:
            user.password = get_password_hash(update_dict['password'])
        
        # Actualizar el resto de  los campos
        for field, value in update_dict.items():
            if field in ['email', 'username', 'password']:
                continue

            if field == "profile_picture":
                value = str(value) if value else None

            if field == "gender":
                value = value.value if value else None

            setattr(user, field, value)
        
        # Persistir cambios
        updated_user = await self.repository.update(user)
        
        return updated_user

    async def change_password( #no tocar
        self, 
        user_id: UUID, 
        current_password: str,
        new_password: str,
        confirm_password: str,
        current_user_id: UUID
    ) ->   None:
        """Cambia la contraseña de un usuario.
        Args:
            user_id: ID del usuario
            current_password: Contraseña actual
            new_password: Nueva contraseña
            confirm_password: Confirmación de nueva contraseña
            current_user_id: ID del usuario que realiza la acción 
        Raises:
            UserNotFoundException: Si el usuario no existe
            InvalidCredentialsException: Si la contraseña actual es incorrecta
            PasswordMismatchException: Si las contraseñas nuevas no coinciden
        """
        user = await self.get_user_by_id(user_id)
    
        # Verifica la contraseña actual
        if not verify_password(current_password, user.password):
            raise InvalidCredentialsException()
        
        # Verifica que las contraseñas nuevas coincidan
        if new_password != confirm_password:
            raise PasswordMismatchException()
        
        # Actualizar contraseña
        user.password = get_password_hash(new_password)
        await self.repository.update(user)

    async def verify_email(self, user_id: UUID, current_user_id: UUID) -> User:
        user = await self.get_user_by_id(user_id)

        # Regla de negocio
        if user.email_verified:
            raise EmailAlreadyVerifiedException()

        user.email_verified = True
        user.email_verified_at = datetime.utcnow()

        return await self.repository.update(user)

    async def activate_user(self, user_id: UUID, current_user_id: UUID) -> User: #no tocar
        """Activa un usuario."""
        user = await self.get_user_by_id(user_id, include_inactive=True)
        
        # Verificar si el usuario ya estaba activo
        if user.is_active:
            raise UserAlreadyActiveException()
        
        user.is_active = True
        user.is_deleted = False
        return await self.repository.update(user)

    async def deactivate_user(self, user_id: UUID, current_user_id: UUID) -> User: #no tocar
        """Desactiva un usuario (sin eliminarlo)."""
        user = await self.get_user_by_id(user_id)

        if not user.is_active:
            raise UserAlreadyInactiveException()

        user.is_active = False
        return await self.repository.update(user)

    async def request_password_reset(self, reset_data: PasswordResetRequest) -> None: #no tocar (es para el ulti endpoint)
        """Solicita un restablecimiento de contraseña.
        Args:
            reset_data: Datos de la solicitud (email) 
        Returns:
            None
        Raises:
            EmailNotFoundException: Si el email no está registrado
            EmailNotVerifiedException: Si el email no está verificado
        """
        # Buscar usuario por email
        user = await self.repository.get_by_email(reset_data.email)
        
        if not user:
            raise EmailNotFoundException()

        if not user.email_verified:
            raise EmailNotVerifiedException()

        # Generar token seguro
        token = secrets.token_urlsafe(32)

        # Guardar token y expiración (ejemplo 30 min)
        user.password_reset_token = token
        user.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=30)

        await self.repository.update(user)

        # Enviar correo (pseudo)
        await self.email_service.send_password_reset_email(
            email=user.email,
            token=token
        )

        return None

    # ========== OPERACIONES DELETE ==========
    async def delete_user( #no tocar
        self, 
        user_id: UUID,
        hard_delete: bool = False,
        current_user_id: Optional[UUID] = None  # Quien realiza la acción
    ) -> UserDeleteResult:
        """Elimina un usuario (soft o hard delete).
        Args:
            user_id: ID del usuario
            hard_delete: Si True, elimina permanentemente
            current_user_id: ID del usuario que realiza la acción (opcional)
        Returns:
            UserDeleteResult: Resultado de la eliminación  
        Raises:
            UserNotFoundException: Si el usuario no existe
        """
        user = await self.get_user_by_id(user_id, include_inactive=True)
        
        # Evitar doble borrado lógico
        if not hard_delete and user.is_deleted:
            raise BusinessException("El usuario ya está eliminado")

        if hard_delete:
            await self.repository.hard_delete(user)
            deleted_at = datetime.now(timezone.utc)
        else:
            user = await self.repository.soft_delete(user)
            deleted_at = user.deleted_at

        return UserDeleteResult(
            id=user_id,
            is_deleted=True,
            deleted_at=deleted_at
        )

    async def restore_user( #no tocar
        self, 
        user_id: UUID, 
        current_user_id: Optional[UUID] = None
    ) -> UserRestoreResult:

        user = await self.repository.get_by_id(
            user_id,
            include_inactive=True,
            include_deleted=True
        )

        if not user:
            raise UserNotFoundException(f"Usuario con ID {user_id} no encontrado")

        if not user.is_deleted:
            raise UserNotDeletedException()

        user.is_deleted = False
        user.is_active = True
        user.deleted_at = None

        restored_user = await self.repository.update(user)

        return UserRestoreResult(
            id=restored_user.id,
            is_deleted=restored_user.is_deleted,
            deleted_at=restored_user.deleted_at
        )

# ========== INYECCIÓN DE DEPENDENCIAS ==========
async def get_user_service(
    repository: UserRepository
) -> UserService:
    """Factory function para inyección de dependencias.
    Uso en endpoints:
        service: UserService = Depends(get_user_service)
    """
    return UserService(repository)