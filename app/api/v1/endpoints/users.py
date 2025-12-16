# app/api/v1/endpoints/users.py
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, HTTPException, Body, status

from app.schemas.user import (
    User,
    UserCreateRequest,
    UserUpdateRequest,
    UserPartialUpdateRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PagedUsersResult,
    UserBasic,
    UserDeleteResult,
    UserRestoreResult,
    UserEmailVerifyResult,
    UserToggleActiveResult,
    ApiResponseUserList,
    ApiResponseUser,
    ApiResponseUserBasic,
    ApiResponseUserDelete,
    ApiResponseUserRestore,
    ApiResponseUserEmailVerify,
    ApiResponseUserToggleActive,
    ApiResponseSimple,
    ApiError
)
from app.schemas.common import CommonQueryParams
from app.services.user_service import UserService
from app.dependencies import get_user_service

router = APIRouter()


@router.get(
    "",
    response_model=ApiResponseUserList,
    responses={
        200: {"model": ApiResponseUserList},
        401: {"model": ApiError},
        403: {"model": ApiError},
        500: {"model": ApiError}
    },
    summary="Obtener todos los usuarios",
    description="Devuelve una lista paginada de usuarios con soporte para paginación, ordenamiento y filtros."
)
async def get_users(
    commons: CommonQueryParams = Depends(),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    is_deleted: Optional[bool] = Query(None, description="Filtrar por estado de eliminación lógica"),
    is_superuser: Optional[bool] = Query(None, description="Filtrar por usuarios con privilegios de superusuario."),
    email_verified: Optional[bool] = Query(None, description="Filtrar por estado de verificación de email."),
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseUserList:
    """Obtener todos los usuarios con paginación y filtros"""
    try:
        result = await user_service.get_users(
            skip=commons.skip,
            limit=commons.limit,
            is_active=is_active,
            is_deleted=is_deleted,
            is_superuser=is_superuser,
            email_verified=email_verified,
            sort_by=commons.sort,
            order=commons.order
        )
        
        return ApiResponseUserList(
            codigo=200,
            mensaje="Usuarios obtenidos exitosamente.",
            resultado=result
        )
    except HTTPException:
        # Re-lanzar HTTPException que ya vienen con su código y detalle
        raise

    except Exception as e:
       # Capturar cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "codigo": 500,
                "mensaje": f"Error interno del servidor: {str(e)}",
                "resultado": None
            }
        )

@router.post(
    "",
    response_model=ApiResponseUserBasic,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": ApiResponseUserBasic},
        400: {"model": ApiError},
        409: {"model": ApiError}
    },
    summary="Crear un nuevo usuario",
    description="Crea un nuevo usuario con la información proporcionada en el cuerpo de la petición."
)
async def create_user(
    user_data: UserCreateRequest,
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseUserBasic:
    """Crear un nuevo usuario"""
    try:
        # Intentar crear el usuario
        new_user = await user_service.create_user(user_data)
        
        # Convertir a UserBasic para la respuesta
        user_basic = UserBasic(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            is_active=new_user.is_active,
            role=new_user.role
        )
        
        return ApiResponseUserBasic(
            codigo=201,
            mensaje="Usuario creado exitosamente.",
            resultado=user_basic
        )

    except ValueError as e:
        # Error de validación de datos
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "codigo": 400,
                "mensaje": f"Datos inválidos: {str(e)}",
                "resultado": None
            }
        )

    except HTTPException as e:
        # Re-lanzar excepciones HTTP ya manejadas (como 409)
        raise

    except Exception as e:
        # Error 409: Usuario o email ya existe
        error_message = str(e).lower()
        if "duplicate" in error_message or "already exists" in error_message or "unique constraint" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "codigo": 409,
                    "mensaje": "Nombre de usuario o email ya registrado.",
                    "resultado": None
                }
            )

        # Error 500: Cualquier otro error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "codigo": 500,
                "mensaje": f"Error interno del servidor: {str(e)}",
                "resultado": None
            }
        )

@router.get(
    "/{id}",
    response_model=ApiResponseUser,
    responses={
        200: {"model": ApiResponseUser},
        401: {"model": ApiError},
        403: {"model": ApiError},
    },
    summary="Obtener un usuario por ID",
    description="Retorna los detalles completos de un usuario específico."
)
async def get_user(
    user_id: UUID = Path(..., description="ID del usuario"),
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseUser:
    """Obtener un usuario por su ID"""
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ApiError(
                codigo=404,
                mensaje="Usuario no encontrado",
                resultado=None
            ).model_dump()
        )
    
    return ApiResponseUser(
        codigo=200,
        mensaje="Usuario obtenido exitosamente.",
        resultado=user
    )

@router.put(
    "/{id}",
    response_model=ApiResponseUserBasic,
    responses={
        200: {"model": ApiResponseUserBasic},
        400: {"model": ApiError},
        404: {"model": ApiError},
        409: {"model": ApiError},
        500: {"model": ApiError}
    },
    summary="Actualizar un usuario (completo)",
    description="Actualiza completamente un usuario especificado por su ID."
)
async def update_user(
    user_id: UUID = Path(..., description="ID del usuario"),
    user_data: UserUpdateRequest = None,
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseUserBasic:
    """Actualizar completamente un usuario (PUT)"""
    try:
        user = await user_service.update_user(user_id, user_data)
        
        return ApiResponseUserBasic(
            codigo=200,
            mensaje="Usuario actualizado exitosamente.",
            resultado=user
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ApiError(
                codigo=400,
                mensaje=f"Error al actualizar usuario: {str(e)}",
                resultado=None
            ).model_dump()
        )

@router.patch(
    "/{id}",
    response_model=UserPartialUpdateRequest,
    responses={
        200: {"model": ApiResponseUserBasic},
        400: {"model": ApiError},
        404: {"model": ApiError},
        409: {"model": ApiError},
        500: {"model": ApiError}
    },
    summary="Actualizar un usuario (parcial)",
    description="Actualiza parcialmente un usuario; solo se modifican los campos enviados."
) 
async def partial_update_user(
    user_id: UUID = Path(..., description="ID del usuario"),
    user_data: UserPartialUpdateRequest = None,
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseUserBasic:
    """Actualizar parcialmente un usuario (PATCH)"""
    try:
        user = await user_service.partial_update_user(user_id, user_data)
        
        return ApiResponseUserBasic(
            codigo=200,
            mensaje="Usuario actualizado parcialmente exitosamente.",
            resultado=user
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ApiError(
                codigo=400,
                mensaje=f"Error al actualizar usuario: {str(e)}",
                resultado=None
            ).model_dump()
        )

@router.delete(
    "/{id}",
    response_model=ApiResponseUserDelete,
    responses={
        200: {"model": ApiResponseUserDelete},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError}
    },
    summary="Eliminar un usuario (borrado lógico)",
    description="Marca el usuario como eliminado sin borrar físicamente de la base de datos"
)
async def delete_user(
    user_id: UUID = Path(..., description="ID del usuario"),
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseUserDelete:
    """Eliminar un usuario (borrado lógico)"""
    try:
        result = await user_service.delete_user(user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ApiError(
                    codigo=404,
                    mensaje="Usuario no encontrado",
                    resultado=None
                ).model_dump()
            )
        
        return ApiResponseUserDelete(
            codigo=200,
            mensaje="Usuario eliminado exitosamente.",
            resultado=result
        )
    except HTTPException as http_exc:
        # Convertir HTTPException existente a formato ApiError
        raise HTTPException(
            status_code=http_exc.status_code,
            detail=ApiError(
                codigo=http_exc.status_code,
                mensaje=http_exc.detail,
                resultado=None
            ).model_dump()
        )
        
    except Exception as e:
        # Log del error interno
        # import logging
        # logging.error(f"Error inesperado en delete_user: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiError(
                codigo=500,
                mensaje="Error interno del servidor al eliminar usuario",
                resultado=None
            ).model_dump()
        )

@router.patch(
    "/{id}/restore",
    response_model=ApiResponseUserRestore,
    responses={
        200: {"model": ApiResponseUserRestore},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError}
    },
    summary="Restaurar un usuario eliminado",
    description="Restaura un usuario que fue eliminado lógicamente."
)
async def restore_user(
    user_id: UUID = Path(..., description="ID del usuario"),
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseUserRestore:
    """Restaurar un usuario eliminado"""
    try:
        result = await user_service.restore_user(user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ApiError(
                    codigo=404,
                    mensaje="Usuario no encontrado",
                    resultado=None
                ).model_dump()
            )
        
        return ApiResponseUserRestore(
            codigo=200,
            mensaje="Usuario restaurado exitosamente.",
            resultado=result
        )
    except HTTPException as http_exc:
        # Convertir HTTPException existente a formato ApiError
        raise HTTPException(
            status_code=http_exc.status_code,
            detail=ApiError(
                codigo=http_exc.status_code,
                mensaje=http_exc.detail,
                resultado=None
            ).model_dump()
        )
        
    except Exception as e:
        # Log del error interno
        # import logging
        # logging.error(f"Error inesperado en restore_user: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiError(
                codigo=500,
                mensaje="Error interno del servidor al restaurar usuario",
                resultado=None
            ).model_dump()
        )

@router.post(
    "/{id}/verify-email",
    response_model=ApiResponseUserEmailVerify,
    responses={
        200: {"model": ApiResponseUserEmailVerify},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError}
    },
    summary="Verificar email del usuario",
    description="Marca el email del usuario como verificado."
)
async def verify_user_email(
    user_id: UUID = Path(..., description="ID del usuario"),
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseUserEmailVerify:
    """Verificar email del usuario"""
    try:
        result = await user_service.verify_user_email(user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ApiError(
                    codigo=404,
                    mensaje="Usuario no encontrado",
                    resultado=None
                ).model_dump()
            )
        
        return ApiResponseUserEmailVerify(
            codigo=200,
            mensaje="Email del usuario verificado exitosamente.",
            resultado=result
        )
    except HTTPException as http_exc:
        # Convertir HTTPException existente a formato ApiError
        raise HTTPException(
            status_code=http_exc.status_code,
            detail=ApiError(
                codigo=http_exc.status_code,
                mensaje=http_exc.detail,
                resultado=None
            ).model_dump()
        )
        
    except Exception as e:
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiError(
                codigo=500,
                mensaje="Error interno del servidor al verificar email del usuario",
                resultado=None
            ).model_dump()
        )

@router.patch(
    "/{id}/activate",
    response_model=ApiResponseUserToggleActive,
    responses={
        200: {"model": ApiResponseUserToggleActive},
        400: {"model": ApiError},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    summary="Activar un usuario",
    description="Activa un usuario (is_active = true)."
)
async def activate_user(
    user_id: UUID = Path(..., description="ID del usuario"),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponseUserToggleActive:
    try:
        result = await user_service.activate_user(user_id)

        return ApiResponseUserToggleActive(
            codigo=200,
            mensaje="Usuario activado exitosamente.",
            resultado=result
        )

    except HTTPException:
        # Re-lanzar excepciones ya controladas (400, 404, 403, etc.)
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiError(
                codigo=500,
                mensaje="Error interno del servidor.",
                resultado=None
            ).model_dump()
        )

@router.patch(
    "/{id}/deactivate",
    response_model=ApiResponseUserToggleActive,
    responses={
        200: {"model": ApiResponseUserToggleActive},
        400: {"model": ApiError},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError},
    },
    summary="Desactivar un usuario",
    description="Desactiva un usuario (is_active = false)."
)
async def deactivate_user(
    user_id: UUID = Path(..., description="ID del usuario"),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponseUserToggleActive:
    try:
        result = await user_service.deactivate_user(user_id)

        return ApiResponseUserToggleActive(
            codigo=200,
            mensaje="Usuario desactivado exitosamente.",
            resultado=result
        )

    except HTTPException:
        # 400, 404, 401, 403 se relanzan tal cual
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiError(
                codigo=500,
                mensaje="Error interno del servidor.",
                resultado=None
            ).model_dump()
        )

@router.post(
    "/{id}/change-password",
    response_model=ApiResponseSimple,
    responses={
        200: {"model": ApiResponseSimple},
        400: {"model": ApiError},
        401: {"model": ApiError},
        403: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError}
    },
    summary="Cambiar contraseña de usuario",
    description="Permite cambiar la contraseña proporcionando la contraseña actual y la nueva contraseña."
)
async def change_user_password(
    user_id: UUID = Path(..., description="ID del usuario"),
    password_data: PasswordChangeRequest = None,
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseSimple:
    """Cambiar contraseña de un usuario"""
    try:
        await user_service.change_password(
            user_id=user_id,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
            confirm_password=password_data.confirm_password
        )
        
        return ApiResponseSimple(
            codigo=200,
            mensaje="Contraseña cambiada exitosamente.",
            resultado=None
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ApiError(
                codigo=400,
                mensaje=f"Error al cambiar contraseña: {str(e)}",
                resultado=None
            ).model_dump()
        )

@router.post(
    "/request-password-reset",
    response_model=ApiResponseSimple,
    responses={
        200: {"model": ApiResponseSimple},
        400: {"model": ApiError},
        404: {"model": ApiError},
        500: {"model": ApiError}
    },
    summary="Restablecer contraseña de usuario",
    description="Inicia el proceso de restablecimiento de contraseña enviando un email al usuario."
)
async def request_password_reset(
    reset_data: PasswordResetRequest = Body(...),
    user_service: UserService = Depends(get_user_service)
) -> ApiResponseSimple:
    """Solicitar restablecimiento de contraseña"""
    try:
        await user_service.request_password_reset(reset_data.email)
        
        return ApiResponseSimple(
            codigo=200,
            mensaje="Instrucciones para restablecer la contraseña enviadas al email.",
            resultado=None
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ApiError(
                codigo=400,
                mensaje=f"Error al solicitar restablecimiento de contraseña: {str(e)}",
                resultado=None
            ).model_dump()
        )


