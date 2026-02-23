from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserPartialUpdateRequest
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, UserCreateRequest, UserPartialUpdateRequest]):
    def __init__(self):
        """
        Inicializa el repositorio de usuarios heredando las funciones
        base del repositorio genérico.
        """
        super().__init__(User)

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """
        Busca un usuario en la base de datos por su nombre de usuario único.
        """
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Busca un usuario en la base de datos por su dirección de correo electrónico.
        """
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi_users(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "created_at",
        order: str = "desc",
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_deleted: bool = False
    ) -> Dict[str, Any]:
        """
        Versión especializada para usuarios que incluye filtros de estado y búsqueda en campos específicos.
        """
        filters = {"is_deleted": is_deleted}
        if is_active is not None:
            filters["is_active"] = is_active
            
        return await self.get_multi(
            db,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order,
            filters=filters,
            search=search,
            search_fields=["username", "email", "first_name", "last_name"]
        )

    async def soft_delete(self, db: AsyncSession, *, user_id: Any, **kwargs) -> Optional[User]:
        """
        Implementación de eliminación lógica específica para usuarios.
        """
        return await self.soft_remove(db, id=user_id, **kwargs)

    async def is_active(self, user: User) -> bool:
        """
        Verifica si el usuario se encuentra activo en el sistema.
        """
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """
        Verifica si el usuario cuenta con privilegios de administrador.
        """
        return user.is_superuser

