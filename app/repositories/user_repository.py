from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from sqlmodel import select, func, and_, or_, desc, asc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User

class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========== CREATE ==========
    async def add(self, user: User) -> User:  #no tocar
        """Persiste un usuario en la base de datos.
        Args:
            user: Instancia de User ya creada y configurada    
        Returns:
            User: Usuario persistido con ID asignado    
        Nota:
            El usuario debe venir completamente configurado desde el servicio.
            Este método solo persiste, no crea ni asigna valores.
        """
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    # ========== READ ==========
    async def get_by_id(self, user_id: UUID, include_inactive: bool = False, include_deleted: bool = False,) -> Optional[User]: #no tocar
        """
        Obtiene un usuario por ID.
        - Por defecto excluye usuarios inactivos y eliminados.
        - El filtrado se controla desde el service.
        """
        query = select(User).where(User.id == user_id)

        if not include_inactive:
            query = query.where(User.is_active == True)

        if not include_deleted:
            query = query.where(User.is_deleted == False)

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_active_by_id(self, user_id: UUID) -> Optional[User]:
        #Obtiene un usuario activo y no eliminado por ID
        query = select(User).where(
            User.id == user_id,
            User.is_deleted == False,
            User.is_active == True
        )
        result = await self.session.execute(query)
        return result.first()

    async def get_by_email(
        self, 
        email: str, 
        active_only: bool = True
    ) -> Optional[User]:
        """Obtiene un usuario por email.
        Args:
            email: Email del usuario
            active_only: Si True, solo devuelve usuarios activos y no eliminados
        """
        query = select(User).where(User.email == email)
        
        if active_only:
            query = query.where(
                User.is_deleted == False,
                User.is_active == True
            )
        
        result = await self.session.execute(query)
        #return result.first()
        return result.scalars().first()

    async def get_by_username(
        self, 
        username: str, 
        active_only: bool = True
    ) -> Optional[User]:
        """Obtiene un usuario por username.
        Args:
            username: Username del usuario
            active_only: Si True, solo devuelve usuarios activos y no eliminados
        """
        query = select(User).where(User.username == username)
        
        if active_only:
            query = query.where(
                User.is_deleted == False,
                User.is_active == True
            )
        
        result = await self.session.exec(query)
        return result.first()

    async def get_multi( #no tocar
        self,
        page: int = 1,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort: str = "created_at",
        order: str = "desc",
        is_active: Optional[bool] = None,
        is_deleted: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        email_verified: Optional[bool] = None,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> Tuple[List[User], int]:
        """Obtiene múltiples usuarios con filtros, búsqueda y paginación.
        Args:
            skip: Número de registros a saltar (paginación)
            limit: Número máximo de registros a devolver
            filters: Diccionario de filtros {campo: valor}
            sort_by: Campo por el cual ordenar
            sort_order: Orden ascendente ('asc') o descendente ('desc')
            search: Texto para buscar en email y username
            active_only: Si True, solo devuelve usuarios activos y no eliminados
        Returns:
            Tuple[List[User], int]: Lista de usuarios y total de registros
        """
        # Query base
        query = select(User)
        conditions = []
        
        # Filtro de usuarios activos por defecto
        if active_only:
            conditions.extend([
                User.is_deleted == False,
                User.is_active == True
            ])
        
        # Aplicar filtros adicionales
        if filters:
            for field, value in filters.items():
                if hasattr(User, field) and value is not None:
                    # Soporta listas para filtros IN
                    if isinstance(value, (list, tuple)):
                        conditions.append(getattr(User, field).in_(value))
                    else:
                        conditions.append(getattr(User, field) == value)
        
        # Búsqueda en email y username
        if search:
            search_condition = or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%")
            )
            conditions.append(search_condition)
        
        # Aplicar todas las condiciones
        if conditions:
            query = query.where(and_(*conditions))
        
        # Contar total de registros
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        # Usar .scalar() en lugar de .one()
        total = total_result.scalar() or 0
        total = int(total)  # Asegurar que sea int
        
        # Aplicar ordenamiento
        #sort_column = getattr(User, sort, User.created_at)
        if sort and hasattr(User, sort):
            sort_column = getattr(User, sort)
            if order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        else: 
            # Orden por defecto
            if order.lower() == "desc":
                query = query.order_by(User.created_at.desc())
            else:
                query = query.order_by(User.created_at.asc())
        
        # Aplicar paginación
        skip = (page - 1) * limit
        query = query.offset(skip).limit(limit) 
        
        # Ejecutar query
        result = await self.session.execute(query)
        users = result.scalars().all()
        
        return users, total

    # ========== UPDATE ==========
    async def update(self, user: User) -> User:  #no tocar
        """Actualiza un usuario existente.
        Args:
            user: Usuario con los campos ya modificados
        Returns:
            User: Usuario actualizado
        Nota:
            Actualiza automáticamente el campo modified_at
            El usuario debe venir con los cambios ya aplicados desde el servicio
        """
        user.modified_at = datetime.utcnow()
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    # ========== DELETE ==========
    async def soft_delete(self, user: User) -> User:  #no tocar
        """Eliminación lógica (marca como eliminado, no borra físicamente)
        Args:
            user: Usuario a eliminar
        Returns:
            User: Usuario marcado como eliminado
        """
        """Realiza soft delete de un usuario."""       
        now = datetime.now(timezone.utc)
        user.is_deleted = True
        user.deleted_at = now
        user.modified_at = now
        
        # También desactivar el usuario al eliminarlo
        user.is_active = False
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    async def soft_delete_by_id(self, user_id: UUID) -> Optional[User]:
        #Método de conveniencia para soft delete por ID
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        return await self.soft_delete(user)

    async def hard_delete(self, user: User) -> None:  #no tocar
        """Eliminación física (borra permanentemente de la BD)
        Args:
            user: Usuario a eliminar
        ADVERTENCIA:
            Esta operación es irreversible y se debe usar con precaución
        """
        await self.session.delete(user)
        await self.session.commit()

    async def hard_delete_by_id(self, user_id: UUID) -> bool:
        """Método de conveniencia para hard delete por ID
        Returns:
            bool: True si se eliminó, False si no existía
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        await self.hard_delete(user)
        return True

    # ========== METODOS SI EXISTEN ==========
    async def exists_by_email( #no tocar
        self, 
        email: str, 
        active_only: bool = True
    ) -> bool:
        """Verifica si existe un usuario con el email dado
        Args:
            email: Email a verificar
            active_only: Si True, solo considera usuarios activos
        Returns:
            bool: True si existe, False si no
        """
        query = select(User.id).where(User.email == email)
        
        if active_only:
            query = query.where(
                User.is_deleted == False,
                User.is_active == True
            )
        
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.first() is not None

    async def exists_by_username(  #no tocar
        self, 
        username: str, 
        active_only: bool = True
    ) -> bool:
        """Verifica si existe un usuario con el username dado
        Args:
            username: Username a verificar
            active_only: Si True, solo considera usuarios activos
        Returns:
            bool: True si existe, False si no
        """
        query = select(User.id).where(User.username == username)
        
        if active_only:
            query = query.where(
                User.is_deleted == False,
                User.is_active == True
            )
        
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.first() is not None

    # ==========  ==========
    async def count(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        active_only: bool = True
    ) -> int:
        """Cuenta el total de usuarios
        Args:
            filters: Filtros opcionales a aplicar
            active_only: Si True, solo cuenta usuarios activos
        Returns:
            int: Total de usuarios
        """
        query = select(func.count(User.id))
        conditions = []
        
        if active_only:
            conditions.extend([
                User.is_deleted == False,
                User.is_active == True
            ])
        
        if filters: 
            for field, value in filters.items():
                if hasattr(User, field) and value is not None:
                    conditions.append(getattr(User, field) == value)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.session.exec(query)
        return result.one()


# ========== INYECCION DE DEPENDENCIA ==========
async def get_user_repository(session: AsyncSession) -> UserRepository:
    """Factory function para inyección de dependencias
    Uso en endpoints:
        repo: UserRepository = Depends(get_user_repository)
    """
    return UserRepository(session)