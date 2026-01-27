"""Excepciones personalizadas de la aplicación."""

class AppException(Exception):
    """Excepción base de la aplicación."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# ========== EXCEPCIONES DE USUARIO ==========
class UserNotFoundException(AppException):
    """Usuario no encontrado."""
    def __init__(self, message: str = "Usuario no encontrado"):
        super().__init__(message, status_code=404)

class UserAlreadyExistsException(AppException):
    """Usuario ya existe."""
    def __init__(self, message: str = "Usuario ya existe"):
        super().__init__(message, status_code=409)

class InvalidCredentialsException(AppException):
    """Credenciales inválidas."""
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(message, status_code=401)

class InactiveUserException(AppException):
    """Usuario inactivo."""
    def __init__(self, message: str = "Usuario inactivo"):
        super().__init__(message, status_code=403)

class PermissionDeniedException(AppException):
    """Permiso denegado."""
    def __init__(self, message: str = "Permiso denegado"):
        super().__init__(message, status_code=403)

# ========== EXCEPCIONES DE AUTENTICACIÓN ==========
class TokenExpiredException(AppException):
    """Token expirado."""
    def __init__(self, message: str = "Token expirado"):
        super().__init__(message, status_code=401)

class InvalidTokenException(AppException):
    """Token inválido."""
    def __init__(self, message: str = "Token inválido"):
        super().__init__(message, status_code=401)