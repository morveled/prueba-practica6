"""
Test completo para UserService
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Dict, Any

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
    UserPartialUpdateRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    Gender
)
#from app.core.exceptions import (
#    UserAlreadyExistsException,
#    UserNotFoundException,
#    InvalidCredentialsException,
#    InactiveUserException
#)
from app.core.exceptions.user_exceptions import UserNotFoundException


class TestUserService:
    """Suite de tests para UserService."""
    
    def __init__(self):
        self.engine = None
        self.session = None
        self.repository = None
        self.service = None
    
    async def setup(self):
        """Configuración inicial antes de cada test."""
        # Crear engine en memoria
        DATABASE_URL = "sqlite+aiosqlite:///:memory:"
        self.engine = create_async_engine(DATABASE_URL, echo=False)

        
        # Crear tablas
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        # Crear sesión, repositorio y servicio
        self.session = AsyncSession(self.engine, expire_on_commit=False)
        self.repository = UserRepository(self.session)
        self.service = UserService(self.repository)
    
    async def teardown(self):
        """Limpieza después de cada test."""
        if self.session:
            await self.session.close()
        if self.engine:
            self.engine.dispose()
    
    async def _create_test_user(
        self, 
        username: str = "testuser",
        email: str = "test@example.com",
        first_name: str = "Test",
        last_name: str = "User",
        password: str = "Password123!",
        is_active: bool = True,
        is_deleted: bool = False
    ) -> User:
        """Crea un usuario de prueba directamente en la base de datos."""
        from app.core.security import get_password_hash
        
        now = datetime.now(timezone.utc)
        
        user = User(
            #id=str(uuid4()),
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=get_password_hash(password),
            is_active=is_active,
            is_superuser=False,
            created_at=now,
            modified_at=now,
            date_joined=now,
            is_deleted=is_deleted,
            deleted_at=now if is_deleted else None,
            email_verified=False,
            email_verified_at=None,
            last_login=None,
            profile_picture=None,
            nationality=None,
            occupation=None,
            date_of_birth=None,
            contact_phone_number=None,
            gender=None,
            address=None,
            address_number=None,
            address_interior_number=None,
            address_complement=None,
            address_neighborhood=None,
            address_zip_code=None,
            address_city=None,
            address_state=None,
            role=None
        )
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def _clean_users(self):
        """Limpia todos los usuarios de la base de datos."""
        users = await self.repository.get_multi(limit=1000, active_only=False)
        for user in users[0]:
            await self.session.delete(user)
        await self.session.commit()
    
    # ============================================
    # TESTS DE REGISTRO Y AUTENTICACIÓN
    # ============================================
    
    async def test_01_register_user_success(self):
        """Test de registro exitoso de usuario."""
        print("📝 Probando register_user() exitoso...")
        
        user_data = UserCreateRequest(
            username="newuser",
            email="newuser@example.com",
            first_name="New",
            last_name="User",
            password="SecurePassword123!",
            is_active=True,
            is_superuser=False
        )
        
        user = await self.service.register_user(user_data)
        
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.is_active == True
        assert user.is_deleted == False
        
        print(f"✅ Usuario registrado: {user.id}")
        return True
    
    async def test_02_register_user_duplicate_email(self):
        """Test de registro con email duplicado."""
        print("📧 Probando register_user() con email duplicado...")
        
        # Crear usuario primero
        await self._create_test_user(
            username="existinguser",
            email="existing@example.com",
            first_name="Existing",
            last_name="User"
        )
        
        # Intentar registrar con mismo email
        user_data = UserCreateRequest(
            username="newuser2",
            email="existing@example.com",  # Email duplicado
            first_name="New",
            last_name="User",
            password="Password123!",
            is_active=True
        )
        
        try:
            await self.service.register_user(user_data)
            assert False, "Debería haber lanzado UserAlreadyExistsException"
        except UserAlreadyExistsException as e:
            assert "email" in str(e).lower()
            print(f"✅ Correctamente rechazado: {e}")
            return True
    
    async def test_03_register_user_duplicate_username(self):
        """Test de registro con username duplicado."""
        print("👤 Probando register_user() con username duplicado...")
        
        # Crear usuario primero
        await self._create_test_user(
            username="existinguser",
            email="unique@example.com",
            first_name="Existing",
            last_name="User"
        )
        
        # Intentar registrar con mismo username
        user_data = UserCreateRequest(
            username="existinguser",  # Username duplicado
            email="newemail@example.com",
            first_name="New",
            last_name="User",
            password="Password123!",
            is_active=True
        )
        
        try:
            await self.service.register_user(user_data)
            assert False, "Debería haber lanzado UserAlreadyExistsException"
        except UserAlreadyExistsException as e:
            assert "username" in str(e).lower()
            print(f"✅ Correctamente rechazado: {e}")
            return True
    
    async def test_04_authenticate_user_success(self):
        """Test de autenticación exitosa."""
        print("🔐 Probando authenticate_user() exitoso...")
        
        # Crear usuario con contraseña conocida
        password = "MySecurePassword123!"
        user = await self._create_test_user(
            username="authuser",
            email="auth@example.com",
            first_name="Auth",
            last_name="User",
            password=password
        )
        
        # Autenticar
        authenticated_user, token = await self.service.authenticate_user(
            email="auth@example.com",
            password=password
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert token is not None
        assert len(token) > 0
        
        print(f"✅ Usuario autenticado: {authenticated_user.username}")
        print(f"✅ Token generado: {token[:20]}...")
        return True
    
    async def test_05_authenticate_user_wrong_password(self):
        """Test de autenticación con contraseña incorrecta."""
        print("❌ Probando authenticate_user() con contraseña incorrecta...")
        
        await self._create_test_user(
            username="wrongpassuser",
            email="wrongpass@example.com",
            first_name="Wrong",
            last_name="Pass",
            password="CorrectPassword123!"
        )
        
        try:
            await self.service.authenticate_user(
                email="wrongpass@example.com",
                password="WrongPassword123!"  # Contraseña incorrecta
            )
            assert False, "Debería haber lanzado InvalidCredentialsException"
        except InvalidCredentialsException as e:
            print(f"✅ Correctamente rechazado: {e}")
            return True
    
    async def test_06_authenticate_user_inactive(self):
        """Test de autenticación de usuario inactivo."""
        print("⏸️ Probando authenticate_user() con usuario inactivo...")
        
        await self._create_test_user(
            username="inactiveuser",
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            password="Password123!",
            is_active=False  # Usuario inactivo
        )
        
        try:
            await self.service.authenticate_user(
                email="inactive@example.com",
                password="Password123!"
            )
            assert False, "Debería haber lanzado InactiveUserException"
        except InactiveUserException as e:
            print(f"✅ Correctamente rechazado: {e}")
            return True
    
    # ============================================
    # TESTS DE CONSULTA
    # ============================================
    
    async def test_07_get_user_by_id_success(self):
        """Test de obtención de usuario por ID."""
        print("🔍 Probando get_user_by_id() exitoso...")
        
        user = await self._create_test_user(
            username="getbyiduser",
            email="getbyid@example.com",
            first_name="GetById",
            last_name="User"
        )
        
        retrieved = await self.service.get_user_by_id(user.id)
        
        assert retrieved is not None
        assert retrieved.id == user.id
        assert retrieved.username == "getbyiduser"
        assert retrieved.email == "getbyid@example.com"
        
        print(f"✅ Usuario encontrado por ID: {retrieved.username}")
        return True
    
    async def test_08_get_user_by_id_not_found(self):
        """Test de obtención de usuario por ID no existente."""
        print("🔍 Probando get_user_by_id() no encontrado...")
        
        non_existent_id = uuid4()
        
        try:
            await self.service.get_user_by_id(non_existent_id)
            assert False, "Debería haber lanzado UserNotFoundException"
        except UserNotFoundException as e:
            print(f"✅ Correctamente rechazado: {e}")
            return True
    
    async def test_09_get_user_by_email_success(self):
        """Test de obtención de usuario por email."""
        print("📧 Probando get_user_by_email() exitoso...")
        
        await self._create_test_user(
            username="emailuser",
            email="emailsearch@example.com",
            first_name="Email",
            last_name="Search"
        )
        
        user = await self.service.get_user_by_email("emailsearch@example.com")
        
        assert user is not None
        assert user.email == "emailsearch@example.com"
        assert user.username == "emailuser"
        
        print(f"✅ Usuario encontrado por email: {user.username}")
        return True
    
    async def test_10_list_users_basic(self):
        """Test de listado básico de usuarios."""
        print("📋 Probando list_users() básico...")
        
        await self._clean_users()
        
        # Crear varios usuarios
        for i in range(5):
            await self._create_test_user(
                username=f"listuser{i}",
                email=f"listuser{i}@example.com",
                first_name=f"List{i}",
                last_name="User"
            )
        
        users, total = await self.service.list_users(
            skip=0,
            limit=10,
            include_inactive=False
        )
        
        assert len(users) == 5
        assert total == 5
        assert all(user.is_active for user in users)
        
        print(f"✅ Listados {len(users)} de {total} usuarios")
        return True
    
    async def test_11_list_users_with_search(self):
        """Test de listado con búsqueda."""
        print("🔎 Probando list_users() con búsqueda...")
        
        await self._clean_users()
        
        # Crear usuarios con diferentes emails
        await self._create_test_user(
            username="searchuser1",
            email="buscador1@example.com",
            first_name="Search",
            last_name="One"
        )
        
        await self._create_test_user(
            username="otheruser",
            email="other@example.com",
            first_name="Other",
            last_name="User"
        )
        
        # Buscar por texto
        users, total = await self.service.list_users(
            search="buscador",
            limit=10
        )
        
        assert len(users) == 1
        assert users[0].email == "buscador1@example.com"
        
        print(f"✅ Búsqueda encontrada: {total} usuario(s)")
        return True
    
    async def test_12_list_users_with_filters(self):
        """Test de listado con filtros."""
        print("🔍 Probando list_users() con filtros...")
        
        await self._clean_users()
        
        # Crear usuarios con diferentes estados
        await self._create_test_user(
            username="activefilter",
            email="activefilter@example.com",
            first_name="Active",
            last_name="Filter",
            is_active=True
        )
        
        await self._create_test_user(
            username="inactivefilter",
            email="inactivefilter@example.com",
            first_name="Inactive",
            last_name="Filter",
            is_active=False
        )
        
        # Filtrar por activos
        active_users, active_total = await self.service.list_users(
            filters={"is_active": True},
            include_inactive=True
        )
        
        assert len(active_users) == 1
        assert active_users[0].username == "activefilter"
        
        # Filtrar por inactivos
        inactive_users, inactive_total = await self.service.list_users(
            filters={"is_active": False},
            include_inactive=True
        )
        
        assert len(inactive_users) == 1
        assert inactive_users[0].username == "inactivefilter"
        
        print(f"✅ Filtros funcionando: {active_total} activos, {inactive_total} inactivos")
        return True
    
    # ============================================
    # TESTS DE ACTUALIZACIÓN
    # ============================================
    
    async def test_13_update_user_full_success(self):
        """Test de actualización completa de usuario."""
        print("✏️ Probando update_user_full() exitoso...")
        
        user = await self._create_test_user(
            username="updateuser",
            email="update@example.com",
            first_name="Update",
            last_name="User",
            password="OldPassword123!"
        )
        
        current_user_id = user.id  # Simular que el mismo usuario se actualiza
        
        update_data = UserUpdateRequest(
            username="updateduser",
            email="updated@example.com",
            first_name="Updated",
            last_name="Name",
            password="NewPassword123!",
            is_active=True,
            is_superuser=False,
            profile_picture="https://example.com/avatar.jpg",
            nationality="Mexican",
            occupation="Developer",
            gender=Gender.MALE,
            role="user"
        )
        
        updated_user = await self.service.update_user_full(
            user_id=user.id,
            update_data=update_data,
            current_user_id=current_user_id
        )
        
        assert updated_user.username == "updateduser"
        assert updated_user.email == "updated@example.com"
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.nationality == "Mexicana"
        assert updated_user.occupation == "Developer"
        
        print(f"✅ Usuario actualizado: {updated_user.username}")
        return True
    
    async def test_14_update_user_partial_success(self):
        """Test de actualización parcial de usuario."""
        print("✏️ Probando update_user_partial() exitoso...")
        
        user = await self._create_test_user(
            username="partialuser",
            email="partial@example.com",
            first_name="Partial",
            last_name="User"
        )
        
        current_user_id = user.id
        
        update_data = UserPartialUpdateRequest(
            first_name="PartiallyUpdated",
            last_name="LastName",
            occupation="Engineer"
        )
        
        updated_user = await self.service.update_user_partial(
            user_id=user.id,
            update_data=update_data,
            current_user_id=current_user_id
        )
        
        assert updated_user.first_name == "PartiallyUpdated"
        assert updated_user.last_name == "LastName"
        assert updated_user.occupation == "Engineer"
        # Campos no actualizados deben permanecer igual
        assert updated_user.username == "partialuser"
        assert updated_user.email == "partial@example.com"
        
        print(f"✅ Actualización parcial exitosa")
        return True
    
    async def test_15_change_password_success(self):
        """Test de cambio de contraseña exitoso."""
        print("🔒 Probando change_password() exitoso...")
        
        from app.core.security import verify_password
        
        user = await self._create_test_user(
            username="changepass",
            email="changepass@example.com",
            first_name="Change",
            last_name="Pass",
            password="OldPassword123!"
        )
        
        password_data = PasswordChangeRequest(
            current_password="OldPassword123!",
            new_password="NewSecurePassword456!",
            confirm_password="NewSecurePassword456!"
        )
        
        updated_user = await self.service.change_password(
            user_id=user.id,
            password_data=password_data
        )
        
        # Verificar que la nueva contraseña funciona
        assert verify_password("NewSecurePassword456!", updated_user.password)
        
        print(f"✅ Contraseña cambiada exitosamente")
        return True
    
    async def test_16_change_password_wrong_current(self):
        """Test de cambio de contraseña con contraseña actual incorrecta."""
        print("❌ Probando change_password() con contraseña actual incorrecta...")
        
        user = await self._create_test_user(
            username="wrongcurrent",
            email="wrongcurrent@example.com",
            first_name="Wrong",
            last_name="Current",
            password="CorrectPassword123!"
        )
        
        password_data = PasswordChangeRequest(
            current_password="WrongPassword123!",  # Incorrecta
            new_password="NewPassword456!",
            confirm_password="NewPassword456!"
        )
        
        try:
            await self.service.change_password(user.id, password_data)
            assert False, "Debería haber lanzado InvalidCredentialsException"
        except InvalidCredentialsException as e:
            print(f"✅ Correctamente rechazado: {e}")
            return True
    
    async def test_17_toggle_active(self):
        """Test de alternar estado activo/inactivo."""
        print("🔄 Probando toggle_active()...")
        
        user = await self._create_test_user(
            username="toggleuser",
            email="toggle@example.com",
            first_name="Toggle",
            last_name="User",
            is_active=True
        )
        
        # Desactivar
        deactivated = await self.service.toggle_active(user.id)
        assert deactivated.is_active == False
        
        # Reactivar
        reactivated = await self.service.toggle_active(user.id)
        assert reactivated.is_active == True
        
        print(f"✅ Toggle activo/inactivo funcionando")
        return True
    
    # ============================================
    # TESTS DE ELIMINACIÓN
    # ============================================
    
    async def test_18_soft_delete_user(self):
        """Test de eliminación suave de usuario."""
        print("🗑️ Probando delete_user() soft delete...")
        
        user = await self._create_test_user(
            username="deleteuser",
            email="delete@example.com",
            first_name="Delete",
            last_name="User"
        )
        
        deleted_user = await self.service.delete_user(
            user_id=user.id,
            hard_delete=False
        )
        
        assert deleted_user.is_deleted == True
        assert deleted_user.deleted_at is not None
        
        # Verificar que no aparece en listados normales
        users, total = await self.service.list_users(include_inactive=False)
        user_ids = [u.id for u in users]
        assert user.id not in user_ids
        
        print(f"✅ Usuario eliminado (soft): {deleted_user.username}")
        return True
    
    async def test_19_restore_user(self):
        """Test de restauración de usuario."""
        print("🔄 Probando restore_user()...")
        
        user = await self._create_test_user(
            username="restoreuser",
            email="restore@example.com",
            first_name="Restore",
            last_name="User",
            is_deleted=True  # Ya eliminado
        )
        
        restored_user = await self.service.restore_user(user.id)
        
        assert restored_user.is_deleted == False
        assert restored_user.deleted_at is None
        assert restored_user.is_active == True
        
        # Verificar que ahora aparece en listados
        users, total = await self.service.list_users(include_inactive=False)
        user_ids = [u.id for u in users]
        assert user.id in user_ids
        
        print(f"✅ Usuario restaurado: {restored_user.username}")
        return True
    
    async def test_20_count_users(self):
        """Test de conteo de usuarios."""
        print("📊 Probando count_users()...")
        
        await self._clean_users()
        
        # Crear usuarios en diferentes estados
        await self._create_test_user(
            username="countactive1",
            email="countactive1@example.com",
            first_name="Count",
            last_name="Active1",
            is_active=True
        )
        
        await self._create_test_user(
            username="countactive2",
            email="countactive2@example.com",
            first_name="Count",
            last_name="Active2",
            is_active=True
        )
        
        await self._create_test_user(
            username="countinactive",
            email="countinactive@example.com",
            first_name="Count",
            last_name="Inactive",
            is_active=False
        )
        
        # Contar solo activos (por defecto)
        active_count = await self.service.count_users(include_inactive=False)
        assert active_count == 2
        
        # Contar incluyendo inactivos
        total_count = await self.service.count_users(include_inactive=True)
        assert total_count == 3
        
        # Contar con filtro
        filtered_count = await self.service.count_users(
            filters={"is_active": False},
            include_inactive=True
        )
        assert filtered_count == 1
        
        print(f"✅ Conteos: {active_count} activos, {total_count} total")
        return True
    
    # ============================================
    # TESTS DE INTEGRACIÓN
    # ============================================
    
    async def test_21_integration_workflow(self):
        """Test de flujo completo de integración."""
        print("🔄 Probando flujo de integración completo...")
        
        # 1. REGISTRO
        register_data = UserCreateRequest(
            username="workflowuser",
            email="workflow@example.com",
            first_name="Workflow",
            last_name="User",
            password="WorkflowPassword123!",
            is_active=True
        )
        
        user = await self.service.register_user(register_data)
        assert user is not None
        
        # 2. AUTENTICACIÓN
        auth_user, token = await self.service.authenticate_user(
            email="workflow@example.com",
            password="WorkflowPassword123!"
        )
        assert auth_user.id == user.id
        assert token is not None
        
        # 3. ACTUALIZACIÓN PARCIAL
        update_data = UserPartialUpdateRequest(
            occupation="Software Engineer",
            nationality="Mexicana"
        )
        
        updated = await self.service.update_user_partial(
            user_id=user.id,
            update_data=update_data,
            current_user_id=user.id
        )
        assert updated.occupation == "Software Engineer"
        
        # 4. CAMBIO DE CONTRASEÑA
        pass_data = PasswordChangeRequest(
            current_password="WorkflowPassword123!",
            new_password="NewWorkflowPassword456!",
            confirm_password="NewWorkflowPassword456!"
        )
        
        pass_changed = await self.service.change_password(user.id, pass_data)
        
        # 5. VERIFICAR NUEVA CONTRASEÑA
        new_auth, _ = await self.service.authenticate_user(
            email="workflow@example.com",
            password="NewWorkflowPassword456!"
        )
        assert new_auth.id == user.id
        
        # 6. DESACTIVAR
        deactivated = await self.service.deactivate_user(user.id)
        assert deactivated.is_active == False
        
        # 7. ACTIVAR
        activated = await self.service.activate_user(user.id)
        assert activated.is_active == True
        
        # 8. SOFT DELETE
        deleted = await self.service.delete_user(user.id, hard_delete=False)
        assert deleted.is_deleted == True
        
        # 9. RESTAURAR
        restored = await self.service.restore_user(user.id)
        assert restored.is_deleted == False
        
        print("✅ Flujo de integración completo pasado")
        return True
    
    async def test_22_verify_email(self):
        """Test de verificación de email."""
        print("✓ Probando verify_email()...")
        
        user = await self._create_test_user(
            username="verifyemail",
            email="verifyemail@example.com",
            first_name="Verify",
            last_name="Email"
        )
        
        assert user.email_verified == False
        assert user.email_verified_at is None
        
        verified_user = await self.service.verify_email(user.id)
        
        assert verified_user.email_verified == True
        assert verified_user.email_verified_at is not None
        
        print(f"✅ Email verificado: {verified_user.email}")
        return True
    
    async def test_23_request_password_reset(self):
        """Test de solicitud de restablecimiento de contraseña."""
        print("📧 Probando request_password_reset()...")
        
        # Crear usuario
        await self._create_test_user(
            username="resetuser",
            email="reset@example.com",
            first_name="Reset",
            last_name="User"
        )
        
        # Solicitar reset (debería siempre retornar True por seguridad)
        reset_data = PasswordResetRequest(email="reset@example.com")
        result = await self.service.request_password_reset(reset_data)
        
        assert result == True
        
        # También con email no existente (debería retornar True)
        reset_data2 = PasswordResetRequest(email="nonexistent@example.com")
        result2 = await self.service.request_password_reset(reset_data2)
        
        assert result2 == True
        
        print("✅ Solicitud de reset funcionando (siempre retorna True por seguridad)")
        return True
    
    # ============================================
    # EJECUTOR DE TESTS
    # ============================================
    
    async def run_test(self, test_name: str, test_func):
        """Ejecuta un test individual."""
        print(f"\n{'=' * 60}")
        print(f"🧪 PRUEBA: {test_name}")
        print(f"{'=' * 60}")
        
        try:
            await self.setup()
            result = await test_func()
            await self.teardown()
            
            if result:
                print(f"✅ {test_name}: PASÓ")
                return True, None
            else:
                print(f"❌ {test_name}: FALLÓ")
                return False, "Test falló sin excepción"
                
        except Exception as e:
            await self.teardown()
            print(f"💥 ERROR en {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, str(e)
    
    async def run_all_tests(self):
        """Ejecuta todos los tests."""
        tests = [
            ("01. Registro exitoso", self.test_01_register_user_success),
            ("02. Registro email duplicado", self.test_02_register_user_duplicate_email),
            ("03. Registro username duplicado", self.test_03_register_user_duplicate_username),
            ("04. Autenticación exitosa", self.test_04_authenticate_user_success),
            ("05. Autenticación contraseña incorrecta", self.test_05_authenticate_user_wrong_password),
            ("06. Autenticación usuario inactivo", self.test_06_authenticate_user_inactive),
            ("07. Obtener usuario por ID", self.test_07_get_user_by_id_success),
            ("08. Obtener usuario ID no existente", self.test_08_get_user_by_id_not_found),
            ("09. Obtener usuario por email", self.test_09_get_user_by_email_success),
            ("10. Listar usuarios básico", self.test_10_list_users_basic),
            ("11. Listar con búsqueda", self.test_11_list_users_with_search),
            ("12. Listar con filtros", self.test_12_list_users_with_filters),
            ("13. Actualización completa", self.test_13_update_user_full_success),
            ("14. Actualización parcial", self.test_14_update_user_partial_success),
            ("15. Cambio de contraseña", self.test_15_change_password_success),
            ("16. Cambio contraseña actual incorrecta", self.test_16_change_password_wrong_current),
            ("17. Toggle activo/inactivo", self.test_17_toggle_active),
            ("18. Soft delete", self.test_18_soft_delete_user),
            ("19. Restaurar usuario", self.test_19_restore_user),
            ("20. Contar usuarios", self.test_20_count_users),
            ("21. Flujo de integración", self.test_21_integration_workflow),
            ("22. Verificar email", self.test_22_verify_email),
            ("23. Solicitar reset de contraseña", self.test_23_request_password_reset),
        ]
        
        results = []
        for test_name, test_func in tests:
            passed, error = await self.run_test(test_name, test_func)
            results.append((test_name, passed, error))
            
            # Pequeña pausa entre tests
            await asyncio.sleep(0.05)
        
        return results


# ============================================
# PROGRAMA PRINCIPAL
# ============================================
async def main():
    print("=" * 70)
    print("🧪 TESTING USER SERVICE - PRUEBAS COMPLETAS")
    print("=" * 70)
    print("🚀 Inicializando tests...")
    print("=" * 70)
    
    tester = TestUserService()
    results = await tester.run_all_tests()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL DE PRUEBAS")
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\n✅ PASADAS: {passed}")
    print(f"❌ FALLADAS: {total - passed}")
    print(f"📈 TOTAL EJECUTADAS: {total}")
    print(f"🎯 PORCENTAJE: {(passed/total)*100:.1f}%")
    
    # Mostrar errores
    errors = [(name, error) for name, success, error in results if not success]
    if errors:
        print(f"\n📋 ERRORES DETALLADOS:")
        for name, error in errors:
            print(f"  💥 {name}: {error}")
    else:
        print(f"\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    
    print("\n" + "=" * 70)
    
    return all(success for _, success, _ in results)


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrumpidos por el usuario")
        sys.exit(1)