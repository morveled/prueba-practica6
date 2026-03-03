"""
Servicio de tokens JWT.

Equivalencia con la guía .NET (sección 7.10):
- IJwtService  → Interfaz implícita (Python usa duck typing / protocolos)
- JwtService   → TokenService

Responsabilidades:
- Generar par de tokens (access + refresh)
- Verificar y decodificar tokens
- Refrescar tokens usando el refresh token
"""

from datetime import timedelta
from typing import Tuple
from uuid import UUID

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.exceptions.auth_exceptions import (
    InvalidTokenException,
    ExpiredTokenException,
    TokenRefreshException,
)
from app.schemas.auth import TokenResponse, TokenData
from app.models.user import User


class TokenService:
    """
    Servicio encargado de la generación y validación de tokens JWT.
    Encapsula toda la lógica de tokens para desacoplarla del servicio de auth.
    """

    @staticmethod
    def generate_tokens(user: User) -> TokenResponse:
        """
        Genera un par access_token + refresh_token para un usuario autenticado.

        Args:
            user: El modelo de usuario autenticado.

        Returns:
            TokenResponse con ambos tokens y metadata.
        """
        # Claims que irán dentro del JWT
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "is_superuser": user.is_superuser,
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        refresh_token = create_refresh_token(
            data=token_data,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @staticmethod
    def verify_access_token(token: str) -> TokenData:
        """
        Verifica un access token y retorna los datos decodificados.

        Raises:
            InvalidTokenException: Si el token es inválido o expirado.
        """
        token_data = verify_token(token, expected_type="access")
        if token_data is None:
            raise InvalidTokenException()
        return token_data

    @staticmethod
    def verify_refresh_token(token: str) -> TokenData:
        """
        Verifica un refresh token y retorna los datos decodificados.

        Raises:
            TokenRefreshException: Si el token de refresco es inválido.
        """
        token_data = verify_token(token, expected_type="refresh")
        if token_data is None:
            raise TokenRefreshException(
                message="El refresh token es inválido o ha expirado."
            )
        return token_data
