from typing import Optional
from uuid import UUID
from app.core.exceptions.base import AppException

class UserNotFoundException(AppException):
    """Lanzada cuando un usuario solicitado no existe por su ID."""
    def __init__(self, user_id: Optional[UUID] = None):
        self.user_id = user_id
        super().__init__(
            message="Usuario no encontrado.",
            code=404
        )

class UserAlreadyExistsException(AppException):
    """Lanzada cuando el email o el username ya están en uso."""
    def __init__(self, conflict_type: Optional[str] = None, value: Optional[str] = None):
        if conflict_type == "email":
            message = f"El email {value} ya está registrado"
        elif conflict_type == "username":
            message = f"El username {value} ya está en uso"
        else:
            message = "El usuario ya existe"

        super().__init__(message=message, code=409)

class UserNotDeletedException(AppException):
    """Lanzada al intentar restaurar un usuario que no estaba eliminado."""
    def __init__(self):
        super().__init__(
            message="El usuario no estaba eliminado",
            code=400
        )

class EmailAlreadyVerifiedException(AppException):
    """Lanzada al intentar verificar un email que ya lo estaba."""
    def __init__(self):
        super().__init__(
            message="El email ya estaba verificado.",
            code=400
        )

class UserAlreadyActiveException(AppException):
    """Lanzada al intentar activar un usuario que ya está activo."""
    def __init__(self):
        super().__init__(
            message="El usuario ya estaba activo.",
            code=400
        )

class UserAlreadyInactiveException(AppException):
    """Lanzada al intentar desactivar un usuario que ya está inactivo."""
    def __init__(self):
        super().__init__(
            message="El usuario ya estaba desactivado.",
            code=400
        )

class InvalidCredentialsException(AppException):
    """Lanzada cuando las credenciales de inicio de sesión son incorrectas."""
    def __init__(self):
        super().__init__(
            message="Datos inválidos o la contraseña actual no coincide.",
            code=401
        )

class PasswordMismatchException(AppException):
    """Lanzada cuando las nuevas contraseñas no coinciden en el cambio de clave."""
    def __init__(self):
        super().__init__(
            message="Las nuevas contraseñas no coinciden.",
            code=400
        )

class EmailNotVerifiedException(AppException):
    """Lanzada al intentar operaciones que requieren email verificado."""
    def __init__(self):
        super().__init__(
            message="El email no ha sido verificado.",
            code=400
        )

class EmailNotFoundException(AppException):
    """Lanzada cuando no se encuentra una cuenta asociada a un email."""
    def __init__(self):
        super().__init__(
            message="No se encontró una cuenta con ese email.",
            code=404
        )

