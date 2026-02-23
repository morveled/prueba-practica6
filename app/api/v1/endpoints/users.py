from fastapi import APIRouter, Depends, Query, Path, Body, status
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_user_service, get_current_user_id_flexible
from app.services.user_service import UserService
from app.schemas.response import (
    ApiResponse,
    ApiError,
    ApiResponseSimple,
    PagedResponse
)
from app.schemas.user import (
    User as UserSchema,
    UserCreateRequest,
    UserBasic,
    UserUpdateRequest,
    UserPartialUpdateRequest,
    UserToggleActiveResult,
    UserDeleteResult,
    UserRestoreResult,
    UserEmailVerifyResult,
    PasswordChangeRequest,
    PasswordResetRequest
)

# Se crea el router para el módulo de usuarios
router = APIRouter()

# ---------- READ ----------

@router.get(
    "",
    response_model=ApiResponse[PagedResponse[UserSchema]],
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los usuarios",
    description="Devuelve una lista paginada de usuarios con filtros y ordenamiento."
)
async def list_users(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Registros por página"),
    search: Optional[str] = Query(None, description="Buscar por username o email"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    is_deleted: bool = Query(False, description="Filtrar por borrado lógico"),
    sort_by: str = Query("created_at", description="Campo por el cual ordenar"),
    order: str = Query("desc", description="Dirección del ordenamiento (asc/desc)"),
    service: UserService = Depends(get_user_service),
):
    result = await service.get_multi_users(
        db, 
        page=page, 
        limit=limit,
        sort_by=sort_by,
        order=order,
        search=search,
        is_active=is_active,
        is_deleted=is_deleted
    )
    
    # Adaptar el resultado del repositorio al esquema de PagedResponse
    paged_data = PagedResponse[UserSchema](
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        data=result["items"]
    )
    
    return ApiResponse[PagedResponse[UserSchema]](
        codigo=200,
        mensaje="Usuarios obtenidos exitosamente.",
        resultado=paged_data
    )

@router.get(
    "/{id}",
    response_model=ApiResponse[UserSchema],
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por ID",
    description="Devuelve la información detallada de un usuario específico por su ID."
)
async def get_user_by_id(
    id: UUID = Path(..., description="ID del usuario a obtener"),
    db: AsyncSession = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user_by_id(db, user_id=id, include_inactive=True)
    return ApiResponse[UserSchema](
        codigo=200,
        mensaje="Usuario obtenido exitosamente.",
        resultado=user
    )

# ---------- CREATE ----------

@router.post(
    "",
    response_model=ApiResponse[UserBasic],
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario",
    description="Crea un nuevo usuario con la información proporcionada."
)
async def create_user(
    db: AsyncSession = Depends(get_db),
    user_data: UserCreateRequest = Body(..., description="Datos del nuevo usuario"),
    service: UserService = Depends(get_user_service),
):
    new_user = await service.create_user(db, obj_in=user_data)
    return ApiResponse[UserBasic](
        codigo=201,
        mensaje="Usuario creado exitosamente.",
        resultado=UserBasic.model_validate(new_user)
    )

# ---------- UPDATE ----------

@router.put(
    "/{id}",
    response_model=ApiResponse[UserBasic],
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario por ID (Completo)",
    description="Actualiza toda la información de un usuario específico."
)
async def update_user(
    db: AsyncSession = Depends(get_db),
    id: UUID = Path(..., description="ID del usuario a actualizar"),
    user_data: UserUpdateRequest = Body(..., description="Datos completos del usuario"),
    service: UserService = Depends(get_user_service),
):
    updated_user = await service.update_user(db, user_id=id, obj_in=user_data)
    return ApiResponse[UserBasic](
        codigo=200,
        mensaje="Usuario actualizado exitosamente.",
        resultado=UserBasic.model_validate(updated_user)
    )

@router.patch(
    "/{id}",
    response_model=ApiResponse[UserBasic],
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente usuario por ID",
    description="Actualiza solo los campos enviados del usuario."
)
async def partial_update_user(
    db: AsyncSession = Depends(get_db),
    id: UUID = Path(..., description="ID del usuario a actualizar parcialmente"),
    user_data: UserPartialUpdateRequest = Body(..., description="Datos parciales del usuario"),
    service: UserService = Depends(get_user_service),
):
    updated_user = await service.update_user(db, user_id=id, obj_in=user_data)
    return ApiResponse[UserBasic](
        codigo=200,
        mensaje="Usuario actualizado parcialmente exitosamente.",
        resultado=UserBasic.model_validate(updated_user)
    )

@router.patch(
    "/{id}/activate",
    response_model=ApiResponse[UserToggleActiveResult],
    status_code=status.HTTP_200_OK,
    summary="Activar un usuario",
    description="Activa a un usuario que se encontraba inactivo o eliminado lógicamente."
)
async def activate_user(
    db: AsyncSession = Depends(get_db),
    id: UUID = Path(..., description="ID del usuario a activar"),
    service: UserService = Depends(get_user_service),
):
    user = await service.activate_user(db, user_id=id)
    return ApiResponse[UserToggleActiveResult](
        codigo=200,
        mensaje="Usuario activado exitosamente.",
        resultado=UserToggleActiveResult.model_validate(user)
    )

@router.patch(
    "/{id}/deactivate",
    response_model=ApiResponse[UserToggleActiveResult],
    status_code=status.HTTP_200_OK,
    summary="Desactivar un usuario",
    description="Desactiva a un usuario sin eliminarlo del sistema."
)
async def deactivate_user(
    db: AsyncSession = Depends(get_db),
    id: UUID = Path(..., description="ID del usuario a desactivar"),
    reason: Optional[str] = Query(None, description="Motivo de la desactivación"),
    service: UserService = Depends(get_user_service),
):
    user = await service.deactivate_user(db, user_id=id, reason=reason)
    return ApiResponse[UserToggleActiveResult](
        codigo=200,
        mensaje="Usuario desactivado exitosamente.",
        resultado=UserToggleActiveResult.model_validate(user)
    )

@router.post(
    "/{id}/change-password",
    response_model=ApiResponseSimple,
    status_code=status.HTTP_200_OK,
    summary="Cambiar contraseña",
    description="Cambia la contraseña del usuario previa validación de la actual."
)
async def change_user_password(
    db: AsyncSession = Depends(get_db),
    id: UUID = Path(..., description="ID del usuario"),
    password_data: PasswordChangeRequest = Body(...),
    service: UserService = Depends(get_user_service),
):
    await service.change_password(
        db, 
        user_id=id, 
        current_password=password_data.current_password, 
        new_password=password_data.new_password
    )
    return ApiResponseSimple(
        codigo=200,
        mensaje="Contraseña cambiada exitosamente.",
        resultado={}
    )

# ---------- DELETE & RESTORE ----------

@router.delete(
    "/{id}",
    response_model=ApiResponse[UserDeleteResult],
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario por ID",
    description="Realiza borrado lógico (por defecto) o físico si hard=true."
)
async def delete_user(
    db: AsyncSession = Depends(get_db),
    id: UUID = Path(..., description="ID del usuario a eliminar"),
    hard: bool = Query(False, description="Si es True, realiza borrado físico"),
    reason: Optional[str] = Query(None, description="Motivo de la eliminación"),
    service: UserService = Depends(get_user_service),
    current_user_id: UUID = Depends(get_current_user_id_flexible)
):
    deleted_user = await service.delete_user(
        db, 
        user_id=id, 
        hard_delete=hard, 
        deleted_by=current_user_id,
        reason=reason
    )
    
    # En caso de borrado físico exitoso, deleted_user podría ser None o el objeto borrado
    return ApiResponse[UserDeleteResult](
        codigo=200,
        mensaje="Usuario eliminado exitosamente.",
        resultado=UserDeleteResult.model_validate(deleted_user) if deleted_user else {"id": id, "is_deleted": True}
    )

@router.patch(
    "/{id}/restore",
    response_model=ApiResponse[UserRestoreResult],
    status_code=status.HTTP_200_OK,
    summary="Restaurar usuario por ID",
    description="Restaura un usuario que fue borrado de forma lógica."
)
async def restore_user(
    db: AsyncSession = Depends(get_db),
    id: UUID = Path(..., description="ID del usuario a restaurar"),
    service: UserService = Depends(get_user_service),
):
    restored_user = await service.restore_user(db, user_id=id)
    return ApiResponse[UserRestoreResult](
        codigo=200,
        mensaje="Usuario restaurado exitosamente.",
        resultado=UserRestoreResult.model_validate(restored_user)
    )

