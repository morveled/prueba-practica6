from fastapi import APIRouter, Depends, Query, Path, HTTPException, Body, status
from typing import Optional, Literal
from uuid import UUID

from app.dependencies import get_user_service, get_current_user_id, get_current_user_id_flexible
from app.services.user_service import UserService
from app.schemas.response import (
    ApiResponse, 
    ApiError, 
    ApiResponseUserList, 
    ApiResponseUserBasic, 
    ApiResponseUser, 
    ApiResponseUserDelete, 
    ApiResponseUserRestore, 
    ApiResponseUserEmailVerify, 
    ApiResponseUserToggleActive,
    ApiResponseSimple
    )
from app.schemas.user import (
    User,
    UserCreateRequest,
    UserBasic, 
    UserUpdateRequest,
    UserPartialUpdateRequest,
    UserToggleActiveResult,
    PasswordChangeRequest,
    PasswordResetRequest
)
from app.schemas.common import CommonQueryParams
from app.schemas.user import User as UserSchema # ← Usar alias para claridad
from app.core.exceptions.user_exceptions import UserAlreadyExistsException  # ← Agregar esta importación

router = APIRouter(  )

@router.get(  #endpoint para listar usuarios metodo GET
    "",
    response_model=ApiResponseUserList,
    responses={
        401: {"model": ApiError},
        403: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los usuarios",
    description="Devuelve una lista paginada de usuarios con filtros y ordenamiento."
)
async def list_users(
    params: CommonQueryParams = Depends(),
    is_active: Optional[bool] = None,
    is_deleted: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    email_verified: Optional[bool] = None,
    service: UserService = Depends(get_user_service),
):
    users, total = await service.list_users(
        page=params.page,
        limit=params.limit,
        sort=params.sort,
        order=params.order,
        is_active=is_active,
        is_deleted=is_deleted,
        is_superuser=is_superuser,
        email_verified=email_verified,
    )

    # CONVERTIR objetos SQLAlchemy a UserSchema
    user_schemas = [UserSchema.from_orm(user) for user in users]

    return ApiResponseUserList(
        codigo=200,
        mensaje="Usuarios obtenidos exitosamente.",
        resultado={
            "total": total,
            "page": params.page,
            "limit": params.limit,
            "users": user_schemas,
        },
    )

@router.post( #endpoint para crear usuario metodo POST
    "",
    response_model=ApiResponseUserBasic,#,,,kljkhh
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ApiError, "description": "Datos inválidos"},
        409: {"model": ApiError, "description": "Usuario ya existe"},
        500: {"model": ApiError, "description": "Error interno del servidor"},
    },
    summary="Crear un nuevo usuario",
    description="Crea un nuevo usuario con la información proporcionada."

)
async def create_user(
    user_data: UserCreateRequest = Body(..., description="Datos del nuevo usuario"),
    service: UserService = Depends(get_user_service),
):
    new_user = await service.register_user(user_data)
    user_basic = UserBasic.from_orm(new_user)

    return ApiResponseUserBasic(
        codigo=201,
        mensaje="Usuario creado exitosamente.",
        resultado=user_basic,
    )

@router.get(  #endpoint para obtener usuario por ID metodo GET
    "/{id}",
    response_model=ApiResponseUser,
    responses={
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por ID",
    description="Devuelve la información de un usuario específico por su ID."
)
async def get_user_by_id(
    id: UUID = Path(..., description="ID del usuario a obtener"),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user_by_id(id)
    user_schema = UserSchema.from_orm(user)

    return ApiResponseUser(
        codigo=200,
        mensaje="Usuario obtenido exitosamente.",
        resultado=user_schema,
    )

@router.put(  #endpoint para actualizar usuario por ID metodo PUT
    "/{id}",
    response_model=ApiResponseUserBasic,
    responses={
        400: {"model": ApiError, "description": "Datos inválidos"},
        401: {"model": ApiError},
        404: {"model": ApiError},
        409: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario por ID",
    description="Actualiza la información de un usuario específico por su ID."
)
async def update_user(
    id: UUID = Path(..., description="ID del usuario a actualizar"),
    user_data: UserUpdateRequest = Body(..., description="Datos actualizados del usuario"),
    service: UserService = Depends(get_user_service),
    #current_user_id: UUID = Depends(get_current_user_id),  #Obtiene ID del token    descomentar cuando ya tenga la validacion del token
    current_user_id: UUID = Body(..., embed=True, description="ID del usuario que realiza la acción")  # Recibe en body / solo en desarrollo
):
    updated_user = await service.update_user_full(
        user_id=id,
        update_data=user_data,
        current_user_id=current_user_id  # <- Pasa el ID del usuario actual
    )
    user_basic = UserBasic.from_orm(updated_user)

    return ApiResponseUserBasic(
        codigo=200,
        mensaje="Usuario actualizado exitosamente.",
        resultado=user_basic,
    )

@router.patch(  #endpoint para actualizar parcialmente usuario por ID metodo PATCH
    "/{id}",
    response_model=ApiResponseUserBasic,
    responses={
        400: {"model": ApiError, "description": "Datos inválidos"},
        404: {"model": ApiError},
        409: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente usuario por ID",
    description="Actualiza parcialmente un usuario específico por su ID."
)
async def partial_update_user(
    id: UUID = Path(..., description="ID del usuario a actualizar parcialmente"),
    user_data: UserPartialUpdateRequest = Body(..., description="Datos parcialmente actualizados del usuario"),
    service: UserService = Depends(get_user_service),
    #current_user_id: UUID = Depends(get_current_user_id),  #Obtiene ID del token    descomentar cuando ya tenga la validacion del token
    current_user_id: UUID = Body(..., embed=True, description="ID del usuario que realiza la acción")  # Recibe en body / solo en desarrollo
):
    updated_user = await service.update_user_partial(
        user_id=id,
        update_data=user_data,
        current_user_id=current_user_id  # <- Pasa el ID del usuario actual
    )
    user_basic = UserBasic.from_orm(updated_user)

    return ApiResponseUserBasic(
        codigo=200,
        mensaje="Usuario actualizado parcialmente exitosamente.",
        resultado=user_basic,
    )

@router.delete(  #endpoint para eliminar usuario por ID metodo DELETE
    "/{id}",
    response_model=ApiResponseUserDelete,
    responses={
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario por ID",
    description="Si True, elimina permanentemente (hard delete). Por defecto False (soft delete)."
)
async def delete_user(
    id: UUID,
    hard: bool = Query(False),
    service: UserService = Depends(get_user_service),
    current_user_id: UUID = get_current_user_id_flexible()  #modo flexible para desarrollo y producción (aqui se impplementa el dependencies para prod y desarrollo)
):
    delete_result = await service.delete_user(
        user_id=id,
        current_user_id=current_user_id,  # ID del usuario actual
        hard_delete=hard
    )

    return ApiResponseUserDelete(
        codigo=200,
        mensaje="Usuario eliminado exitosamente.",
        resultado=delete_result,
    )

@router.patch(  #endpoint para restaurar usuario por ID metodo PATCH
    "/{id}/restore",
    response_model=ApiResponseUserRestore,
    responses={
        400: {"model": ApiError},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Restaurar usuario por ID",
    description="Restaura un usuario eliminado lógicamente (soft delete)."
)
async def restore_user(
    id: UUID = Path(..., description="ID del usuario a restaurar"),
    service: UserService = Depends(get_user_service),
    current_user_id: UUID = get_current_user_id_flexible()):
    restore_result = await service.restore_user(
        user_id=id,
        current_user_id=current_user_id  # ID del usuario actual
    )

    return ApiResponseUserRestore(
        codigo=200,
        mensaje="Usuario restaurado exitosamente.",
        resultado=restore_result,
    )

@router.post( #endpoint para verificar email metodo POST
    "/{id}/verify-email",
    response_model=ApiResponseUserEmailVerify,
    responses={
        400: {"model": ApiError},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Verificar si un email está verificado",
    description="Marca el email de un usuario como verificado y actualiza la fecha de verificación en el campo email_verified_at."
)
async def verify_email(
    id: UUID,
    service: UserService = Depends(get_user_service),
    current_user_id: UUID = get_current_user_id_flexible()
):
    user = await service.verify_email(
        user_id=id,
        current_user_id=current_user_id
    )

    return ApiResponseUserEmailVerify(
        codigo=200,
        mensaje="Email verificado exitosamente.",
        resultado=user,
    )

@router.patch( #endpoint para activar usuario por ID metodo PATCH
    "/{id}/activate",
    response_model=ApiResponseUserToggleActive,
    responses={
        400: {"model": ApiError},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Activar un usuario",
    description="Activa un usuario (is_active = true)."
)
async def activate_user(
    id: UUID,
    service: UserService = Depends(get_user_service),
    current_user_id: UUID = Depends(get_current_user_id_flexible)
):
    user = await service.activate_user(
        user_id=id,
        current_user_id=current_user_id
    )

    return ApiResponseUserToggleActive(
        codigo=200,
        mensaje="Usuario activado exitosamente.",
        resultado=UserToggleActiveResult(
            id=user.id,
            username=user.username,
            is_active=user.is_active
        ),
    )

@router.patch( #endpoint para desactivar usuario por ID metodo PATCH
    "/{id}/deactivate",
    response_model=ApiResponseUserToggleActive,
    responses={
        400: {"model": ApiError},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Desactivar un usuario",
    description="Desactiva un usuario (is_active = false)."
)
async def deactivate_user(
    id: UUID,
    service: UserService = Depends(get_user_service),
    current_user_id: UUID = Depends(get_current_user_id_flexible)
):
    user = await service.deactivate_user(
        user_id=id,
        current_user_id=current_user_id
    )

    return ApiResponseUserToggleActive(
        codigo=200,
        mensaje="Usuario desactivado exitosamente.",
        resultado=UserToggleActiveResult(
            id=user.id,
            username=user.username,
            is_active=user.is_active
        ),
    )

@router.post( #endpoint para cambiar contraseña metodo POST
    "/{id}/change-password",
    response_model=ApiResponseSimple,
    responses={
        400: {"model": ApiError},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Cambiar la contraseña de un usuario",
    description="Cambia la contraseña de un usuario dado su ID."
)
async def change_user_password(
    id: UUID,
    password_data: PasswordChangeRequest,
    service: UserService = Depends(get_user_service),
    current_user_id: UUID = Depends(get_current_user_id_flexible)
):
    await service.change_password(
        user_id=id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
        confirm_password=password_data.confirm_password,
        current_user_id=current_user_id
    )

    return ApiResponseSimple(
        codigo=200,
        mensaje="Contraseña cambiada exitosamente.",
        resultado={}
    )

@router.post( #endpoint para solicitar restablecimiento de contraseña metodo POST
    "/request-password-reset",
    response_model=ApiResponseSimple,
    responses={
        400: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    status_code=status.HTTP_200_OK,
    summary="Solicitar restablecimiento de contraseña",
    description="Permite solicitar un restablecimiento de contraseña enviando un enlace o token al correo electrónico registrado del usuario."
)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    service: UserService = Depends(get_user_service),
):
    await service.request_password_reset(
        reset_request
    )

    return ApiResponseSimple(
        codigo=200,
        mensaje="Instrucciones para restablecer la contraseña enviadas al correo electrónico.",
        resultado={}
    )