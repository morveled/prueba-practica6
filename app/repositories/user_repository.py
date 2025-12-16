from typing import Optional, Tuple, List, Dict, Any
from uuid import UUID
from sqlmodel import select, func, and_, or_, desc, asc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest, UserPartialUpdateRequest


class UserRepository: #repositorio para operaciones CRUD de usuarios en la base de datos (Cada repositorio recibe una sesión de BD que comparte con otros repositorios)
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_multi( #metodo para obtener una lista paginada de usuarios con múltiples opciones de filtrado
        self,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None,
        is_deleted: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        email_verified: Optional[bool] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> Tuple[List[User], int]:
        """Obtiene múltiples usuarios con paginación y filtros."""
        
        # Query base
        query = select(User) #SELECT * FROM users
        
        # Aplicar filtros
        filters = []
        if is_active is not None:
            filters.append(User.is_active == is_active)
        if is_deleted is not None:
            filters.append(User.is_deleted == is_deleted)
        if is_superuser is not None:
            filters.append(User.is_superuser == is_superuser)
        if email_verified is not None:
            filters.append(User.email_verified == email_verified)
        
        # Solo usuarios no eliminados por defecto
        if is_deleted is None:
            filters.append(User.is_deleted == False)
        
        if filters: #aplicar filtros al query si existen  
            query = query.where(and_(*filters)) #WHERE filter1 AND filter2 AND ...
        
        # Contar total para paginación
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.exec(count_query)
        total = total_result.one() #obtener el conteo total de usuarios que cumplen los filtros
        
        # Ordenar resultados por columna y orden especificados
        sort_column = getattr(User, sort_by, User.created_at)
        if order.lower() == "desc": 
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Paginar 
        query = query.offset(skip).limit(limit)
        
        # Ejecutar
        result = await self.session.exec(query)
        users = result.all() #obtener la lista de usuarios
        
        return users, total
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        query = select(User).where(User.id == user_id)
        result = await self.session.exec(query)
        return result.first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su email."""
        query = select(User).where(User.email == email)
        result = await self.session.exec(query)
        return result.first()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por su username."""
        query = select(User).where(User.username == username)
        result = await self.session.exec(query)
        return result.first()
    
    async def create(self, user_data: UserCreateRequest, hashed_password: str) -> User:
        """Crea un nuevo usuario."""
        from datetime import datetime
        
        db_user = User(
            **user_data.model_dump(exclude={"password"}), #excluir el campo password ya que se usará el hashed_password
            password=hashed_password, #almacenar la contraseña hasheada
            created_at=datetime.now(), 
            modified_at=datetime.now(),
            date_joined=datetime.now(),
        )
        
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user
    
    async def update(self, user_id: UUID, user_data: UserUpdateRequest) -> Optional[User]: #actualiza un usuario existente según los datos proporcionados
        """Actualiza un usuario existente."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # Actualizar campos dinámicamente
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.modified_at = datetime.now() #actualizar la fecha de modificación
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update_password(self, user_id: UUID, hashed_password: str) -> Optional[User]: 
        """Actualiza la contraseña de un usuario."""
        user = await self.get_by_id(user_id) #obtener el usuario por su ID
        if not user:
            return None
        
        user.password = hashed_password #establecer la nueva contraseña hasheada
        user.modified_at = datetime.now() #actualizar la fecha de modificación
        
        self.session.add(user) 
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def soft_delete(self, user_id: UUID) -> Optional[User]:
        """Eliminación lógica de un usuario."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        #modificar los campos 
        user.is_deleted = True
        user.deleted_at = datetime.now()
        user.modified_at = datetime.now()
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def restore(self, user_id: UUID) -> Optional[User]:
        """Restaura un usuario eliminado lógicamente."""
        user = await self.get_by_id(user_id) #obtener el usuario por su ID
        if not user:
            return None
        
        user.is_deleted = False
        user.deleted_at = None
        user.modified_at = datetime.now()
        
        self.session.add(user) #agregar el usuario modificado a la sesión
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def toggle_active(self, user_id: UUID) -> Optional[User]:
        """Alterna el estado activo/inactivo de un usuario."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        user.is_active = not user.is_active #alternar el estado activo
        user.modified_at = datetime.now()
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def verify_email(self, user_id: UUID) -> Optional[User]: #que marca el email como verificado
        """Marca el email como verificado."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        user.email_verified = True
        user.email_verified_at = datetime.now()
        user.modified_at = datetime.now()
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user