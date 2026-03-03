"""
Endpoints de autenticación.

Equivalencia con la guía .NET (sección 7.11.3):
- IAuthController → auth router
- Login           → POST /auth/login
- Register        → POST /auth/register
- RefreshToken    → POST /auth/refresh-token
- Me              → GET  /auth/me

Nota: El endpoint de login usa OAuth2PasswordRequestForm para que
Swagger muestre el formulario de autenticación nativo (sección 7.12).
"""

from fastapi import APIRouter, Depends, Body, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import (
    get_auth_service,
    get_current_active_user,
)
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    CurrentUser,
)
from app.schemas.user import UserCreateRequest, UserBasic
from app.schemas.response import ApiResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description=(
        "Autentica al usuario con username y password. "
        "Retorna un par de tokens (access + refresh). "
        "Compatible con el formulario OAuth2 de Swagger. "
        "La respuesta sigue el estándar OAuth2 (RFC 6749) con "
        "access_token en la raíz del JSON."
    ),
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    login_data = LoginRequest(
        username=form_data.username,
        password=form_data.password,
    )
    tokens = await auth_service.login(db, login_data=login_data)
    return tokens


@router.post(
    "/register",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description=(
        "Registra un nuevo usuario y retorna tokens JWT para "
        "iniciar sesión inmediatamente."
    ),
)
async def register(
    user_data: UserCreateRequest = Body(..., description="Datos del nuevo usuario"),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = await auth_service.register(db, user_data=user_data)
    return ApiResponse[TokenResponse](
        codigo=201,
        mensaje="Usuario registrado exitosamente.",
        resultado=tokens,
    )


@router.post(
    "/refresh-token",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Refrescar token de acceso",
    description=(
        "Genera un nuevo par de tokens usando un refresh token válido. "
        "El refresh token anterior deja de ser útil (rotación implícita)."
    ),
)
async def refresh_token(
    refresh_data: RefreshTokenRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = await auth_service.refresh_token(
        db, refresh_token=refresh_data.refresh_token
    )
    return ApiResponse[TokenResponse](
        codigo=200,
        mensaje="Token refrescado exitosamente.",
        resultado=tokens,
    )


@router.get(
    "/me",
    response_model=ApiResponse[CurrentUser],
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario actual",
    description="Retorna la información del usuario autenticado a partir del token JWT.",
)
async def get_me(
    current_user: CurrentUser = Depends(get_current_active_user),
):
    return ApiResponse[CurrentUser](
        codigo=200,
        mensaje="Usuario autenticado obtenido exitosamente.",
        resultado=current_user,
    )
