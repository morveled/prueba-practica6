# tests/test_user_repository_final.py
import asyncio
import sys
from pathlib import Path
from uuid import uuid4, UUID
from datetime import datetime
from typing import Dict, Any

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User
from app.repositories.user_repository import UserRepository, get_user_repository


class TestUserRepositoryFinal:
    """Suite de pruebas completa para UserRepository (tu versión)"""
    
    @classmethod
    async def setup_class(cls):
        """Configuración inicial para todas las pruebas"""
        # Base de datos en memoria para pruebas
        DATABASE_URL = "sqlite+aiosqlite:///:memory:"
        
        # Crear engine
        cls.engine = create_async_engine(
            DATABASE_URL, 
            echo=False, 
            connect_args={"check_same_thread": False}
        )
        
        # Crear sesión factory
        cls.async_session = sessionmaker(
            cls.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Crear tablas
        async with cls.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        print("🚀 CONFIGURACIÓN INICIAL COMPLETADA")
        print(f"📦 Base de datos: {DATABASE_URL}")
    
    async def setup_method(self):
        """Configuración antes de cada prueba"""
        self.session = self.async_session()
        self.repository = UserRepository(self.session)
        print(f"\n{'='*60}")
        print(f"🧪 INICIANDO NUEVA PRUEBA")
    
    async def teardown_method(self):
        """Limpieza después de cada prueba"""
        await self.session.rollback()  # Rollback para limpiar cambios
        await self.session.close()
        print("✅ Sesión limpiada")
    
    @classmethod
    async def teardown_class(cls):
        """Limpieza final"""
        await cls.engine.dispose()
        print("🔧 Engine cerrado")
    
    # ========== PRUEBAS DE CREACIÓN ==========
    
    async def test_01_add_user(self):
        """Prueba básica de creación de usuario"""
        print("📝 Probando add()...")
        
        # Crear usuario manualmente (como lo haría el servicio)
        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="hashed_password_123",
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow(),
            date_joined=datetime.utcnow(),
            email_verified=False,
            is_active=True,
            is_deleted=False
        )
        
        # Persistir con el repositorio
        saved_user = await self.repository.add(user)
        
        # Verificaciones
        assert saved_user is not None
        assert saved_user.id == user.id
        assert saved_user.email == "test@example.com"
        assert saved_user.username == "testuser"
        assert saved_user.first_name == "Test"
        assert saved_user.last_name == "User"
        assert saved_user.password == "hashed_password_123"
        assert saved_user.is_active is True
        assert saved_user.is_deleted is False
        
        print(f"✅ Usuario creado: {saved_user.id}")
        print(f"   Email: {saved_user.email}")
        print(f"   Username: {saved_user.username}")
        
        return saved_user
    
    async def test_02_create_multiple_users(self):
        """Prueba creación de múltiples usuarios"""
        print("👥 Creando múltiples usuarios...")
        
        users = []
        for i in range(5):
            user = User(
                id=uuid4(),
                email=f"user{i}@example.com",
                username=f"user{i}",
                first_name=f"First{i}",
                last_name=f"Last{i}",
                password=f"hashed_{i}",
                created_at=datetime.utcnow(),
                modified_at=datetime.utcnow(),
                date_joined=datetime.utcnow(),
                is_active=(i % 2 == 0),  # Alternar activos
                is_deleted=False
            )
            saved_user = await self.repository.add(user)
            users.append(saved_user)
        
        print(f"✅ {len(users)} usuarios creados")
        return users
    
    # ========== PRUEBAS DE LECTURA ==========
    
    async def test_03_get_by_id(self):
        """Prueba obtener usuario por ID"""
        print("🔍 Probando get_by_id()...")
        
        # Crear usuario de prueba
        user = await self._create_test_user(
            email="getbyid@example.com",
            username="getbyiduser",
            first_name="Get",
            last_name="ByID"
        )
        
        # Obtener por ID
        retrieved = await self.repository.get_by_id(user.id)
        
        # Verificaciones
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.email == user.email
        
        # Probar con ID inexistente
        non_existent = await self.repository.get_by_id(uuid4())
        assert non_existent is None
        
        print("✅ get_by_id funciona correctamente")
    
    async def test_04_get_active_by_id(self):
        """Prueba obtener usuario activo por ID"""
        print("🔍 Probando get_active_by_id()...")
        
        # Crear usuario activo
        active_user = await self._create_test_user(
            email="active@example.com",
            username="activeuser",
            first_name="Active",
            last_name="User",
            is_active=True,
            is_deleted=False
        )
        
        # Crear usuario inactivo
        inactive_user = await self._create_test_user(
            email="inactive@example.com",
            username="inactiveuser",
            first_name="Inactive",
            last_name="User",
            is_active=False,
            is_deleted=False
        )
        
        # Crear usuario eliminado
        deleted_user = await self._create_test_user(
            email="deleted@example.com",
            username="deleteduser",
            first_name="Deleted",
            last_name="User",
            is_active=False,
            is_deleted=True
        )
        
        # Verificar que solo el activo es retornado
        active_result = await self.repository.get_active_by_id(active_user.id)
        assert active_result is not None
        
        inactive_result = await self.repository.get_active_by_id(inactive_user.id)
        assert inactive_result is None
        
        deleted_result = await self.repository.get_active_by_id(deleted_user.id)
        assert deleted_result is None
        
        print("✅ get_active_by_id filtra correctamente")
    
    async def test_05_get_by_email(self):
        """Prueba obtener usuario por email"""
        print("📧 Probando get_by_email()...")
        
        # Crear usuario
        user = await self._create_test_user(
            email="emailtest@example.com",
            username="emailuser",
            first_name="Email",
            last_name="User"
        )
        
        # Obtener por email
        result = await self.repository.get_by_email("emailtest@example.com")
        assert result is not None
        assert result.id == user.id
        
        # Con active_only=False debería encontrar aunque esté inactivo
        inactive_user = await self._create_test_user(
            email="inactive_email@example.com",
            username="inactiveemailuser",
            first_name="InactiveEmail",
            last_name="User",
            is_active=False
        )
        
        result_inactive = await self.repository.get_by_email(
            "inactive_email@example.com",
            active_only=False
        )
        assert result_inactive is not None
        
        result_inactive_active_only = await self.repository.get_by_email(
            "inactive_email@example.com",
            active_only=True
        )
        assert result_inactive_active_only is None
        
        print("✅ get_by_email funciona con ambos modos")
    
    async def test_06_get_by_username(self):
        """Prueba obtener usuario por username"""
        print("👤 Probando get_by_username()...")
        
        user = await self._create_test_user(
            email="usernametest@example.com",
            username="testusername",
            first_name="Username",
            last_name="Test"
        )
        
        result = await self.repository.get_by_username("testusername")
        assert result is not None
        assert result.username == "testusername"
        
        print("✅ get_by_username funciona")
    
    async def test_07_get_multi_basic(self):
        """Prueba básica de get_multi con paginación"""
        print("📊 Probando get_multi() básico...")
        
        # Limpiar usuarios previos
        await self._clean_users()
        
        # Crear 15 usuarios
        for i in range(15):
            await self._create_test_user(
                email=f"multiuser{i}@example.com",
                username=f"multiuser{i}",
                first_name=f"Multi{i}",
                last_name=f"User{i}"
            )
        
        # Obtener primera página
        users_page1, total1 = await self.repository.get_multi(
            skip=0,
            limit=10
        )
        
        # Verificaciones
        assert len(users_page1) == 10
        assert total1 == 15
        
        # Segunda página
        users_page2, total2 = await self.repository.get_multi(
            skip=10,
            limit=10
        )
        
        assert len(users_page2) == 5
        assert total2 == total1
        
        print(f"✅ Paginación: Página 1={len(users_page1)}, Página 2={len(users_page2)}, Total={total1}")
    
    async def test_08_get_multi_with_filters(self):
        """Prueba get_multi con filtros"""
        print("🔍 Probando get_multi() con filtros...")
        
        await self._clean_users()
        
        # Crear usuarios con diferentes estados
        for i in range(3):
            await self._create_test_user(
                email=f"filter_active{i}@example.com",
                username=f"filteractive{i}",
                first_name=f"Active{i}",
                last_name=f"User{i}",
                is_active=True
            )
        
        for i in range(2):
            await self._create_test_user(
                email=f"filter_inactive{i}@example.com",
                username=f"filterinactive{i}",
                first_name=f"Inactive{i}",
                last_name=f"User{i}",
                is_active=False
            )
        
        # IMPORTANTE: Desactivar active_only para poder filtrar inactivos
        # Filtrar solo activos - CON active_only=False
        filters_active = {"is_active": True}
        active_users, active_total = await self.repository.get_multi(
            filters=filters_active,
            limit=100,
            active_only=False  # <-- IMPORTANTE: Desactivar para ver inactivos
        )
        
        print(f"DEBUG: Encontrados {len(active_users)} usuarios activos")
        for user in active_users:
            print(f"  - {user.username}: active={user.is_active}")
        
        assert len(active_users) == 3, f"Esperaba 3 activos, obtuve {len(active_users)}"
        assert all(user.is_active for user in active_users)
        
        # Filtrar inactivos
        filters_inactive = {"is_active": False}
        inactive_users, inactive_total = await self.repository.get_multi(
            filters=filters_inactive,
            limit=100,
            active_only=False  # <-- IMPORTANTE: Desactivar
        )
        
        print(f"DEBUG: Encontrados {len(inactive_users)} usuarios inactivos")
        for user in inactive_users:
            print(f"  - {user.username}: active={user.is_active}")
        
        assert len(inactive_users) == 2, f"Esperaba 2 inactivos, obtuve {len(inactive_users)}"
        assert all(not user.is_active for user in inactive_users)
        
        # TEST ADICIONAL: Verificar que active_only=True funciona
        # Por defecto (active_only=True) debería devolver solo activos
        default_users, default_total = await self.repository.get_multi(
            limit=100,
            active_only=True  # <-- Valor por defecto
        )
        
        print(f"DEBUG: Por defecto (active_only=True): {default_total} usuarios")
        assert all(user.is_active for user in default_users)
        assert all(not user.is_deleted for user in default_users)
        
        print(f"✅ Filtros: Activos={active_total}, Inactivos={inactive_total}")
        print("✅ Sesión limpiada")
        return True 
        
    async def test_09_get_multi_with_search(self):
        """Prueba get_multi con búsqueda"""
        print("🔎 Probando get_multi() con búsqueda...")
        
        await self._clean_users()
        
        # Crear usuarios con patrones específicos
        await self._create_test_user(
            email="john.doe@company.com",
            username="johndoe",
            first_name="John",
            last_name="Doe"
        )
        
        await self._create_test_user(
            email="jane.doe@company.com",
            username="janedoe",
            first_name="Jane",
            last_name="Doe"
        )
        
        await self._create_test_user(
            email="other.user@example.com",
            username="otheruser",
            first_name="Other",
            last_name="User"
        )
        
        # Buscar "doe"
        users_doe, total_doe = await self.repository.get_multi(
            search="doe",
            limit=100
        )
        
        assert total_doe == 2
        emails = {user.email for user in users_doe}
        assert "john.doe@company.com" in emails
        assert "jane.doe@company.com" in emails
        
        # Buscar "john"
        users_john, total_john = await self.repository.get_multi(
            search="john",
            limit=100
        )
        
        assert total_john == 1
        assert users_john[0].email == "john.doe@company.com"
        
        print(f"✅ Búsqueda: 'doe'={total_doe} resultados, 'john'={total_john} resultado")
    
    async def test_10_get_multi_sorting(self):
        """Prueba get_multi con ordenamiento"""
        print("📈 Probando get_multi() con ordenamiento...")
        
        await self._clean_users()
        
        # Crear usuarios con diferentes fechas
        import time
        users_data = [
            ("oldest@example.com", "oldestuser", "Oldest", "User", 3),
            ("middle@example.com", "middleuser", "Middle", "User", 2),
            ("newest@example.com", "newestuser", "Newest", "User", 1),
        ]

        for email, username, first_name, last_name, days_ago in users_data:
            user = User(
                id=uuid4(),
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                password="hashed",
                created_at=datetime.now().replace(
                    day=datetime.now().day - days_ago
                ),
                modified_at=datetime.now(),
                date_joined=datetime.now(),
                is_active=True, 
                is_deleted=False
            )
            await self.repository.add(user)
        
        # Orden ascendente (más antiguo primero)
        users_asc, _ = await self.repository.get_multi(
            sort_by="created_at",
            sort_order="asc",
            limit=100
        )
        
        assert users_asc[0].email == "oldest@example.com"
        assert users_asc[-1].email == "newest@example.com"
        
        # Orden descendente (más nuevo primero)
        users_desc, _ = await self.repository.get_multi(
            sort_by="created_at",
            sort_order="desc",
            limit=100
        )
        
        assert users_desc[0].email == "newest@example.com"
        assert users_desc[-1].email == "oldest@example.com"
        
        print("✅ Ordenamiento funciona correctamente")
    
    # ========== PRUEBAS DE ACTUALIZACIÓN ==========
    
    async def test_11_update_user(self):
        """Prueba actualización de usuario"""
        print("✏️ Probando update()...")
        
        user = await self._create_test_user(
            email="update@example.com",
            username="updateuser",
            first_name="Update",
            last_name="User"
        )
        
        original_modified = user.modified_at
        
        # Modificar algunos campos
        user.email = "updated@example.com"
        user.username = "updateduser"
        user.first_name = "Updated"
        user.last_name = "Name"
        
        # Aplicar update
        updated_user = await self.repository.update(user)
        
        # Verificaciones
        assert updated_user.email == "updated@example.com"
        assert updated_user.username == "updateduser"
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.modified_at > original_modified
        
        print("✅ update() funciona correctamente")
    
    async def test_12_update_by_id(self):
        """Prueba update_by_id (método de conveniencia)"""
        print("✏️ Probando update_by_id()...")
        
        user = await self._create_test_user(
            email="updatebyid@example.com",
            username="updatebyiduser",
            first_name="UpdateBy",
            last_name="ID"
        )
        
        update_data = {
            "email": "updated_by_id@example.com",
            "username": "updatedbyid",
            "first_name": "Updated By",
            "last_name": "ID"
        }
        
        updated_user = await self.repository.update_by_id(user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.email == "updated_by_id@example.com"
        assert updated_user.username == "updatedbyid"
        assert updated_user.first_name == "Updated By"
        assert updated_user.last_name == "ID"
        
        # Probar con usuario inexistente
        non_existent_update = await self.repository.update_by_id(
            uuid4(),
            {"email": "test@test.com"}
        )
        assert non_existent_update is None
        
        print("✅ update_by_id() funciona")
    
    # ========== PRUEBAS DE ELIMINACIÓN ==========
    
    async def test_13_soft_delete(self):
        """Prueba eliminación lógica"""
        print("🗑️ Probando soft_delete()...")
        
        user = await self._create_test_user(
            email="softdelete@example.com",
            username="softdeleteuser",
            first_name="Soft",
            last_name="Delete"
        )
        
        # Soft delete
        deleted_user = await self.repository.soft_delete(user)
        
        assert deleted_user.is_deleted is True
        assert deleted_user.is_active is False
        assert deleted_user.deleted_at is not None
        
        # Verificar que no aparece en get_active_by_id
        active_user = await self.repository.get_active_by_id(user.id)
        assert active_user is None
        
        # Verificar que sí aparece en get_by_id
        full_user = await self.repository.get_by_id(user.id)
        assert full_user is not None
        
        print("✅ soft_delete() funciona")
    
    async def test_14_soft_delete_by_id(self):
        """Prueba soft_delete_by_id"""
        print("🗑️ Probando soft_delete_by_id()...")
        
        user = await self._create_test_user(
            email="softdeleteid@example.com",
            username="softdeleteiduser",
            first_name="SoftID",
            last_name="Delete"
        )
        
        deleted = await self.repository.soft_delete_by_id(user.id)
        assert deleted is not None
        assert deleted.is_deleted is True
        
        # Probar con ID inexistente
        non_existent = await self.repository.soft_delete_by_id(uuid4())
        assert non_existent is None
        
        print("✅ soft_delete_by_id() funciona")
    
    async def test_15_hard_delete(self):
        """Prueba eliminación física"""
        print("💥 Probando hard_delete()...")
        
        user = await self._create_test_user(
            email="harddelete@example.com",
            username="harddeleteuser",
            first_name="Hard",
            last_name="Delete"
        )
        
        user_id = user.id
        
        # Verificar que existe
        exists_before = await self.repository.exists_by_email("harddelete@example.com")
        assert exists_before is True
        
        # Hard delete
        await self.repository.hard_delete(user)
        
        # Verificar que ya no existe
        exists_after = await self.repository.exists_by_email("harddelete@example.com")
        assert exists_after is False
        
        # Verificar con get_by_id
        retrieved = await self.repository.get_by_id(user_id)
        assert retrieved is None
        
        print("✅ hard_delete() funciona")
    
    async def test_16_hard_delete_by_id(self):
        """Prueba hard_delete_by_id"""
        print("💥 Probando hard_delete_by_id()...")
        
        user = await self._create_test_user(
            email="harddeleteid@example.com",
            username="harddeleteiduser",
            first_name="HardID",
            last_name="Delete"
        )
        
        # Eliminar
        result = await self.repository.hard_delete_by_id(user.id)
        assert result is True
        
        # Verificar eliminado
        retrieved = await self.repository.get_by_id(user.id)
        assert retrieved is None
        
        # Probar con ID inexistente
        non_existent_result = await self.repository.hard_delete_by_id(uuid4())
        assert non_existent_result is False
        
        print("✅ hard_delete_by_id() funciona")
    
    # ========== PRUEBAS DE EXISTENCIA ==========
    
    async def test_17_exists_methods(self):
        """Prueba métodos exists_by_*"""
        print("🔍 Probando métodos exists...")
        
        await self._clean_users()
        
        # Crear usuarios
        await self._create_test_user(
            email="exists@example.com",
            username="existsuser",
            first_name="Exists",
            last_name="User"
        )
        
        # exists_by_email
        email_exists = await self.repository.exists_by_email("exists@example.com")
        assert email_exists is True
        
        email_not_exists = await self.repository.exists_by_email("nonexistent@example.com")
        assert email_not_exists is False
        
        # exists_by_username
        username_exists = await self.repository.exists_by_username("existsuser")
        assert username_exists is True
        
        username_not_exists = await self.repository.exists_by_username("nonexistentuser")
        assert username_not_exists is False
        
        # Probar con active_only=False
        inactive_user = await self._create_test_user(
            email="inactive_exists@example.com",
            username="inactiveexists",
            first_name="InactiveExists",
            last_name="User",
            is_active=False
        )
        
        exists_active_only = await self.repository.exists_by_email(
            "inactive_exists@example.com",
            active_only=True
        )
        assert exists_active_only is False
        
        exists_all = await self.repository.exists_by_email(
            "inactive_exists@example.com",
            active_only=False
        )
        assert exists_all is True
        
        print("✅ Métodos exists funcionan correctamente")
    
    # ========== PRUEBAS DE CONTEO ==========
    
    async def test_18_count_users(self):
        """Prueba método count()"""
        print("📊 Probando count()...")
        
        await self._clean_users()
        
        # Crear usuarios para contar
        for i in range(3):
            await self._create_test_user(
                email=f"count{i}@example.com",
                username=f"countuser{i}",
                first_name=f"Count{i}",
                last_name=f"User{i}",
                is_active=True
            )
        
        for i in range(2):
            await self._create_test_user(
                email=f"count_inactive{i}@example.com",
                username=f"countinactive{i}",
                first_name=f"CountInactive{i}",
                last_name=f"User{i}",
                is_active=False
            )
        
        # Contar todos los activos
        total_active = await self.repository.count(active_only=True)
        assert total_active == 3
        
        # Contar todos (incluyendo inactivos)
        total_all = await self.repository.count(active_only=False)
        assert total_all == 5
        
        # Contar con filtros
        filters = {"is_active": False}
        total_inactive = await self.repository.count(
            filters=filters,
            active_only=False
        )
        assert total_inactive == 2
        
        print(f"✅ Count: Activos={total_active}, Todos={total_all}, Inactivos={total_inactive}")
    
    # ========== PRUEBAS DE INYECCIÓN DE DEPENDENCIAS ==========
    
    async def test_19_dependency_injection(self):
        """Prueba la función factory de inyección de dependencias"""
        print("🏭 Probando get_user_repository()...")
        
        repo = await get_user_repository(self.session)
        
        assert repo is not None
        assert isinstance(repo, UserRepository)
        assert repo.session == self.session
        
        # Probar que funciona
        user = await self._create_test_user(
            email="dependency@example.com",
            username="dependencyuser",
            first_name="Dependency",
            last_name="Test"
        )
        
        retrieved = await repo.get_by_id(user.id)
        assert retrieved is not None
        
        print("✅ Inyección de dependencias funciona")
    
    # ========== PRUEBAS DE INTEGRACIÓN ==========
    
    async def test_20_integration_workflow(self):
        """Prueba un flujo completo de integración"""
        print("🔄 Probando flujo completo...")
        
        # 1. Crear usuario
        user = User(
            id=uuid4(),
            email="workflow@example.com",
            username="workflowuser",
            first_name="Workflow",
            last_name="User",
            password="hashed_workflow",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            date_joined=datetime.now(),
            is_active=True,
            is_deleted=False
        )
        
        saved_user = await self.repository.add(user)
        assert saved_user.id is not None
        
        # 2. Verificar que existe
        exists = await self.repository.exists_by_email("workflow@example.com")
        assert exists is True
        
        # 3. Obtener el usuario
        retrieved = await self.repository.get_by_id(saved_user.id)
        assert retrieved is not None
        
        # 4. Actualizar
        retrieved.first_name = "Workflow"
        retrieved.last_name = "Test"
        updated = await self.repository.update(retrieved)
        assert updated.first_name == "Workflow"
        
        # 5. Buscar en lista
        users, total = await self.repository.get_multi(
            search="workflow",
            limit=100
        )
        assert total >= 1
        
        # 6. Eliminar lógicamente
        soft_deleted = await self.repository.soft_delete_by_id(saved_user.id)
        assert soft_deleted.is_deleted is True
        
        # 7. Verificar que no aparece en búsquedas activas
        active_users, active_total = await self.repository.get_multi(
            active_only=True,
            limit=100
        )
        assert all(u.email != "workflow@example.com" for u in active_users)
        
        print("✅ Flujo completo funciona correctamente")
    
    # ========== MÉTODOS AUXILIARES ==========
    
    async def _create_test_user(
        self,
        email: str,
        username: str,
        first_name: str,
        last_name: str,
        is_active: bool = True,
        is_deleted: bool = False
    ) -> User:
        """Método auxiliar para crear usuarios de prueba"""
        user = User(
            id=uuid4(),
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=f"hashed_{username}",
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow(),
            date_joined=datetime.utcnow(),
            is_active=is_active,
            is_deleted=is_deleted
        )
        return await self.repository.add(user)
    
    async def _clean_users(self):
        """Limpia todos los usuarios (para pruebas aisladas)"""
        users, _ = await self.repository.get_multi(limit=1000, active_only=False)
        for user in users:
            await self.repository.hard_delete(user)


async def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*70)
    print("🧪 TESTING USER REPOSITORY - VERSIÓN FINAL")
    print("="*70)
    
    test_suite = TestUserRepositoryFinal()
    
    # Lista ordenada de pruebas
    test_methods = [
        test_suite.test_01_add_user,
        test_suite.test_02_create_multiple_users,
        test_suite.test_03_get_by_id,
        test_suite.test_04_get_active_by_id,
        test_suite.test_05_get_by_email,
        test_suite.test_06_get_by_username,
        test_suite.test_07_get_multi_basic,
        test_suite.test_08_get_multi_with_filters,
        test_suite.test_09_get_multi_with_search,
        test_suite.test_10_get_multi_sorting,
        test_suite.test_11_update_user,
        test_suite.test_12_update_by_id,
        test_suite.test_13_soft_delete,
        test_suite.test_14_soft_delete_by_id,
        test_suite.test_15_hard_delete,
        test_suite.test_16_hard_delete_by_id,
        test_suite.test_17_exists_methods,
        test_suite.test_18_count_users,
        test_suite.test_19_dependency_injection,
        test_suite.test_20_integration_workflow,
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    try:
        # Configuración inicial
        await test_suite.setup_class()
        
        # Ejecutar cada prueba
        for i, test_method in enumerate(test_methods, 1):
            try:
                print(f"\n{'─'*50}")
                print(f"PRUEBA {i:02d}/{len(test_methods)}: {test_method.__name__}")
                print(f"{'─'*50}")
                
                await test_suite.setup_method()
                await test_method()
                await test_suite.teardown_method()
                
                passed += 1
                print(f"✅ PASÓ")
                
            except AssertionError as e:
                failed += 1
                errors.append(f"❌ {test_method.__name__}: AssertionError - {str(e)}")
                print(f"❌ FALLÓ: {e}")
                
            except Exception as e:
                failed += 1
                errors.append(f"💥 {test_method.__name__}: {type(e).__name__} - {str(e)}")
                print(f"💥 ERROR: {type(e).__name__}: {e}")
                
    finally:
        # Limpieza final
        await test_suite.teardown_class()
        
        # Mostrar resumen
        print("\n" + "="*70)
        print("📊 RESUMEN FINAL DE PRUEBAS")
        print("="*70)
        print(f"✅ PASADAS: {passed}")
        print(f"❌ FALLADAS: {failed}")
        print(f"📈 TOTAL EJECUTADAS: {len(test_methods)}")
        print(f"🎯 PORCENTAJE: {(passed/len(test_methods))*100:.1f}%")
        
        if errors:
            print(f"\n📋 ERRORES DETALLADOS:")
            for error in errors:
                print(f"  {error}")
        
        if failed == 0:
            print(f"\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
            print("✨ El repositorio está listo para producción")
        else:
            print(f"\n⚠️  {failed} prueba(s) fallaron - Revisar los errores")
        
        print(f"\n{'='*70}")


if __name__ == "__main__":
    # Ejecutar pruebas
    asyncio.run(run_all_tests())