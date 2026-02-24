from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.product import Product
from app.schemas.product import ProductCreateRequest, ProductPartialUpdateRequest
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product, ProductCreateRequest, ProductPartialUpdateRequest]):
    def __init__(self):
        """
        Inicializa el repositorio de productos heredando las funciones
        base del repositorio genérico.
        """
        super().__init__(Product)

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Product]:
        """
        Busca un producto en la base de datos por su nombre.
        """
        statement = select(Product).where(Product.name == name)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_product_key(self, db: AsyncSession, *, product_key: str) -> Optional[Product]:
        """
        Busca un producto en la base de datos por su clave de producto.
        """
        statement = select(Product).where(Product.product_key == product_key)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

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
        Versión especializada para productos que incluye filtros de estado,
        tipo y búsqueda en campos específicos.
        """
        filters: Dict[str, Any] = {"is_deleted": is_deleted}
        if status is not None:
            filters["status"] = status
        if type is not None:
            filters["type"] = type

        return await self.get_multi(
            db,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order,
            filters=filters,
            search=search,
            search_fields=["name", "description", "product_key"]
        )

    async def soft_delete(self, db: AsyncSession, *, product_id: Any, **kwargs) -> Optional[Product]:
        """
        Implementación de eliminación lógica específica para productos.
        """
        return await self.soft_remove(db, id=product_id, **kwargs)
