from typing import Optional, Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreateRequest, ProductPartialUpdateRequest
from app.core.exceptions.product_exceptions import (
    ProductNotFoundException,
    ProductAlreadyExistsException,
    ProductNotDeletedException,
    ProductAlreadyDeletedException,
    ProductAlreadyActiveException,
    ProductAlreadyInactiveException,
)


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        """
        Inicializa el servicio de productos con su repositorio correspondiente.
        """
        self.product_repo = product_repository

    async def create_product(self, db: AsyncSession, *, obj_in: ProductCreateRequest) -> Product:
        """
        Gestiona el registro de nuevos productos validando duplicidad de nombre y product_key.
        """
        # 1. Verificar si el nombre ya está registrado
        product_exists = await self.product_repo.get_by_name(db, name=obj_in.name)
        if product_exists:
            raise ProductAlreadyExistsException(conflict_type="name", value=obj_in.name)

        # 2. Verificar si la clave de producto ya está en uso
        if obj_in.product_key:
            key_exists = await self.product_repo.get_by_product_key(db, product_key=obj_in.product_key)
            if key_exists:
                raise ProductAlreadyExistsException(conflict_type="product_key", value=obj_in.product_key)

        # 3. Crear el producto utilizando el repositorio genérico
        return await self.product_repo.create(db, obj_in=obj_in)

    async def get_product_by_id(
        self, db: AsyncSession, *, product_id: Any, include_deleted: bool = False
    ) -> Product:
        """
        Retorna un producto por su ID o lanza una excepción 404 si no existe.
        """
        product = await self.product_repo.get(db, id=product_id)
        if not product:
            raise ProductNotFoundException(product_id=product_id)

        # Si no se permiten eliminados y el producto lo está
        if not include_deleted and product.is_deleted:
            raise ProductNotFoundException(product_id=product_id)

        return product

    async def get_multi_products(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "created_at",
        order: str = "desc",
        search: Optional[str] = None,
        status: Optional[bool] = None,
        type: Optional[str] = None,
        is_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        Obtiene una lista paginada de productos con filtros de búsqueda, estado y tipo.
        """
        return await self.product_repo.get_multi_products(
            db,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order,
            search=search,
            status=status,
            type=type,
            is_deleted=is_deleted
        )

    async def update_product(
        self, db: AsyncSession, *, product_id: Any, obj_in: Any
    ) -> Product:
        """
        Actualiza la información de un producto existente.
        """
        db_obj = await self.get_product_by_id(db, product_id=product_id)

        update_data = obj_in.model_dump(exclude_unset=True)

        # Validar unicidad de nombre si se está cambiando
        if "name" in update_data and update_data["name"] != db_obj.name:
            existing = await self.product_repo.get_by_name(db, name=update_data["name"])
            if existing:
                raise ProductAlreadyExistsException(conflict_type="name", value=update_data["name"])

        # Validar unicidad de product_key si se está cambiando
        if "product_key" in update_data and update_data["product_key"] and update_data["product_key"] != db_obj.product_key:
            existing = await self.product_repo.get_by_product_key(db, product_key=update_data["product_key"])
            if existing:
                raise ProductAlreadyExistsException(conflict_type="product_key", value=update_data["product_key"])

        return await self.product_repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def delete_product(
        self,
        db: AsyncSession,
        *,
        product_id: Any,
        hard_delete: bool = False
    ) -> Optional[Product]:
        """
        Elimina un producto. Puede ser física (hard_delete) o lógica (soft_delete).
        """
        db_obj = await self.get_product_by_id(db, product_id=product_id, include_deleted=True)

        if hard_delete:
            return await self.product_repo.remove(db, id=product_id)

        # Evitar doble eliminación lógica
        if db_obj.is_deleted:
            raise ProductAlreadyDeletedException()

        return await self.product_repo.soft_delete(db, product_id=product_id)

    async def restore_product(self, db: AsyncSession, *, product_id: Any) -> Product:
        """
        Restaura un producto eliminado lógicamente.
        """
        db_obj = await self.get_product_by_id(db, product_id=product_id, include_deleted=True)

        if not db_obj.is_deleted:
            raise ProductNotDeletedException()

        # Restaurar estado y limpiar campos de auditoría de borrado
        update_data = {
            "is_deleted": False,
            "status": True,
            "deleted_at": None,
        }
        return await self.product_repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def activate_product(self, db: AsyncSession, *, product_id: Any) -> Product:
        """
        Activa (hace disponible) un producto que se encontraba no disponible.
        """
        db_obj = await self.get_product_by_id(db, product_id=product_id, include_deleted=True)

        if db_obj.status and not db_obj.is_deleted:
            raise ProductAlreadyActiveException()

        update_data = {
            "status": True,
            "is_deleted": False,
        }
        return await self.product_repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def deactivate_product(self, db: AsyncSession, *, product_id: Any) -> Product:
        """
        Desactiva (hace no disponible) un producto sin eliminarlo.
        """
        db_obj = await self.get_product_by_id(db, product_id=product_id)

        if not db_obj.status:
            raise ProductAlreadyInactiveException()

        return await self.product_repo.update(db, db_obj=db_obj, obj_in={"status": False})
