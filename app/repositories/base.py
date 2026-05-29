from datetime import datetime, timezone
from typing import Generic, TypeVar, Type, Optional, List, Any, Union, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select, func, or_, and_
from sqlalchemy import desc, asc
from pydantic.networks import AnyUrl

# Definición de tipos genéricos para el Modelo y los Esquemas
ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=Any)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=Any)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Repositorio base con operaciones CRUD fundamentales.
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Obtiene un registro por su clave primaria."""
        return await db.get(self.model, id)

    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        limit: int = 10,
        sort_by: str = "created_at",
        order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene una lista paginada de registros con filtros y búsqueda avanzada.
        """
        skip = (page - 1) * limit
        
        # Consulta base
        query = select(self.model)
        conditions = []

        # 1. Filtros exactos o por lista (IN)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    if isinstance(value, (list, tuple)):
                        conditions.append(getattr(self.model, field).in_(value))
                    else:
                        conditions.append(getattr(self.model, field) == value)

        # 2. Búsqueda global (ilike)
        if search and search_fields:
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    search_conditions.append(getattr(self.model, field).ilike(f"%{search}%"))
            if search_conditions:
                conditions.append(or_(*search_conditions))

        # Aplicar condiciones
        if conditions:
            query = query.where(and_(*conditions))

        # 3. Ordenamiento
        order_fn = desc if order.lower() == "desc" else asc
        if hasattr(self.model, sort_by):
            query = query.order_by(order_fn(getattr(self.model, sort_by)))
        
        # 4. Paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecución
        result = await db.execute(query)
        items = result.scalars().all()

        # 5. Conteo total (respetando filtros)
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": items
        }

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Crea un nuevo registro en la base de datos."""
        obj_in_data = {
            k: str(v) if isinstance(v, AnyUrl) else v
            for k, v in obj_in.model_dump().items()
        }
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Actualiza un registro existente."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        # Si el modelo tiene modified_at, lo actualizamos
        if hasattr(db_obj, "modified_at"):
            db_obj.modified_at = datetime.now(timezone.utc)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType:
        """Elimina un registro de forma física."""
        obj = await db.get(self.model, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def soft_remove(self, db: AsyncSession, *, id: Any, **kwargs) -> Optional[ModelType]:
        """
        Realiza una eliminación lógica si el modelo lo permite.
        """
        obj = await db.get(self.model, id)
        if not obj:
            return None
            
        # Solo aplicamos lógica si existen los campos correspondientes
        if hasattr(obj, "is_deleted"):
            obj.is_deleted = True
        if hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.now(timezone.utc)
        if hasattr(obj, "is_active"):
            obj.is_active = False
            
        # Aplicamos cualquier otro campo adicional pasado por kwargs
        for field, value in kwargs.items():
            if hasattr(obj, field):
                setattr(obj, field, value)

        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

