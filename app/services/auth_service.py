from datetime import datetime, timezone
from typing import Optional, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.token_service import TokenService
from app.schemas.auth import LoginRequest, TokenResponse, CurrentUser
from app.schemas.user import UserCreateRequest
from app.core.security import get_password_hash, verify_password
from app.core.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    InactiveUserException,
    TokenRefreshException,
)
from app.core.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)


class AuthService:
    """
    Servicio de autenticación. Orquesta UserRepository y TokenService
    para implementar el flujo completo de auth.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenService,
    ):
        self.user_repo = user_repository
        self.token_service = token_service

    async def login(
        self, db: AsyncSession, *, login_data: LoginRequest
    ) -> TokenResponse:
        """
        Autentica al usuario con username + password y genera tokens JWT.

        Raises:
            InvalidCredentialsException: Si el usuario no existe o la contraseña es incorrecta.
            InactiveUserException: Si la cuenta está desactivada.
        """
        user = await self.user_repo.get_by_username(
            db, username=login_data.username
        )

        if not user:
            raise InvalidCredentialsException()

        if not verify_password(login_data.password, user.password):
            raise InvalidCredentialsException()

        if not user.is_active or user.is_deleted:
            raise InactiveUserException()

        # Actualizar last_login
        user.last_login = datetime.now(timezone.utc)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return self.token_service.generate_tokens(user)

    async def register(
        self, db: AsyncSession, *, user_data: UserCreateRequest
    ) -> TokenResponse:
        """
        Registra un nuevo usuario y genera tokens JWT.

        Raises:
            UserAlreadyExistsException: Si el username o email ya están en uso.
        """
        # Verificar duplicados
        existing_user = await self.user_repo.get_by_username(
            db, username=user_data.username
        )
        if existing_user:
            raise UserAlreadyExistsException(
                conflict_type="username", value=user_data.username
            )

        if user_data.email:
            existing_email = await self.user_repo.get_by_email(
                db, email=user_data.email
            )
            if existing_email:
                raise UserAlreadyExistsException(
                    conflict_type="email", value=user_data.email
                )

        # Hashear contraseña y crear usuario
        user_dict = user_data.model_dump()
        user_dict["password"] = get_password_hash(user_data.password)
        user_dict["last_login"] = datetime.now(timezone.utc)

        # Convertir profile_picture a string si es HttpUrl
        if user_dict.get("profile_picture") is not None:
            user_dict["profile_picture"] = str(user_dict["profile_picture"])

        db_user = User(**user_dict)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return self.token_service.generate_tokens(db_user)

    async def refresh_token(
        self, db: AsyncSession, *, refresh_token: str
    ) -> TokenResponse:
        """
        Genera un nuevo par de tokens usando un refresh token válido.

        Raises:
            TokenRefreshException: Si el refresh token es inválido.
            InactiveUserException: Si el usuario ya no está activo.
        """
        token_data = self.token_service.verify_refresh_token(refresh_token)

        # Verificar que el usuario aún existe y está activo
        user = await self.user_repo.get(db, id=UUID(token_data.sub))
        if not user:
            raise TokenRefreshException(
                message="El usuario asociado al token ya no existe."
            )

        if not user.is_active or user.is_deleted:
            raise InactiveUserException()

        return self.token_service.generate_tokens(user)

    async def get_current_user(
        self, db: AsyncSession, *, token: str
    ) -> CurrentUser:
        """
        Extrae y valida el usuario actual desde un access token.

        Raises:
            InvalidTokenException: Si el token es inválido.
            InactiveUserException: Si el usuario está desactivado.
        """
        token_data = self.token_service.verify_access_token(token)

        user = await self.user_repo.get(db, id=UUID(token_data.sub))
        if not user:
            raise InvalidTokenException(
                message="El usuario asociado al token no existe."
            )

        if not user.is_active or user.is_deleted:
            raise InactiveUserException()

        return CurrentUser(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
        )
